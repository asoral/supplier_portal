import frappe
from frappe import _

def update_delivery_percent(doc,method):
    if not doc.items:
        doc.custom_total_blanket_quantity = 0
        doc.total = 0
        return

    total_blanket_qty = 0
    total_amount = 0

    for row in doc.items:
        qty = row.qty or 0
        rate = row.rate or 0

        total_blanket_qty += qty

        amount = qty * rate
        row.custom_amount = amount

        total_amount += amount

    doc.custom_total_blanket_quantity = total_blanket_qty
    doc.custom_total_inr = total_amount

def recalculate_blanket_order_total(blanket_order):
    print("------------------------working")

    result = frappe.db.sql("""
        SELECT
            SUM(qty) AS total_blanket_qty,
            SUM(ordered_qty) AS total_ordered_qty
        FROM `tabBlanket Order Item`
        WHERE parent = %s
    """, blanket_order, as_dict=True)[0]

    total_blanket_qty = result.total_blanket_qty or 0
    total_ordered_qty = result.total_ordered_qty or 0

    print("--------------------total ordered qty", total_ordered_qty)

    delivery_percent = 0
    if total_blanket_qty > 0:
        delivery_percent = (total_ordered_qty / total_blanket_qty) * 100

    frappe.db.set_value(
        "Blanket Order",
        blanket_order,
        {
            "custom_total_ordered_quantity": total_ordered_qty,
            "custom_delivery_": delivery_percent
        }
    )

    frappe.db.commit()

def update_total_ordered_qty(doc, method):
    print("-----------------working")
    for ref in doc.references:
        if ref.reference_doctype != "Purchase Order":
            continue

        po = frappe.get_doc("Purchase Order", ref.reference_name)

        for po_item in po.items:
            if not po_item.blanket_order:
                continue

            recalculate_blanket_order_total(po_item.blanket_order)

