from frappe.query_builder import DocType
from frappe.utils import nowdate,add_days
#D1
import frappe
@frappe.whitelist()
def share_job_card(job_card_name, user_email):
    frappe.share.add("Job Card", job_card_name, user_email, read=1, write=0, share=0)
    return "Job Card shared successfully"

#D1
@frappe.whitelist()
def manager_action():
    frappe.only_for("QF Manager")
    return "Manager action executed successfully"


#D2
def job_card_permission_query(user):
    if "QF Technician" in frappe.get_roles(user):
        return f"""
            `tabJob Card`.assigned_technician IN (
                SELECT name FROM `tabTechnician`
                WHERE user = '{user}'
            )
        """
    return ""

#D2
def service_invoice_permission(doc,user):
    if "QF Manager" in frappe.get_roles(user):
        return True
    
    job_card = frappe.get_doc("Job Card", doc.job_card)

    if job_card.payment_status == "Paid":
        return False
    return True

#D2 - Unsafe
@frappe.whitelist()
def get_all_records():
    return frappe.get_all("Job Card", fields=["*"])

#D2 - Safe
@frappe.whitelist()
def get_records(user):
    if "QF Manager" in frappe.get_roles(user):
       return frappe.get_list("Job Card", filters={"assigned_technician": user}, fields=["*"])

#E2
@frappe.whitelist()
def rename_technician(old_name, new_name):
    # Merge = True may cause data loss if there are records linked to the technician being renamed.
    # Two Records with the same name will be merged, and the one with the old_name will be deleted.
    frappe.rename_doc("Technician", old_name, new_name, merge=False)


@frappe.whitelist()
def send_job_ready_email(job_card_name):
    job_card = frappe.get_value("Job Card", job_card_name, ["customer_email", "customer_name"])
    if not job_card.customer_email:
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
    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": doctype,
        "document_name": None,
        "action": "count_queried",
        "user": frappe.session.user,
        "timestamp": frappe.utils.now()
    }).insert(ignore_permissions=True)
    from frappe.client import get_count
    return get_count(doctype, filters, debug, cache)


@frappe.whitelist()
def get_overdue_jobs():
    JC = DocType("Job Card")
    seven = add_days(nowdate(), -7)
    result = (
        frappe.qb.from_(JC)
        .select(JC.name, JC.customer_name, JC.assigned_technician, JC.creation)
        .where((JC.status.isin(["Pending Diagnosis","In Repair"])) & (JC.creation < seven))
        .orderby(JC.creation.asc())
        .run(as_dict=True)
    )
    return result

@frappe.whitelist()
def transfer_job(from_tech, to_tech):
    try:
        frappe.db.sql("""
            UPDATE `tabJob Card`
            SET assigned_technician = %s
            WHERE assigned_technician = %s
            AND status NOT IN ('Completed', 'Cancelled')
        """, (to_tech, from_tech))

        frappe.db.commit()

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Job Transfer Failed")
        raise