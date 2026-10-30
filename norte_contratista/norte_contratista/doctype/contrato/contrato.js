// Copyright (c) 2026, Norte Inteligente SpA and contributors
// For license information, please see license.txt

// Muestra los totales al instante mientras se escribe. El cálculo oficial
// (con redondeo comercial) lo hace el servidor al guardar.

function decimales(frm) {
	return frm.doc.moneda === "CLP" ? 0 : 2;
}

// Redondeo comercial (el medio sube) sin el ruido de punto flotante (1,15 × 50 = 57,4999…).
function redondear(valor, precision) {
	const factor = 10 ** precision;
	return Math.round(Number((valor * factor).toPrecision(12))) / factor;
}

function recalcular(frm) {
	const precision = decimales(frm);
	let total = 0;
	(frm.doc.partidas || []).forEach((partida) => {
		partida.total = redondear(flt(partida.cantidad) * flt(partida.precio_unitario), precision);
		total += partida.total;
	});
	frm.refresh_field("partidas");
	frm.set_value("monto_total", redondear(total, precision));
}

frappe.ui.form.on("Contrato", {
	moneda: recalcular,
});

frappe.ui.form.on("Partida de Contrato", {
	cantidad: recalcular,
	precio_unitario: recalcular,
	partidas_remove: recalcular,
});
