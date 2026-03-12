import frappe
import frappe.utils as fu

from quickfix.monkey_patches import apply_all


def prefix_add():
	apply_all()
	frappe.conf.custom_url_prefix = "https://cdn.quickfix.com"
	url = fu.get_url("/assets/quickfix/image.png")
	assert "cdn.quickfix.com" in url


def no_prefix():
	apply_all()
	frappe.conf.custom_url_prefix = ""
	url = fu.get_url("/assets/quickfix/image.png")
	assert "cdn.quickfix.com" not in url
