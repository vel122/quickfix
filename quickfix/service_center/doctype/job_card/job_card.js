frappe.ui.form.on("Job Card", {
    setup(frm) {
        frm.set_query("assigned_technician", function() {
            return {
                filters: {
                    "status": "Active",
                    "specialization": frm.doc.device_type
                }
            };
        });
    },
    onload(frm) {
        frappe.realtime.on("job_ready", (data) => {
            if (data.job_card === frm.doc.name) {
                frappe.show_alert(`Job Card ${data.job_card} is ready!`);
            }
        });

        frappe.call({
            method: "frappe.client.get_count",
            args: {
                doctype: "Job Card",
            }
        });
    },
    refresh(frm) {

        if (frm.doc.docstatus === 1 && frm.doc.status === "Ready for Delivery") {
            frm.add_custom_button("Mark as Delivered", function () {
                frm.set_value("status", "Delivered");
                frm.save();
            });
        }


        if (frm.doc.status === "Pending Diagnosis") {
            frm.dashboard.add_indicator("Pending Diagnosis", "orange");

        } else if (frm.doc.status === "In Repair") {
            frm.dashboard.add_indicator("In Repair", "blue");

        } else if (frm.doc.status === "Ready for Delivery") {
            frm.dashboard.add_indicator("Ready for Delivery", "green");

        } else if (frm.doc.status === "Delivered") {
            frm.dashboard.add_indicator("Delivered", "gray");

        } else if (frm.doc.status === "Cancelled") {
            frm.dashboard.add_indicator("Cancelled", "red");

        } else if (frm.doc.status === "Awaiting Customer Approval") {
            frm.dashboard.add_indicator("Awaiting Customer Approval", "pink");
        }

        if (frappe.boot.quickfix_shop_name) {
            frm.dashboard.set_headline(
                `Shop: ${frappe.boot.quickfix_shop_name}`
            );
        }

        if(frm.doc.docstatus === 1) {
            frm.add_custom_button("Reject Job", function() { 
                let a = new frappe.ui.Dialog({
                    title: "Reject Job",
                    fields: [
                        {
                            label: "Reason for Rejection",
                            fieldname: "reason_for_rejection",
                            fieldtype: "Small Text",
                            reqd: 1
                        }
                    ],
                    primary_action_label: "Submit",
                    primary_action(values) {
                        frm.set_value("status", "Cancelled");
                        frm.set_value("reason_for_rejection", values.reason_for_rejection);
                        frm.save();
                        a.hide();
                    }
                });
                a.show();
            });
        }

        if(frm.doc.docstatus === 1){
            frm.add_custom_button("Transfer Technician", function() {
                frappe.prompt([
                    {
                        label: "Select Technician",
                        fieldname: "new_technician",
                        fieldtype: "Link",
                        options: "Technician",
                        reqd: 1,
                        get_query() {
                            return {
                                filters: {
                                    "status": "Active",
                                    "specialization": frm.doc.device_type
                                }
                            };
                        }
                    }
                ], function(values) {
                    frappe.confirm(`Are you sure you want to transfer this job to ${values.new_technician}?`, function() {
                        if(frm.doc.assigned_technician === values.new_technician) {
                            frappe.msgprint("This technician is already assigned to this job.");
                            return;
                        }
                        frm.call({
                            method: "quickfix.api.transfer_job_card",
                            args: {
                                doctype: "Job Card",
                                name: frm.doc.name,
                                value: values.new_technician
                            },
                            callback() {
                                frm.trigger("assigned_technician");
                            }
                        });
                    });
                });
            });
        }
    },
    assigned_technician(frm) {
        if(!frm.doc.assigned_technician) 
            return;
        frappe.db.get_value("Technician", frm.doc.assigned_technician,"specialization").then(res => {
            if(res.message.specialization !== frm.doc.device_type) {
                frappe.warn("Selected technician does not specialize in the device type. Please select a different technician.");
                frm.set_value("assigned_technician", null);
            }
        });
    }
});


frappe.ui.form.on("Part Usage Entry", {
    quantity(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.quantity && row.unit_price) {
            frappe.model.set_value(cdt, cdn, "total_price", row.quantity * row.unit_price);
        }
    },
});