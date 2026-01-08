
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
        user.user_type = "Website User" 
        user.new_password = password
        user.send_welcome_email = 0  # Avoid email if not configured
        user.save(ignore_permissions=True)
        
        # Add Supplier Role
        user.add_roles("Supplier")

        # 2. Create Supplier
        # Check if supplier with same name exists
        if frappe.db.exists("Supplier", company_name):
            # If exists, we should probably append this user to it? 
            # Or fail? For now let's use the existing one if it exists to avoid errors, 
            # but usually registration implies new entity.
            # Let's try to get the existing one.
            supplier = frappe.get_doc("Supplier", company_name)
        else:
            supplier = frappe.new_doc("Supplier")
            supplier.supplier_name = company_name
            supplier.supplier_group = "All Supplier Groups"
            supplier.tax_id = gst
        
        # Link User to Supplier (portal_users)
        # Check if already linked
        is_linked = False
        if not supplier.portal_users:
            supplier.portal_users = []
        
        for row in supplier.portal_users:
            if row.user == email:
                is_linked = True
                break
        
        if not is_linked:
            supplier.append("portal_users", {
                "user": email
            })
            supplier.save(ignore_permissions=True)
        
        # Commit to ensure persistence even if other things fail later
        frappe.db.commit()

        return {"status": "success", "message": "Vendor registered successfully"}

    except Exception as e:
        frappe.log_error("Vendor Registration Error")
        return {"status": "error", "message": str(e)}
