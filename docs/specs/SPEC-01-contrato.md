# Entrega 01 — Mandante, Contrato e itemizado

**Estado:** en construcción · **Semana:** 0 · **Dueño:** Miguel · **Construye:** Claude · **Revisa:** Codex

## Para qué sirve

El contratista registra cada contrato con su mandante y su itemizado (las partidas con unidad,
cantidad y precio unitario). Todo lo demás del sistema (reporte diario, estado de pago,
retenciones, multas) se calcula a partir de este contrato, así que los montos tienen que cuadrar
peso por peso.

## Qué incluye

1. **Mandante:** nombre, RUT y formato de estado de pago que usa (Genérico, Codelco, BHP,
   Antofagasta Minerals u Otro).
2. **Contrato:** número, nombre, mandante, faena, administrador del contrato del mandante,
   modalidad, moneda, fechas, estado y condiciones (retención, garantía, tope de multas,
   reajuste, días de aprobación del EP).
3. **Itemizado:** tabla de partidas dentro del contrato (ítem, descripción, unidad, cantidad,
   precio unitario, total).
4. **Espacio de trabajo "Norte Contratista"** con accesos a Contratos y Mandantes.
5. **Importación desde Excel:** con la herramienta Data Import de Frappe se carga un contrato con
   todas sus partidas.

Fuera de esta entrega: reporte diario, estado de pago, PDF, carpeta laboral, garantías.

## Criterios de aceptación

| # | Dado | Cuando | Entonces |
|---|---|---|---|
| C1 | Un contrato con partidas | Se guarda | Cada partida tiene total = cantidad × precio unitario, y el monto del contrato es la suma de los totales |
| C2 | Un contrato en CLP | Se calculan los totales | Los montos quedan redondeados a pesos, sin decimales |
| C3 | Fecha de término anterior a la de inicio | Se guarda | Se rechaza con un mensaje claro |
| C4 | Fechas válidas | Se guarda | El plazo en días corridos se calcula solo (inicio y término incluidos) |
| C5 | Dos partidas con el mismo número de ítem | Se guarda | Se rechaza indicando el ítem repetido |
| C6 | Una partida con cantidad o precio negativos | Se guarda | Se rechaza |
| C7 | Retención, garantía o tope de multas fuera de 0–100 % | Se guarda | Se rechaza |
| C8 | Un contrato nuevo | Se crea | Trae por defecto retención 5 %, garantía 3 %, tope de multas 10 % y 5 días hábiles de aprobación, todos editables |
| C9 | Un contrato sin partidas | Se marca como Vigente | Se rechaza: un contrato vigente necesita itemizado |
| C10 | Dos contratos con el mismo número | Se guarda el segundo | Se rechaza |
| C11 | Un mandante con RUT de dígito verificador incorrecto | Se guarda | Se rechaza; un RUT válido se guarda con formato 12.345.678-5 |
| C12 | Un monto con medio peso exacto (por ejemplo $1.000,5) | Se redondea | Sube al peso siguiente ($1.001), como se redondea comercialmente en Chile |

## Cómo lo revisa Miguel

1. Las pruebas automáticas en GitHub están en verde.
2. ChatGPT (Codex) revisó el cambio y no dejó problemas graves abiertos.
3. En el sitio de prueba se crea un contrato de ejemplo con 3 partidas y los totales cuadran con
   una calculadora.
