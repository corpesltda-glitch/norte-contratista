"""Cálculo y redondeo de montos como se hace comercialmente en Chile.

Todo se calcula con Decimal: multiplicar o sumar en punto flotante produce errores
como 1,15 por 50 = 57,4999… que, al redondear, cobran un peso menos.
"""

from decimal import ROUND_HALF_UP, Decimal

# Decimales por moneda: los pesos chilenos no llevan decimales.
PRECISION_POR_MONEDA = {"CLP": 0, "UF": 2, "USD": 2}

# Tasa del IVA en Chile (DL 825). Es ley, no condición del contrato: un solo lugar para cambiarla.
TASA_IVA = Decimal("19")


def precision_moneda(moneda: str | None) -> int:
	return PRECISION_POR_MONEDA.get(moneda or "CLP", 2)


def a_decimal(valor: float | int | str | None) -> Decimal:
	"""Convierte el número tal como se escribió (1.15 -> Decimal('1.15'))."""
	return Decimal(str(valor or 0))


def redondear(valor: float | int | str | Decimal | None, precision: int) -> float:
	"""Redondea al entero o decimal más cercano; el medio sube (1.000,5 -> 1.001)."""
	cuantizador = Decimal(1).scaleb(-precision)
	return float(a_decimal(valor).quantize(cuantizador, rounding=ROUND_HALF_UP))


def multiplicar(cantidad, precio_unitario, precision: int) -> float:
	"""Total de una línea: cantidad por precio unitario, redondeado sin errores de punto flotante."""
	return redondear(a_decimal(cantidad) * a_decimal(precio_unitario), precision)


def sumar(valores, precision: int) -> float:
	"""Suma montos sin errores de punto flotante y redondea el resultado."""
	return redondear(sum((a_decimal(v) for v in valores), Decimal(0)), precision)


def aplicar_tasa(monto, tasa, precision: int) -> float:
	"""Monto por tasa dividido por 100, redondeado comercialmente (IVA, retención)."""
	return redondear(a_decimal(monto) * a_decimal(tasa) / Decimal(100), precision)
