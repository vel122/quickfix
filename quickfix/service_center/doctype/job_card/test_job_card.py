# Copyright (c) 2026, Velmurugan and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase


# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]



class IntegrationTestJobCard(IntegrationTestCase):
	"""
	Integration tests for JobCard.
	Use this class for testing interactions between multiple components.
	"""

	def test_job_card_invalid_phone(self):
		doc = frappe.new_doc("Job Card")
		doc.customer_name = "Test Customer"
		#if super().validate is missed
		doc.customer_phone = "123456"
		with self.assertRaises(frappe.ValidationError):
			doc.save()
