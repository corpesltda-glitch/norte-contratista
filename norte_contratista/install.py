"""Tareas de instalación de la app."""

import frappe

ROLES = ("Administrador de Contratos", "Supervisor de Terreno")

# Formato chileno: 1.234,5 y 28-10-2026. Se aplica solo al instalar, para no pisar
# cambios que el cliente haga después.
CONFIGURACION_CHILE = {
	"country": "Chile",
	"time_zone": "America/Santiago",
	"language": "es",
	"date_format": "dd-mm-yyyy",
	"number_format": "#.###,##",
	"first_day_of_the_week": "Monday",
}


def before_install():
	crear_roles()


def after_install():
	configurar_chile()


def after_migrate():
	crear_roles()


def crear_roles():
	"""Los DocTypes dan permisos a estos roles, así que deben existir antes de instalarlos."""
	for rol in ROLES:
		if not frappe.db.exists("Role", rol):
			frappe.get_doc({"doctype": "Role", "role_name": rol, "desk_access": 1}).insert()


def configurar_chile():
	ajustes = frappe.get_single("System Settings")
	ajustes.update(CONFIGURACION_CHILE)
	ajustes.flags.ignore_mandatory = True
	ajustes.save()
