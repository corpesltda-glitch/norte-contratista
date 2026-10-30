# Entrega 02 — Reporte diario de avance

**Estado:** borrador, espera aprobación de Miguel · **Construye:** quien la tome según `docs/ESTADO.md` · **Revisa:** el otro agente

## Para qué sirve

El supervisor registra cada día, desde faena, cuánto se avanzó en cada partida del contrato, cuánta
gente y cuántos equipos trabajaron, con fotos. Es el respaldo del estado de pago del mes y la base de
las horas-persona que piden el formulario E-200 y las licitaciones (tasas de accidentabilidad).

## Qué incluye

1. **Reporte diario:** contrato, fecha, turno, supervisor, observaciones y estado (Borrador / Enviado).
2. **Avance por partida:** ítem del itemizado del contrato, cantidad avanzada ese día y comentario.
   La unidad se completa sola desde el contrato.
3. **Personal:** por cargo (por ejemplo "Operador", "Ayudante"), número de personas y horas trabajadas.
   Se registra por cargo y no por trabajador, para no guardar datos personales que no se necesitan.
4. **Equipos:** equipo, horas operativas y horas en espera.
5. **Fotos:** una o varias fotos con su descripción.
6. Totales del día: horas-persona y horas de equipo.

Fuera de esta entrega: modo sin conexión, app instalable en el celular, firma del mandante, PDF del reporte.

## Criterios de aceptación

| # | Dado | Cuando | Entonces |
| --- | --- | --- | --- |
| R1 | Un contrato que no está Vigente | Se crea un reporte para él | Se rechaza |
| R2 | Una fecha fuera del plazo del contrato | Se guarda el reporte | Se rechaza |
| R3 | Una fecha futura | Se guarda el reporte | Se rechaza |
| R4 | Ya existe un reporte del mismo contrato, fecha y turno | Se crea otro igual | Se rechaza |
| R5 | Un avance con un ítem que no está en el itemizado | Se guarda | Se rechaza indicando el ítem |
| R6 | Un avance con cantidad negativa | Se guarda | Se rechaza |
| R7 | Un avance con un ítem válido | Se guarda | La unidad se copia desde la partida del contrato |
| R8 | El avance acumulado de una partida supera lo contratado | Se guarda | Se guarda, pero la fila queda marcada y aparece un aviso: "requiere orden de cambio" |
| R9 | Personal: 4 personas × 12 horas y 2 personas × 10 horas | Se guarda | Total del día = 68 horas-persona |
| R10 | Equipos con horas operativas y en espera | Se guarda | Se suman por separado |
| R11 | Personas u horas negativas | Se guarda | Se rechaza |

## Preguntas para Miguel antes de construir

1. ¿Los contratos trabajan por turno de día y de noche, o un solo turno diario?
2. Para los equipos, ¿basta con horas operativas y en espera, o el mandante pide también horas en panne?
3. ¿Quién llena el reporte (supervisor, capataz) y quién lo revisa antes de enviarlo?
4. ¿El mandante pide el reporte diario firmado o en un formato propio?
