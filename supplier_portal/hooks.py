app_name = "supplier_portal"
app_title = "supplier_portal"
app_publisher = "rutuja chavan"
app_description = "supplier_portal"
app_email = "rchavan@dexciss.io"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "supplier_portal",
# 		"logo": "/assets/supplier_portal/logo.png",
# 		"title": "supplier_portal",
# 		"route": "/supplier_portal",
# 		"has_permission": "supplier_portal.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/supplier_portal/css/supplier_portal.css"
# app_include_js = "/assets/supplier_portal/js/supplier_portal.js"

# include js, css files in header of web template
# web_include_css = "/assets/supplier_portal/css/supplier_portal.css"
# web_include_js = "/assets/supplier_portal/js/supplier_portal.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "supplier_portal/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "supplier_portal/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# website user home page (by Role)
role_home_page = {
	"Supplier": "/supplier-portal"
}

website_user_home = "/supplier-portal"

website_route_rules = [
	{'from_route': '/supplier-portal/<path:app_path>', 'to_route': 'supplier-portal'},
	{'from_route': '/supplier-portal', 'to_route': 'supplier-portal'},
]