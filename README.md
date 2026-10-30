# Norte Contratista

Sistema simple para **empresas contratistas de la minería** en Chile, construido por Norte Inteligente SpA.
Gira en torno al **estado de pago**: contrato e itemizado, reporte diario de avance, estado de pago mensual,
carpeta laboral, documentos con vencimiento, garantías y retenciones, y datos de cobro.

## Estado

| Entrega | Qué incluye | Estado |
| --- | --- | --- |
| 01 | Mandantes, contratos e itemizado, con validación de RUT y redondeo comercial | Lista para revisar |
| 02 | Reporte diario de avance con fotos y horas-persona | Especificación en borrador |
| 03 | Estado de pago mensual con retención y PDF por mandante | Pendiente |

Las especificaciones de cada entrega están en [`docs/specs/`](docs/specs/).
Para cargar un contrato con su itemizado desde Excel, use la plantilla
[`docs/plantillas/plantilla_contrato.xlsx`](docs/plantillas/plantilla_contrato.xlsx) con la herramienta Data Import.

## Cómo trabajamos

- **Claude** construye, **ChatGPT (Codex)** revisa, y **Miguel** aprueba. Las reglas que ambos siguen están en [`AGENTS.md`](AGENTS.md).
- El estado del proyecto y el traspaso entre agentes están en [`docs/ESTADO.md`](docs/ESTADO.md).
- El prompt para trabajar con ChatGPT está en [`docs/prompt-chatgpt.md`](docs/prompt-chatgpt.md).
- Cada cambio llega como propuesta (pull request) con sus pruebas. Solo se acepta con las pruebas automáticas en verde.

## Para desarrolladores

App de [Frappe Framework](https://frappeframework.com) v16 (Python 3.14+, Node 24+).

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch main
bench --site <sitio> install-app norte_contratista
bench --site <sitio> run-tests --app norte_contratista
```

## Licencia

Propietaria. © 2026 Norte Inteligente SpA. Ver [`license.txt`](license.txt).
