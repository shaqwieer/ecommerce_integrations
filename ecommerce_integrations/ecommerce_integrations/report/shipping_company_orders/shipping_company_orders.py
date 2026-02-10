# Copyright (c) 2026, Shaqwieer and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.utils import flt
from pypika import Order


def execute(filters=None):
	"""Execute the Shipping Company Orders report with filters and Query Builder."""
	columns = get_columns()
	data = get_data(filters)
	report_summary = get_report_summary(data, filters)
	chart = get_chart_data(data, filters)
	return columns, data, None, chart, report_summary


def get_columns():
	return [
		{
			"fieldname": "delivery_note",
			"label": _("Delivery Note"),
			"fieldtype": "Link",
			"options": "Delivery Note",
			"width": 120,
		},
		{"fieldname": "posting_date", "label": _("Date"), "fieldtype": "Date", "width": 100},
		{
			"fieldname": "sales_order",
			"label": _("Sales Order"),
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": 120,
		},
		# {"fieldname": "customer", "label": _("Customer"), "fieldtype": "Link", "options": "Customer", "width": 140},
		{
			"fieldname": "shopify_shipping_customer_name",
			"label": _("Shipping Name"),
			"fieldtype": "Data",
			"width": 110,
		},
		{
			"fieldname": "shopify_shipping_phone",
			"label": _("Shipping Phone"),
			"fieldtype": "Data",
			"width": 110,
		},
		{
			"fieldname": "shopify_shipping_address",
			"label": _("Shipping Address"),
			"fieldtype": "Data",
			"width": 140,
		},
		{"fieldname": "city_display", "label": _("City"), "fieldtype": "Data", "width": 100},
		{
			"fieldname": "shipping_company_display",
			"label": _("Shipping Company"),
			"fieldtype": "Data",
			"width": 130,
		},
		{
			"fieldname": "tracking_shipment_number",
			"label": _("Tracking No"),
			"fieldtype": "Data",
			"width": 130,
		},
		{"fieldname": "shipping_status", "label": _("Shipping Status"), "fieldtype": "Data", "width": 110},
		{"fieldname": "payment_status", "label": _("Payment Status"), "fieldtype": "Data", "width": 110},
		{
			"fieldname": "grand_total",
			"label": _("DN Amount"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 110,
		},
		{
			"fieldname": "total_invoice_amount",
			"label": _("Invoiced Amount"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 110,
		},
		{
			"fieldname": "paid_amount",
			"label": _("Paid Amount"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 110,
		},
		{
			"fieldname": "open_amount",
			"label": _("Outstanding"),
			"fieldtype": "Currency",
			"options": "currency",
			"width": 110,
		},
	]


def get_data(filters):
	dn = DocType("Delivery Note")
	dni = DocType("Delivery Note Item")
	city = DocType("City")
	ship_co = DocType("Shipping Company")

	query = (
		frappe.qb.from_(dn)
		.left_join(dni)
		.on(dni.parent == dn.name)
		.left_join(city)
		.on(city.name == dn.city)  # Join to get City Name
		.left_join(ship_co)
		.on(ship_co.name == dn.shipping_company)  # Join to get Shipping Company Name
		.select(
			dn.name.as_("delivery_note"),
			dn.posting_date,
			# dn.customer,
			city.city_name.as_("city_display"),  # Readable city
			dn.tracking_shipment_number,
			dn.shopify_shipping_customer_name,
			dn.shopify_shipping_phone,
			dn.shopify_shipping_address,
			ship_co.shipping_name.as_("shipping_company_display"),  # Readable company
			dn.shipping_status,
			dni.against_sales_order.as_("sales_order"),
			dn.grand_total,
			dn.currency,
		)
		.distinct()
		.orderby(dn.posting_date, order=Order.desc)
	)

	# Filtering logic remains the same
	if filters.get("from_date"):
		query = query.where(dn.posting_date >= filters["from_date"])
	if filters.get("to_date"):
		query = query.where(dn.posting_date <= filters["to_date"])

	data = query.run(as_dict=True)

	for row in data:
		status, total_inv, paid, open_amt = get_payment_info_for_so(row.get("sales_order"))
		row["payment_status"] = status
		row["total_invoice_amount"] = total_inv
		row["paid_amount"] = paid
		row["open_amount"] = open_amt

	return data


def get_payment_info_for_so(sales_order):
	if not sales_order:
		return ("No Order", 0, 0, 0)

	# Get sum of totals and outstanding from all submitted SIs linked to this SO
	invoices = frappe.db.sql(
		"""
        SELECT 
            SUM(si.grand_total) as total_grand,
            SUM(si.outstanding_amount) as total_outstanding
        FROM `tabSales Invoice` si
        WHERE EXISTS (
            SELECT name FROM `tabSales Invoice Item` sii 
            WHERE sii.parent = si.name AND sii.sales_order = %s
        ) AND si.docstatus = 1
    """,
		(sales_order,),
		as_dict=True,
	)

	if not invoices or not invoices[0].total_grand:
		return ("Not Invoiced", 0, 0, 0)

	inv = invoices[0]
	grand = flt(inv.total_grand)
	out = flt(inv.total_outstanding)
	paid = grand - out

	if out <= 0:
		return ("Paid", grand, paid, 0)
	if out >= grand:
		return ("Unpaid", grand, paid, out)
	return ("Partially Paid", grand, paid, out)


def get_payment_info_for_so(sales_order):
	"""
	Get payment status and amounts: SO -> Sales Invoice.
	Returns: (status, total_invoice_amount, paid_amount, open_amount)
	"""
	empty = ("", 0, 0, 0)
	if not sales_order:
		return empty

	# Get all submitted Sales Invoices against this Sales Order
	invoices = frappe.db.sql(
		"""
		SELECT si.name, si.outstanding_amount, si.grand_total
		FROM `tabSales Invoice` si
		INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
		WHERE sii.sales_order = %(so)s
			AND si.docstatus = 1
		GROUP BY si.name
		""",
		{"so": sales_order},
		as_dict=True,
	)

	if not invoices:
		return ("Not Invoiced", 0, 0, 0)

	total_outstanding = sum(flt(inv.outstanding_amount) for inv in invoices)
	total_grand = sum(flt(inv.grand_total) for inv in invoices)
	paid_amount = flt(total_grand) - flt(total_outstanding)

	if flt(total_grand) <= 0:
		return ("Fully Paid", total_grand, paid_amount, 0)
	if flt(total_outstanding) <= 0:
		return ("Fully Paid", total_grand, paid_amount, 0)
	if flt(total_outstanding) >= flt(total_grand):
		return ("Not Paid", total_grand, paid_amount, total_outstanding)
	return ("Partially Paid", total_grand, paid_amount, total_outstanding)


def get_report_summary(data, filters):
	"""KPI cards for the report."""
	total_orders = len(data)
	total_amount = sum(flt(row.get("grand_total")) for row in data)
	total_invoice_amount = sum(flt(row.get("total_invoice_amount")) for row in data)
	paid_amount = sum(flt(row.get("paid_amount")) for row in data)
	open_amount = sum(flt(row.get("open_amount")) for row in data)
	fully_paid = sum(1 for r in data if r.get("payment_status") == "Fully Paid")
	not_paid = sum(1 for r in data if r.get("payment_status") == "Not Paid")
	partial_paid = sum(1 for r in data if r.get("payment_status") == "Partially Paid")
	not_invoiced = sum(1 for r in data if r.get("payment_status") == "Not Invoiced")

	currency = frappe.defaults.get_global_default("currency") or "USD"
	if data:
		currency = data[0].get("currency") or currency

	return [
		{
			"value": total_orders,
			"label": _("Total Delivery Notes"),
			"datatype": "Int",
			"indicator": "Blue",
		},
		{
			"value": total_amount,
			"label": _("Total DN Amount"),
			"datatype": "Currency",
			"currency": currency,
			"indicator": "Green",
		},
		{
			"value": total_invoice_amount,
			"label": _("Total Invoice Amount"),
			"datatype": "Currency",
			"currency": currency,
			"indicator": "Blue",
		},
		{
			"value": paid_amount,
			"label": _("Paid Amount"),
			"datatype": "Currency",
			"currency": currency,
			"indicator": "Green",
		},
		{
			"value": open_amount,
			"label": _("Open Amount"),
			"datatype": "Currency",
			"currency": currency,
			"indicator": "Red" if open_amount else "Green",
		},
		{
			"value": fully_paid,
			"label": _("Fully Paid"),
			"datatype": "Int",
			"indicator": "Green",
		},
		{
			"value": partial_paid,
			"label": _("Partially Paid"),
			"datatype": "Int",
			"indicator": "Orange",
		},
		{
			"value": not_paid,
			"label": _("Not Paid"),
			"datatype": "Int",
			"indicator": "Red",
		},
		{
			"value": not_invoiced,
			"label": _("Not Invoiced"),
			"datatype": "Int",
			"indicator": "Gray",
		},
	]


def get_chart_data(data, filters):
	"""Charts: Orders by shipping company (bar) or Payment status (pie)."""
	if not data:
		return None

	chart_type = filters.get("chart_type") or "shipping_company"

	if chart_type == "payment_status":
		# Pie chart: Payment status breakdown
		payment_counts = {}
		for row in data:
			status = row.get("payment_status") or _("Unknown")
			payment_counts[status] = payment_counts.get(status, 0) + 1
		labels = list(payment_counts.keys())
		values = list(payment_counts.values())
		return {
			"data": {
				"labels": labels,
				"datasets": [{"name": _("Payment Status"), "values": values}],
			},
			"type": "pie",
			"height": 300,
			"colors": ["#26a69a", "#f0932b", "#eb4d4b", "#95a5a6", "#5e64ff"],
		}

	# Bar chart: Orders by Shipping Company (default)
	company_counts = {}
	for row in data:
		company = row.get("shipping_company") or _("Unknown")
		company_counts[company] = company_counts.get(company, 0) + 1
	companies = list(company_counts.keys())[:10]
	company_orders = [company_counts.get(c, 0) for c in companies]
	return {
		"data": {
			"labels": companies,
			"datasets": [
				{"name": _("Orders by Shipping Company"), "values": company_orders},
			],
		},
		"type": "bar",
		"height": 300,
		"colors": ["#5e64ff", "#26a69a", "#f0932b", "#eb4d4b", "#95a5a6"],
		"axisOptions": {"xAxisMode": "tick", "yAxisMode": "tick"},
	}
