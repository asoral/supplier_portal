
import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def register_vendor(company_name, email, contact_person, phone, gst=None, password=None):
    """
    Registers a new vendor user and supplier document.
    """
    try:
        if frappe.db.exists("User", email):
            return {"status": "failed", "message": "Email already registered"}

        # 1. Create User
        user = frappe.new_doc("User")
        user.email = email
        user.first_name = contact_person
        user.mobile_no = phone
        user.enabled = 1
        user.new_password = password
        user.send_welcome_email = 0  # Avoid email if not configured
        user.save(ignore_permissions=True)
        
        # Add Supplier Role
        user.add_roles("Supplier")

        # 2. Create Supplier
        # Check if supplier with same name exists
        if frappe.db.exists("Supplier", company_name):
            # Maybe append a number or just accept it? 
            # Ideally unique, but let's try to create it.
            pass

        supplier = frappe.new_doc("Supplier")
        supplier.supplier_name = company_name
        supplier.supplier_group = "All Supplier Groups"  # Ensure this group exists or pick default
        supplier.tax_id = gst
        
        # Link User to Supplier if needed for 'Supplier Portal' standard flow
        # In standard ERPNext, the link is often done via 'Portal User' in Supplier
        # or just matching email if 'Grant Commission' etc. 
        # For now, we just create the record.
        
        supplier.save(ignore_permissions=True)
        
        # Commit to ensure persistence even if other things fail later
        frappe.db.commit()

        return {"status": "success", "message": "Vendor registered successfully"}

    except Exception as e:
        frappe.log_error("Vendor Registration Error")
        return {"status": "error", "message": str(e)}
