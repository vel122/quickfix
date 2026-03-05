// Copyright (c) 2026, Velmurugan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Card", {
    onload(frm) {
        frappe.call({
            method: "frappe.client.get_count",
            args: {
                doctype: "Job Card",
            }
        });
    },
    refresh(frm) {
        frappe.realtime.on("job_ready", function(data) {
            frappe.msgprint(`Job Card ${data.job_card} is ready!`);
        });
    }
});