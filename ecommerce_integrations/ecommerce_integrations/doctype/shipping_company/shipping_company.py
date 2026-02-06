# Copyright (c) 2026, Shaqwieer and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


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
	pass
