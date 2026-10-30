# Copyright (c) 2026, Norte Inteligente SpA and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []

MANDANTE_PRUEBA = "Minera de Prueba"


def asegurar_mandante():
	if not frappe.db.exists("Mandante", MANDANTE_PRUEBA):
		frappe.get_doc({"doctype": "Mandante", "mandante_nombre": MANDANTE_PRUEBA}).insert()


def nuevo_contrato(partidas=None, **campos):
	"""Arma un contrato de prueba; partidas = [(item, descripcion, unidad, cantidad, precio), ...]."""
	asegurar_mandante()
	contrato = frappe.get_doc(
		{
			"doctype": "Contrato",
			"numero_contrato": "CT-" + frappe.generate_hash(length=8),
			"nombre_contrato": "Contrato de prueba",
			"mandante": MANDANTE_PRUEBA,
			"fecha_inicio": "2026-11-01",
			"fecha_termino": "2027-10-31",
			**campos,
		}
	)
	for item, descripcion, unidad, cantidad, precio in partidas or []:
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
	return contrato


ITEMIZADO_BASE = [
	("1.1", "Excavación masiva", "m3", 120, 15500),
	("1.2", "Relleno compactado", "m3", 80, 9800.5),
	("2.1", "Instalación de faena", "gl", 1, 2500000),
]


class IntegrationTestContrato(IntegrationTestCase):
	def test_c1_totales_de_partidas_y_contrato(self):
		contrato = nuevo_contrato(ITEMIZADO_BASE)
		contrato.insert()
		self.assertEqual([p.total for p in contrato.partidas], [1860000, 784040, 2500000])
		self.assertEqual(contrato.monto_total, 5144040)

	def test_c2_pesos_sin_decimales(self):
		contrato = nuevo_contrato([("1", "Servicio", "gl", 3, 333.33)])
		contrato.insert()
		self.assertEqual(contrato.partidas[0].total, 1000)
		self.assertEqual(contrato.monto_total, 1000)

	def test_c3_termino_antes_del_inicio(self):
		contrato = nuevo_contrato(fecha_inicio="2026-12-01", fecha_termino="2026-11-30")
		with self.assertRaises(frappe.ValidationError):
			contrato.insert()

	def test_c4_plazo_en_dias_corridos(self):
		contrato = nuevo_contrato(fecha_inicio="2026-11-01", fecha_termino="2026-11-30")
		contrato.insert()
		self.assertEqual(contrato.plazo_dias, 30)

	def test_c5_item_repetido(self):
		contrato = nuevo_contrato([("1.1", "A", "m3", 1, 100), ("1.1", "B", "m3", 1, 100)])
		with self.assertRaisesRegex(frappe.ValidationError, "1.1"):
			contrato.insert()

	def test_c6_cantidad_negativa(self):
		contrato = nuevo_contrato([("1", "A", "m3", -5, 100)])
		with self.assertRaises(frappe.ValidationError):
			contrato.insert()

	def test_c6_precio_negativo(self):
		contrato = nuevo_contrato([("1", "A", "m3", 5, -100)])
		with self.assertRaises(frappe.ValidationError):
			contrato.insert()

	def test_c7_porcentajes_fuera_de_rango(self):
		for campo, valor in (
			("porcentaje_retencion", 120),
			("porcentaje_garantia", -1),
			("tope_multas", 101),
		):
			with self.subTest(campo=campo):
				contrato = nuevo_contrato(**{campo: valor})
				with self.assertRaises(frappe.ValidationError):
					contrato.insert()

	def test_c8_valores_por_defecto(self):
		contrato = frappe.new_doc("Contrato")
		self.assertEqual(contrato.porcentaje_retencion, 5)
		self.assertEqual(contrato.porcentaje_garantia, 3)
		self.assertEqual(contrato.tope_multas, 10)
		self.assertEqual(contrato.dias_aprobacion_ep, 5)
		self.assertEqual(contrato.estado, "Borrador")
		self.assertEqual(contrato.moneda, "CLP")

	def test_c8_valores_por_defecto_son_editables(self):
		contrato = nuevo_contrato(ITEMIZADO_BASE, porcentaje_retencion=10)
		contrato.insert()
		self.assertEqual(contrato.porcentaje_retencion, 10)

	def test_c9_vigente_sin_itemizado(self):
		contrato = nuevo_contrato(estado="Vigente")
		with self.assertRaises(frappe.ValidationError):
			contrato.insert()

	def test_c9_vigente_con_itemizado(self):
		contrato = nuevo_contrato(ITEMIZADO_BASE, estado="Vigente")
		contrato.insert()
		self.assertEqual(contrato.estado, "Vigente")

	def test_c10_numero_de_contrato_repetido(self):
		primero = nuevo_contrato(ITEMIZADO_BASE)
		primero.insert()
		segundo = nuevo_contrato(ITEMIZADO_BASE, numero_contrato=primero.numero_contrato)
		with self.assertRaises(frappe.DuplicateEntryError):
			segundo.insert()

	def test_c12_medio_peso_sube(self):
		contrato = nuevo_contrato([("1", "Servicio", "gl", 1, 1000.5)])
		contrato.insert()
		self.assertEqual(contrato.monto_total, 1001)

	def test_c12_uf_con_dos_decimales(self):
		contrato = nuevo_contrato([("1", "Servicio", "gl", 0.5, 20.25)], moneda="UF")
		contrato.insert()
		self.assertEqual(contrato.monto_total, 10.13)
