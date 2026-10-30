# Copyright (c) 2026, Norte Inteligente SpA and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, today

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []

MANDANTE = "Minera de Prueba RD"
# Usuarios inventados para las pruebas (no son personas reales).
SUPERVISOR = "supervisor.prueba@example.com"
REVISOR = "revisor.prueba@example.com"


def asegurar_usuario(correo, rol):
	if not frappe.db.exists("User", correo):
		usuario = frappe.get_doc(
			{"doctype": "User", "email": correo, "first_name": "Prueba", "send_welcome_email": 0}
		)
		usuario.append("roles", {"role": rol})
		usuario.insert()


def nuevo_contrato(estado="Vigente"):
	if not frappe.db.exists("Mandante", MANDANTE):
		frappe.get_doc({"doctype": "Mandante", "mandante_nombre": MANDANTE}).insert()
	contrato = frappe.get_doc(
		{
			"doctype": "Contrato",
			"numero_contrato": "RD-CT-" + frappe.generate_hash(length=8),
			"nombre_contrato": "Contrato de prueba para reportes",
			"mandante": MANDANTE,
			"faena": "Faena de prueba",
			"fecha_inicio": "2026-01-01",
			"fecha_termino": "2027-12-31",
			"estado": estado,
		}
	)
	if estado == "Vigente":
		contrato.append(
			"partidas",
			{
				"item": "1.1",
				"descripcion": "Excavación",
				"unidad": "m3",
				"cantidad": 100,
				"precio_unitario": 1000,
			},
		)
		contrato.append(
			"partidas",
			{"item": "1.2", "descripcion": "Relleno", "unidad": "m3", "cantidad": 50, "precio_unitario": 800},
		)
	return contrato.insert()


def nuevo_reporte(contrato, fecha="2026-10-01", avances=None, **campos):
	reporte = frappe.get_doc(
		{"doctype": "Reporte Diario", "contrato": contrato.name, "fecha": fecha, "turno": "Día", **campos}
	)
	for item, cantidad in avances or []:
		reporte.append("avances", {"item": item, "cantidad": cantidad})
	return reporte


