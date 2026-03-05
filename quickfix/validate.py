import frappe

def validate(self):
        if self.customer_phone:
            if not self.customer_phone.isdigit() or len(self.customer_phone) != 10:
                frappe.throw("Customer phone number must be 10 digits.")