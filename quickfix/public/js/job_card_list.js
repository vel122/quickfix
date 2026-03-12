frappe.listview_settings["Job Card"] = {
    onload(listview) {
        console.log("Job Card List View Loaded");
    },
    add_fields: ["status", "final_amount", "priority"],
    has_indicator_for_draft: true,

    get_indicator: function(doc) {
        if (doc.status === "Pending Diagnosis") {
            return [__("Pending Diagnosis"), "orange", "status,=,Pending Diagnosis"];
        } 
        else if (doc.status === "In Repair") {
            return [__("In Repair"), "blue", "status,=,In Repair"];
        } 
        else if (doc.status === "Ready for Delivery") {
            return [__("Ready for Delivery"), "green", "status,=,Ready for Delivery"];
        } 
        else if (doc.status === "Delivered") {
            return [__("Delivered"), "yellow", "status,=,Delivered"];
        } 
        else if (doc.status === "Cancelled") {
            return [__("Cancelled"), "red", "status,=,Cancelled"];
        } 
        else if (doc.status === "Awaiting Customer Approval") {
            return [__("Awaiting Customer Approval"), "pink", "status,=,Awaiting Customer Approval"];
        }
    },
    formatters: {
        final_amount(val) {
            if (!val) return "";
            return format_currency(val);
        }
    },

    button: {

        show: function(doc) {
            return doc.status === "In Repair";
        },

        get_label: function() {
            return __("Mark Ready");
        },

        get_description: function(doc) {
            return __("Mark as Ready for Delivery");
        },

        action: function(doc) {

            frappe.confirm(
                __("Are you sure you want to mark this Job Card as Ready for Delivery?"),
                function() {

                    frappe.call({
                        method: "frappe.client.set_value",
                        args: {
                            doctype: "Job Card",
                            name: doc.name,
                            fieldname: "status",
                            value: "Ready for Delivery"
                        },
                        callback: function(r) {
                            if (!r.exc) {

                                frappe.show_alert({
                                    message: `${doc.name} marked as Ready for Delivery`,
                                    indicator: "green"
                                }, 5);

                                cur_list.refresh();
                            }
                        }
                    });

                }
            );

        }
    }

};