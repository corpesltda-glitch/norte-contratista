"""Tareas de instalación de la app."""

import frappe

ROL_ADMINISTRADOR = "Administrador de Contratos"


def before_install():
	crear_rol()


def after_migrate():
	crear_rol()


def crear_rol():
	"""Los DocTypes dan permisos a este rol, así que debe existir antes de instalarlos."""
	if not frappe.db.exists("Role", ROL_ADMINISTRADOR):
		frappe.get_doc({"doctype": "Role", "role_name": ROL_ADMINISTRADOR, "desk_access": 1}).insert()
