
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

@frappe.whitelist()
def get_supplier_details():
    user = frappe.session.user
    if user == "Guest":
        return {}
    
    # Infer child doctype for portal_users
    meta = frappe.get_meta("Supplier")
    field = meta.get_field("portal_users")
    if not field:
        return {}
    
    child_doctype = field.options
    
    suppliers = frappe.get_all("Supplier", filters={
        "name": ["in", frappe.get_all(child_doctype, filters={"user": user}, pluck="parent")]
    }, fields=["name", "supplier_name", "email_id"])
    
    if suppliers:
        return suppliers[0]
        
    return {}

@frappe.whitelist(allow_guest=True)
def get_active_tenders(limit=20, offset=0):
    user = frappe.session.user
    limit = int(limit)
    offset = int(offset)
    
    # Context switch to Admin to ensure we can read all necessary headers/child tables
    original_user = frappe.session.user
    frappe.set_user("Administrator")
    
    invited_rfq_names = []
    
    try:
        if user != "Guest":
            # 1. Broadly find all Suppliers this user is linked to
            # We don't filter by parenttype to be safe, assuming 'parent' is the Supplier
            suppliers = [s.parent for s in frappe.get_all("Portal User", filters={"user": user}, fields=["parent"])]
            
            if suppliers:
                # 2. Find all RFQs inviting these suppliers
                invited_rfq_names = [r.parent for r in frappe.get_all("Request for Quotation Supplier", 
                                                                    filters={"supplier": ["in", suppliers]}, 
                                                                    fields=["parent"])]
    except Exception as e:
        frappe.log_error(f"Active Tenders Permission Error: {str(e)}")
        # Continue to at least show public tenders
        pass
    finally:
        frappe.set_user(original_user)
        
    # 3. Construct SQL for data fetching
    # We pass the list of allowed private RFQs to the query
    
    # Handle the 'IN' clause safely
    if invited_rfq_names:
        in_placeholder = ', '.join(['%s'] * len(invited_rfq_names))
        private_condition = f"OR name IN ({in_placeholder})"
        query_values = invited_rfq_names + [limit, offset]
    else:
        private_condition = "OR 1=0" # False condition if no invites
        query_values = [limit, offset]

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
            custom_publish_on_website
        FROM `tabRequest for Quotation`
        WHERE docstatus < 2
        AND (
            custom_publish_on_website = 1
            {private_condition}
        )
        ORDER BY modified DESC
        LIMIT %s OFFSET %s
    """
    
    try:
        data = frappe.db.sql(sql, tuple(query_values), as_dict=True)
    except Exception as e:
        frappe.log_error("Get Active Tenders SQL Error", str(e))
        return []

    return data

@frappe.whitelist(allow_guest=True)
def get_tender_details(name):
    from frappe import _
    # Security/Permission Check
    user = frappe.session.user
    
    has_access = False
    
    # Check if published (Allow Draft/Submitted)
    is_published = frappe.db.get_value("Request for Quotation", name, "custom_publish_on_website")
    if is_published:
        has_access = True
    elif user != "Guest":
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

    # Bypass standard permission checks since we have validated access via custom logic
    # This allows Guests/Suppliers to view the doc even if they don't have direct DocType read permissions
    original_user = frappe.session.user
    frappe.set_user("Administrator")
    try:
        doc = frappe.get_doc("Request for Quotation", name)
    finally:
        frappe.set_user(original_user)
    
    # Prepare Items / Specs
    items = []
    for item in doc.items:
        items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "description": item.description,
            "qty": item.qty,
            "uom": item.uom,
            "image": item.image,
            "budget": item.custom_budget,
            "budget_amount": item.custom_budget_amount,
            "attach_boq": item.custom_attach_boq
        })
        
    # Calculate Total Quantity from items
    total_qty = sum([item.qty for item in doc.items])

    # Get Attachments (Standard Files)
    attachments = frappe.db.get_all("File", 
        filters={"attached_to_name": name, "attached_to_doctype": "Request for Quotation", "is_private": 0},
        fields=["file_name", "file_url", "file_size"]
    )
    
    # Add custom_downloadable_forms if exists
    if doc.get("custom_downloadable_forms"):
        attachments.append({
            "file_name": "Tender Form", # Label for the main form
            "file_url": doc.get("custom_downloadable_forms"),
            "file_size": "-" 
        })
    
    # Map fields dynamically with safety checks
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
        "auto_extension_limit": doc.get("custom_auto_extension_limit"), # Use get to avoid error if missing
        "department": doc.get("custom_department"),
        "contact_person": doc.get("custom_contact_person"), 
        "contact_display": doc.get("custom_contact_display"),
        "billing_address": doc.get("billing_address_display"),
        "terms": doc.terms,
        "items": items,
        "documents": attachments,
        "custom_contact_display": doc.get("custom_contact_display") or doc.get("custom_contact_person"),
        "custom_address_display": doc.get("custom_address_display"),
        "enable_live_bidding": doc.get("custom_enable_live_bidding"),
        # Timelines
        "transaction_date": doc.transaction_date, 
        "schedule_date": doc.schedule_date
    }

@frappe.whitelist()
def get_dashboard_stats():
    user = frappe.session.user
    if user == "Guest":
        return {"error": "Not logged in"}
    
    # Context switch to Admin for full visibility
    original_user = frappe.session.user
    frappe.set_user("Administrator")
    
    try:
        # 1. Find ALL Suppliers linked to this user
        suppliers = frappe.get_all("Portal User", 
                                 filters={"user": user, "parenttype": "Supplier"}, 
                                 fields=["parent"])
        
        if not suppliers:
            return {"error": "No supplier linked"}
            
        supplier_names = [s.parent for s in suppliers]
        
        # 2. Aggregate Stats across all linked suppliers
        
        # Total Bids (Supplier Quotations)
        total_bids = frappe.db.count("Supplier Quotation", filters={"supplier": ["in", supplier_names], "docstatus": ["<", 2]})
        
        # Orders Won (Purchase Orders)
        orders_won = frappe.db.count("Purchase Order", filters={"supplier": ["in", supplier_names], "docstatus": 1})
        
        # Pending Review (Supplier Quotation Submitted count - assuming 'Submitted' status)
        pending_review = frappe.db.count("Supplier Quotation", filters={"supplier": ["in", supplier_names], "status": "Submitted"})
        
        # Win Rate
        win_rate = 0
        if total_bids > 0:
            win_rate = int((orders_won / total_bids) * 100)
        
        # 3. Recent Bids (Fetch for ANY of the suppliers)
        placeholders = ', '.join(['%s'] * len(supplier_names))
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
        
        return {
            "stats": {
                "total_bids": total_bids,
                "orders_won": orders_won,
                "pending_review": pending_review,
                "win_rate": f"{win_rate}%"
            },
            "recent_bids": recent_bids,
            "supplier_name": display_supplier_name,
            "user_name": frappe.db.get_value("User", user, "full_name") or user
        }

    except Exception as e:
        frappe.log_error(f"Dashboard Stats Error: {str(e)}")
        return {"error": "Error fetching dashboard data"}
        
    finally:
        frappe.set_user(original_user)

@frappe.whitelist()
def get_saved_tenders():
    """
    Fetches saved tenders for the current user.
    """
    user = frappe.session.user
    if user == "Guest":
        return []

    original_user = frappe.session.user
    frappe.set_user("Administrator")
    
    try:
        # 1. Fetch Saved RFQ records owned by this user
        saved_rfqs = frappe.get_all("Saved RFQ", 
            filters={"owner": user}, 
            fields=["name", "rfq", "creation"]
        )
        
        formatted_data = []
        for saved in saved_rfqs:
            rfq = frappe.db.get_value("Request for Quotation", saved.rfq, 
                ["name", "custom_rfq_subject", "custom_rfq_category", "custom_total_budget_", "custom_bid_submission_last_date", "custom_bid_status", "status", "custom_enable_live_bidding"],
                as_dict=True
            )
            
            if not rfq:
                continue
                
            if rfq.status == "Cancelled" or frappe.db.get_value("Request for Quotation", saved.rfq, "docstatus") == 2:
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
            # We count unique Supplier Quotations (parents) that reference this RFQ
            bids_count = len(frappe.get_all("Supplier Quotation Item", 
                filters={"request_for_quotation": rfq.name, "docstatus": 1}, 
                pluck="parent", 
                distinct=True
            ))

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
    finally:
        frappe.set_user(original_user)

@frappe.whitelist()
def delete_saved_tender(saved_id):
    user = frappe.session.user
    if user == "Guest":
        return {"status": "error", "message": "Unauthorized"}
        
    try:
        # Check permission: belongs to a supplier user is linked to
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


@frappe.whitelist()
def save_tender(rfq_id):
    user = frappe.session.user
    if user == "Guest":
         frappe.throw(_("Please login to save tenders"), frappe.PermissionError)

    # Get linked supplier
    supplier_details = get_supplier_details()
    if not supplier_details:
         frappe.throw(_("No supplier linked to your account"), frappe.PermissionError)
         
    supplier = supplier_details.get("name")
    
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
    return frappe.session.user

@frappe.whitelist(allow_guest=True)
def get_csrf_token():
    return frappe.sessions.get_csrf_token()

@frappe.whitelist()
def get_my_queries():
    user = frappe.session.user
    if user == "Guest":
        return []
    
    # Get linked suppliers
    supplier_details = get_supplier_details()
    supplier = supplier_details.get("name") if supplier_details else None

    filters = {"owner": user}
    # If using supplier field, we could add: if supplier: filters["supplier"] = supplier
    # But usually owner is enough for creation. 
    # Let's try to match by owner OR supplier if field exists.
    
    or_filters = []
    or_filters.append(["owner", "=", user])
    if supplier:
         # Check if 'supplier' field exists in RFQ Query
         if frappe.get_meta("RFQ Query").has_field("supplier"):
             or_filters.append(["supplier", "=", supplier])

    queries = frappe.get_all("RFQ Query", 
        filters=or_filters if len(or_filters) > 1 else filters,
        fields=["name", "subject", "rfq", "query", "response", "status", "creation"],
        order_by="creation desc"
    )
    return queries

@frappe.whitelist()
def create_rfq_query(subject, rfq, query):
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please login to submit a query"), frappe.PermissionError)

    # Validate RFQ access
    if not frappe.db.exists("Request for Quotation", rfq):
        frappe.throw(_("Invalid Tender ID"), frappe.ValidationError)

    doc = frappe.new_doc("RFQ Query")
    doc.subject = subject
    doc.rfq = rfq
    doc.query = query
    doc.status = "Pending"
    
    # Link Supplier if possible
    supplier_details = get_supplier_details()
    if supplier_details and doc.meta.has_field("supplier"):
        doc.supplier = supplier_details.get("name")
    
    doc.save(ignore_permissions=True)
    return {"status": "success", "message": "Query submitted successfully", "data": doc.name}

@frappe.whitelist()
def create_rfq_questionnaire(rfq, subject, query):
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please login to submit a request"), frappe.PermissionError)

    if not frappe.db.exists("Request for Quotation", rfq):
        frappe.throw(_("Invalid Tender ID"), frappe.ValidationError)

    doc = frappe.new_doc("RFQ Questionnaires")
    doc.rfq = rfq
    doc.subject = subject 
    # Also set the type field explicitly since the frontend passes the type as 'subject'
    if doc.meta.has_field("type_of_questionnaire"):
        doc.type_of_questionnaire = subject
        
    doc.query = query
    doc.date = frappe.utils.today()
    doc.status = "Pending"
    
    doc.save(ignore_permissions=True)
    return {"status": "success", "message": "Questionnaire requested successfully", "data": doc.name}

@frappe.whitelist()
def get_my_questionnaires():
    user = frappe.session.user
    if user == "Guest":
        return []
    
    # Filter by owner (standard)
    questionnaires = frappe.get_all("RFQ Questionnaires", 
        filters={"owner": user},
        fields=["name", "subject", "rfq", "query", "response", "status", "creation", "date"],
        order_by="creation desc"
    )
    return questionnaires


@frappe.whitelist()
def get_catalog_items():
    user = frappe.session.user

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
        # 1. Initialize ALL local variables at the very start of the loop
        tax_val = 0 
        is_my_item = False
        
        # Check if it belongs to the supplier catalog
        is_my_item = frappe.db.exists("Item Supplier", {
            "parent": item.id,
            "supplier": current_supplier
        })
        
        item['is_my_item'] = True if is_my_item else False
        item['status'] = "active"
        
        # 2. Lookup Tax Rate
        # We use frappe.db.get_value with only the parent filter
        tax_template = frappe.db.get_value("Item Tax", {"parent": item.id}, "item_tax_template")

        if tax_template:
            # Look up the rate from the detail table
            found_rate = frappe.db.get_value("Item Tax Template Detail", {"parent": tax_template}, "tax_rate")
            if found_rate:
                tax_val = found_rate
        
        # Now use the variable
        item['tax'] = f"{int(tax_val)}% GST"

        # 3. Purchasing Data
        lead_days = item.get('lead_time_days')
        item['leadTime'] = f"{lead_days} days" if lead_days else "N/A"
        item['moq'] = int(item.get('min_order_qty') or 1)

    return {
        "items": items,
        "current_supplier": current_supplier
    }


@frappe.whitelist()
def add_to_catalog(item_id):
    user = frappe.session.user
    supplier = frappe.db.get_value("Portal User", {"user": user, "parenttype": "Supplier"}, "parent")
    
    if not supplier:
        frappe.throw("Supplier not found for this user.")

    doc = frappe.get_doc("Item", item_id)
    doc.append("supplier_items", {
        "supplier": supplier
    })
    doc.save(ignore_permissions=True)
    
    return "success"


@frappe.whitelist()
def create_supplier_item():
    data = frappe.local.form_dict
    user = frappe.session.user
    
    current_supplier = frappe.db.get_value("Portal User", {"user": user}, "parent")

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

@frappe.whitelist()
def remove_from_catalog(item_id):

    user = frappe.session.user
    current_supplier = frappe.db.get_value("Portal User", {"user": user}, "parent")
    
    if not current_supplier:
        frappe.throw("Supplier not found for the current user.")

    frappe.db.delete("Item Supplier", {
        "parent": item_id,
        "supplier": current_supplier
    })
    
    return "success"

@frappe.whitelist()
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
    
@frappe.whitelist()
def get_similar_tenders(category, exclude_id):
    print("---------------working----------")
    return frappe.db.get_list('Request for Quotation', 
        filters={
            'custom_rfq_category': category, 
            'name': ['!=', exclude_id],
            'docstatus': 0
        },
        fields=[
            'name as id', 
            'custom_rfq_subject as title', 
            'custom_total_budget_ as budget', 
            'custom_bid_submission_last_date as deadline'
        ],
        limit=5
    )

@frappe.whitelist()
def place_supplier_bid(rfq_id, amount):
    try:
        supplier_name = frappe.db.get_value("Portal User", 
            {"user": frappe.session.user, "parenttype": "Supplier"}, 
            "parent")

        if not supplier_name:
            return {"status": "error", "message": "Your user account is not linked to a Supplier."}

        # Rest of your code as seen in your screenshot...
        rfq = frappe.get_doc("Request for Quotation", rfq_id)
        
        # Check if live bidding is actually enabled on the backend for security
        if not rfq.custom_enable_live_bidding:
            return {"status": "error", "message": "Live bidding is not active for this tender."}

        sq = frappe.new_doc("Supplier Quotation")
        sq.request_for_quotation = rfq_id
        sq.supplier = supplier_name
        sq.transaction_date = frappe.utils.nowdate()

        for item in rfq.items:
            sq.append("items", {
                "item_code": item.item_code,
                "qty": item.qty,
                "rate": amount,
                "uom": item.uom,
                "warehouse": item.warehouse
            })

        sq.insert(ignore_permissions=True)
        
        return {
            "status": "success", 
            "message": f"Bid placed successfully! Quotation {sq.name} created."
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Bid Placement Error")
        return {"status": "error", "message": str(e)}
    

@frappe.whitelist()
def get_recent_bid_activity(rfq_id):
    return frappe.db.get_list("Supplier Quotation", 
        filters={
            "request_for_quotation": rfq_id, 
            "docstatus": 0 
        },
        fields=["supplier", "grand_total as total", "creation"],
        order_by="creation desc", 
        limit=5,
        ignore_permissions=True
    )
    
@frappe.whitelist()
def place_supplier_bid(rfq_id, amount):
    try:
        supplier_name = frappe.db.get_value("Portal User", {"user": frappe.session.user}, "parent")

        rfq = frappe.get_doc("Request for Quotation", rfq_id)

        sq = frappe.new_doc("Supplier Quotation")
        
        sq.request_for_quotation = rfq_id 
        sq.supplier = supplier_name
        sq.transaction_date = frappe.utils.nowdate()

        for item in rfq.items:
            sq.append("items", {
                "item_code": item.item_code,
                "qty": item.qty,
                "rate": amount,
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