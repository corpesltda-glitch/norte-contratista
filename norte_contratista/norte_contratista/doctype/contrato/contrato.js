// Copyright (c) 2026, Norte Inteligente SpA and contributors
// For license information, please see license.txt

// Muestra los totales al instante mientras se escribe. El cálculo oficial
// (con redondeo comercial) lo hace el servidor al guardar.

function decimales(frm) {
	return frm.doc.moneda === "CLP" ? 0 : 2;
}

function recalcular(frm) {
	const precision = decimales(frm);
	let total = 0;
	(frm.doc.partidas || []).forEach((partida) => {
		partida.total = flt(flt(partida.cantidad) * flt(partida.precio_unitario), precision);
		total += partida.total;
	});
	frm.refresh_field("partidas");
	frm.set_value("monto_total", flt(total, precision));
}

frappe.ui.form.on("Contrato", {
	moneda: recalcular,
});

frappe.ui.form.on("Partida de Contrato", {
	cantidad: recalcular,
	precio_unitario: recalcular,
	partidas_remove: recalcular,
});
