import frappe

from ecommerce_integrations.shopify.constants import SHIPPING_STATUS_FIELD


def execute():
	custom_field_name = frappe.db.get_value(
		"Custom Field",
		{"dt": "Delivery Note", "fieldname": SHIPPING_STATUS_FIELD},
	)
	if custom_field_name:
		frappe.delete_doc("Custom Field", custom_field_name)
