import json

import frappe
from frappe import _
from frappe.query_builder.functions import Sum
from frappe.utils import nowdate, strip_html
from frappe.utils.file_manager import save_file

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
        user.user_type = "System User" 
        user.new_password = password
        user.send_welcome_email = 0  
        user.save(ignore_permissions=True)
        
        # Add Supplier Role
        user.add_roles("Supplier")

        # 2. Create Supplier
        # Check if supplier with same name exists (using specific field to avoid ID conflicts)
        existing_supplier_name = frappe.db.get_value("Supplier", {"supplier_name": company_name}, "name")
        
        if existing_supplier_name:
            supplier = frappe.get_doc("Supplier", existing_supplier_name)
        else:
            supplier = frappe.new_doc("Supplier")
            supplier.supplier_name = company_name
            supplier.supplier_group = "All Supplier Groups"
            supplier.tax_id = gst
            # Do not save yet, wait for linking
        
        # Link User to Supplier (portal_users)
        # Check if already linked
        is_linked = False
        
        # Ensure child table exists (for new docs it's empty list)
        if not supplier.get("portal_users"):
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
        
        # Commit to ensure persistence
        frappe.db.commit()

        return {"status": "success", "message": "Vendor registered successfully"}

    except Exception as e:
        frappe.log_error(f"Vendor Registration Error: {str(e)}", "Vendor Registration Error")
        return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=True)
def get_supplier_details():
    user = frappe.session.user
    if not user or user == "Guest":
        return {}
    
    try:
        child_doctype = "Portal User"
        meta = frappe.get_meta("Supplier")
        field = meta.get_field("portal_users")
        if field and field.options:
            child_doctype = field.options
        
        # Find supplier where this user is listed in portal_users
        suppliers = frappe.get_all("Supplier", filters={
            "name": ["in", frappe.get_all(child_doctype, filters={"user": user, "parenttype": "Supplier"}, pluck="parent")]
        }, fields=["name", "supplier_name", "email_id"])
        
        if suppliers:
            return suppliers[0]
            
    except Exception as e:
        frappe.log_error(f"Get Supplier Details Error: {str(e)}")
        
    return {}

@frappe.whitelist(allow_guest=True)
def get_active_tenders(limit=20, offset=0, priority=None):
    user = frappe.session.user
    limit = int(limit)
    offset = int(offset)

    invited_rfq_names = []

    if user and user != "Guest":
        suppliers = frappe.get_all(
            "Portal User",
            filters={"user": user, "parenttype": "Supplier"},
            pluck="parent",
            ignore_permissions=True
        )

        if suppliers:
            invited_rfq_names = frappe.get_all(
                "Request for Quotation Supplier",
                filters={"supplier": ["in", suppliers]},
                pluck="parent",
                ignore_permissions=True
            )

    query_values = []

    # Build private condition
    private_condition = ""
    if invited_rfq_names:
        placeholders = ', '.join(['%s'] * len(invited_rfq_names))
        private_condition = f" OR name IN ({placeholders})"
        query_values.extend(invited_rfq_names)

    priority_sql = ""
    if priority and priority != "All":
        priority_sql = " AND custom_priority = %s"
        query_values.append(priority)

    query_values.extend([limit, offset])

    sql = f"""
        SELECT 
            name,
            COALESCE(custom_rfq_subject, name) as custom_rfq_subject,
            custom_rfq_description, 
            custom_rfq_category,
            custom_bid_status, 
            custom_total_budget_, 
            custom_bid_submission_last_date,
            custom_publish_date, 
            custom_enable_live_bidding, 
            transaction_date, 
            status,
            custom_priority,
            custom_publish_on_website
        FROM `tabRequest for Quotation`
        WHERE docstatus = 1
        AND (
            custom_publish_on_website = 1
            {private_condition}
        )
        {priority_sql}
        ORDER BY modified DESC
        LIMIT %s OFFSET %s
    """

    return frappe.db.sql(sql, tuple(query_values), as_dict=True)

@frappe.whitelist(allow_guest=True)
def get_tender_details(name):
    # Security/Permission Check
    user = frappe.session.user
    
    has_access = False
    
    # Check if published (Allow Draft/Submitted)
    is_published = frappe.db.get_value("Request for Quotation", name, "custom_publish_on_website")
    if is_published:
        has_access = True
    elif user and user != "Guest":
        # Check if user is linked to a supplier invited to this RFQ
        supplier_details = get_supplier_details()
        if supplier_details:
             supplier = supplier_details.get("name")
             # Check if this supplier is in the RFQ's supplier list child table
             # Field: suppliers (standard) -> Doctype: Request for Quotation Supplier (standard)
             if frappe.db.exists("Request for Quotation Supplier", {"parent": name, "supplier": supplier}):
                 has_access = True
    
    if not has_access:
        frappe.throw(_("You do not have permission to view this Tender"), frappe.PermissionError)

    # Bypass standard permission checks logic
    # Using get_all and constructing dict to avoid set_user("Administrator")
    
    # Fetch Main Doc Fields
    rfq_data = frappe.get_all("Request for Quotation", filters={"name": name}, fields=["*"], ignore_permissions=True)
    if not rfq_data:
         frappe.throw(_("Tender not found"), frappe.DuplicateEntryError)
    
    doc = rfq_data[0]
    
    # Fetch Items
    rfq_items = frappe.get_all("Request for Quotation Item", filters={"parent": name}, fields=["*"], ignore_permissions=True)
    
    # Prepare Items / Specs
    items = []
    total_qty = 0
    for item in rfq_items:
        items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "description": item.description,
            "qty": item.qty,
            "uom": item.uom,
            "image": item.image,
            "budget": item.custom_budget,
            "budget_amount": item.custom_budget_amount,
            "attach_boq": item.custom_attach_boq,
            "custom_contact_person_display": doc.custom_contact_person_display,
            "custom_contact_address_display": doc.custom_contact_address_display,
        })
        total_qty += item.qty
        
    attachments = frappe.get_all("File", 
    filters={"attached_to_name": name, "attached_to_doctype": "Request for Quotation", "is_private": 0},
    fields=["file_name", "file_url", "file_size"],
    ignore_permissions=True
)
    
    if doc.get("custom_downloadable_forms"):
        attachments.append({
            "file_name": "Tender Form", 
            "file_url": doc.get("custom_downloadable_forms"),
            "file_size": "-" 
        })
    
    # Map fields dynamically
    return {
        "name": doc.name,
        "title": doc.get("custom_rfq_subject") or doc.name,
        "description": doc.get("custom_rfq_description"),
        "category": doc.get("custom_rfq_category"),
        "status": doc.get("custom_bid_status"),
        "total_quantity": total_qty, 
        "total_budget": doc.get("custom_total_budget_"),
        "submission_date": doc.get("custom_bid_submission_last_date"),
        "submission_start_date": doc.get("custom_bid_submission_start_date"),
        "result_date": doc.get("custom_result_date"),
        "publish_date": doc.get("custom_publish_date"),
        "min_bid_decrement": doc.get("custom_min_live_bid_decrement"),
        "emd_amount": doc.get("custom_emd_amount"),
        "auto_extension_limit": doc.get("custom_auto_extension_limit"), 
        "department": doc.get("custom_department"),
        "custom_contact_person_display": doc.get("custom_contact_person_display"), 
        "custom_contact_address_display": doc.get("custom_contact_address_display"),
        "billing_address": doc.get("billing_address_display") or doc.get("custom_address_display"),
        "terms": doc.terms,
        "items": items,
        "uom": items[0]["uom"] if items else "",
        "documents": attachments,
        "enable_live_bidding": doc.get("custom_enable_live_bidding"),
        # Timelines
        "transaction_date": doc.transaction_date, 
        "schedule_date": doc.schedule_date,
        "incoterm":doc.incoterm
    }

