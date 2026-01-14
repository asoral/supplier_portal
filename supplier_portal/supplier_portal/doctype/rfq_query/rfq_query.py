import frappe
from frappe.model.document import Document

class RFQQuery(Document):
    def validate(self):
        self.update_status_validation()

    def update_status_validation(self):
        if self.response and self.status == "Pending":
            frappe.throw("Please change status to 'Answered' before saving the response.")

