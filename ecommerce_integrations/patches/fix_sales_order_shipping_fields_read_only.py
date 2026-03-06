import frappe

from ecommerce_integrations.shopify.constants import (
	SHIPPING_ADDRESS_FIELD,
	SHIPPING_CUSTOMER_NAME_FIELD,
	SHIPPING_PHONE_FIELD,
)

SALES_ORDER_SHIPPING_FIELDS = [
	SHIPPING_CUSTOMER_NAME_FIELD,
	SHIPPING_ADDRESS_FIELD,
	SHIPPING_PHONE_FIELD,
]


def execute():
	for fieldname in SALES_ORDER_SHIPPING_FIELDS:
		if frappe.db.exists(
			"Custom Field", {"dt": "Sales Order", "fieldname": fieldname}
		):
			frappe.db.set_value(
				"Custom Field",
				{"dt": "Sales Order", "fieldname": fieldname},
				"read_only",
				0,
			)

	frappe.clear_cache()