@frappe.whitelist(allow_guest=True)
def get_dashboard_stats():
    user = frappe.session.user
    if not user or user == "Guest":
        return {"error": "Not logged in"}
    
    # Removed set_user("Administrator")
    
    try:
        # 1. Find ALL Suppliers linked to this user
        # Added ignore_permissions=True
        suppliers = frappe.get_all("Portal User", 
                                 filters={"user": user, "parenttype": "Supplier"}, 
                                 fields=["parent"],
                                 ignore_permissions=True)
        
        if not suppliers:
            return {"error": "No supplier linked"}
            
        supplier_names = [s.parent for s in suppliers]
                
        # Total Bids (Supplier Quotations)
        total_bids = frappe.db.count("Supplier Quotation", filters={"supplier": ["in", supplier_names], "docstatus": ["<", 2]})
        
        # Orders Won (Purchase Orders)
        orders_won = frappe.db.count("Purchase Order", filters={"supplier": ["in", supplier_names], "docstatus": 1})
        
        # Pending Review
        pending_review = frappe.db.count("Supplier Quotation", filters={"supplier": ["in", supplier_names], "status": "Submitted"})
        
        # NOTE: If frappe.db.count fails due to permissions, we'd need SQL. But let's assume it works or fallback to SQL if errors reported. 
        # Actually safer to use SQL if we are really worried about perms, but db.count is usually low level? 
        # Wait, db.count DOES check permissions in recent versions.
        # Let's use SQL for safety since we removed set_user.
        
        placeholders = ', '.join(['%s'] * len(supplier_names))
        
        total_bids = frappe.db.sql(f"""
            SELECT count(*) FROM `tabSupplier Quotation` 
            WHERE supplier IN ({placeholders}) AND docstatus < 2
        """, tuple(supplier_names))[0][0]
    
        orders_won = frappe.db.sql(f"""
            SELECT count(*) FROM `tabSupplier Quotation` 
            WHERE supplier IN ({placeholders}) 
            AND status = 'Ordered' 
            AND docstatus = 1
        """, tuple(supplier_names))[0][0]

        pending_review = frappe.db.sql(f"""
            SELECT count(*) FROM `tabSupplier Quotation` 
            WHERE supplier IN ({placeholders}) 
            AND status = 'Submitted'
        """, tuple(supplier_names))[0][0]

        win_rate = int((total_bids / orders_won) * 100) if total_bids > 0 else 0
                
        # 3. Recent Bids (Fetch for ANY of the suppliers)
        # SQL already bypasses perms required
        recent_bids_data = frappe.db.sql(f"""
            SELECT 
                sq.name, sq.transaction_date, sq.grand_total, sq.status, 
                rfq.custom_rfq_subject as title, sq.request_for_quotation
            FROM `tabSupplier Quotation` sq
            LEFT JOIN `tabRequest for Quotation` rfq ON sq.request_for_quotation = rfq.name
            WHERE sq.supplier IN ({placeholders}) AND sq.docstatus < 2
            ORDER BY sq.transaction_date DESC
            LIMIT 5
        """, tuple(supplier_names), as_dict=True)
        
        # Format Recent Bids
        recent_bids = []
        for bid in recent_bids_data:
            status_color = "bg-gray-100 text-gray-800"
            if bid.status == "Ordered":
                status_color = "bg-green-100 text-green-800"
            elif bid.status == "Submitted":
                status_color = "bg-yellow-100 text-yellow-800"
            elif bid.status == "Lost":
                status_color = "bg-red-100 text-red-800"
                
            recent_bids.append({
                "title": bid.title or bid.request_for_quotation or bid.name,
                "id": bid.name,
                "amount": bid.grand_total,
                "date": bid.transaction_date,
                "status": bid.status,
                "statusColor": status_color
            })
            
        # Get primary supplier name(s) for display
        display_supplier_name = ", ".join(supplier_names)
        profile_data = get_supplier_profile()
        
        return {
            "stats": {
                "total_bids": total_bids,
                "orders_won": orders_won,
                "pending_review": pending_review,
                "win_rate": f"{win_rate}%"
            },
            "recent_bids": recent_bids,
            "supplier_name": display_supplier_name,
            "user_name": frappe.db.get_value("User", user, "full_name") or user,
            "profile": profile_data
        }

    except Exception as e:
        frappe.log_error(f"Dashboard Stats Error: {str(e)}")
        return {"error": "Error fetching dashboard data"}

