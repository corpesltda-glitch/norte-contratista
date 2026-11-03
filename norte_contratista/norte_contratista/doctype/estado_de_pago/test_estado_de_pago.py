# Copyright (c) 2026, Norte Inteligente SpA and Contributors
# See license.txt

# Todos los datos son inventados: los documentos reales de clientes no se guardan en el repositorio.

import frappe
from frappe.tests import IntegrationTestCase

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []

MANDANTE = "Minera de Prueba EP"

# Itemizado de tarifas mensuales (cantidad = meses) y de obra.
ITEMIZADO = [
	("1.1", "Supervisor de turno", "mes", 2, 3333333),
	("1.2", "Operadores", "mes", 2, 4500000),
	("2.1", "Camión aljibe", "mes", 2, 8000000),
	("3.1", "Excavación", "m3", 1000, 15000),
]


def nuevo_contrato(itemizado=ITEMIZADO, estado="Vigente", **campos):
	if not frappe.db.exists("Mandante", MANDANTE):
		frappe.get_doc({"doctype": "Mandante", "mandante_nombre": MANDANTE}).insert()
	contrato = frappe.get_doc(
		{
			"doctype": "Contrato",
			"numero_contrato": "EP-CT-" + frappe.generate_hash(length=8),
			"nombre_contrato": "Contrato de prueba para estados de pago",
			"mandante": MANDANTE,
			"fecha_inicio": "2026-01-01",
			"fecha_termino": "2026-12-31",
			"estado": estado,
			**campos,
		}
	)
	for item, descripcion, unidad, cantidad, precio in itemizado if estado == "Vigente" else []:
		contrato.append(
			"partidas",
			{
				"item": item,
				"descripcion": descripcion,
				"unidad": unidad,
				"cantidad": cantidad,
				"precio_unitario": precio,
			},
		)
	return contrato.insert()


def nuevo_ep(contrato, desde="2026-01-01", hasta="2026-01-31", acumulado=None, **campos):
	ep = frappe.get_doc(
		{
			"doctype": "Estado de Pago",
			"contrato": contrato.name,
			"periodo_desde": desde,
			"periodo_hasta": hasta,
			**campos,
		}
	)
	ep.insert()
	if acumulado:
		for fila in ep.partidas:
			if fila.item in acumulado:
				fila.cantidad_acumulada = acumulado[fila.item]
		ep.save()
	return ep


def aprobar(ep, monto=None, **campos):
	ep.reload()
	ep.estado = "Presentado"
	ep.save()
	ep.estado = "Aprobado"
	ep.monto_aprobado = ep.neto if monto is None else monto
	ep.fecha_aprobacion = "2026-02-05"
	ep.update(campos)
	ep.save()
	return ep


def fila(ep, item):
	return next(f for f in ep.partidas if f.item == item)


