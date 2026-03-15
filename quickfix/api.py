import hashlib
import hmac
import json

# D1
import frappe
import requests
from frappe.utils import add_days, nowdate, today


@frappe.whitelist()
def share_job_card(job_card_name, user_email):
	frappe.share.add("Job Card", job_card_name, user_email, read=1, write=0, share=0)
	return "Job Card shared successfully"


# D1
@frappe.whitelist()
def manager_action():
	frappe.only_for("QF Manager")
	return "Manager action executed successfully"


# D2
def job_card_permission_query(user):
	if "QF Technician" in frappe.get_roles(user):
		return f"""
            `tabJob Card`.assigned_technician IN (
                SELECT name FROM `tabTechnician`
                WHERE user = '{user}'
            )
        """
	return ""


# D2
def service_invoice_permission(doc, user):
	if "QF Manager" in frappe.get_roles(user):
		return True

	job_card = frappe.get_doc("Job Card", doc.job_card)

	if job_card.payment_status == "Paid":
		return False
	return True


# D2 - Unsafe
@frappe.whitelist()
def get_all_records():
	return frappe.get_all("Job Card", fields=["*"])


# D2 - Safe
@frappe.whitelist()
def get_records(user):
	if "QF Manager" in frappe.get_roles(user):
		return frappe.get_list("Job Card", filters={"assigned_technician": user}, fields=["*"])


# E2
@frappe.whitelist()
def rename_technician(old_name, new_name):
	# Merge = True may cause data loss if there are records linked to the technician being renamed.
	# Two Records with the same name will be merged, and the one with the old_name will be deleted.
	frappe.rename_doc("Technician", old_name, new_name, merge=False)


@frappe.whitelist()
def send_job_ready_email(job_card_name):
	job_card = frappe.get_value("Job Card", job_card_name, ["customer_email", "customer_name"], as_dict=True)
	if job_card.customer_email is None:
		return "No customer email found for this Job Card."

	subject = f"Your Job {job_card_name} is Ready for Pickup"
	message = f"""
    Dear {job_card.customer_name},
    Please visit our shop at your earliest convenience to collect your repaired device.

    Best regards,
    QuickFix Team
    """
	frappe.sendmail(recipients=job_card.customer_email, subject=subject, message=message)
	return "Email sent successfully"


@frappe.whitelist(allow_guest=True)
def custom_get_count(doctype, filters=None, debug=False, cache=False):
	frappe.get_doc(
		{
			"doctype": "Audit Log",
			"doctype_name": doctype,
			"document_name": None,
			"action": "count_queried",
			"user": frappe.session.user,
			"timestamp": frappe.utils.now(),
		}
	).insert(ignore_permissions=True)
	from frappe.client import get_count

	return get_count(doctype, filters, debug, cache)


@frappe.whitelist()
def get_overdue_jobs():
	seven = add_days(nowdate(), -7)
	result = frappe.get_all(
		"Job Card",
		fields=["name", "customer_name", "assigned_technician", "creation"],
		filters={"status": ["in", ["Pending Diagnosis", "In Repair"]], "creation": ["<", seven]},
		order_by="creation asc",
	)
	return result


@frappe.whitelist()
def transfer_job(from_tech, to_tech):
	try:
		frappe.db.sql(
			"""
            UPDATE `tabJob Card`
            SET assigned_technician = %s
            WHERE assigned_technician = %s
            AND status NOT IN ('Completed', 'Cancelled')
        """,
			(to_tech, from_tech),
		)

		frappe.db.commit()

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Job Transfer Failed")
		raise Exception("Failed to transfer jobs. Please check error logs for details.")


@frappe.whitelist()
def transfer_job_card(doctype, name, value):
	doc = frappe.get_doc(doctype, name)
	doc.assigned_technician = value
	doc.save(ignore_permissions=True)


@frappe.whitelist()
def generate_monthly_revenue_report(year):
	months = range(1, 13)

	for i, month in enumerate(months, 1):
		revenue = frappe.db.sql(
			"""
            SELECT SUM(final_amount)
            FROM `tabJob Card`
            WHERE YEAR(creation)=%s AND MONTH(creation)=%s
        """,
			(year, month),
		)[0][0]

		frappe.publish_progress(
			percent=round(i / 12 * 100),
			title="Generating Revenue Report",
			description=f"Processing month {month}...",
		)
	return "Revenue report completed"


@frappe.whitelist()
def start_generating_report(year):
	frappe.enqueue(
		method="quickfix.api.generate_monthly_revenue_report", year=year, queue="long", timeout=600
	)


@frappe.whitelist()
def check_low_stock():
	low_stock = frappe.get_value("Audit Log", {"action": "low_stock_check", "timestamp": today()}, "name")

	if low_stock:
		return
	frappe.get_doc({"doctype": "Audit Log", "action": "low_stock_check", "timestamp": today()}).insert(
		ignore_permissions=True
	)