@frappe.whitelist(allow_guest=True)
def get_saved_tenders():
    """
    Fetches saved tenders for the current user.
    """
    user = frappe.session.user
    if not user or user == "Guest":
        return []

    # Removed set_user("Administrator")
    
    try:
        # 1. Fetch Saved RFQ records owned by this user
        saved_rfqs = frappe.get_all("Saved RFQ", 
            filters={"owner": user}, 
            fields=["name", "rfq", "creation"],
            ignore_permissions=True # Safely fetch own saved items even if strict perms
        )
        
        formatted_data = []
        for saved in saved_rfqs:
            # Use ignore_permissions=True to get RFQ details as we are logged in
            rfq = frappe.get_value("Request for Quotation", saved.rfq, 
                ["name", "custom_rfq_subject", "custom_rfq_category", "custom_total_budget_", "custom_bid_submission_last_date", "custom_bid_status", "status", "custom_enable_live_bidding", "docstatus"],
                as_dict=True
            )
            
            # get_value might check perms? standard get_value does NOT check perms usually, but better safe.
            # If get_value fails to get due to perm, we skip.
            # But wait, we want to show it if saved.
            # Let's assume get_value is fine or use SQL if paranoid. get_value usually bypasses if not restricted by specific hook.
            
            if not rfq:
                continue
                
            if rfq.status == "Cancelled" or rfq.docstatus == 2:
                continue

            deadline_status = ""
            deadline_str = ""
            if rfq.custom_bid_submission_last_date:
                from frappe.utils import getdate, today
                deadline_date = getdate(rfq.custom_bid_submission_last_date)
                deadline_str = deadline_date.strftime("%d %b %Y")
                if deadline_date < getdate(today()):
                     deadline_status = "Deadline passed"
            
            # Count bids: Link is in the child table 'Supplier Quotation Item'
            # Use SQL count to be safe on perms
            bids_count = frappe.db.sql("""
                SELECT COUNT(DISTINCT parent) 
                FROM `tabSupplier Quotation Item` 
                WHERE request_for_quotation = %s AND docstatus = 1
            """, (rfq.name,))[0][0]

            formatted_data.append({
                "id": rfq.name,
                "saved_id": saved.name,
                "title": rfq.custom_rfq_subject or rfq.name,
                "category": rfq.custom_rfq_category or "General",
                "value": rfq.custom_total_budget_ or 0,
                "deadline": deadline_str,
                "savedOn": saved.creation.strftime("%d %b %Y"),
                "status": rfq.custom_bid_status or "Active",
                "alerts": False, 
                "deadlineStatus": deadline_status,
                "bids": bids_count,
                "liveBidding": rfq.custom_bid_status == 'Active' and rfq.custom_enable_live_bidding
            })
            
        return formatted_data

    except Exception as e:
        frappe.log_error(f"Get Saved Tenders Error: {str(e)}")
        return []

@frappe.whitelist(allow_guest=True)
def delete_saved_tender(saved_id):
    user = frappe.session.user
    if not user or user == "Guest":
        return {"status": "error", "message": "Unauthorized"}
        
    try:
        if not frappe.db.exists("Saved RFQ", saved_id):
            return {"status": "error", "message": "Document not found"}

        saved_doc = frappe.get_doc("Saved RFQ", saved_id)
        supplier = saved_doc.supplier
        
        is_linked = frappe.db.exists("Portal User", {"parent": supplier, "user": user})
        
        if not is_linked and user != "Administrator":
             return {"status": "error", "message": "Permission Denied"}
             
        frappe.delete_doc("Saved RFQ", saved_id)
        return {"status": "success", "message": "Removed from Saved"}
        
    except Exception as e:
         frappe.log_error(f"Delete Saved Tender Error: {str(e)}")
         return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=True)
def save_tender(rfq_id):
    user = frappe.session.user
    if not user or user == "Guest":
         frappe.log_error(f"Save Tender: Unauthorized access attempt. User: {user}, SID: {frappe.session.sid}", "Supplier Portal Auth Debug")
         return {"status": "error", "message": "Please login to save tenders", "type": "AuthError"}

    # Get linked supplier
    supplier_details = get_supplier_details()
    
    supplier = None
    if supplier_details:
        supplier = supplier_details.get("name")
    
    if not supplier:
        if user == "Administrator":
             # Try to find any supplier to attribute this to for testing
             any_supplier = frappe.db.get_value("Supplier", {}, "name")
             if any_supplier:
                 supplier = any_supplier
             else:
                 return {"status": "error", "message": "No suppliers exist in system to link to."}
        else:
             return {"status": "error", "message": "No supplier linked to your account. Please contact support."}
    
    # Check if already saved
    exists = frappe.db.exists("Saved RFQ", {"rfq": rfq_id, "supplier": supplier})
    if exists:
        return {"status": "skipped", "message": "Already saved", "name": exists}

    doc = frappe.new_doc("Saved RFQ")
    doc.rfq = rfq_id
    doc.supplier = supplier
    doc.save(ignore_permissions=True)
    
    return {"status": "success", "message": "Tender saved", "name": doc.name}

@frappe.whitelist(allow_guest=True)
def get_logged_user():
    """
    Returns the currently logged in user.
    """
    # Prevent Caching of Auth Status
    frappe.response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    frappe.response["Pragma"] = "no-cache"
    frappe.response["Expires"] = "0"

    if frappe.session.user in ["Guest", None]:
        return "Guest"
    return frappe.session.user

@frappe.whitelist(allow_guest=True)
def get_csrf_token():
    return frappe.sessions.get_csrf_token()

@frappe.whitelist(allow_guest=True)
def get_my_queries():
    user = frappe.session.user
    if not user or user == "Guest":
        return []
    
    supplier_details = get_supplier_details()
    supplier = supplier_details.get("name") if supplier_details else None

    filters = {"owner": user}
    
    or_filters = []
    or_filters.append(["owner", "=", user])
    if supplier:
         if frappe.get_meta("RFQ Query").has_field("supplier"):
             or_filters.append(["supplier", "=", supplier])

    queries = frappe.get_all("RFQ Query", 
        filters=or_filters if len(or_filters) > 1 else filters,
        fields=["name", "subject", "rfq", "query", "response", "status", "creation"],
        order_by="creation desc"
    )
    return queries

@frappe.whitelist(allow_guest=True)
def create_rfq_query(subject, rfq, query):
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("Please login to submit a query"), frappe.PermissionError)

    if not frappe.db.exists("Request for Quotation", rfq):
        frappe.throw(_("Invalid Tender ID"), frappe.ValidationError)

    doc = frappe.new_doc("RFQ Query")
    doc.subject = subject
    doc.rfq = rfq
    doc.query = query
    doc.status = "Pending"
    
    supplier_details = get_supplier_details()
    if supplier_details and doc.meta.has_field("supplier"):
        doc.supplier = supplier_details.get("name")
    
    doc.save(ignore_permissions=True)
    return {"status": "success", "message": "Query submitted successfully", "data": doc.name}

