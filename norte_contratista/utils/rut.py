"""Validación y formato del RUT chileno (módulo 11)."""

import re

import frappe
from frappe import _


def limpiar_rut(rut: str | None) -> str:
	"""Deja solo dígitos y la K final, en mayúscula: '12.345.678-k' -> '12345678K'."""
	return re.sub(r"[^0-9kK]", "", rut or "").upper()


def digito_verificador(cuerpo: str) -> str:
	"""Calcula el dígito verificador de un RUT sin puntos ni guion."""
	suma, factor = 0, 2
	for digito in reversed(cuerpo):
		suma += int(digito) * factor
		factor = 2 if factor == 7 else factor + 1
	resto = 11 - (suma % 11)
	return {11: "0", 10: "K"}.get(resto, str(resto))


def formatear_rut(rut: str) -> str:
	"""Valida el RUT y lo devuelve con puntos y guion: '12.345.678-5'.

	Lanza un error de validación si el formato o el dígito verificador no corresponden.
	"""
	limpio = limpiar_rut(rut)
	cuerpo, dv = limpio[:-1], limpio[-1:]
	if len(limpio) < 2 or not cuerpo.isdigit():
		frappe.throw(_("El RUT {0} no tiene un formato válido.").format(rut))
	if digito_verificador(cuerpo) != dv:
		frappe.throw(_("El RUT {0} no es válido: el dígito verificador no corresponde.").format(rut))
	return f"{int(cuerpo):,}".replace(",", ".") + "-" + dv
