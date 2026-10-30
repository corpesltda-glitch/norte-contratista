# Entrega 02 — Reporte diario de avance

**Estado:** aprobada por Miguel el 2026-10-29 · **Construye:** Claude · **Revisa:** Codex

## Para qué sirve

El supervisor registra cada día, desde faena, cuánto se avanzó en cada partida del contrato, cuánta
gente y cuántos equipos trabajaron, con fotos. Otra persona lo revisa, se envía al mandante y el
mandante lo firma en su formato. Es el respaldo del estado de pago del mes y la base de las
horas-persona que piden el formulario E-200 y las licitaciones.

## Respuestas de Miguel que definen esta entrega

- Se trabaja por **turno de día** (el sistema deja también "Noche" por si un contrato lo necesita).
- **Quien llena el reporte y quien lo revisa son dos personas distintas**; todavía no se sabe qué cargos.
- El **mandante firma el reporte** en un formato.
- Para los equipos bastan **horas operativas y en espera** (sin horas en panne).

## Qué incluye

1. **Reporte diario:** contrato (trae mandante y faena), fecha, turno, responsable, observaciones y estado.
2. **Avance por partida:** ítem del itemizado, cantidad avanzada ese día y comentario. La descripción y
   la unidad se copian del contrato, y se muestra el avance acumulado de la partida a esa fecha.
3. **Personal:** por cargo, número de personas y horas. Se registra por cargo y no por trabajador,
   para no guardar datos personales que no se necesitan.
4. **Equipos:** equipo, horas operativas y horas en espera.
5. **Fotos:** una o varias, con descripción.
6. **Totales del día:** horas-persona, horas operativas y horas en espera.
7. **Estados:** Borrador → Revisado → Enviado al mandante → Firmado por el mandante. Se puede volver a
   Borrador para corregir, salvo cuando ya está firmado.
8. **Formato de impresión** para la firma del mandante, con espacios de firma para el responsable,
   quien revisó y el mandante. Por ahora es un formato general; el formato propio de cada mandante
   se agrega cuando Miguel consiga un ejemplo.
9. **Rol "Supervisor de Terreno":** puede crear y editar reportes y ver contratos y mandantes.

Fuera de esta entrega: modo sin conexión, app instalable en el celular, formato propio de cada mandante.

## Criterios de aceptación

| # | Dado | Cuando | Entonces |
| --- | --- | --- | --- |
| R1 | Un contrato que no está Vigente | Se crea un reporte para él | Se rechaza |
| R2 | Una fecha fuera del plazo del contrato | Se guarda el reporte | Se rechaza |
| R3 | Una fecha futura | Se guarda el reporte | Se rechaza |
| R4 | Ya existe un reporte del mismo contrato, fecha y turno | Se crea otro igual | Se rechaza |
| R5 | Un avance con un ítem que no está en el itemizado | Se guarda | Se rechaza indicando el ítem |
| R6 | Un avance con cantidad negativa | Se guarda | Se rechaza |
| R7 | Un avance con un ítem válido | Se guarda | La descripción y la unidad se copian desde la partida del contrato |
| R8 | El avance acumulado de una partida supera lo contratado | Se guarda | Se guarda, pero la fila queda marcada y aparece el aviso "requiere orden de cambio" |
| R9 | Personal: 4 personas × 12 horas y 2 personas × 10 horas | Se guarda | Total del día = 68 horas-persona |
| R10 | Equipos con horas operativas y en espera | Se guarda | Se suman por separado |
| R11 | Personas, horas u horas de equipo negativas | Se guarda | Se rechaza |
| R12 | Un reporte en Borrador | Se intenta pasar directo a Enviado o a Firmado | Se rechaza: los estados van en orden |
| R13 | Un reporte llenado por una persona | La misma persona intenta marcarlo Revisado | Se rechaza; otra persona sí puede, y queda registrado quién revisó y cuándo |
| R14 | Un reporte Enviado al mandante | Se marca Firmado sin copia firmada adjunta o sin fecha de firma | Se rechaza |
| R15 | Un reporte Firmado por el mandante | Se intenta modificar | Se rechaza |
| R16 | Un reporte con avances | Se imprime | El formato muestra contrato, fecha, avances y los espacios de firma, incluido el del mandante |