class IntegrationTestReporteDiario(IntegrationTestCase):
	def setUp(self):
		asegurar_usuario(SUPERVISOR, "Supervisor de Terreno")
		asegurar_usuario(REVISOR, "Administrador de Contratos")
		self.contrato = nuevo_contrato()

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_r1_contrato_no_vigente(self):
		borrador = nuevo_contrato(estado="Borrador")
		with self.assertRaises(frappe.ValidationError):
			nuevo_reporte(borrador).insert()

	def test_r2_fecha_fuera_del_plazo(self):
		with self.assertRaises(frappe.ValidationError):
			nuevo_reporte(self.contrato, fecha="2025-12-31").insert()

	def test_r3_fecha_futura(self):
		with self.assertRaises(frappe.ValidationError):
			nuevo_reporte(self.contrato, fecha=add_days(today(), 1)).insert()

	def test_r4_reporte_repetido(self):
		nuevo_reporte(self.contrato).insert()
		with self.assertRaises(frappe.DuplicateEntryError):
			nuevo_reporte(self.contrato).insert()

	def test_r4_otro_turno_si_se_permite(self):
		nuevo_reporte(self.contrato).insert()
		noche = nuevo_reporte(self.contrato, turno="Noche").insert()
		self.assertTrue(noche.name)

	def test_r5_item_inexistente(self):
		with self.assertRaisesRegex(frappe.ValidationError, "9.9"):
			nuevo_reporte(self.contrato, avances=[("9.9", 10)]).insert()

	def test_r6_avance_negativo(self):
		with self.assertRaises(frappe.ValidationError):
			nuevo_reporte(self.contrato, avances=[("1.1", -5)]).insert()

	def test_r7_copia_descripcion_y_unidad(self):
		reporte = nuevo_reporte(self.contrato, avances=[("1.1", 10)]).insert()
		fila = reporte.avances[0]
		self.assertEqual((fila.descripcion, fila.unidad, fila.cantidad_contratada), ("Excavación", "m3", 100))

	def test_r8_acumulado_que_excede_se_guarda_marcado(self):
		primero = nuevo_reporte(self.contrato, fecha="2026-10-01", avances=[("1.1", 60)]).insert()
		segundo = nuevo_reporte(self.contrato, fecha="2026-10-02", avances=[("1.1", 50)]).insert()
		self.assertEqual(primero.avances[0].acumulado, 60)
		self.assertFalse(primero.avances[0].excede_contrato)
		self.assertEqual(segundo.avances[0].acumulado, 110)
		self.assertTrue(segundo.avances[0].excede_contrato)

	def test_r8_acumulado_ignora_reportes_posteriores(self):
		nuevo_reporte(self.contrato, fecha="2026-10-05", avances=[("1.2", 30)]).insert()
		anterior = nuevo_reporte(self.contrato, fecha="2026-10-03", avances=[("1.2", 10)]).insert()
		self.assertEqual(anterior.avances[0].acumulado, 10)

	def test_r9_horas_persona(self):
		reporte = nuevo_reporte(self.contrato)
		reporte.append("personal", {"cargo": "Operador", "personas": 4, "horas": 12})
		reporte.append("personal", {"cargo": "Ayudante", "personas": 2, "horas": 10})
		reporte.insert()
		self.assertEqual([p.horas_persona for p in reporte.personal], [48, 20])
		self.assertEqual(reporte.total_horas_persona, 68)

	def test_r10_horas_de_equipo_por_separado(self):
		reporte = nuevo_reporte(self.contrato)
		reporte.append("equipos", {"equipo": "Excavadora", "horas_operativas": 8, "horas_espera": 2})
		reporte.append("equipos", {"equipo": "Camión aljibe", "horas_operativas": 6.5, "horas_espera": 1.5})
		reporte.insert()
		self.assertEqual(reporte.total_horas_operativas, 14.5)
		self.assertEqual(reporte.total_horas_espera, 3.5)

	def test_r11_negativos_en_personal_y_equipos(self):
		casos = (
			("personal", {"cargo": "Operador", "personas": -1, "horas": 8}),
			("personal", {"cargo": "Operador", "personas": 1, "horas": -8}),
			("equipos", {"equipo": "Excavadora", "horas_operativas": -1, "horas_espera": 0}),
			("equipos", {"equipo": "Excavadora", "horas_operativas": 1, "horas_espera": -2}),
		)
		for tabla, fila in casos:
			with self.subTest(tabla=tabla, fila=fila):
				reporte = nuevo_reporte(self.contrato, fecha="2026-09-01")
				reporte.append(tabla, fila)
				with self.assertRaises(frappe.ValidationError):
					reporte.insert()

	def test_r12_estados_en_orden(self):
		reporte = nuevo_reporte(self.contrato).insert()
		for salto in ("Enviado al mandante", "Firmado por el mandante"):
			with self.subTest(salto=salto):
				reporte.reload()
				reporte.estado = salto
				with self.assertRaises(frappe.ValidationError):
					reporte.save()

	def test_r12_reporte_nuevo_parte_en_borrador(self):
		with self.assertRaises(frappe.ValidationError):
			nuevo_reporte(self.contrato, estado="Revisado").insert()

	def test_r13_quien_llena_no_puede_revisar(self):
		frappe.set_user(SUPERVISOR)
		reporte = nuevo_reporte(self.contrato).insert()
		reporte.estado = "Revisado"
		with self.assertRaises(frappe.ValidationError):
			reporte.save()

		frappe.set_user(REVISOR)
		reporte = frappe.get_doc("Reporte Diario", reporte.name)
		reporte.estado = "Revisado"
		reporte.save()
		self.assertEqual(reporte.revisado_por, REVISOR)
		self.assertTrue(reporte.fecha_revision)

	def test_r13_volver_a_borrador_borra_la_revision(self):
		frappe.set_user(SUPERVISOR)
		reporte = nuevo_reporte(self.contrato).insert()
		frappe.set_user(REVISOR)
		reporte = frappe.get_doc("Reporte Diario", reporte.name)
		reporte.estado = "Revisado"
		reporte.save()
		reporte.estado = "Borrador"
		reporte.save()
		self.assertFalse(reporte.revisado_por)

	def enviar_al_mandante(self):
		frappe.set_user(SUPERVISOR)
		reporte = nuevo_reporte(self.contrato, avances=[("1.1", 10)]).insert()
		frappe.set_user(REVISOR)
		reporte = frappe.get_doc("Reporte Diario", reporte.name)
		reporte.estado = "Revisado"
		reporte.save()
		reporte.estado = "Enviado al mandante"
		reporte.save()
		return reporte

	def adjuntar_copia_firmada(self, reporte):
		archivo = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": "reporte-firmado.txt",
				"content": "copia firmada de prueba",
				"is_private": 1,
				"attached_to_doctype": "Reporte Diario",
				"attached_to_name": reporte.name,
			}
		).insert()
		return archivo.file_url

	def test_r14_firmado_exige_copia_y_fecha(self):
		reporte = self.enviar_al_mandante()
		reporte.estado = "Firmado por el mandante"
		with self.assertRaises(frappe.ValidationError):
			reporte.save()

		copia = self.adjuntar_copia_firmada(reporte)
		reporte.reload()
		reporte.estado = "Firmado por el mandante"
		reporte.copia_firmada = copia
		with self.assertRaises(frappe.ValidationError):
			reporte.save()

		# Un guardado fallido deja la copia en memoria desactualizada: se recarga.
		reporte.reload()
		reporte.estado = "Firmado por el mandante"
		reporte.copia_firmada = copia
		reporte.fecha_firma_mandante = "2026-10-02"
		reporte.save()
		self.assertEqual(reporte.estado, "Firmado por el mandante")

	def test_r15_firmado_no_se_modifica(self):
		reporte = self.enviar_al_mandante()
		copia = self.adjuntar_copia_firmada(reporte)
		reporte.reload()
		reporte.estado = "Firmado por el mandante"
		reporte.copia_firmada = copia
		reporte.fecha_firma_mandante = "2026-10-02"
		reporte.save()
		for cambio in ({"observaciones": "cambio después de firmar"}, {"estado": "Borrador"}):
			with self.subTest(cambio=cambio):
				reporte.reload()
				reporte.update(cambio)
				with self.assertRaises(frappe.ValidationError):
					reporte.save()

	def test_r16_formato_para_firma(self):
		reporte = nuevo_reporte(self.contrato, avances=[("1.1", 10)]).insert()
		html = frappe.get_print("Reporte Diario", reporte.name, print_format="Reporte Diario para Firma")
		for texto in (
			self.contrato.name,
			"Excavación",
			"Responsable del reporte",
			"Revisó",
			"Firma mandante",
		):
			with self.subTest(texto=texto):
				self.assertIn(texto, html)
