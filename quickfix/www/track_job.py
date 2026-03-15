import re

import frappe
from frappe.rate_limiter import rate_limit

no_cache = 1


@rate_limit(limit=10, seconds=60)
def get_context(context=None):
	if context is None:
		context = frappe._dict()

	context.title = "Track Your Repair Job"

	phone = frappe.form_dict.get("phone")

	if phone:
		phone = phone.strip()

		if not re.fullmatch(r"\d{10}", phone):
			context.message = "Invalid phone number"
			return context

		jobs = frappe.get_all(
			"Job Card", filters={"customer_phone": phone}, fields=["name", "customer_name", "status"], limit=5
		)

		if not jobs:
			context.message = "No jobs found"
		else:
			context.jobs = jobs

	return context
