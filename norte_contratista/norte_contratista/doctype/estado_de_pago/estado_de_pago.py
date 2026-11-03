# Copyright (c) 2026, Norte Inteligente SpA and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.query_builder.functions import Max, Sum
from frappe.utils import flt, getdate, today

from norte_contratista.utils.montos import (
	TASA_IVA,
	a_decimal,
	aplicar_tasa,
	multiplicar,
	precision_moneda,
	redondear,
	sumar,
)

BORRADOR = "Borrador"
PRESENTADO = "Presentado"
RECHAZADO = "Rechazado"
APROBADO = "Aprobado"
ABIERTOS = (BORRADOR, PRESENTADO, RECHAZADO)
TRANSICIONES = {
	BORRADOR: {PRESENTADO},
	PRESENTADO: {APROBADO, RECHAZADO, BORRADOR},
	RECHAZADO: {BORRADOR},
	APROBADO: set(),
}
# Tolerancia para comparar cantidades con decimales.
EPSILON = 1e-9


class EstadodePago(Document):
	def validate(self):
		self.anterior = self.get_doc_before_save()
		self.validar_aprobado_inmutable()
		contrato = frappe.get_doc("Contrato", self.contrato)
		if self.is_new():
			self.validar_contrato_vigente(contrato)
			self.validar_sin_ep_abierto()
			self.numero = self.siguiente_numero()
			self.moneda = contrato.moneda
			self.porcentaje_retencion = contrato.porcentaje_retencion
		self.ep_previo = self.buscar_ep_previo()
		self.validar_periodo(contrato)
		self.cargar_partidas(contrato)
		self.cargar_anteriores()
		self.aplicar_porcentaje_global()
		self.calcular_partidas()
		self.calcular_resumen()
		self.validar_estado()

	# --- reglas de creación -------------------------------------------------

	def validar_aprobado_inmutable(self):
		if self.anterior and self.anterior.estado == APROBADO:
			frappe.throw(_("El estado de pago ya fue aprobado por el mandante y no se puede modificar."))

	def validar_contrato_vigente(self, contrato):
		if contrato.estado != "Vigente":
			frappe.throw(
				_("Solo se emiten estados de pago de contratos vigentes. El contrato {0} está {1}.").format(
					contrato.name, contrato.estado
				)
			)

	def validar_sin_ep_abierto(self):
		abierto = frappe.db.get_value(
			"Estado de Pago",
			{"contrato": self.contrato, "estado": ["in", ABIERTOS], "name": ["!=", self.name or ""]},
			["name", "numero", "estado"],
			as_dict=True,
		)
		if abierto:
			frappe.throw(
				_("El estado de pago N° {0} ({1}) está en estado {2}. Ciérrelo antes de crear otro.").format(
					abierto.numero, abierto.name, abierto.estado
				)
			)

	def siguiente_numero(self):
		ep = frappe.qb.DocType("Estado de Pago")
		ultimo = (frappe.qb.from_(ep).select(Max(ep.numero)).where(ep.contrato == self.contrato)).run()
		return (ultimo[0][0] or 0) + 1

	def buscar_ep_previo(self):
		"""El último estado de pago aprobado de este contrato con número menor."""
		previos = frappe.get_all(
			"Estado de Pago",
			filters={"contrato": self.contrato, "estado": APROBADO, "numero": ["<", self.numero]},
			fields=["name", "numero", "periodo_hasta"],
			order_by="numero desc",
			limit=1,
		)
		return previos[0] if previos else None

	def validar_periodo(self, contrato):
		desde, hasta = getdate(self.periodo_desde), getdate(self.periodo_hasta)
		if hasta < desde:
			frappe.throw(_("El período termina antes de empezar."))
		if desde < getdate(contrato.fecha_inicio) or hasta > getdate(contrato.fecha_termino):
			frappe.throw(_("El período está fuera del plazo del contrato."))
		if self.ep_previo and desde <= getdate(self.ep_previo.periodo_hasta):
			frappe.throw(
				_("El período debe empezar después del {0}, fin del estado de pago N° {1}.").format(
					frappe.format(self.ep_previo.periodo_hasta, {"fieldtype": "Date"}), self.ep_previo.numero
				)
			)

	# --- partidas ------------------------------------------------------------

	def cargar_partidas(self, contrato):
		"""Copia el itemizado del contrato. Las partidas del EP siempre reflejan las del contrato."""
		itemizado = {(p.item or "").strip(): p for p in contrato.partidas}
		if not self.partidas:
			for partida in contrato.partidas:
				self.append("partidas", {"item": partida.item})
		for fila in self.partidas:
			item = (fila.item or "").strip()
			partida = itemizado.get(item)
			if not partida:
				frappe.throw(
					_("El ítem {0} no está en el itemizado del contrato {1}.").format(item, contrato.name)
				)
			fila.item = item
			fila.descripcion = partida.descripcion
			fila.unidad = partida.unidad
			fila.cantidad_contratada = partida.cantidad
			fila.precio_unitario = partida.precio_unitario
			fila.valor_contratado = partida.total

	def cargar_anteriores(self):
		anteriores = {}
		if self.ep_previo:
			for fila in frappe.get_all(
				"Partida de Estado de Pago",
				filters={"parent": self.ep_previo.name, "parenttype": "Estado de Pago"},
				fields=["item", "cantidad_acumulada", "valor_acumulado"],
			):
				anteriores[fila.item] = fila
		for fila in self.partidas:
			previo = anteriores.get(fila.item)
			fila.cantidad_anterior = flt(previo.cantidad_acumulada) if previo else 0
			fila.valor_anterior = flt(previo.valor_acumulado) if previo else 0
			# Un EP nuevo parte "sin avance en el período": acumulado = lo anterior.
			if self.is_new() and not flt(fila.cantidad_acumulada):
				fila.cantidad_acumulada = fila.cantidad_anterior

	def aplicar_porcentaje_global(self):
		if self.modo_avance != "Porcentaje global":
			return
		porcentaje = flt(self.porcentaje_global)
		if porcentaje < 0 or porcentaje > 100:
			frappe.throw(_("El porcentaje de avance global debe estar entre 0 % y 100 %."))
		for fila in self.partidas:
			cantidad = a_decimal(fila.cantidad_contratada) * a_decimal(porcentaje) / 100
			fila.cantidad_acumulada = float(cantidad)

	def calcular_partidas(self):
		precision = precision_moneda(self.moneda)
		for fila in self.partidas:
			acumulada, anterior = flt(fila.cantidad_acumulada), flt(fila.cantidad_anterior)
			if acumulada > flt(fila.cantidad_contratada) + EPSILON:
				frappe.throw(
					_(
						"El acumulado del ítem {0} supera lo contratado ({1} de {2}). Requiere orden de cambio."
					).format(fila.item, acumulada, flt(fila.cantidad_contratada))
				)
			if acumulada < anterior - EPSILON:
				frappe.throw(
					_("El acumulado del ítem {0} es menor que el del estado de pago anterior ({1}).").format(
						fila.item, anterior
					)
				)
			fila.valor_acumulado = multiplicar(acumulada, fila.precio_unitario, precision)
			fila.cantidad_presente = float(a_decimal(acumulada) - a_decimal(anterior))
			fila.valor_presente = redondear(
				a_decimal(fila.valor_acumulado) - a_decimal(fila.valor_anterior), precision
			)
			fila.porcentaje_acumulado = self.porcentaje(fila.valor_acumulado, fila.valor_contratado)
			fila.porcentaje_presente = self.porcentaje(fila.valor_presente, fila.valor_contratado)
		self.total_contrato = sumar((f.valor_contratado for f in self.partidas), precision)
		self.total_anterior = sumar((f.valor_anterior for f in self.partidas), precision)
		self.total_acumulado = sumar((f.valor_acumulado for f in self.partidas), precision)
		self.total_presente = sumar((f.valor_presente for f in self.partidas), precision)

	@staticmethod
	def porcentaje(valor, total):
		if not flt(total):
			return 0
		return redondear(a_decimal(valor) * 100 / a_decimal(total), 2)

	# --- resumen -------------------------------------------------------------

	def calcular_resumen(self):
		precision = precision_moneda(self.moneda)
		descuentos = flt(self.descuentos)
		if descuentos < 0:
			frappe.throw(_("Los descuentos no pueden ser negativos."))
		if descuentos and not (self.motivo_descuentos or "").strip():
			frappe.throw(_("Indique el motivo de los descuentos (por ejemplo, la multa y su cláusula)."))
		if descuentos > flt(self.total_presente):
			frappe.throw(_("Los descuentos no pueden superar el total del período."))
		self.neto = redondear(a_decimal(self.total_presente) - a_decimal(descuentos), precision)
		self.iva = aplicar_tasa(self.neto, TASA_IVA, precision)
		self.total_factura = sumar((self.neto, self.iva), precision)
		# La retención no rebaja la factura: se descuenta del pago.
		self.retencion = aplicar_tasa(self.neto, self.porcentaje_retencion, precision)
		self.liquido_a_pagar = redondear(a_decimal(self.total_factura) - a_decimal(self.retencion), precision)

	# --- estados ---------------------------------------------------------------

	def validar_estado(self):
		if self.is_new() or not self.anterior:
			if self.estado != BORRADOR:
				frappe.throw(_("Un estado de pago nuevo parte en Borrador."))
			return
		previo = self.anterior.estado
		if self.estado == previo:
			return
		if self.estado not in TRANSICIONES[previo]:
			frappe.throw(_("Un estado de pago no puede pasar de {0} a {1}.").format(previo, self.estado))
		if self.estado == PRESENTADO and not self.fecha_presentacion:
			self.fecha_presentacion = today()
		if self.estado == RECHAZADO and not (self.motivo_rechazo or "").strip():
			frappe.throw(_("Indique el motivo del rechazo del mandante."))
		if self.estado == APROBADO:
			self.registrar_aprobacion()

	def registrar_aprobacion(self):
		if self.monto_aprobado in (None, "") or not self.fecha_aprobacion:
			frappe.throw(_("Para aprobarlo, registre el monto neto aprobado por el mandante y la fecha."))
		precision = precision_moneda(self.moneda)
		self.diferencia_aprobado = redondear(a_decimal(self.monto_aprobado) - a_decimal(self.neto), precision)
		if self.diferencia_aprobado and not (self.motivo_diferencia or "").strip():
			frappe.throw(
				_("El mandante aprobó {0} y se presentó {1}. Indique el motivo de la diferencia.").format(
					frappe.format(self.monto_aprobado, {"fieldtype": "Currency"}),
					frappe.format(self.neto, {"fieldtype": "Currency"}),
				)
			)

	# --- acciones ----------------------------------------------------------------

	@frappe.whitelist()
	def traer_avance_de_reportes(self):
		"""Carga la cantidad acumulada desde los reportes diarios firmados por el mandante."""
		if self.estado != BORRADOR:
			frappe.throw(_("Solo se puede traer el avance a un estado de pago en Borrador."))
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
				& (reporte.estado == "Firmado por el mandante")
				& (reporte.fecha <= self.periodo_hasta)
			)
			.groupby(avance.item)
		).run()
		firmado = {item: flt(total) for item, total in filas}
		self.modo_avance = "Por cantidad"
		for fila in self.partidas:
			fila.cantidad_acumulada = firmado.get(fila.item, 0)
		self.save()
		return firmado
