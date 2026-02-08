from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from ecommerce_integrations.shopify.constants import SHIPPING_COMPANY_FIELD, SHIPPING_PHONE_FIELD


def execute():
	custom_fields = {
		"Delivery Note": [
		dict(
					fieldname=SHIPPING_COMPANY_FIELD,
					label="Shipping Company",
					fieldtype="Link",
					insert_after=SHIPPING_PHONE_FIELD,
					options="Shipping Company",
					reqd=1
				),
		],
	}
	create_custom_fields(custom_fields)
