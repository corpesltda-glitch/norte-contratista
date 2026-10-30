# Copyright (c) 2026, Norte Inteligente SpA and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from norte_contratista.utils.rut import digito_verificador, formatear_rut

# RUT de prueba inventados (no corresponden a personas reales).
EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


def nuevo_mandante(nombre, rut=None):
	return frappe.get_doc({"doctype": "Mandante", "mandante_nombre": nombre, "rut": rut})


class IntegrationTestMandante(IntegrationTestCase):
	def test_c11_rut_valido_se_guarda_con_formato(self):
		mandante = nuevo_mandante("Mandante RUT válido " + frappe.generate_hash(length=6), "111111111")
		mandante.insert()
		self.assertEqual(mandante.rut, "11.111.111-1")

	def test_c11_rut_con_k_minuscula(self):
		self.assertEqual(formatear_rut("10.000.013-k"), "10.000.013-K")

	def test_c11_digito_cero(self):
		self.assertEqual(digito_verificador("20000008"), "0")

	def test_c11_rut_invalido_se_rechaza(self):
		mandante = nuevo_mandante("Mandante RUT inválido " + frappe.generate_hash(length=6), "11.111.111-2")
		with self.assertRaises(frappe.ValidationError):
			mandante.insert()

	def test_c11_rut_con_letras_se_rechaza(self):
		with self.assertRaises(frappe.ValidationError):
			formatear_rut("ABC-1")

	def test_rut_es_opcional(self):
		mandante = nuevo_mandante("Mandante sin RUT " + frappe.generate_hash(length=6))
		mandante.insert()
		self.assertFalse(mandante.rut)
