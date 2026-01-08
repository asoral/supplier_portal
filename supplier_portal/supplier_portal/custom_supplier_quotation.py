import frappe
from frappe.utils import flt

def validate_bid_decrement(doc, method=None):
    # Only validate for Supplier Quotation linked to an RFQ
    rfq_name = doc.get("request_for_quotation")
    
    if not rfq_name and doc.items:
        # Try to find RFQ from items
        for item in doc.items:
            if item.get("request_for_quotation"):
                rfq_name = item.get("request_for_quotation")
                break
                
    if not rfq_name:
        return

    rfq = frappe.get_doc("Request for Quotation", rfq_name)
    
    # Check if Live Bidding is enabled and there is a decrement value
    if not rfq.custom_enable_live_bidding or not rfq.custom_min_live_bid_decrement:
        return

    decrement = flt(rfq.custom_min_live_bid_decrement)
    
    # Find the current lowest bid (submitted) for this RFQ
    # Since SQ is linked to RFQ usually via Items in standard, we need to query carefully.
    # However, if we found rfq_name from items, it means standard link exists.
    # We need to find other Supplier Quotations linked to this RFQ.
    # They are linked via Supplier Quotation Item -> request_for_quotation.
    
    # Get all Supplier Quotations that have items linked to this RFQ
    # This is a bit complex query if parent doesn't have the field.
    # But usually, if SQ is created from RFQ, the field might be set or mapped.
    # Let's rely on finding standard SQs.
    
    # If the parent field exists in DB but not in Doc object (unlikely for get_value), 
    # we should check how SQs are normally queried for an RFQ.
    
    lowest_bid = frappe.db.sql("""
        SELECT sq.grand_total 
        FROM `tabSupplier Quotation` sq
        JOIN `tabSupplier Quotation Item` sqi ON sqi.parent = sq.name
        WHERE sqi.request_for_quotation = %s
        AND sq.docstatus = 1
        AND sq.name != %s
        ORDER BY sq.grand_total ASC
        LIMIT 1
    """, (rfq_name, doc.name))
    
    if lowest_bid:
        lowest_bid_val = lowest_bid[0][0]
    else:
        lowest_bid_val = None

    if lowest_bid_val is not None:
        lowest_bid_amount = flt(lowest_bid_val)
        max_allowed_bid = lowest_bid_amount - decrement
        
        if doc.grand_total > max_allowed_bid:
            frappe.throw(
                f"Your bid ({doc.grand_total}) must be at least {decrement} less than the current lowest bid ({lowest_bid_amount}). Maximum allowed bid is {max_allowed_bid}.",
                title="Bid Validation"
            )
