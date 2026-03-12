frappe.ui.form.on("Job Card", {
	refresh(frm) {
		console.log("Job Card Refreshed");
		if (!frappe.get_roles(user).includes("QF Manager")) {
			frm.set_df_property("customer_phone", "hidden", 1);
		}
	},
});
