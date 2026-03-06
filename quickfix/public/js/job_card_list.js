frappe.listview_settings["Job Card"] = {
    onload(listview) {
        console.log("Job Card List View Loaded");
    },
    add_fields: ["status", "final_amount", "priority"],

    get_indicator: function(doc) {
        if (doc.status === "Pending Diagnosis") {
            return [__("Pending Diagnosis"), "orange", "status,=,Pending Diagnosis"];
        } else if (doc.status === "In Repair") {
            return [__("In Repair"), "blue", "status,=,In Repair"];
        } else if (doc.status === "Ready for Delivery") {
            return [__("Ready for Delivery"), "green", "status,=,Ready for Delivery"];
        } else if (doc.status === "Delivered") {
            return [__("Delivered"), "gray", "status,=,Delivered"];
        } else if (doc.status === "Cancelled") {
            return [__("Cancelled"), "red", "status,=,Cancelled"];
        } else if (doc.status === "Awaiting Customer Approval") {
            return [__("Awaiting Customer Approval"), "pink", "status,=,Awaiting Customer Approval"];
        }
    },
    formatters: {
        final_amount(val,field,doc){
            if(!val){
                return ""
            }
            return format_currency(val);
        }
    }
    // button: {
    //     show: function(doc) {
    //         return doc.status === "In Repair";
    //     },
    //     get_label: function() {
    //         return "Complete Repair";
    //     },
    //     action: function(doc) {
    //         frappe.call({
    //             method: "quickfix.api.mark_job_ready",
    //             args: {
    //                 job_card_name: doc.name
    //             },
    //             callback: function() {
    //                 frappe.show_alert("Job marked as Ready for Delivery");
    //                 frappe.listview.refresh();
    //             }
    //         });
    //     }
    // }
};