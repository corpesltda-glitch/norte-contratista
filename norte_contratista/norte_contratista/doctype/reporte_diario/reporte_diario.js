// Copyright (c) 2026, Norte Inteligente SpA and contributors
// For license information, please see license.txt

frappe.ui.form.on("Reporte Diario", {
	setup(frm) {
		// Solo se ofrecen contratos vigentes.
		frm.set_query("contrato", () => ({ filters: { estado: "Vigente" } }));
	},
});
