import frappe

import sys

def check_user():
    if len(sys.argv) > 1:
        user = sys.argv[1]
    else:
        user = input("Enter user email: ")
        
    if not frappe.db.exists("User", user):
        print(f"User {user} not found.")
        return

    u = frappe.get_doc("User", user)
    print(f"User: {u.name}")
    print(f"Enabled: {u.enabled}")
    print(f"User Type: {u.user_type}")
    print(f"Roles: {[r.role for r in u.roles]}")
    
    # Check if has desk access
    print(f"Has Desk Access: {u.user_type == 'System User'}")

check_user()