@frappe.whitelist(allow_guest=True)
def create_rfq_questionnaire(rfq, subject, query):
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("Please login to submit a request"), frappe.PermissionError)

    if not frappe.db.exists("Request for Quotation", rfq):
        frappe.throw(_("Invalid Tender ID"), frappe.ValidationError)

    doc = frappe.new_doc("RFQ Questionnaires")
    doc.rfq = rfq
    doc.subject = subject 
    if doc.meta.has_field("type_of_questionnaire"):
        doc.type_of_questionnaire = subject
        
    doc.query = query
    doc.date = frappe.utils.today()
    doc.status = "Pending"
    
    doc.save(ignore_permissions=True)
    return {"status": "success", "message": "Questionnaire requested successfully", "data": doc.name}

@frappe.whitelist(allow_guest=True)
def get_my_questionnaires():
    user = frappe.session.user
    if not user or user == "Guest":
        return []
    
    questionnaires = frappe.get_all("RFQ Questionnaires", 
        filters={"owner": user},
        fields=["name", "subject", "rfq", "query", "response", "status", "creation", "date"],
        order_by="creation desc"
    )
    return questionnaires

@frappe.whitelist(allow_guest=True)
def get_catalog_items():
    user = frappe.session.user
    # Safe fetch for supplier link
    current_supplier = frappe.db.get_value("Portal User", 
        {"user": user, "parenttype": "Supplier"}, "parent")

    if not current_supplier:
        current_supplier = frappe.db.get_value("Supplier", {"email_id": user}, "name")

    items = frappe.get_all("Item", 
        filters={"is_purchase_item": 1},
        fields=[
            "name as id", 
            "item_name as name", 
            "item_code as sku", 
            "item_group as category", 
            "stock_uom as unit", 
            "description", 
            "valuation_rate as price", 
            "is_purchase_item",
            "lead_time_days",
            "min_order_qty"
        ]
    )

    for item in items:
        tax_val = 0 
        is_my_item = False
        
        if current_supplier:
            is_my_item = frappe.db.exists("Item Supplier", {
                "parent": item.id,
                "supplier": current_supplier
            })
        
        item['is_my_item'] = True if is_my_item else False
        item['status'] = "active"
        
        tax_template = frappe.db.get_value("Item Tax", {"parent": item.id}, "item_tax_template")

        if tax_template:
            found_rate = frappe.db.get_value("Item Tax Template Detail", {"parent": tax_template}, "tax_rate")
            if found_rate:
                tax_val = found_rate
        
        item['tax'] = f"{int(tax_val)}% GST"

        lead_days = item.get('lead_time_days')
        item['leadTime'] = f"{lead_days} days" if lead_days else "N/A"
        item['moq'] = int(item.get('min_order_qty') or 1)

    return {
        "items": items,
        "current_supplier": current_supplier
    }

@frappe.whitelist() # Remove allow_guest=True for security; catalog belongs to users
def add_to_catalog(item_id):
    user = frappe.session.user
    supplier = frappe.db.get_value("Portal User", {"user": user}, "parent")
    
    if not supplier:
        frappe.throw("No Supplier account associated with your profile.")

    doc = frappe.get_doc("Item", item_id)
    
    exists = any(row.supplier == supplier for row in doc.get("supplier_items", []))
    
    if not exists:
        doc.append("supplier_items", {
            "supplier": supplier
        })
        doc.save(ignore_permissions=True)
        frappe.db.commit() 
    
    return "success"

@frappe.whitelist(allow_guest=True)
def create_supplier_item():
    data = frappe.local.form_dict
    user = frappe.session.user
    
    current_supplier = frappe.db.get_value("Portal User", {"user": user, "parenttype": "Supplier"}, "parent")
    # Backup check in case not linked via Portal User but email matches? (Optional fallback)

    if not current_supplier:
         return {"error": "No linked supplier found"}

    new_item = frappe.get_doc({
        "doctype": "Item",
        "item_code": data.get("sku") or data.get("name"), 
        "item_name": data.get("name"),
        "item_group": data.get("category") or "All Item Groups",
        "stock_uom": data.get("unit") or "Nos",
        "is_purchase_item": 1,
        "valuation_rate": data.get("price") or 0,
        "description": data.get("description"),
        "supplier_items": [{
            "supplier": current_supplier,
            "supplier_part_no": data.get("sku")
        }]
    })
    
    new_item.insert(ignore_permissions=True)
    return "success"

@frappe.whitelist(allow_guest=True)
def remove_from_catalog(item_id):

    user = frappe.session.user
    current_supplier = frappe.db.get_value("Portal User", {"user": user, "parenttype": "Supplier"}, "parent")
    
    if not current_supplier:
        frappe.throw("Supplier not found for the current user.")

    frappe.db.delete("Item Supplier", {
        "parent": item_id,
        "supplier": current_supplier
    })
    
    return "success"
@frappe.whitelist()
def update_catalog_item(**args):
    """Consolidated update function for the catalog"""
    item_id = args.get('item_id')
    if not item_id:
        frappe.throw("Item ID is required for updating.")

    try:
        doc = frappe.get_doc("Item", item_id)
        
        # Core Fields
        doc.item_name = args.get('name')
        doc.standard_rate = args.get('price')
        doc.description = args.get('description')
        
        # Custom Fields - Ensure these internal names match your Item DocType exactly
        # If your Frappe fields use different names, change the left side (doc.field_name)
        doc.lead_time_days = args.get('leadTime')
        doc.min_order_qty = args.get('moq')
        
        # If you have a custom tax field:
        # doc.custom_gst_rate = args.get('tax') 
        
        doc.save(ignore_permissions=True)
        frappe.db.commit() 
        
        return "success"
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Catalog Update Error")
        return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=True)
def update_supplier_item(**args):
    item_id = args.get('id')
    if not item_id:
        return "error: missing item id"

    try:
        item = frappe.get_doc("Item", item_id)
        
        item.item_name = args.get('name')
        item.standard_rate = args.get('price')
        item.description = args.get('description')
        item.lead_time_days = args.get('leadTime')
        item.stock_uom = args.get('unit')
        
        item.save(ignore_permissions=True)
        return "success"
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update Catalog Error")
        return f"error: {str(e)}"
    
