# Entrega 03 — Estado de pago mensual

**Estado:** aprobada por Miguel el 2026-11-03 · **Construye:** Claude · **Revisa:** Codex

## Para qué sirve

Es el corazón del sistema: transforma el avance del mes en el documento con el que el contratista cobra.
Calcula lo contratado, lo acumulado anterior, lo acumulado a la fecha y lo del período por partida; aplica
descuentos, retención e IVA; registra lo que aprueba el mandante y avisa cuando no coincide con lo presentado.

## De dónde salen las reglas

Se revisaron estados de pago y órdenes de facturación reales que entregó Miguel. Sus datos (mandantes,
contratos, personas y montos) **no** se guardan en este repositorio; aquí solo queda la estructura, y las
pruebas usan números inventados.

- **EP de suma alzada:** carátula con resumen (monto original, acumulado, anterior, descuentos, retención,
  anticipo, neto, IVA 19 %, bruto), detalle por partida y hoja de ruta de firmas.
- **EP de tarifas mensuales** (personal, equipos, insumos): se cobra un mismo porcentaje de avance para todas
  las partidas, calculado desde el avance físico de la faena.
- **Orden de facturación del mandante:** aprueba un monto y emite un número que la factura debe citar. En un
  caso real el monto aprobado no coincidió con lo presentado.

Hallazgos que el sistema corrige: las planillas dejaban pesos con decimales en el IVA y en el total, que no se
pueden facturar, y nadie registraba la diferencia entre lo presentado y lo aprobado.

## Qué incluye

1. **Estado de pago por contrato**, con número correlativo (1, 2, 3…), período (desde–hasta) y fecha de presentación.
2. **Detalle por partida**, copiado del itemizado del contrato: contratado, anterior, acumulado y presente,
   en cantidad, valor y porcentaje.
3. **Dos formas de cargar el avance:**
   - **Por cantidad**, partida por partida, o trayéndola de los reportes diarios firmados por el mandante.
   - **Por porcentaje global**, el mismo para todas las partidas.
4. **Resumen:** total presente, descuentos (multas u otros débitos, con su motivo), neto, IVA 19 %, total de
   la factura, retención del período según el contrato y líquido a pagar.
5. **Estados:** Borrador → Presentado → Aprobado. Un EP Rechazado vuelve a Borrador para corregirlo. Al aprobar
   se registra el monto aprobado por el mandante y su fecha.
6. **Formato de impresión** con carátula de resumen, detalle por partida y firmas del contratista y del mandante.

Fuera de esta entrega: anticipos y su devolución, tope de retención, reajustes, multas calculadas
automáticamente, orden de facturación/HES y factura (Entrega 07), formato propio de cada mandante.

## Supuestos (Miguel no tiene ejemplos con descuentos ni retención)

- La retención se calcula sobre el neto del período y **no** rebaja la factura: se descuenta del pago.
  El IVA se calcula sobre el neto completo (regla de referencia de las bases de Codelco).
- Los descuentos (multas, débitos) rebajan el neto antes del IVA.
- Cada partida se redondea a pesos y el total es la suma de las partidas.

## Criterios de aceptación

| # | Dado | Cuando | Entonces |
| --- | --- | --- | --- |
| E1 | Un contrato que no está Vigente | Se crea un EP | Se rechaza |
| E2 | Un contrato vigente sin EP | Se crean EP sucesivos | Se numeran 1, 2, 3… por contrato |
| E3 | Un EP del contrato en Borrador, Presentado o Rechazado | Se crea otro EP | Se rechaza: hay que cerrar el anterior |
| E4 | Un período que empieza antes del término del EP anterior, o con hasta antes que desde | Se guarda | Se rechaza |
| E5 | Un EP nuevo | Se crea | Trae todas las partidas del itemizado con descripción, unidad, cantidad y precio |
| E6 | Un EP N°2 | Se crea | Lo "anterior" de cada partida es lo acumulado del EP N°1 aprobado |
| E7 | Un acumulado mayor que lo contratado en una partida | Se guarda | Se rechaza: requiere orden de cambio |
| E8 | Un acumulado menor que el anterior | Se guarda | Se rechaza |
| E9 | Cantidades con decimales | Se calculan los valores | Cada partida queda en pesos enteros; presente = acumulado − anterior; los totales son la suma |
| E10 | Avance por porcentaje global de 40 % | Se guarda | Cada partida acumula el 40 % de lo contratado |
| E11 | Neto $100.000.005 sin descuentos y retención 5 % | Se calcula el resumen | IVA $19.000.001; factura $119.000.006; retención $5.000.000; líquido $114.000.006 |
| E12 | Descuentos del período | Se guarda | Rebajan el neto; sin motivo se rechaza |
| E13 | Un EP en Borrador | Se intenta pasar directo a Aprobado | Se rechaza: los estados van en orden |
| E14 | Un EP Presentado | Se aprueba | Exige monto aprobado y fecha; si difiere de lo presentado, exige el motivo y muestra la diferencia |
| E15 | Un EP Aprobado | Se intenta modificar | Se rechaza |
| E16 | Reportes diarios firmados por el mandante en el período | Se trae el avance | La cantidad acumulada de cada partida es la de esos reportes hasta el fin del período |
| E17 | Un EP con partidas | Se imprime | Muestra la carátula de resumen, el detalle por partida y las firmas |
