# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Technician(Document):
	def validate(self):
		user = self.email
		if frappe.db.exists("User", user):
			frappe.throw("Email Already exists")

	def after_insert(self):
		frappe.enqueue(
			"quickfix.service_center.doctype.technician.technician.create_user",
			queue="default",
			technician=self.name,
			enqueue_after_commit=True,
		)


def create_user(technician):
	doc = frappe.get_doc("Technician", technician)
	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": doc.email,
			"first_name": doc.technician_name,
			"enabled": 1,
			"send_welcome_email": 1,
			"roles": [{"role": "QF Technician"}],
		}
	).insert()

	doc.user = user.name
	doc.db_update()
