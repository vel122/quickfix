import frappe
from frappe.utils import now


def on_session_creation():
	frappe.get_doc(
		{
			"doctype": "Audit Log",
			"doctype_name": "User",
			"document_name": frappe.session.user,
			"action": "login",
			"user": frappe.session.user,
			"timestamp": now(),
		}
	).insert(ignore_permissions=True)


def on_logout():
	frappe.get_doc(
		{
			"doctype": "Audit Log",
			"doctype_name": "User",
			"document_name": frappe.session.user,
			"action": "logout",
			"user": frappe.session.user,
			"timestamp": now(),
		}
	).insert(ignore_permissions=True)