@frappe.whitelist(allow_guest=False)
def get_dashboard_stats():
    if frappe.session.user == "Guest":
        frappe.throw(_("Please log in to access the portal"), frappe.PermissionError)

    user = frappe.session.user
    
    supplier = frappe.db.get_value("Portal User", 
        {"user": user, "parenttype": "Supplier"}, "parent")
    print("-------------------supplier",supplier)
    
    if not supplier:
        supplier = frappe.db.get_value("Contact", 
            {"email_id": user}, "supplier")

    if not supplier:
        return {
            "error": True,
            "message": _("No Supplier linked to this user. Please check Portal User settings.")
        }

    total_bids = frappe.db.count("Supplier Quotation", {
        "supplier": supplier,
        "docstatus": 1
    })
    print("----------------total_bids",total_bids)

    orders_won = frappe.db.count("Purchase Order", {
        "supplier": supplier,
        "docstatus": 1
    })

    pending_review = frappe.db.count("Supplier Quotation", {
        "supplier": supplier,
        "docstatus": 1,
        "status": "Submitted",
    })

    sq = frappe.qb.DocType("Supplier Quotation")
    total_bid_value = (
        frappe.qb.from_(sq)
        .select(Sum(sq.grand_total))
        .where(sq.supplier == supplier)
        .where(sq.docstatus == 1)
    ).run()[0][0] or 0

    po = frappe.qb.DocType("Purchase Order")
    orders_won_value = (
        frappe.qb.from_(po)
        .select(Sum(po.grand_total))
        .where(po.supplier == supplier)
        .where(po.docstatus == 1)
    ).run()[0][0] or 0

    win_rate = "0%"
    if total_bids > 0:
        rate = (orders_won / total_bids) * 100
        win_rate = f"{int(rate)}%"

    recent_bids = frappe.db.sql("""
       SELECT 
            sq.name, 
            sq.transaction_date, 
            sq.grand_total, 
            sq.status,
            (SELECT rfq.subject 
             FROM `tabSupplier Quotation Item` sqi
             JOIN `tabRequest for Quotation` rfq ON sqi.request_for_quotation = rfq.name
             WHERE sqi.parent = sq.name 
             LIMIT 1) as rfq_subject
        FROM `tabSupplier Quotation` sq
        WHERE sq.supplier = %s
        ORDER BY sq.creation DESC
        LIMIT 5
    """, (supplier,), as_dict=True)

    upcoming_rfqs = frappe.get_all("Request for Quotation",
        filters={
            "docstatus": 1,
            "status": ["!=", "Closed"],
            "custom_bid_submission_last_date": [">=", frappe.utils.nowdate()]
        },
        fields=["name", "custom_rfq_subject", "custom_bid_submission_last_date"],
        order_by="custom_bid_submission_last_date asc",
        limit=5
    )

    formatted_deadlines = []
    for rfq in upcoming_rfqs:
        days_left = frappe.utils.date_diff(rfq.custom_bid_submission_last_date, frappe.utils.nowdate())
        formatted_deadlines.append({
            "id": rfq.name,
            "title": rfq.custom_rfq_subject or rfq.name,
            "deadline": frappe.utils.formatdate(rfq.custom_bid_submission_last_date, "dd MMM yyyy"),
            "days_left": days_left,
            "urgency": "high" if days_left <= 2 else "normal"
        })

    status_colors = {
        "Submitted": "bg-green-100 text-green-700 ring-green-600/20",
        "Draft": "bg-blue-100 text-blue-700 ring-blue-600/20",
        "Cancelled": "bg-red-100 text-red-700 ring-red-600/20",
        "Stopped": "bg-yellow-100 text-yellow-700 ring-yellow-600/20",
        "Expired": "bg-red-100 text-red-700 ring-red-600/20",
        "Under Review": "bg-gray-100 text-gray-600 ring-gray-500/10"
    }

    formatted_bids = [] 
    for d in recent_bids: 
        title = d.rfq_subject or d.name
        
        amount_val = d.grand_total or 0
            
        formatted_bids.append({
            "id": d.name,
            "title": title,
            "date": frappe.utils.formatdate(d.transaction_date, "dd MMM yyyy"),
            "amount": f"₹{amount_val:,.2f}",
            "status": d.status,
            "statusColor": status_colors.get(d.status, "bg-gray-100 text-gray-600 ring-gray-500/10"),
            "rank": "#1" if d.status == "Won" else "" 
        })
    recent_bids = formatted_bids

    recent_activity = frappe.get_all("Activity Log",
        filters={"user": user},
        fields=["subject as title", "creation as time", "operation as icon_type"],
        order_by="creation desc",
        limit=5
    )

    for act in recent_activity:
        act['time'] = frappe.utils.pretty_date(act['time'])

    return {
        "user_name": frappe.get_value("User", user, "first_name") or user,
        "supplier_name": supplier,
        "stats": {
            "total_bids": total_bids,
            "orders_won": orders_won,
            "pending_review": pending_review,
            "win_rate": f"{int((orders_won / total_bids) * 100)}%" if total_bids > 0 else "0%",
            "total_bid_value": f"{float(total_bid_value or 0):,.2f}",
            "orders_won_value": f"{float(orders_won_value):,.2f}"
        },
        "recent_bids": recent_bids,
        "recent_activity": recent_activity,
        "upcoming_deadlines": formatted_deadlines,
    }


@frappe.whitelist()
def get_logged_user_supplier(allow_guest=False):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please log in to access the portal"), frappe.PermissionError)

    user = frappe.session.user
 
    supplier = frappe.db.get_value("Portal User", {"user": user}, "parent")

    if not supplier:
        supplier = frappe.db.get_value("Supplier", {"portal_user": user}, "name")
        
    if not supplier:
        contact = frappe.db.get_value("Contact", {"email_id": user}, "name")
        if contact:
            supplier = frappe.db.get_value("Dynamic Link", 
                {"link_doctype": "Supplier", "parent": contact}, "link_name")

    return supplier

@frappe.whitelist()
def get_blanket_order_payment_stats(blanket_order):
    user_supplier = frappe.db.get_value("Portal User", {"user": frappe.session.user}, "parent")
    
    bo_supplier = frappe.db.get_value("Blanket Order", blanket_order, "supplier")
    
    if user_supplier != bo_supplier:
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    pos = frappe.get_all("Purchase Order", 
        filters={"blanket_order": blanket_order, "docstatus": 1}, 
        pluck="name"
    )

    if not pos:
        return {"total_paid": 0}

    payment_stats = frappe.db.sql("""
        SELECT SUM(per.allocated_amount) 
        FROM `tabPayment Entry Reference` per
        INNER JOIN `tabPayment Entry` pe ON pe.name = per.parent
        WHERE per.reference_doctype = 'Purchase Order' 
        AND per.reference_name IN %(po_list)s
        AND pe.docstatus = 1
    """, {"po_list": pos})

    total_paid = payment_stats[0][0] or 0

    return {
        "total_paid": total_paid
    }


