from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add tracking shipment number field to Delivery Note as required field after city"""
	custom_fields = {
		"Delivery Note": [
			dict(
				fieldname="tracking_shipment_number",
				label="Tracking Shipment Number",
				fieldtype="Data",
				insert_after="city",
				reqd=1,
			),
		],
	}
	create_custom_fields(custom_fields)

