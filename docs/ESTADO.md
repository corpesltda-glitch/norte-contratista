# Estado del proyecto

Archivo de traspaso entre Claude y Codex. **Quien empieza una sesión lo lee primero; quien termina o se detiene lo actualiza.**

## Ahora

- **En curso:** nada. La Entrega 01 está en revisión (PR #1).
- **Quién tiene la tarea:** nadie.
- **Siguiente:** Entrega 02, reporte diario de avance. Falta que Miguel apruebe `docs/specs/SPEC-02-reporte-diario.md`.

## Entregas del MVP

| # | Entrega | Estado | Rama / PR |
| --- | --- | --- | --- |
| 01 | Mandantes, contratos e itemizado | En revisión | `entrega-01-contrato` / PR #1 |
| 02 | Reporte diario con fotos, horas-persona y horas de equipo | Especificación en borrador | — |
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

- **2026-10-29 · Claude:** Entrega 01 lista. Mandante con validación de RUT; Contrato con itemizado,
  totales con redondeo comercial y condiciones editables; espacio de trabajo "Norte Contratista";
  plantilla Excel en `docs/plantillas/`; 21 pruebas (criterios C1 a C12). Se abrió el PR #1.
