# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class SparePart(Document):
	def autoname(self):
		if self.part_code:
			self.part_code = self.part_code.upper()

		self.name = make_autoname("PART-.YYYY.-.#####")

	def validate(self):
		if self.selling_price <= self.unit_cost:
			frappe.throw("Selling Price cannot be less than Cost Price.")

	# def on_update(self):
	# 	# i used frappe.get_value instead of frappe.get_doc because we only need to fetch a single value.
	# 	threshold = frappe.get_value("QuickFix Settings",None,"low_stock_threshold") or 5
	# 	if self.stock_qty is not None and self.stock_qty <= threshold:
	# 		frappe.msgprint(f"Stock for {self.part_name} is low ({self.stock_qty} units left). Consider reordering.")
