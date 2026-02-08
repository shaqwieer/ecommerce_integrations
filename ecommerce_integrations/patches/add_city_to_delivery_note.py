from frappe.custom.doctype.custom_field.custom_field import create_custom_fields




def execute():
	"""Add city field to Delivery Note as required field"""
	custom_fields = {
		"Delivery Note": [
			dict(
				fieldname="city",
				label="City",
				fieldtype="Link",
				options="City",
				insert_after="customer",
				reqd=1,
				in_standard_filter=1,
			),
		],
	}
	create_custom_fields(custom_fields)

