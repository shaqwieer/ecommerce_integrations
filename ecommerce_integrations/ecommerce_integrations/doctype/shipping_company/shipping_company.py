# Copyright (c) 2026, Shaqwieer and contributors
# For license information, please see license.txt

# import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.model.document import Document

from ecommerce_integrations.shopify.constants import (
	ORDER_STATUS_FIELD,
	SHIPPING_ADDRESS_FIELD,
	SHIPPING_COMPANY_FIELD,
	SHIPPING_CUSTOMER_NAME_FIELD,
	SHIPPING_PHONE_FIELD,
	SHIPPING_STATUS_FIELD,
)


class ShippingCompany(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link
		additional_info: DF.Text | None
		contact_address: DF.Data | None
		contact_number: DF.Phone | None
		shipping_name: DF.Data
	# end: auto-generated types
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		account: DF.Link
		additional_info: DF.Text | None
		contact_address: DF.Data | None
		contact_number: DF.Phone | None
		shipping_name: DF.Data

	pass

def setup_custom_fields_on_begining():
		custom_fields = {
			"Sales Order": [
				dict(
					fieldname=SHIPPING_CUSTOMER_NAME_FIELD,
					label="Shopify Shipping Customer Name",
					fieldtype="Data",
					insert_after=ORDER_STATUS_FIELD,
					read_only=1,
				),
				dict(
					fieldname=SHIPPING_ADDRESS_FIELD,
					label="Shopify Shipping Address",
					fieldtype="Small Text",
					insert_after=SHIPPING_CUSTOMER_NAME_FIELD,
					read_only=1,
				),
				dict(
					fieldname=SHIPPING_PHONE_FIELD,
					label="Shopify Shipping Phone",
					fieldtype="Data",
					insert_after=SHIPPING_ADDRESS_FIELD,
					read_only=1,
				),
			],
			"Delivery Note": [
				dict(
					fieldname=SHIPPING_CUSTOMER_NAME_FIELD,
					label="Shopify Shipping Customer Name",
					fieldtype="Data",
					insert_after=ORDER_STATUS_FIELD,
					read_only=1,
				),
				dict(
					fieldname=SHIPPING_ADDRESS_FIELD,
					label="Shopify Shipping Address",
					fieldtype="Small Text",
					insert_after=SHIPPING_CUSTOMER_NAME_FIELD,
					read_only=1,
				),
				dict(
					fieldname=SHIPPING_PHONE_FIELD,
					label="Shopify Shipping Phone",
					fieldtype="Data",
					insert_after=SHIPPING_ADDRESS_FIELD,
					read_only=1,
				),
				dict(
					fieldname=SHIPPING_COMPANY_FIELD,
					label="Shipping Company",
					fieldtype="Link",
					insert_after=SHIPPING_PHONE_FIELD,
					options="Shipping Company",
					# allow_on_submit=1,
				),
				dict(
					fieldname=SHIPPING_STATUS_FIELD,
					label="Shipping Status",
					fieldtype="Select",
					insert_after=SHIPPING_COMPANY_FIELD,
					options="\nPending\nIn Transit\nOut for Delivery\nDelivered\nReturned\nLost",
					allow_on_submit=1,
				),
			],
			"Sales Invoice": [
				dict(
					fieldname=SHIPPING_CUSTOMER_NAME_FIELD,
					label="Shopify Shipping Customer Name",
					fieldtype="Data",
					insert_after=ORDER_STATUS_FIELD,
					read_only=1,
				),
				dict(
					fieldname=SHIPPING_ADDRESS_FIELD,
					label="Shopify Shipping Address",
					fieldtype="Small Text",
					insert_after=SHIPPING_CUSTOMER_NAME_FIELD,
					read_only=1,
				),
				dict(
					fieldname=SHIPPING_PHONE_FIELD,
					label="Shopify Shipping Phone",
					fieldtype="Data",
					insert_after=SHIPPING_ADDRESS_FIELD,
					read_only=1,
				),
			],
		}
		create_custom_fields(custom_fields)
