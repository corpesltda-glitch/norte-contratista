"""Redondeo de montos como se hace comercialmente en Chile."""

from decimal import ROUND_HALF_UP, Decimal

# Decimales por moneda: los pesos chilenos no llevan decimales.
PRECISION_POR_MONEDA = {"CLP": 0, "UF": 2, "USD": 2}


def precision_moneda(moneda: str | None) -> int:
	return PRECISION_POR_MONEDA.get(moneda or "CLP", 2)


def redondear(valor: float | int | None, precision: int) -> float:
	"""Redondea al entero o decimal más cercano; el medio sube (1.000,5 -> 1.001).

	Se usa Decimal para no depender del redondeo bancario de Python ni de la
	configuración del sitio.
	"""
	cuantizador = Decimal(1).scaleb(-precision)
	return float(Decimal(str(valor or 0)).quantize(cuantizador, rounding=ROUND_HALF_UP))
