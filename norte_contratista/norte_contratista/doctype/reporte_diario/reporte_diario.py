# Copyright (c) 2026, Norte Inteligente SpA and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.query_builder.functions import Sum
from frappe.utils import flt, getdate, now_datetime, today

BORRADOR = "Borrador"
REVISADO = "Revisado"
ENVIADO = "Enviado al mandante"
FIRMADO = "Firmado por el mandante"
ESTADOS = [BORRADOR, REVISADO, ENVIADO, FIRMADO]


class ReporteDiario(Document):
	def validate(self):
		self.anterior = self.get_doc_before_save()
		self.validar_firmado_inmutable()
		contrato = frappe.get_doc("Contrato", self.contrato)
		self.validar_contrato(contrato)
		self.validar_fecha(contrato)
		self.validar_unico()
		self.validar_avances(contrato)
		self.validar_personal_y_equipos()
		self.calcular_totales()
		self.validar_estado()

	def validar_firmado_inmutable(self):
		if self.anterior and self.anterior.estado == FIRMADO:
			frappe.throw(_("El reporte ya fue firmado por el mandante y no se puede modificar."))

	def validar_contrato(self, contrato):
		if (self.is_new() or self.has_value_changed("contrato")) and contrato.estado != "Vigente":
			frappe.throw(
				_(
					"Solo se registran reportes de contratos vigentes. El contrato {0} está en estado {1}."
				).format(contrato.name, contrato.estado)
			)

	def validar_fecha(self, contrato):
		fecha = getdate(self.fecha)
		if fecha > getdate(today()):
			frappe.throw(_("La fecha del reporte no puede ser futura."))
		if fecha < getdate(contrato.fecha_inicio) or fecha > getdate(contrato.fecha_termino):
			frappe.throw(
				_("La fecha {0} está fuera del plazo del contrato ({1} a {2}).").format(
					self.get_formatted("fecha"),
					contrato.get_formatted("fecha_inicio"),
					contrato.get_formatted("fecha_termino"),
				)
			)

	def validar_unico(self):
		filtros = {
			"contrato": self.contrato,
			"fecha": self.fecha,
			"turno": self.turno,
			"name": ["!=", self.name or ""],
		}
		if repetido := frappe.db.exists("Reporte Diario", filtros):
			frappe.throw(
				_("Ya existe el reporte {0} para este contrato, fecha y turno.").format(repetido),
				frappe.DuplicateEntryError,
			)

	def validar_avances(self, contrato):
		partidas = {(p.item or "").strip(): p for p in contrato.partidas}
		acumulado = self.avance_previo_por_item()
		excedidas = []
		for avance in self.avances:
			item = (avance.item or "").strip()
			partida = partidas.get(item)
			if not partida:
				frappe.throw(
					_("El ítem {0} no está en el itemizado del contrato {1}.").format(item, contrato.name)
				)
			if flt(avance.cantidad) < 0:
				frappe.throw(_("El avance del ítem {0} no puede ser negativo.").format(item))
			avance.item = item
			avance.descripcion = partida.descripcion
			avance.unidad = partida.unidad
			avance.cantidad_contratada = partida.cantidad
			acumulado[item] = flt(acumulado.get(item, 0) + flt(avance.cantidad), 6)
			avance.acumulado = acumulado[item]
			avance.excede_contrato = 1 if avance.acumulado > flt(partida.cantidad, 6) else 0
			if avance.excede_contrato:
				excedidas.append(item)
		if excedidas:
			frappe.msgprint(
				_("El avance acumulado supera lo contratado en: {0}. Requiere orden de cambio.").format(
					", ".join(excedidas)
				),
				title=_("Avance sobre lo contratado"),
				indicator="orange",
			)

	def avance_previo_por_item(self):
		"""Suma el avance de los otros reportes del contrato hasta la fecha de este reporte."""
		reporte = frappe.qb.DocType("Reporte Diario")
		avance = frappe.qb.DocType("Avance de Partida")
		filas = (
			frappe.qb.from_(avance)
			.join(reporte)
			.on(avance.parent == reporte.name)
			.select(avance.item, Sum(avance.cantidad))
			.where(
				(avance.parenttype == "Reporte Diario")
				& (avance.parentfield == "avances")
				& (reporte.contrato == self.contrato)
				& (reporte.fecha <= self.fecha)
				& (reporte.name != (self.name or ""))
			)
			.groupby(avance.item)
		).run()
		return {item: flt(total) for item, total in filas}

	def validar_personal_y_equipos(self):
		for fila in self.personal:
			if flt(fila.personas) < 0 or flt(fila.horas) < 0:
				frappe.throw(
					_("El personal de {0} no puede tener personas u horas negativas.").format(fila.cargo)
				)
		for fila in self.equipos:
			if flt(fila.horas_operativas) < 0 or flt(fila.horas_espera) < 0:
				frappe.throw(_("El equipo {0} no puede tener horas negativas.").format(fila.equipo))

	def calcular_totales(self):
		for fila in self.personal:
			fila.horas_persona = flt(flt(fila.personas) * flt(fila.horas), 2)
		self.total_horas_persona = flt(sum(flt(f.horas_persona) for f in self.personal), 2)
		self.total_horas_operativas = flt(sum(flt(f.horas_operativas) for f in self.equipos), 2)
		self.total_horas_espera = flt(sum(flt(f.horas_espera) for f in self.equipos), 2)

	def validar_estado(self):
		if self.is_new() or not self.anterior:
			if self.estado != BORRADOR:
				frappe.throw(_("Un reporte nuevo parte en estado Borrador."))
			return
		if self.estado == self.anterior.estado:
			return
		if self.estado == BORRADOR:
			# Se devuelve para corregir: la revisión anterior deja de valer.
			self.revisado_por = None
			self.fecha_revision = None
			return
		if ESTADOS.index(self.estado) != ESTADOS.index(self.anterior.estado) + 1:
			frappe.throw(
				_("El reporte avanza en orden: {0}. No puede pasar de {1} a {2}.").format(
					" → ".join(ESTADOS), self.anterior.estado, self.estado
				)
			)
		if self.estado == REVISADO:
			if frappe.session.user == self.owner:
				frappe.throw(_("Quien llenó el reporte no puede revisarlo. Debe revisarlo otra persona."))
			self.revisado_por = frappe.session.user
			self.fecha_revision = now_datetime()
		if self.estado == FIRMADO and not (self.copia_firmada and self.fecha_firma_mandante):
			frappe.throw(
				_("Para marcarlo firmado, adjunte la copia firmada por el mandante y su fecha de firma.")
			)