@frappe.whitelist()
def failing_job():
	raise Exception("Failed Job")


@frappe.whitelist()
def start_failing_job():
	frappe.enqueue("quickfix.api.failing_job", queue="short")


def check_stock():
	low = frappe.get_all("Spare Part", {"stock_qty": ["<", 5]}, ["name", "stock_qty"])

	for l in low:
		frappe.get_doc(
			{
				"doctype": "Audit Log",
				"doctype_name": "Spare Part",
				"document_name": l.name,
				"action": "Low Stock",
			}
		).insert(ignore_permissions=True)  # system generated


def cancel_old_draft_job_cards():
	frappe.db.sql("""
        UPDATE `tabJob Card`
        SET status='Cancelled'
        WHERE status='Draft'
        LIMIT 1000
    """)

	frappe.db.commit()


def bulk_insert_audit_logs():
	logs = []

	for i in range(500):
		logs.append((f"gok{i}", "Bulk Insert"))

	frappe.db.bulk_insert("Audit Log", ["name", "action"], logs)


def small_insert():
	for i in range(500):
		frappe.get_doc({"doctype": "Audit Log", "action": "Bulk"}).insert()


@frappe.whitelist()
def get_job_summary():
	job_card = frappe.form_dict.get("job_card_name")
	if not job_card:
		frappe.local.response["http_status_code"] = 404
		return {"error": "Not found"}
	if not frappe.db.exists("Job Card", job_card):
		frappe.local.response["http_status_code"] = 404
		return {"error": "Not found"}
	jc = frappe.get_doc("Job Card", job_card)

	return {"job_card": jc.name, "status": jc.status, "date": jc.delivery_date}


@frappe.whitelist(allow_guest=True)
def get_job_by_phone():
	ip = frappe.local.request_ip
	cache = frappe.cache()

	key = f"rate_limit:{ip}"
	count = cache.get(key) or 0

	if int(count) >= 10:
		frappe.throw("Rate limit exceeded. Try again later.", frappe.TooManyRequestsError)

	cache.set(key, int(count) + 1)

	return {"message": "Request processed"}


logger = frappe.logger("quickfix")


def send_webhook(job_card_name, retry_count=0):
	logger.info("Webhook Started")
	a = frappe.get_single("QuickFix Settings")
	if a.webhook_url is None:
		frappe.msgprint("Webhook URL is not defined")
	jc = frappe.get_doc("Job Card", job_card_name)

	payload = {"chat_id": -1003101501276, "text": f"Job Card{jc.name} Submitted\nAmount:{jc.final_amount}"}
	logger.warn("webhook Error")

	webhook_id = hashlib.sha256(f"Job Card Submitted-{jc.name}".encode()).hexdigest()

	if frappe.db.exists("Audit Log", webhook_id):
		return

	try:
		r = requests.post(a.webhook_url, json=payload, timeout=20)
		r.raise_for_status()

		frappe.get_doc(
			{
				"doctype": "Audit Log",
				"doctype_name": "Webhook",
				"document_name": webhook_id,
				"action": json.dumps(payload),
			}
		).insert(ignore_permissions=True)  # system Iniated
		logger.error("Webhook finished")

	except Exception as e:
		frappe.log_error("Webhook Failed", frappe.get_traceback())

		if retry_count < 3:
			frappe.enqueue(
				"quickfix.api.send_webhook",
				queue="default",
				retry_count=retry_count + 1,
				job_card_name=job_card_name,
			)


def send_webhook_tri(doc, method):
	frappe.enqueue(method="quickfix.api.send_webhook", job_card_name=doc.name)


@frappe.whitelist()
def payment_gateway():
	payload = frappe.request.data
	secret = frappe.conf.get("payment_webhook_secret")
	signature = frappe.get_request_header("X-Signature")
	expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

	if not hmac.compare_digest(expected, signature or ""):
		frappe.throw("Invalid Signature", frappe.InvalidSignatureError)

	data = json.loads(payload)
	pay = data.get("ref")
	if frappe.db.exists("Audit Log", {"action": "payment_received", "document_name": pay}):
		return {"message": "Already Processed"}
	jc = data.get("job_card")
	if jc:
		j = frappe.get_doc("Job Card", jc)
		j.payment_status = "Paid"
		j.save(ignore_permissions=True)

		frappe.get_doc({"doctype": "Audit Log", "document_name": pay, "action": "payment_received"}).insert(
			ignore_permissions=True
		)  # system Iniated
	frappe.db.commit()
	return {"status": "OK"}


def clear_cache(doc=None, method=None):
	frappe.cache.delete_value("job_status_chart")
