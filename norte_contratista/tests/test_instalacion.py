# Copyright (c) 2026, Norte Inteligente SpA and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from norte_contratista.install import CONFIGURACION_CHILE, configurar_chile


class IntegrationTestInstalacion(IntegrationTestCase):
	def test_r17_formato_chileno(self):
		configurar_chile()
		ajustes = frappe.get_single("System Settings")
		for campo, valor in CONFIGURACION_CHILE.items():
			with self.subTest(campo=campo):
				self.assertEqual(ajustes.get(campo), valor)
		self.assertEqual(frappe.format_value(3000.5, {"fieldtype": "Float"}), "3.000,50")
		self.assertEqual(frappe.utils.formatdate("2026-10-28"), "28-10-2026")

	def test_roles_creados(self):
		for rol in ("Administrador de Contratos", "Supervisor de Terreno"):
			with self.subTest(rol=rol):
				self.assertTrue(frappe.db.exists("Role", rol))
