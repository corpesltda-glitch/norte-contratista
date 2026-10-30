# Copyright (c) 2026, Norte Inteligente SpA and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, flt, getdate

from norte_contratista.utils.montos import precision_moneda, redondear

PORCENTAJES = (
	("porcentaje_retencion", "La retención"),
	("porcentaje_garantia", "La garantía de fiel cumplimiento"),
	("tope_multas", "El tope de multas"),
)


class Contrato(Document):
	def validate(self):
		self.validar_fechas()
		self.validar_porcentajes()
		self.validar_partidas()
		self.calcular_totales()
		self.validar_estado()

	def validar_fechas(self):
		if not (self.fecha_inicio and self.fecha_termino):
			return
		if getdate(self.fecha_termino) < getdate(self.fecha_inicio):
			frappe.throw(_("La fecha de término no puede ser anterior a la fecha de inicio."))
		# Plazo en días corridos, contando el día de inicio y el de término.
		self.plazo_dias = date_diff(self.fecha_termino, self.fecha_inicio) + 1

	def validar_porcentajes(self):
		for campo, etiqueta in PORCENTAJES:
			valor = flt(self.get(campo))
			if valor < 0 or valor > 100:
				frappe.throw(_("{0} debe estar entre 0 % y 100 %.").format(etiqueta))

	def validar_partidas(self):
		items_vistos = set()
		for partida in self.partidas:
			item = (partida.item or "").strip()
			if item in items_vistos:
				frappe.throw(_("El ítem {0} está repetido en el itemizado.").format(item))
			items_vistos.add(item)
			if flt(partida.cantidad) < 0 or flt(partida.precio_unitario) < 0:
				frappe.throw(_("La partida {0} tiene cantidad o precio unitario negativo.").format(item))

	def calcular_totales(self):
		precision = precision_moneda(self.moneda)
		monto_total = 0
		for partida in self.partidas:
			partida.total = redondear(flt(partida.cantidad) * flt(partida.precio_unitario), precision)
			monto_total += partida.total
		self.monto_total = redondear(monto_total, precision)

	def validar_estado(self):
		if self.estado == "Vigente" and not self.partidas:
			frappe.throw(_("Un contrato vigente necesita su itemizado: agregue al menos una partida."))