class IntegrationTestEstadoDePago(IntegrationTestCase):
	def test_e1_contrato_no_vigente(self):
		contrato = nuevo_contrato(estado="Borrador")
		with self.assertRaises(frappe.ValidationError):
			nuevo_ep(contrato)

	def test_e2_numeracion_correlativa(self):
		contrato = nuevo_contrato()
		primero = aprobar(nuevo_ep(contrato, acumulado={"3.1": 100}))
		segundo = aprobar(nuevo_ep(contrato, "2026-02-01", "2026-02-28", acumulado={"3.1": 200}))
		tercero = nuevo_ep(contrato, "2026-03-01", "2026-03-31")
		self.assertEqual([primero.numero, segundo.numero, tercero.numero], [1, 2, 3])
		otro = nuevo_ep(nuevo_contrato())
		self.assertEqual(otro.numero, 1)

	def test_e3_no_se_abre_otro_ep(self):
		contrato = nuevo_contrato()
		nuevo_ep(contrato)
		with self.assertRaises(frappe.ValidationError):
			nuevo_ep(contrato, "2026-02-01", "2026-02-28")

	def test_e4_periodos(self):
		contrato = nuevo_contrato()
		with self.assertRaises(frappe.ValidationError):
			nuevo_ep(contrato, "2026-01-31", "2026-01-01")
		aprobar(nuevo_ep(contrato))
		with self.assertRaises(frappe.ValidationError):
			nuevo_ep(contrato, "2026-01-15", "2026-02-15")

	def test_e5_copia_el_itemizado(self):
		ep = nuevo_ep(nuevo_contrato())
		self.assertEqual([f.item for f in ep.partidas], ["1.1", "1.2", "2.1", "3.1"])
		excavacion = fila(ep, "3.1")
		self.assertEqual(
			(
				excavacion.descripcion,
				excavacion.unidad,
				excavacion.cantidad_contratada,
				excavacion.precio_unitario,
			),
			("Excavación", "m3", 1000, 15000),
		)
		self.assertEqual(excavacion.valor_contratado, 15000000)

	def test_e6_ep_nuevo_parte_sin_avance_del_periodo(self):
		contrato = nuevo_contrato()
		aprobar(nuevo_ep(contrato, acumulado={"3.1": 250}))
		segundo = nuevo_ep(contrato, "2026-02-01", "2026-02-28")
		self.assertEqual(fila(segundo, "3.1").cantidad_acumulada, 250)
		self.assertEqual(segundo.total_presente, 0)

	def test_e6_anterior_es_el_acumulado_aprobado(self):
		contrato = nuevo_contrato()
		aprobar(nuevo_ep(contrato, acumulado={"3.1": 250, "1.1": 1}))
		segundo = nuevo_ep(contrato, "2026-02-01", "2026-02-28", acumulado={"3.1": 600, "1.1": 2})
		excavacion = fila(segundo, "3.1")
		self.assertEqual((excavacion.cantidad_anterior, excavacion.valor_anterior), (250, 3750000))
		self.assertEqual((excavacion.cantidad_presente, excavacion.valor_presente), (350, 5250000))
		self.assertEqual(segundo.total_anterior, 3750000 + 3333333)
		self.assertEqual(segundo.total_presente, 5250000 + 3333333)

	def test_e7_acumulado_sobre_lo_contratado(self):
		with self.assertRaisesRegex(frappe.ValidationError, "3.1"):
			nuevo_ep(nuevo_contrato(), acumulado={"3.1": 1000.5})

	def test_e8_acumulado_menor_que_el_anterior(self):
		contrato = nuevo_contrato()
		aprobar(nuevo_ep(contrato, acumulado={"3.1": 300}))
		with self.assertRaises(frappe.ValidationError):
			nuevo_ep(contrato, "2026-02-01", "2026-02-28", acumulado={"3.1": 200})

	def test_e9_pesos_enteros_por_partida(self):
		ep = nuevo_ep(nuevo_contrato(), acumulado={"1.1": 0.92})
		supervisor = fila(ep, "1.1")
		# 0,92 por $3.333.333 = $3.066.666,36: la partida queda en pesos enteros.
		self.assertEqual(supervisor.valor_acumulado, 3066666)
		self.assertEqual(ep.total_presente, sum(f.valor_presente for f in ep.partidas))

	def test_e10_porcentaje_global(self):
		ep = nuevo_ep(nuevo_contrato(), modo_avance="Porcentaje global", porcentaje_global=40)
		self.assertEqual([f.cantidad_acumulada for f in ep.partidas], [0.8, 0.8, 0.8, 400])
		self.assertEqual([f.porcentaje_acumulado for f in ep.partidas], [40, 40, 40, 40])
		self.assertEqual(ep.total_presente, 2666666 + 3600000 + 6400000 + 6000000)

	def test_e11_resumen_iva_retencion(self):
		contrato = nuevo_contrato(itemizado=[("1", "Servicio a suma alzada", "gl", 1, 100000005)])
		ep = nuevo_ep(contrato, acumulado={"1": 1})
		self.assertEqual(ep.neto, 100000005)
		self.assertEqual(ep.iva, 19000001)
		self.assertEqual(ep.total_factura, 119000006)
		self.assertEqual(ep.retencion, 5000000)
		self.assertEqual(ep.liquido_a_pagar, 114000006)

	def test_e11_retencion_segun_contrato(self):
		contrato = nuevo_contrato(itemizado=[("1", "Servicio", "gl", 1, 10000000)], porcentaje_retencion=10)
		ep = nuevo_ep(contrato, acumulado={"1": 1})
		self.assertEqual(ep.retencion, 1000000)

	def test_e12_descuentos(self):
		contrato = nuevo_contrato(itemizado=[("1", "Servicio", "gl", 1, 10000000)])
		ep = nuevo_ep(contrato, acumulado={"1": 1})
		ep.descuentos = 500000
		with self.assertRaises(frappe.ValidationError):
			ep.save()
		ep.reload()
		ep.descuentos = 500000
		ep.motivo_descuentos = "Multa por atraso, cláusula de ejemplo"
		ep.save()
		self.assertEqual(ep.neto, 9500000)
		self.assertEqual(ep.iva, 1805000)

	def test_e13_estados_en_orden(self):
		ep = nuevo_ep(nuevo_contrato())
		ep.estado = "Aprobado"
		ep.monto_aprobado = ep.neto
		ep.fecha_aprobacion = "2026-02-05"
		with self.assertRaises(frappe.ValidationError):
			ep.save()

	def test_e13_rechazo_vuelve_a_borrador(self):
		ep = nuevo_ep(nuevo_contrato(), acumulado={"3.1": 100})
		ep.estado = "Presentado"
		ep.save()
		self.assertTrue(ep.fecha_presentacion)
		ep.estado = "Rechazado"
		with self.assertRaises(frappe.ValidationError):
			ep.save()
		ep.reload()
		ep.estado = "Rechazado"
		ep.motivo_rechazo = "Falta respaldo del avance"
		ep.save()
		ep.estado = "Borrador"
		ep.save()
		self.assertEqual(ep.estado, "Borrador")

	def test_e14_aprobacion_y_diferencia(self):
		ep = nuevo_ep(nuevo_contrato(), acumulado={"3.1": 100})
		ep.estado = "Presentado"
		ep.save()
		ep.estado = "Aprobado"
		with self.assertRaises(frappe.ValidationError):
			ep.save()
		ep.reload()
		ep.update({"estado": "Aprobado", "monto_aprobado": 1533450, "fecha_aprobacion": "2026-02-05"})
		with self.assertRaises(frappe.ValidationError):
			ep.save()
		ep.reload()
		ep.update(
			{
				"estado": "Aprobado",
				"monto_aprobado": 1533450,
				"fecha_aprobacion": "2026-02-05",
				"motivo_diferencia": "El mandante reconoció un adicional",
			}
		)
		ep.save()
		self.assertEqual(ep.diferencia_aprobado, 33450)

	def test_e15_aprobado_no_se_modifica(self):
		ep = aprobar(nuevo_ep(nuevo_contrato(), acumulado={"3.1": 100}))
		ep.descuentos = 1
		ep.motivo_descuentos = "intento"
		with self.assertRaises(frappe.ValidationError):
			ep.save()

	def test_e16_traer_avance_de_reportes_firmados(self):
		contrato = nuevo_contrato()
		for fecha, cantidad, estado in (
			("2026-01-10", 120, "Firmado por el mandante"),
			("2026-01-20", 80, "Firmado por el mandante"),
			("2026-01-25", 50, "Borrador"),
			("2026-02-03", 70, "Firmado por el mandante"),
		):
			reporte = frappe.get_doc(
				{"doctype": "Reporte Diario", "contrato": contrato.name, "fecha": fecha, "turno": "Día"}
			)
			reporte.append("avances", {"item": "3.1", "cantidad": cantidad})
			reporte.insert()
			# Para la prueba basta el estado final; el flujo de firma se prueba en el Reporte Diario.
			frappe.db.set_value("Reporte Diario", reporte.name, "estado", estado)
		ep = nuevo_ep(contrato)
		ep.traer_avance_de_reportes()
		ep.reload()
		# Solo los firmados hasta el 31 de enero: 120 + 80.
		self.assertEqual(fila(ep, "3.1").cantidad_acumulada, 200)
		self.assertEqual(fila(ep, "3.1").valor_acumulado, 3000000)

	def test_e17_formato_para_firma(self):
		ep = nuevo_ep(nuevo_contrato(), acumulado={"3.1": 100})
		html = frappe.get_print("Estado de Pago", ep.name, print_format="Estado de Pago para Firma")
		for texto in (
			"Estado de pago N° 1",
			"Excavación",
			"Total a facturar",
			"Líquido a pagar",
			"Administrador del contrato",
			"1.500.000",
			"10,0 %",
		):
			with self.subTest(texto=texto):
				self.assertIn(texto, html)
		# Pesos chilenos sin decimales y hoja horizontal para que quepa el detalle
		self.assertNotIn("1.500.000,00", html)
		self.assertIn("size: A4 landscape", html)
