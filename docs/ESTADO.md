# Estado del proyecto

Archivo de traspaso entre Claude y Codex. **Quien empieza una sesión lo lee primero; quien termina o se detiene lo actualiza.**

## Ahora

- **En curso:** Entrega 02, reporte diario de avance, en la rama `entrega-02-reporte-diario`.
- **Quién tiene la tarea:** Claude.
- **Revisión pendiente:** Entrega 01 (PR #1).

## Entregas del MVP

| # | Entrega | Estado | Rama / PR |
| --- | --- | --- | --- |
| 01 | Mandantes, contratos e itemizado | En revisión | `entrega-01-contrato` / PR #1 |
| 02 | Reporte diario con fotos, horas-persona y horas de equipo, firmado por el mandante | En curso (Claude) | `entrega-02-reporte-diario` |
| 03 | Estado de pago mensual con retención, estados y PDF por mandante | Pendiente | — |
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

## Bitácora (lo más reciente arriba)

- **2026-10-29 · Claude:** Miguel respondió las preguntas de la Entrega 02 (turno de día, quien llena y
  quien revisa son personas distintas, el mandante firma el reporte, equipos con horas operativas y en
  espera). Especificación aprobada; Claude toma la entrega.
- **2026-10-29 · Claude:** Entrega 01 lista. Mandante con validación de RUT; Contrato con itemizado,
  totales con redondeo comercial y condiciones editables; espacio de trabajo "Norte Contratista";
  plantilla Excel en `docs/plantillas/`; 21 pruebas (criterios C1 a C12). Se abrió el PR #1.
