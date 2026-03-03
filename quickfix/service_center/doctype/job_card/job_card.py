# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class JobCard(Document):
    def validate(self):

        if self.customer_phone:
            if not self.customer_phone.isdigit() or len(self.customer_phone) != 10:
                frappe.throw("Customer phone number must be 10 digits.")

        if self.status in ["In Repair","Ready for Delivery","Delivered"] and not self.assigned_technician:
             frappe.throw("Please assign a technician")

        if self.labour_charge is None:
            self.labour_charge = frappe.db.get_single_value("QuickFix Settings", "default_labour_charge") or 0
        
        if self.parts_used:
            for part in self.parts_used:
                part.total_price = (part.quantity or 0) * (part.unit_price or 0)

        self.parts_total = sum(part.total_price for part in self.parts_used) if self.parts_used else 0
        self.final_amount = self.parts_total + (self.labour_charge or 0)

    def before_submit(self):
        if self.status != "Ready for Delivery":
            frappe.throw("Not Ready for Delivery.")

        if self.parts_used:
            for part in self.parts_used:
                available_stock = frappe.db.get_value("Spare Part", part.spare_part, "stock_qty") or 0
                if part.quantity >= available_stock:
                    frappe.throw(f"Not enough stock for {part.spare_part}. Available: {available_stock}, Required: {part.quantity}")
                
    
    def on_cancel(self):
        self.status = "Cancelled"

        if self.parts_used:
            for part in self.parts_used:
                if not part.spare_part:
                    continue
                available_stock = frappe.db.get_value("Spare Part", part.spare_part, "stock_qty") or 0
                new_stock = available_stock + (part.quantity or 0)
                frappe.db.set_value("Spare Part", part.spare_part, "stock_qty", new_stock)

        invoice = frappe.db.get_value("Service Invoice", {"job_card": self.name}, "name")
        if invoice:
            invoice_doc = frappe.get_doc("Service Invoice", invoice)
            if invoice_doc.docstatus == 1:
                invoice_doc.cancel()

    def on_submit(self):

        if self.parts_used:
            for part in self.parts_used:
                if not part.spare_part:
                    continue
                available_stock = frappe.db.get_value("Spare Part", part.spare_part, "stock_qty") or 0
                new_stock = available_stock - (part.quantity or 0)
                # ignore_permissions=True is acceptable because this is a system-triggered
                # stock deduction during document submission, not a user-initiated edit.
                doc = frappe.get_doc("Spare Part", part.spare_part)
                doc.stock_qty = new_stock
                doc.save(ignore_permissions=True)

        frappe.get_doc({
            "doctype": "Service Invoice",
            "job_card": self.name,
            "customer_name": self.customer_name,
            "invoice_date": frappe.utils.nowdate(),
            "labour_charge": self.labour_charge,
            "parts_total": self.parts_total,
            "total_amount": self.final_amount,
            "payment_status": "Unpaid"
        }).insert(ignore_permissions=True)

        frappe.publish_realtime("job_ready", {"job_card": self.name}, user=self.owner)
        frappe.enqueue("quickfix.api.send_job_ready_email", job_card_name=self.name, queue="short", timeout=300)

    def on_trash(self):
        if self.status not in ["Draft", "Cancelled"]:
            frappe.throw("Only Job Cards in Draft or Cancelled status can be deleted.")


