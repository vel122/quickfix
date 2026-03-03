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
def service_invoice_permission(doc,user=None):
    user = user or frappe.session.user
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
def get_records():
    user = frappe.session.user
    if "QF Manager" in frappe.get_roles(user):
       return frappe.get_list("Job Card", filters={"assigned_technician": user}, fields=["*"])

#E2
@frappe.whitelist()
def rename_technician(old_name, new_name):
    # Merge = True may cause data loss if there are records linked to the technician being renamed.
    # Two Records with the same name will be merged, and the one with the old_name will be deleted.
    frappe.rename_doc("Technician", old_name, new_name, merge=False)