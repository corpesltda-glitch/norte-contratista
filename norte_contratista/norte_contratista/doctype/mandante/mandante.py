# Copyright (c) 2026, Norte Inteligente SpA and contributors
# For license information, please see license.txt

from frappe.model.document import Document

from norte_contratista.utils.rut import formatear_rut


class Mandante(Document):
	def validate(self):
		if self.rut:
			self.rut = formatear_rut(self.rut)
