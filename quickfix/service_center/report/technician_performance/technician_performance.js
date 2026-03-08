// Copyright (c) 2026, Velmurugan and contributors
// For license information, please see license.txt

frappe.query_reports["Technician Performance"] = {
	filters: [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default":frappe.datetime.month_start(),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default":frappe.datetime.month_end(),
		},
	],
	formatter: function(value, row, column, data, default_formatter) {

		value = default_formatter(value, row, column, data);

		if (column.fieldname === "completion_rate") {

		if (data.completion_rate < 70) {
			value = `<span style="color:red;font-weight:bold">${value}</span>`;
		}

		if (data.completion_rate >= 90) {
			value = `<span style="color:green;font-weight:bold">${value}</span>`;
		}

		}

		return value;
	}
};
