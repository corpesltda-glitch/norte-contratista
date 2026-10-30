# Norte Contratista — reglas para agentes (Claude y Codex)

Este archivo lo leen Claude (Claude Code) y ChatGPT (Codex). Es la fuente única de reglas del proyecto.

## Qué es el proyecto

Norte Contratista es un sistema simple para **empresas contratistas de la minería** en Chile
(pymes de Antofagasta y el norte). Gira en torno al **estado de pago (EP)** y a lo que lo frena:
contrato e itemizado, reporte diario de avance, EP mensual, carpeta laboral (F30-1), bóveda de
documentos, garantías y retenciones, y datos de cobro (OC, HES, plazos de la Ley 21.131).

Dueño del producto: Miguel Aliaga (Norte Inteligente SpA). No es programador: revisa por
pruebas, capturas y la lista de revisión, no leyendo código.

## Stack

- Frappe Framework **v16** (rama `version-16`), Python 3.14+, Node 24+.
- App propia: `norte_contratista` (módulo "Norte Contratista").
- La app depende **solo de Frappe**. ERPNext no es requisito hasta que se construya el módulo de compras.
- Cada cliente es un sitio de Frappe con su propia base de datos.

## Forma de trabajo

1. Cada tarea parte de una especificación en `docs/specs/` con criterios "Dado / Cuando / Entonces".
2. Cada criterio tiene al menos un test en el archivo `test_*.py` del DocType que corresponda.
3. Una tarea = una rama = una propuesta de cambio (pull request). **Nunca dos agentes trabajan en la misma rama al mismo tiempo.**
4. Quien construye no aprueba su propio cambio: si Claude construye, Codex revisa, y al revés.
5. Solo se hace merge con las pruebas automáticas (CI) en verde y la aprobación de Miguel.
6. La descripción del PR incluye una tabla "criterio → test" y una nota en lenguaje simple para Miguel.

## Traspaso entre Claude y Codex

El trabajo tiene que poder seguir si uno de los dos se detiene (por ejemplo, porque se acabó su cuota de uso).

1. **Al empezar:** leer `docs/ESTADO.md`. Si una tarea figura "En curso" a nombre del otro agente, no tocarla salvo que Miguel lo pida.
2. **Al tomar una tarea:** anotar en `docs/ESTADO.md` la entrega, el agente y la rama, y subir ese cambio.
3. **Al terminar o al detenerse:** actualizar `docs/ESTADO.md` (qué quedó hecho, qué falta, en qué archivo y prueba seguir) y subir todo a la rama, aunque esté incompleto. Si el trabajo no está terminado, el PR queda como borrador.
4. **Para continuar una tarea del otro:** seguir en su misma rama, nunca al mismo tiempo que él, y anotar el cambio de dueño en la bitácora.

## Reglas del código

- **Solo se edita dentro de este repositorio.** Nunca se modifica el código de Frappe ni de ERPNext.
- **Nada fijo en el código que dependa del contrato:** porcentajes de retención y garantía, multas,
  reajustes y plazos son campos del Contrato. Los valores por defecto (5 % retención, 3 % garantía,
  10 % tope de multas, 5 días hábiles de aprobación) son solo sugerencias editables.
- **Montos:** redondear siempre con `norte_contratista.utils.montos.redondear` y la precisión de
  `precision_moneda` (redondeo comercial: el medio sube). Los totales se calculan en el servidor
  (`validate`); el JavaScript solo los muestra mientras se escribe. Los pesos chilenos no llevan decimales.
- **Idioma:** etiquetas, mensajes y documentación en español de Chile. Nombres de campos en
  `snake_case` y en español sin tildes (`precio_unitario`, `fecha_termino`).
- **PDF:** solo formatos de impresión HTML/Jinja (los formatos clásicos dejan de funcionar en v17).
- **Sin Server Scripts:** toda la lógica vive en el código de la app, con sus tests.
- **Dependencias:** no agregar paquetes de Python ni de npm sin justificarlo en el PR y verificar que existen en PyPI/npm.
- **Datos personales (Ley 21.719):** nunca nombres, RUT ni datos reales de trabajadores en tests, fixtures ni ejemplos.
- **Permisos:** nada de `allow_guest`, `ignore_permissions=True` ni `frappe.db.sql` con texto armado a mano sin justificarlo.

## Cómo correr las pruebas

```bash
bench --site test_site set-config allow_tests true
bench --site test_site run-tests --app norte_contratista
```

En GitHub corren solas con cada PR (`.github/workflows/ci.yml`).

## Code Review Rules

### Montos y cálculos
Marcar cualquier cálculo de montos (totales de partidas, EP, retenciones, multas) que no pase por
`redondear` con `precision_moneda`, que se calcule solo en JavaScript, o que use un porcentaje fijo
en el código en vez del campo del Contrato. Un error de un peso en un EP es un rechazo del mandante.

### Permisos y datos
Marcar `ignore_permissions=True`, `allow_guest=True`, SQL armado con texto del usuario, o datos
personales reales en tests. Cada cliente confía en que sus datos no se mezclan con otros.