@frappe.whitelist()
def get_contract_payments(blanket_order):
    frappe.logger().info(f"Fetching payments for Blanket Order: {blanket_order}")
    
    return frappe.db.sql("""
        SELECT DISTINCT
            pe.name as id, 
            pe.posting_date as date, 
            pe.paid_amount as amount, 
            pe.docstatus as docstatus
        FROM `tabPayment Entry` pe
        INNER JOIN `tabPayment Entry Reference` per ON pe.name = per.parent
        INNER JOIN `tabPurchase Order Item` poi ON per.reference_name = poi.parent
        WHERE poi.blanket_order = %s
          AND per.reference_doctype = 'Purchase Order'
    """, (blanket_order,), as_dict=True)

@frappe.whitelist()
def get_contract_documents(blanket_order):
    bo_doc = frappe.get_doc("Blanket Order", blanket_order)
    all_documents = []

    source_field = bo_doc.get('custom_documents')

    if source_field:
        for link in source_field:
            
            folder_id = link.get('document_name') 
            
            print(f"--- Found Folder ID: {folder_id}")

            if folder_id:
                try:
                    folder_doc = frappe.get_doc("Contract Document", folder_id)
                    
                    all_documents.append({
                        "id": folder_doc.name,
                        "document_name": folder_doc.document_name, 
                        "file_url": folder_doc.document,           
                        "date": folder_doc.creation.strftime('%Y-%m-%d') if folder_doc.creation else ""
                    })
                except frappe.DoesNotExistError:
                    print(f"--- Error: Contract Document {folder_id} not found")
                    continue
    
    return all_documents

   
@frappe.whitelist()
def get_similar_tenders(category, exclude_id):
    print("---------------working----------")
    return frappe.db.get_list('Request for Quotation', 
        filters={
            'custom_rfq_category': category, 
            'name': ['!=', exclude_id],
            'docstatus': 1
        },
        fields=[
            'name as id', 
            'custom_rfq_subject as title', 
            'custom_total_budget_ as budget', 
            'custom_bid_submission_last_date as deadline'
        ],
        limit=5
    )

@frappe.whitelist(allow_guest=True)
def get_recent_bid_activity(rfq_id):
    bids = frappe.db.get_list("Supplier Quotation", 
        filters={
            "request_for_quotation": rfq_id, 
            "docstatus": 0
        },
        fields=["supplier", "grand_total as total", "creation"],
        order_by="creation desc", 
        limit=5,
        ignore_permissions=True
    )
    
    current_supplier = frappe.db.get_value("Portal User", 
        {"user": frappe.session.user, "parenttype": "Supplier"}, 
        "parent")

    return {
        "bids": bids,
        "current_supplier": current_supplier
    }
    
