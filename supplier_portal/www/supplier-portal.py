import frappe

def get_context(context):
    context.no_cache = 1
    context.csrf_token = frappe.session.csrf_token
