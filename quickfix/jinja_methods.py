import frappe


def get_shop_name():
	settings = frappe.get_single("QuickFix Settings")
	return settings.shop_name


def format_job_id(value):
	if not value:
		return ""
	return f"JOB#{value}"
