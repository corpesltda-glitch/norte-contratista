// Copyright (c) 2026, Norte Inteligente SpA and contributors
// For license information, please see license.txt

frappe.ui.form.on("Estado de Pago", {
	setup(frm) {
		frm.set_query("contrato", () => ({ filters: { estado: "Vigente" } }));
	},
	traer_avance(frm) {
		frm.call("traer_avance_de_reportes").then(() => {
			frm.reload_doc();
			frappe.show_alert({
				message: __("Avance cargado desde los reportes diarios firmados"),
				indicator: "green",
			});
		});
	},
});
