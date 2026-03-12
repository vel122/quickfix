import frappe

from quickfix.service_center.doctype.job_card.job_card import JobCard


class CustomJobCard(JobCard):
	# MRO (Method Resolution Order) defines how Python resolves method calls
	# for CustomJobCard , MRO is [CustomJobCard, JobCard, Document, object]

	def validate(self):
		# super() is non negotiable to call the parent class method, it ensures that the original validation logic in JobCard is executed before adding custom checks.
		super().validate()
		self._check_urgent_unassigned()

	def _check_urgent_unassigned(self):
		if self.priority == "Urgent" and not self.assigned_technician:
			settings = frappe.get_single("QuickFix Settings")

			frappe.enqueue(
				"quickfix.utils.send_urgent_alert", job_card=self.name, manager=settings.manager_email
			)

	# we use override doctype class , when we need to change the core logic of the doctype, like validate, autoname etc. It allows us to keep our customizations organized and separate from the original doctype definition, making it easier to maintain and upgrade in the future.
	# we use doc events when we want to trigger specific actions based on certain events (like on_update, on_submit) without changing the core logic of the doctype. It is ideal for adding side effects or integrations that should happen in response to doctype events, without modifying the doctype's fundamental behavior.
