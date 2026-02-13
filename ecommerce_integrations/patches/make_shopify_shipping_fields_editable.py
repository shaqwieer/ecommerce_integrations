from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from ecommerce_integrations.shopify.constants import (
	ORDER_STATUS_FIELD,
	SHIPPING_ADDRESS_FIELD,
	SHIPPING_CUSTOMER_NAME_FIELD,
	SHIPPING_PHONE_FIELD,
)


def execute():
	custom_fields = {
		"Sales Order": [
			dict(
				fieldname=SHIPPING_CUSTOMER_NAME_FIELD,
				label="Shopify Shipping Customer Name",
				fieldtype="Data",
				insert_after=ORDER_STATUS_FIELD,
				read_only=0,
			),
			dict(
				fieldname=SHIPPING_ADDRESS_FIELD,
				label="Shopify Shipping Address",
				fieldtype="Small Text",
				insert_after=SHIPPING_CUSTOMER_NAME_FIELD,
				read_only=0,
			),
			dict(
				fieldname=SHIPPING_PHONE_FIELD,
				label="Shopify Shipping Phone",
				fieldtype="Data",
				insert_after=SHIPPING_ADDRESS_FIELD,
				read_only=0,
			),
		],
	}
	create_custom_fields(custom_fields)