@frappe.whitelist(allow_guest=True)
def place_supplier_bid(rfq_id, amount):
    try:
        supplier_name = frappe.db.get_value("Portal User", {"user": frappe.session.user}, "parent")

        rfq = frappe.get_doc("Request for Quotation", rfq_id)

        sq = frappe.new_doc("Supplier Quotation")
        
        sq.request_for_quotation = rfq_id 
        sq.supplier = supplier_name
        sq.company = rfq.company
        sq.transaction_date = frappe.utils.nowdate()

        sq.currency = "INR"
        sq.conversion_rate = 1.0
        sq.buying_price_list = "Standard Buying"

        total_qty = sum([item.qty for item in rfq.items])
        unit_rate = float(amount) / total_qty if total_qty > 0 else float(amount)

        for item in rfq.items:
            sq.append("items", {
                "item_code": item.item_code,
                "qty": item.qty,
                "rate": unit_rate,
                "uom": item.uom,
                "warehouse": item.warehouse,
                "request_for_quotation": rfq_id
            })

        sq.run_method("calculate_taxes_and_totals")
        sq.insert(ignore_permissions=True)
        
        return {"status": "success", "message": "Linked successfully"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Link Error")
        return {"status": "error", "message": str(e)}
    
@frappe.whitelist()
def get_portal_settings():
    percent = frappe.db.get_single_value("Supplier Portal Settings", "live_bidding_quick_entry_percent") or 0
    return {
        "live_bidding_quick_entry_percent": percent 
    }

@frappe.whitelist()
def get_tender_summary_stats(rfq_id):
    total_bids = frappe.db.count("Supplier Quotation", {
        "request_for_quotation": rfq_id,
        "docstatus": ["<", 2]  
    })

    return {
        "total_bids": total_bids
    }

@frappe.whitelist(allow_guest=False)
def get_supplier_profile():
    user = frappe.session.user
    
    supplier_name = frappe.db.get_value("Portal User", 
        {"user": user, "parenttype": "Supplier"}, "parent")
    
    if not supplier_name:
        return {"error": True, "message": _("Supplier link not found.")}

    supplier_doc = frappe.get_doc("Supplier", supplier_name)
    product_categories = get_supplier_categories(supplier_name)

    address = frappe.get_all("Address", 
        filters={"link_doctype": "Supplier", "link_name": supplier_name},
        fields=["address_line1", "address_line2", "city", "state", "pincode", "email_id", "phone"],
        limit=1
    )
    
    contact = frappe.get_all("Contact",
        filters={"link_doctype": "Supplier", "link_name": supplier_name},
        fields=["first_name", "last_name", "email_id", "mobile_no"],
        limit=1
    )

    return {
        "supplier_name": supplier_doc.supplier_name,
        "business_type": supplier_doc.supplier_type,
        "gst_number": supplier_doc.gstin or "", 
        "pan_number": supplier_doc.pan or "", 
        "country": supplier_doc.country,
        "address": address[0] if address else {},
        "contact": contact[0] if contact else {},
        "member_since": supplier_doc.creation,
        "product_categories": product_categories,
        "supplier_details":supplier_doc.supplier_details,
        "website":supplier_doc.website,
        "annual_turnover": supplier_doc.custom_annual_turnover,
        "employee_count": supplier_doc.custom_employee_count,
        "custom_supplier_documents": supplier_doc.get("custom_supplier_documents") or [],
        "custom_supplier_certificates": supplier_doc.get("custom_supplier_certificates") or []
        }

def get_supplier_categories(supplier_name):
    if not supplier_name:
        return []
        
    rfq_list = frappe.get_all("Request for Quotation Supplier", 
        filters={"supplier": supplier_name, "docstatus": 1}, 
        pluck="parent"
    )

    if not rfq_list:
        return []

    categories = frappe.get_all("Request for Quotation",
        filters={
            "name": ["in", rfq_list],
            "custom_rfq_category": ["!=", ""],
            "docstatus": 1
        },
        pluck="custom_rfq_category"
    )
    
    return list(set(categories)) if categories else []

@frappe.whitelist(allow_guest=False)
def count_saved_tenders():
    user = frappe.session.user
    print("-------------------------user",user)
    count = frappe.db.count("Saved RFQ", filters={"owner": user})
    print("--------------------count",count)
   
    return count

@frappe.whitelist(allow_guest=False)
def get_dashboard_counts():
    user = frappe.session.user
    supplier = frappe.db.get_value("Portal User", {"user": user}, "parent")
    today = nowdate()

    if not supplier:
        return {
            "counts": {"total": 0, "in_transit": 0, "delivered": 0, "delayed": 0},
            "deliveries": []
        }

    total = frappe.db.count("Purchase Receipt", filters={"supplier": supplier, "docstatus": ["!=", 2]})
    
    in_transit = frappe.db.count("Purchase Receipt", filters={
        "supplier": supplier, 
        "docstatus": 0, 
        "posting_date": [">=", today]
    })

    delivered = frappe.db.count("Purchase Receipt", filters={
        "supplier": supplier, 
        "docstatus": 1, 
        "status": "Completed"
    })

    delayed = frappe.db.count("Purchase Receipt", filters={
        "supplier": supplier, 
        "docstatus": 0, 
        "posting_date": ["<", today]
    })

    delivery_rows = frappe.db.sql("""
        SELECT 
            pri.item_name as title,
            pri.purchase_order as po,
            pri.qty as quantity,
            pri.uom as uom,
            pr.status as receipt_status,
            pr.name as receipt_id,
            pr.posting_date as posting_date,
            pr.dispatch_address_display as dispatch_address
        FROM `tabPurchase Receipt Item` pri
        JOIN `tabPurchase Receipt` pr ON pri.parent = pr.name
        LEFT JOIN `tabPurchase Order` po ON pri.purchase_order = po.name
        WHERE pr.supplier = %s 
        AND pr.docstatus < 2
        ORDER BY pr.posting_date DESC
    """, (supplier), as_dict=1)

    deliveries_list = []
    for d in delivery_rows:
        raw_address = d.get("dispatch_address")
        clean_address = strip_html(raw_address).replace("\n", ", ") if raw_address else "Address Pending"

        deliveries_list.append({
            "id": d.receipt_id,
            "title": d.title,
            "po": d.po or "N/A",
            "quantity": f"{float(d.quantity)} {d.uom}", 
            "status": "Delivered" if d.receipt_status == "Completed" else "In Transit",
            "scheduled": d.posting_date, 
            "expected": d.posting_date,
            "location": clean_address, 
            "progress": 100 if d.receipt_status == "Completed" else 65,
            "milestones": [
                {"name": "Order Confirmed", "completed": True},
                {"name": "Dispatched", "completed": True},
                {"name": "Delivered", "completed": True if d.receipt_status == "Completed" else False}
            ]
        })

    return {
        "counts": {
            "total": total,
            "in_transit": in_transit,
            "delivered": delivered,
            "delayed": delayed
        },
        "deliveries": deliveries_list 
    }

@frappe.whitelist(allow_guest=False)
def update_delivery_status():
    data = frappe.request.get_json()
    
    receipt_id = data.get("receipt_id")
    new_status = data.get("status")
    expected_date = data.get("expected_date")
    note = data.get("note")

    if not receipt_id:
        frappe.throw(_("Purchase Receipt ID is missing."))

        frappe.db.set_value("Purchase Receipt", receipt_id, "status", new_status)

        items=frappe.get_all("Purchase Receipt Items",filters={"parent":receipt_id}, fields=["purchase_order"])

        for i in items:
            if items.purchase_order:
                frappe.db.set_value("Purchase Order Item",items.purchase_order,{
                    "expected_delivery_date":"expected_date",
                    "description":f"{note}" if note else None
                })
        frappe.db.commit()

        return {"status": "success"}     

@frappe.whitelist()
def get_supplier_invoices():
    user = frappe.session.user
    
    # 1. Get the Supplier ID and Name
    portal_user = frappe.db.get_value("Portal User", {"user": user}, ["parent"], as_dict=True)
    
    if not portal_user:
        return []
    
    supplier_id = portal_user.parent
    supplier_name = frappe.db.get_value("Supplier", supplier_id, "supplier_name")

    # 2. SQL Join logic to include the Purchase Order from Connections
    invoices = frappe.db.sql("""
        SELECT DISTINCT
            si.name as id,
            si.posting_date as date,
            si.due_date as dueDate,
            si.grand_total as amount,
            si.total_taxes_and_charges as tax,
            si.status as status,
            poi.parent as po,
            so.project as project,
            %s as supplier_name  -- Passing the fetched name into the result
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        JOIN `tabSales Order` so ON sii.sales_order = so.name
        JOIN `tabSales Order Item` soi ON soi.parent = so.name AND soi.item_code = sii.item_code
        LEFT JOIN `tabPurchase Order Item` poi ON poi.sales_order = so.name AND poi.item_code = soi.item_code
        WHERE soi.supplier = %s
        ORDER BY si.creation DESC
    """, (supplier_name, supplier_id), as_dict=True)

    return invoices

@frappe.whitelist()
def get_supplier_payments():
    user = frappe.session.user
    
    supplier_id = frappe.db.get_value("Portal User", {"user": user}, "parent")
    
    if not supplier_id:
        return []

    payments = frappe.get_all("Payment Entry", 
        filters={
            "party_type": "Supplier",
            "party": supplier_id, 
            "docstatus": 1 
        },
        fields=["name as id", "posting_date as date", "paid_amount as amount", 
                "reference_no as ref_no", "mode_of_payment as method"]
    )
    
    for pay in payments:
        invoice_ref = frappe.db.get_value("Payment Entry Reference", 
            {"parent": pay.id}, "reference_name")
        pay["against_invoice"] = invoice_ref or "Multiple/Advance"

    return payments

@frappe.whitelist()
def get_invoice_pdf(name, view="download"):
    pdf_content = frappe.get_print("Sales Invoice", name, as_pdf=True)
    
    frappe.response.filename = f"{name}.pdf"
    frappe.response.filecontent = pdf_content

    frappe.response.type = "pdf"
    frappe.response.display_content_as = "inline" if view == "inline" else "attachment"


import frappe
from frappe import _
from frappe.utils.file_manager import save_file

@frappe.whitelist()
def upload_supplier_document(doc_name, filename, filedata):
    user = frappe.session.user
    supplier_id = frappe.db.get_value("Portal User", {"user": user}, "parent")
    
    if not supplier_id:
        frappe.throw(_("Supplier profile not found."))

    try:
        file_doc = save_file(filename, filedata, "Supplier", supplier_id, is_private=1)

        new_entry = frappe.get_doc({
            "doctype": "Supplier Document",
            "document_name": doc_name, 
            "supplier": supplier_id,
            "document": file_doc.file_url,
            "upload_date": frappe.utils.nowdate()
        })
        
        new_entry.name = frappe.model.naming.make_autoname("hash") 

        new_entry.insert(ignore_permissions=True)

        supplier = frappe.get_doc("Supplier", supplier_id)
        supplier.append("custom_supplier_documents", {
            "document_name": doc_name,
            "file": file_doc.file_url,
            "date": frappe.utils.nowdate()
        })
        
        supplier.save(ignore_permissions=True)
        frappe.db.commit()

        return "success"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Document Upload Error"))
        return {"message": "error", "reason": str(e)}


@frappe.whitelist()
def upload_supplier_certificate(doc_name, filename, filedata, expiry_date=None):
    user = frappe.session.user
    supplier_id = frappe.db.get_value("Portal User", {"user": user}, "parent")
    
    if not supplier_id:
        frappe.throw(_("Supplier profile not found."))

    try:
        if not filedata:
            return {"message": "error", "reason": "No file data received."}

        file_doc = save_file(filename, filedata, "Supplier", supplier_id, is_private=1)

        cert_entry = frappe.get_doc({
            "doctype": "Supplier Certificates",
            "supplier_certificate_name": doc_name,
            "supplier": supplier_id,
            "expiry_date": expiry_date,
            "certificates": file_doc.file_url,
            "status": "Active"
        })
        cert_entry.insert(ignore_permissions=True)

        supplier = frappe.get_doc("Supplier", supplier_id)
        supplier.append("custom_supplier_certificates", {
            "supplier_certificate_name": cert_entry.name, 
            "file": file_doc.file_url,
            "expiry_date": expiry_date,
            "status": "Active"
        })
        
        supplier.save(ignore_permissions=True)
        frappe.db.commit()

        return "success"

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Certificate Upload Error"))
        return {"message": "error", "reason": str(e)}
    
@frappe.whitelist()
def delete_supplier_certificate(certificate_name):
    user = frappe.session.user
    supplier_id = frappe.db.get_value("Portal User", {"user": user}, "parent")
    
    if not supplier_id:
        frappe.throw(_("Unauthorized access."))

    try:
        frappe.db.sql("""
            DELETE FROM `tabSupplier Certificate Items` 
            WHERE parent = %s AND supplier_certificate_name = %s
        """, (supplier_id, certificate_name))

        if frappe.db.exists("Supplier Certificates", certificate_name):
            frappe.delete_doc("Supplier Certificates", certificate_name, ignore_permissions=True)

        frappe.db.commit()
        return "success"
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Delete Certificate Error"))
        return {"message": "error", "reason": str(e)}
    

@frappe.whitelist()
def delete_supplier_document(doc_entry_name):
    user = frappe.session.user
    supplier_id = frappe.db.get_value("Portal User", {"user": user}, "parent")
    
    if not supplier_id:
        frappe.throw(_("Unauthorized access."))

    try:
    
        frappe.db.sql("""
            DELETE FROM `tabSupplier Document Item` 
            WHERE parent = %s AND name = %s
        """, (supplier_id, doc_entry_name))

        if frappe.db.exists("Supplier Document", doc_entry_name):
            frappe.delete_doc("Supplier Document", doc_entry_name, ignore_permissions=True)

        frappe.db.commit()
        return "success"
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Delete Document Error"))
        return {"message": "error", "reason": str(e)}
    
@frappe.whitelist()
def create_tender_alert(payload):
    if isinstance(payload, str):
        payload = json.loads(payload)
        
    user = frappe.session.user
    
    supplier_id = frappe.db.get_value("Portal User", {"user": user}, "parent")
    
    if not supplier_id:
        supplier_id = frappe.db.get_value("Supplier", {"supplier_name": "Test Supplier"}, "name")

    if not supplier_id:
        frappe.throw(_("Supplier link not found. Please link your user to a Supplier in the Desk."))

    selected_cats = payload.get("selected_categories", [])
    clean_cats = [c for c in selected_cats if c != "All"]

    doc = frappe.get_doc({
        "doctype": "Tender Alert",
        "supplier": supplier_id,
        "alert_name": payload.get("alert_name"),
        "budget_max": payload.get("budget_max"),
        "categories": ", ".join(clean_cats) if clean_cats else "General"
    })
    doc.insert(ignore_permissions=True) 
    
    create_portal_notification(doc)
    
    return doc.name

def create_portal_notification(alert_doc):
    frappe.get_doc({
        "doctype": "Supplier Portal Notification", 
        "for_user": frappe.session.user,           
        "title": _("Alert Created"),               
        "type": "Alert",                           
        "message": _("We will notify you about tenders in {0}").format(alert_doc.categories),
        "read": 0                                 
    }).insert(ignore_permissions=True)

@frappe.whitelist()
def get_my_notifications():
    notifications = frappe.get_all("Supplier Portal Notification",
        filters={"for_user": frappe.session.user},
        fields=["name", "title", "message", "type", "read", "creation"],
        order_by="creation desc",
        limit=10
    )
    
    for n in notifications:
        n["time_ago"] = frappe.utils.pretty_date(n.creation)
        
    return notifications

@frappe.whitelist()
def delete_portal_account():
    user = frappe.session.user
    
    if user == "Administrator" or user == "Guest":
        frappe.throw("Invalid user for this operation.")

    user_doc = frappe.get_doc("User", user)
    user_doc.enabled = 0
    user_doc.save(ignore_permissions=True)

    supplier_name = frappe.db.get_value("Supplier", {"email_id": user}, "name")
    
    if supplier_name:
        supp_doc = frappe.get_doc("Supplier", supplier_name)
        supp_doc.disabled = 1
        supp_doc.save(ignore_permissions=True)
    
    frappe.local.login_manager.logout()
    
    return True
