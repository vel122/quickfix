import frappe


def after_install():
	frappe.make_property_setter("Job Card", "remarks", "bold", 1, "Check")
	create_default_devicetypes()
	create_default_quickfix_settings()
	frappe.msgprint("QuickFix Service Center setup completed successfully.")


def before_uninstall():
	check_job_card()


def create_default_devicetypes():
	device_types = ["Mobile", "Laptop", "Tablet"]
	for device in device_types:
		if not frappe.db.exists("Device Type", device):
			doc = frappe.get_doc({"doctype": "Device Type", "device_type": device})
			doc.insert(ignore_permissions=True)


def create_default_quickfix_settings():
	if not frappe.db.exists("QuickFix Settings", "QuickFix Settings"):
		doc = frappe.get_doc(
			{
				"doctype": "QuickFix Settings",
				"shop_name": "QuickFix Shop",
				"manager_email": "manager@example.com",
				"default_labour_charge": 50.0,
				"low_stock_alert_enabled": 1,
			}
		)
		doc.insert(ignore_permissions=True)


def check_job_card():
	if frappe.db.exists("Job Card", {"docstatus": 1}):
		frappe.throw("Submitted Job Cards exist", frappe.ValidationError)
