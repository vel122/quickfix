// Copyright (c) 2026, Velmurugan and contributors
// For license information, please see license.txt

frappe.query_reports["Spare Parts Inventory"] = {
	formatter: function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (data && data.stock_qty < data.reorder_level) {
			value = `<span style="color: red; font-weight: bold;">${value}</span>`;
		}

		return value;
	}
};
