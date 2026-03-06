import frappe

def extend_boot_info(bootinfo):
    frappe.logger().info("BOOT FUNCTION EXECUTED")

    settings = frappe.get_single("QuickFix Settings")

    bootinfo.quickfix_shop_name = settings.shop_name
    bootinfo.quickfix_manager_email = settings.manager_email
    