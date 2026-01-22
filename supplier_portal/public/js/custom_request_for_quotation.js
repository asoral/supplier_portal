frappe.ui.form.on("Request for Quotation", {
    refresh: function (frm) {
        if (frm.doc.custom_rfq_category) {
            frm.trigger("set_item_query");
        }

        if (frm.doc.custom_publish_date == 1) {
            frm.set_df_property("custom_publish_on_website", "read_only", 1);
        } else {
            frm.set_df_property("custom_publish_on_website", "read_only", 0);
        }
        if (frm.doc.custom_contact_person) {
            frm.trigger("custom_contact_person");
        }
        if (frm.doc.custom_contact_address) {
            frm.trigger("custom_contact_address");
        }
    },
    custom_publish_on_website: function (frm) {
        if (frm.doc.custom_publish_on_website == 1) {
            frm.set_df_property("custom_publish_on_website", "read_only", 1);
            frm.set_value("custom_publish_date", frappe.datetime.get_today());
        } else {
            frm.set_df_property("custom_publish_on_website", "read_only", 0);
            frm.set_value("custom_publish_date", "");
        }
    },


    custom_rfq_category: function (frm) {
        frm.set_value("items", []); // Clear items if category changes? Optional but safer for consistency
        frm.trigger("set_item_query");
    },
    set_item_query: function (frm) {
        if (frm.doc.custom_rfq_category) {
            frappe.call({
                method: "supplier_portal.supplier_portal.custom_request_for_quotation.get_allowed_item_groups",
                args: {
                    rfq_category: frm.doc.custom_rfq_category
                },
                callback: function (r) {
                    if (r.message) {
                        let item_groups = r.message;
                        frm.set_query("item_code", "items", function () {
                            return {
                                filters: {
                                    item_group: ["in", item_groups],
                                    is_purchase_item: 1,
                                    has_variants: 0,
                                    disabled: 0
                                }
                            };
                        });
                    }
                }
            });
        }
    },
    custom_contact_person: function (frm) {
        if (frm.doc.custom_contact_person) {
            frappe.call({
                method: 'frappe.contacts.doctype.contact.contact.get_contact_details',
                args: { contact: frm.doc.custom_contact_person },
                callback: function (r) {
                    if (r.message) {
                        frm.set_value('custom_contact_display', r.message.contact_display);
                    }
                }
            });
        } else {
            frm.set_value('custom_contact_display', "");
        }
    },
    custom_contact_address: function (frm) {
        if (frm.doc.custom_contact_address) {
            frappe.call({
                method: 'frappe.contacts.doctype.address.address.get_address_display',
                args: { address_dict: frm.doc.custom_contact_address },
                callback: function (r) {
                    // get_address_display usually returns html directly or inside message
                    if (r.message) {
                        frm.set_value('custom_address_display', r.message);
                    }
                }
            });
        } else {
            frm.set_value('custom_address_display', "");
        }
    }
});

frappe.ui.form.on("Request for Quotation Item", {
    custom_budget: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        row.custom_budget_amount = (row.custom_budget || 0) * (row.qty || 0);
        row.custom_budget_as_per_stock_uom = (row.custom_budget || 0) * (row.conversion_factor || 1);
        frm.refresh_field("items");
        calculate_total_budget(frm);
    },

    qty: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        row.custom_budget_amount = (row.custom_budget || 0) * (row.qty || 0);
        frm.refresh_field("items");
        calculate_total_budget(frm);
    }
});

function calculate_total_budget(frm) {
    let total = 0;
    (frm.doc.items || []).forEach(row => {
        total += (row.custom_budget_amount || 0);
    });
    frm.set_value("custom_total_budget_", total);
}
