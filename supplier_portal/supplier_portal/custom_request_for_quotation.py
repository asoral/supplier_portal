import frappe
from frappe.utils import now_datetime

def validate(doc, method=None):
    if doc.custom_publish_on_website:
        if not doc.custom_publish_date:
            doc.custom_publish_date = now_datetime()
        
        if not doc.custom_rfq_subject:
             frappe.throw("RFQ Subject is mandatory when publishing on website")
        if not doc.custom_rfq_description:
             frappe.throw("RFQ Description is mandatory when publishing on website")

    # Calculate Total Budget
    total = 0.0
    for item in doc.items:
        # Calculate budget per line
        if item.custom_budget and item.qty:
            item.custom_budget_amount = item.custom_budget * item.qty
            total += item.custom_budget_amount
            
        if item.custom_budget and item.conversion_factor:
            item.custom_budget_as_per_stock_uom = item.custom_budget * item.conversion_factor
            
    doc.custom_total_budget_ = total

    total_qty = 0
    
    if doc.items:
        for item in doc.items:
            total_qty += (item.qty or 0)
    
    doc.custom_total_quantity = total_qty

def before_save(doc, method=None):
    # Ensure total budget is saved correctly if updated in JS or otherwise
    validate(doc, method)

@frappe.whitelist()
def get_allowed_item_groups(rfq_category):
    if not rfq_category:
        return []
    
    # Fetch RFQ Category
    category = frappe.get_doc("RFQ Category", rfq_category)
    if not category.item_groups:
        return []
    
    # Since RFQ Category Item Group now links directly to the standard Item Group,
    # we can just return the values directly.
    return [d.item_group for d in category.item_groups]

def update_bid_status():
    """
    Scheduled job to update Bid Status based on dates.
    Active: Open / Ongoing
    Closing Soon: Within 3 days (or configured fence) of closing
    Closed: Past submission date
    """
    settings = frappe.get_single("Supplier Portal Settings")
    fence_days = settings.bid_closing_soon_fence or 3
    
    # Find active RFQs or those that need updating
    # Logic:
    # If now > custom_bid_submission_last_date -> Closed
    # If custom_bid_submission_last_date - now <= fence days -> Closing Soon
    # Else -> Active
    
    now = frappe.utils.now_datetime()
    
    # Update to Closed
    frappe.db.sql("""
        UPDATE `tabRequest for Quotation`
        SET custom_bid_status = 'Closed'
        WHERE custom_publish_on_website = 1
        AND custom_bid_submission_last_date < %s
        AND custom_bid_status != 'Closed'
    """, (now,))
    
    # Update to Closing Soon
    # Date condition: last_date > now AND last_date <= now + fence
    fence_date = frappe.utils.add_days(now, fence_days)
    
    frappe.db.sql("""
        UPDATE `tabRequest for Quotation`
        SET custom_bid_status = 'Closing Soon'
        WHERE custom_publish_on_website = 1
        AND custom_bid_submission_last_date > %s
        AND custom_bid_submission_last_date <= %s
        AND custom_bid_status != 'Closing Soon'
        AND custom_bid_status != 'Closed'
    """, (now, fence_date))
    
    # Update to Active (if dates changed or it was pending)
    # last_date > now + fence
    frappe.db.sql("""
        UPDATE `tabRequest for Quotation`
        SET custom_bid_status = 'Active'
        WHERE custom_publish_on_website = 1
        AND custom_bid_submission_last_date > %s
        AND custom_bid_status NOT IN ('Active', 'Closed', 'Closing Soon')
    """, (fence_date,))
    
    frappe.db.commit()
