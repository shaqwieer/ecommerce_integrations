# Copyright (c) 2026, Shaqwieer and contributors
# For license information, please see license.txt

# import frappe


import frappe
from frappe import _
from frappe.utils import flt, getdate

from ecommerce_integrations.shopify.constants import SHIPPING_COMPANY_FIELD, SHIPPING_STATUS_FIELD


def execute(filters=None):
	return ShippingCompanySummary(filters).run()


class ShippingCompanySummary:
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})
		self.date_field = "posting_date"

	def run(self):
		self.get_columns()
		self.get_data()
		self.get_chart_data()

		return self.columns, self.data, None, self.chart

	def get_columns(self):
		self.columns = [
			{
				"label": _("Delivery Note"),
				"fieldname": "delivery_note",
				"fieldtype": "Link",
				"options": "Delivery Note",
				"width": 150,
			},
			{
				"label": _("Posting Date"),
				"fieldname": "posting_date",
				"fieldtype": "Date",
				"width": 120,
			},
			{
				"label": _("Customer"),
				"fieldname": "customer",
				"fieldtype": "Link",
				"options": "Customer",
				"width": 150,
			},
			{
				"label": _("Shipping Company"),
				"fieldname": "shipping_company",
				"fieldtype": "Link",
				"options": "Shipping Company",
				"width": 180,
			},
			{
				"label": _("Shipping Status"),
				"fieldname": "shipping_status",
				"fieldtype": "Data",
				"width": 130,
			},
			{
				"label": _("Grand Total"),
				"fieldname": "grand_total",
				"fieldtype": "Currency",
				"width": 120,
			},
			{
				"label": _("Company"),
				"fieldname": "company",
				"fieldtype": "Link",
				"options": "Company",
				"width": 120,
			},
		]

	def get_data(self):
		conditions = self.get_conditions()

		query = f"""
			SELECT
				dn.name as delivery_note,
				dn.posting_date,
				dn.customer,
				dn.`{SHIPPING_COMPANY_FIELD}` as shipping_company,
				dn.`{SHIPPING_STATUS_FIELD}` as shipping_status,
				dn.grand_total,
				dn.company
			FROM `tabDelivery Note` dn
			WHERE dn.docstatus = 1
				AND dn.`{SHIPPING_COMPANY_FIELD}` IS NOT NULL
				AND dn.`{SHIPPING_COMPANY_FIELD}` != ''
				{conditions}
			ORDER BY dn.posting_date DESC, dn.`{SHIPPING_COMPANY_FIELD}`
		"""

		self.data = frappe.db.sql(query, self.filters, as_dict=1)

		# Add summary row
		if self.data:
			total_row = {
				"delivery_note": _("Total"),
				"grand_total": sum(flt(d.get("grand_total", 0)) for d in self.data),
				"bold": 1,
			}
			self.data.append(total_row)

	def get_conditions(self):
		conditions = []

		if self.filters.get("from_date"):
			conditions.append(f"dn.{self.date_field} >= %(from_date)s")

		if self.filters.get("to_date"):
			conditions.append(f"dn.{self.date_field} <= %(to_date)s")

		if self.filters.get("shipping_company"):
			conditions.append(f"dn.`{SHIPPING_COMPANY_FIELD}` = %(shipping_company)s")

		if self.filters.get("shipping_status"):
			conditions.append(f"dn.`{SHIPPING_STATUS_FIELD}` = %(shipping_status)s")

		if self.filters.get("company"):
			conditions.append("dn.company = %(company)s")

		if self.filters.get("customer"):
			conditions.append("dn.customer = %(customer)s")

		return " AND " + " AND ".join(conditions) if conditions else ""

	def get_chart_data(self):
		if not self.data or len(self.data) <= 1:  # Only total row
			self.chart = None
			return

		# Chart 1: Shipping Status Distribution
		status_data = {}
		company_data = {}

		for row in self.data:
			if row.get("delivery_note") == _("Total"):
				continue

			status = row.get("shipping_status") or _("Not Set")
			status_data[status] = status_data.get(status, 0) + 1

			company = row.get("shipping_company") or _("Unknown")
			company_data[company] = company_data.get(company, 0) + 1

		# Status Distribution Chart
		status_chart = {
			"data": {
				"labels": list(status_data.keys()),
				"datasets": [
					{
						"name": _("Delivery Notes Count"),
						"values": list(status_data.values()),
					}
				],
			},
			"type": "pie",
			"colors": ["#7cd6fd", "#743ee2", "#ffa00a", "#5e64ff", "#28a745", "#dc3545"],
		}

		# Company Distribution Chart
		company_chart = {
			"data": {
				"labels": list(company_data.keys())[:10],  # Top 10 companies
				"datasets": [
					{
						"name": _("Delivery Notes Count"),
						"values": list(company_data.values())[:10],
					}
				],
			},
			"type": "bar",
			"colors": ["#5e64ff"],
		}

		# Combined chart data
		self.chart = {
			"data": {
				"labels": list(status_data.keys()),
				"datasets": [
					{
						"name": _("Delivery Notes by Status"),
						"values": list(status_data.values()),
					}
				],
			},
			"type": "pie",
			"colors": ["#7cd6fd", "#743ee2", "#ffa00a", "#5e64ff", "#28a745", "#dc3545"],
		}

