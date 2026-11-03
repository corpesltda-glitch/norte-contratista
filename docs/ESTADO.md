# Estado del proyecto

Archivo de traspaso entre Claude y Codex. **Quien empieza una sesión lo lee primero; quien termina o se detiene lo actualiza.**

## Ahora

- **En curso:** nada. La Entrega 03 está lista y espera revisión de Codex.
- **Revisión pendiente:** Entrega 01 (PR #1), Entrega 02 (PR #9) y Entrega 03 (PR de la rama
  `entrega-03-estado-de-pago`). Se aprueban en ese orden: cada una parte de la anterior.
- **Siguiente:** Entrega 04, carpeta laboral. Antes hay que entrevistar a Miguel y escribir su especificación.

## Entregas del MVP

| # | Entrega | Estado | Rama / PR |
| --- | --- | --- | --- |
| 01 | Mandantes, contratos e itemizado | En revisión | `entrega-01-contrato` / PR #1 |
| 02 | Reporte diario con fotos, horas-persona y horas de equipo, firmado por el mandante | En revisión | `entrega-02-reporte-diario` / PR #9 |
| 03 | Estado de pago mensual con retención, estados y PDF por mandante | En revisión | `entrega-03-estado-de-pago` |
| 04 | Carpeta laboral mensual (F30-1, cotizaciones, E-200) con semáforo en el EP | Pendiente | — |
| 05 | Bóveda documental con vencimientos y avisos | Pendiente | — |
| 06 | Garantías y retenciones (boletas y pólizas en UF, saldo retenido) | Pendiente | — |
| 07 | Datos de cobro (OC, HES, 8 días del SII, 30 días legales, mora) | Pendiente | — |
| 08 | Panel de margen y caja por contrato | Pendiente | — |

## Decisiones tomadas

- La app depende solo de Frappe v16; ERPNext se suma cuando se construya compras.
- Cada cliente es un sitio de Frappe con su propia base de datos.
- Redondeo comercial (el medio sube); pesos chilenos sin decimales; UF y USD con 2 decimales.
- Porcentajes, multas, reajustes y plazos son campos del Contrato, nunca fijos en el código.
- Licencia propietaria de Norte Inteligente SpA.
- Al instalar, el sitio queda en formato chileno (es, dd-mm-yyyy, #.###,##, America/Santiago).
- El personal del reporte diario se registra por cargo, no por trabajador (menos datos personales).
- Los documentos reales de clientes nunca se suben al repositorio: solo su estructura.

## Bitácora (lo más reciente arriba)

- **2026-11-03 · Claude:** Miguel pidió actualizar los años de las pruebas. Se corrieron las 64 pruebas
  simulando las fechas 2028-06-15 y 2032-03-10 (y 2026-01-15 como control, donde fallan como se espera):
  ninguna vence con el paso de los años. Se ajustó R3 en la Entrega 02 (PR #9): el contrato de prueba
  termina a fin del próximo año y la prueba verifica el mensaje de fecha futura, para que no pase por
  el motivo equivocado desde 2028. Para repetir la simulación: instalar `freezegun` en el entorno local
  (no en la app) y correr las pruebas con `FECHA_SIMULADA=AAAA-MM-DD` y un `sitecustomize.py` que la active.

- **2026-11-03 · Claude:** al generar el PDF con wkhtmltopdf (el motor de PDF de Frappe) se vio que no soporta
  flexbox: en el EP desaparecía el cuadro de montos y en el reporte diario la tabla de equipos. Ambos formatos
  pasan a tablas de dos columnas; E17 y R16 verifican que no se use flexbox. La corrección del reporte diario
  está en `entrega-02-reporte-diario` (PR #9) y se trajo a esta rama. También se corrigió un falso positivo de
  Semgrep (`test-is-missing-assert`) en las pruebas del EP.

- **2026-11-03 · Claude:** Entrega 03 lista. Estado de Pago con partidas copiadas del itemizado, anterior
  = acumulado del último EP aprobado, avance por cantidad, por porcentaje global o traído de los reportes
  diarios firmados; resumen con descuentos, neto, IVA, factura, retención del contrato y líquido; estados
  Borrador → Presentado → Aprobado/Rechazado con monto aprobado y diferencia con motivo; formato de impresión
  horizontal con carátula y firmas en la hoja 1 y detalle en la hoja 2. Nuevo `aplicar_tasa` en
  `utils/montos.py`. 64 pruebas en verde (20 nuevas, E1 a E17). Se probó en local con las planillas reales
  de Miguel: los montos cuadran con las planillas, pero en pesos enteros (las planillas dejaban decimales).

- **2026-11-03 · Claude:** con estados de pago y órdenes de facturación reales que entregó Miguel se escribió
  `SPEC-03-estado-de-pago.md`, aprobada por Miguel; Claude toma la entrega. Los datos reales (mandantes,
  contratos, personas y montos) no se guardan en el repositorio; las pruebas usan números inventados.

- **2026-10-29 · Claude:** Codex revisó el PR #1 y encontró un P1: 1,15 × $50 daba $57 en vez de $58 por
  el punto flotante. Corregido con Decimal (`multiplicar` y `sumar` en `utils/montos.py`), con prueba nueva;
  C8 ahora prueba los cuatro valores editables y el CI quedó fijado a Frappe `version-16`. La corrección
  también está en la rama de la Entrega 02. PR #1 y #9 en verde (22 y 44 pruebas).

- **2026-10-29 · Claude:** Entrega 02 lista. Reporte Diario con avance por partida (acumulado y aviso si
  supera lo contratado), personal por cargo, equipos, fotos, estados Borrador → Revisado → Enviado →
  Firmado (quien llena no revisa; firmado exige copia y fecha, y queda bloqueado), formato de impresión
  para la firma del mandante, rol Supervisor de Terreno y formato chileno al instalar. 43 pruebas en verde.

- **2026-10-29 · Claude:** Miguel respondió las preguntas de la Entrega 02 (turno de día, quien llena y
  quien revisa son personas distintas, el mandante firma el reporte, equipos con horas operativas y en
  espera). Especificación aprobada; Claude toma la entrega.
- **2026-10-29 · Claude:** Entrega 01 lista. Mandante con validación de RUT; Contrato con itemizado,
  totales con redondeo comercial y condiciones editables; espacio de trabajo "Norte Contratista";
  plantilla Excel en `docs/plantillas/`; 21 pruebas (criterios C1 a C12). Se abrió el PR #1.
