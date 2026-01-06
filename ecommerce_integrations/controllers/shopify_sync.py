import re
from typing import Any

import frappe
from frappe import _
from frappe.utils import validate_phone_number

from ecommerce_integrations.controllers.customer import EcommerceCustomer
from ecommerce_integrations.shopify.constants import (
	ADDRESS_ID_FIELD,
	CUSTOMER_ID_FIELD,
	MODULE_NAME,
	ORDER_ID_FIELD,
)


@frappe.whitelist()
def sync_customers_from_excel(file_url: str):
	"""Enrich existing customers (created from sales order webhooks) with Excel data.

	Expects `file_url` an Attach field value (e.g. /files/filename.xlsx).

	**Use Case**: Customers already exist in ERPNext (from Shopify sales order webhooks)
	with only their customer_id. This function enriches them with:
	- Customer name (first_name + last_name)
	- Email address
	- Phone number
	- Shipping address and contact details

	**Performance Note**: Filter Excel by date to match recent sales orders, then
	this function updates only the relevant customers.

	Required fields in Excel:
	- customer_id: Unique identifier (must match existing customer record)
	- first_name, last_name: Customer name data
	- email: Customer email address
	- phone: Phone number (optional, added to address and contact)
	- shipping_address fields: address1, address2, city, state/province, zip, country

	Respects the `personally_identifiable_information_access` flag from Shopify Settings.
	"""
	if not file_url:
		frappe.throw(_("file_url is required"))

	site_path = _check_file_path(file_url)
	updated = 0
	skipped = 0
	errors = []
	rows = _read_file_and_extract_rows(site_path)
	date_from = _fetch_earliest_date(rows)
	row_dict = {str(row.get("Id")).strip(): row for row in rows if row.get("Id")}
	sales_orders = _get_sales_orders_from_erpnext_with_customer_info(date_from)
	# need to iterate over sales order and from row dictionary i enrich with customer name and contact and address from ecommerece class two func contact and address
	for so in sales_orders:
		order_id = str(so.get(ORDER_ID_FIELD)).strip()
		if order_id in row_dict:
			order_full_data = row_dict[order_id]
			ecommerece_customer = EcommerceCustomer(so.customer, "name", MODULE_NAME)
			try:
				customer_doc = ecommerece_customer.get_customer_doc()
				customer_name = order_full_data.get("Shipping Name").strip()
				if not customer_name:
					customer_name = order_full_data.get("Email", "").strip()
				if customer_doc.customer_name != customer_name:
					customer_doc.customer_name = customer_name
					customer_doc.save(ignore_permissions=True)
				# create address
				shipping_address = _map_address_fields(
					order_full_data, customer_name, "Shipping", order_full_data.get("Email", "").strip()
				)
				ecommerece_customer.create_customer_address(shipping_address)
				# create contact
				contact = _map_customer_contact(order_full_data)
				ecommerece_customer.create_customer_contact(contact)

				updated += 1
			except frappe.DoesNotExistError:
				skipped += 1
			except Exception as e:
				errors.append(frappe._("{0}: {1}").format(so.name, str(e)))
		else:
			skipped += 1

	return {"updated": updated, "skipped": skipped, "errors": errors}


def _check_file_path(file_url: str) -> str:
	"""Check and return valid file path."""
	site_path = frappe.get_site_path("public", file_url.lstrip("/"))
	import os

	if not os.path.exists(site_path):
		# try with files/ prefix
		site_path = frappe.get_site_path("public", "files", os.path.basename(file_url))
		if not os.path.exists(site_path):
			frappe.throw(_("File not found: {0}").format(file_url))
	return site_path


def _read_file_and_extract_rows(site_path: str) -> list[dict[str, Any]]:
	"""Read Excel or CSV file and extract rows as list of dicts."""
	import os

	ext = os.path.splitext(site_path)[1].lower()
	rows = []
	try:
		if ext in (".xlsx", ".xlsm", ".xltx", ".xltm"):
			from openpyxl import load_workbook

			wb = load_workbook(site_path, read_only=True, data_only=True)
			ws = wb[wb.sheetnames[0]]
			it = ws.iter_rows(values_only=True)
			headers = [str(h).strip() if h is not None else "" for h in next(it)]
			for r in it:
				rows.append(dict(zip(headers, r)))
		else:
			import csv

			with open(site_path, newline="") as f:
				reader = csv.DictReader(f)
				for r in reader:
					rows.append(r)
	except Exception as e:
		frappe.throw(_("Failed to read uploaded file: {0}").format(e))
	return rows


def _get_sales_orders_from_erpnext_with_customer_info(date_from: str) -> list[dict[str, Any]]:
	"""Get sales orders with customer name id from ERPNext created on or after `date_from`."""
	sales_orders = frappe.db.get_all(
		"Sales Order",
		filters={
			"creation": [">=", date_from],
			ORDER_ID_FIELD: ["is", "set"],
		},
		fields=["name", "customer", ORDER_ID_FIELD],
	)
	return sales_orders


def _map_address_fields(shopify_address, customer_name, address_type, email):
	"""returns dict with shopify address fields mapped to equivalent ERPNext fields"""

	country_mapping = {
		"EG": "Egypt",
		"US": "United States",
		"GB": "United Kingdom",
		"DE": "Germany",
		"FR": "France",
		"IT": "Italy",
		"ES": "Spain",
		"CA": "Canada",
		"AU": "Australia",
		"JP": "Japan",
		"CN": "China",
		"IN": "India",
	}
	address_fields = {
		"address_title": customer_name,
		"address_type": address_type,
		ADDRESS_ID_FIELD: shopify_address.get("Id"),
		"address_line1": shopify_address.get("Shipping Street") or "Shipping Address1",
		"address_line2": shopify_address.get("Shipping Address1"),
		"city": shopify_address.get("Shipping City"),
		"state": shopify_address.get("Shipping Province"),
		"pincode": shopify_address.get("Shipping Zip"),
		"country": country_mapping.get(shopify_address.get("Shipping Country"), "Egypt"),
		"email_id": email,
	}

	phone = shopify_address.get("Phone")
	# if validate_phone_number(phone, throw=False):
	address_fields["Phone"] = phone

	return address_fields


def _map_customer_contact(shopify_customer: dict[str, Any]) -> None:
	contact_fields = {
		"status": "Passive",
		"first_name": shopify_customer.get("Shipping Name").split(" ")[0],
		"last_name": shopify_customer.get("Shipping Name").split(" ")[-1],
		"unsubscribed": True,
	}

	if shopify_customer.get("email"):
		contact_fields["email_ids"] = [{"email_id": shopify_customer.get("email"), "is_primary": True}]

	phone_no = shopify_customer.get("phone") or shopify_customer.get("default_address", {}).get("phone")

	if validate_phone_number(phone_no, throw=False):
		contact_fields["phone_nos"] = [{"phone": phone_no, "is_primary_phone": True}]

	return contact_fields


def _fetch_earliest_date(rows: list[dict[str, Any]]) -> str:
	"""Fetch the earliest date from the rows to limit sales order fetch."""
	date_from = None
	date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
	for row in rows:
		created_at = row.get("Created at")
		if created_at:
			match = date_pattern.search(created_at)
			if match:
				row_date = match.group(0)
				if not date_from or row_date < date_from:
					date_from = row_date
	return date_from if date_from else "1970-01-01"
