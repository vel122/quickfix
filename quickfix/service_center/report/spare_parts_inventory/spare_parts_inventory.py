# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns()
	data = get_data()

	total_parts = len(data)
	below_reorder = sum(1 for row in data if row.stock_qty < row.reorder_level)
	total_value = sum(row.stock_qty * row.unit_cost for row in data)

	report_summary = [
		{"label": _("Total Parts"), "value": total_parts},
		{"label": _("Below Reorder Level"), "value": below_reorder},
		{"label": _("Total Inventory Value"), "value": total_value, "currency": "currency"},
	]

	total_stock_qty = sum(row.stock_qty for row in data)
	data.append(
		{
			"part_name": _("Total"),
			"stock_qty": total_stock_qty,
		}
	)

	for d in data:
		if d.get("unit_cost") is not None:
			d["unit_cost"] = f"{d['unit_cost']:.2f}"
		if d.get("selling_price") is not None:
			d["selling_price"] = f"{d['selling_price']:.2f}"
	return columns, data, None, None, report_summary


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		{
			"label": _("Part Name"),
			"fieldname": "part_name",
			"fieldtype": "Data",
		},
		{
			"label": _("Part Code"),
			"fieldname": "part_code",
			"fieldtype": "Data",
		},
		{
			"label": _("Device Type"),
			"fieldname": "compatible_device_type",
			"fieldtype": "Data",
		},
		{
			"label": _("Stock Qty"),
			"fieldname": "stock_qty",
			"fieldtype": "Int",
		},
		{
			"label": _("Reorder Level"),
			"fieldname": "reorder_level",
			"fieldtype": "Int",
		},
		{
			"label": _("Unit Cost"),
			"fieldname": "unit_cost",
			"fieldtype": "Currency",
			"options": "currency",
		},
		{
			"label": _("Selling Price"),
			"fieldname": "selling_price",
			"fieldtype": "Currency",
			"options": "currency",
		},
		{
			"label": _("Margin %"),
			"fieldname": "margin_percentage",
			"fieldtype": "Percent",
		},
	]


def get_data() -> list[list]:
	return frappe.db.sql(
		"""
		SELECT
			part_name,
			part_code,
			compatible_device_type,
			stock_qty,
			reorder_level,
			unit_cost,
			selling_price,
			((selling_price - unit_cost) / selling_price * 100) AS margin_percentage
		FROM `tabSpare Part`
	""",
		as_dict=True,
	)
