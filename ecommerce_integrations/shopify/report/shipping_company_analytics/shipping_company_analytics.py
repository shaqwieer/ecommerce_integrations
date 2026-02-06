# Copyright (c) 2026, Shaqwieer and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, today, date_diff


from ecommerce_integrations.shopify.constants import SHIPPING_COMPANY_FIELD, SHIPPING_STATUS_FIELD


def execute(filters=None):
	return ShippingCompanyAnalytics(filters).run()


class ShippingCompanyAnalytics:
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})

	def run(self):
		self.get_columns()
		self.get_data()
		self.get_report_summary()
		self.get_chart_data()

		return self.columns, self.data, None, self.chart, self.report_summary

	# ──────────────────────────────────────────────
	# Columns
	# ──────────────────────────────────────────────
	def get_columns(self):
		self.columns = [
			{
				"label": _("Delivery Note"),
				"fieldname": "delivery_note",
				"fieldtype": "Link",
				"options": "Delivery Note",
				"width": 180,
			},
			{
				"label": _("Posting Date"),
				"fieldname": "posting_date",
				"fieldtype": "Date",
				"width": 110,
			},
			{
				"label": _("Customer"),
				"fieldname": "customer",
				"fieldtype": "Link",
				"options": "Customer",
				"width": 150,
			},
			{
				"label": _("Status"),
				"fieldname": "status",
				"fieldtype": "Data",
				"width": 100,
			},
			{
				"label": _("Shipping Status"),
				"fieldname": "shipping_status",
				"fieldtype": "Data",
				"width": 120,
			},
			{
				"label": _("COD Amount"),
				"fieldname": "cod_amount",
				"fieldtype": "Currency",
				"width": 130,
			},
			{
				"label": _("Amount Received"),
				"fieldname": "amount_received",
				"fieldtype": "Currency",
				"width": 140,
			},
			{
				"label": _("Advance Offset"),
				"fieldname": "advance_offset",
				"fieldtype": "Currency",
				"width": 140,
			},
			{
				"label": _("Outstanding Balance"),
				"fieldname": "outstanding_balance",
				"fieldtype": "Currency",
				"width": 150,
			},
			{
				"label": _("Aging (Days)"),
				"fieldname": "aging",
				"fieldtype": "Int",
				"width": 100,
			},
		]

	# ──────────────────────────────────────────────
	# Data
	# ──────────────────────────────────────────────
	def get_data(self):
		conditions = self._build_conditions()

		self.delivery_notes = frappe.db.sql(
			f"""
			SELECT
				dn.name          AS delivery_note,
				dn.posting_date,
				dn.customer,
				dn.status,
				dn.`{SHIPPING_COMPANY_FIELD}` AS shipping_company,
				dn.`{SHIPPING_STATUS_FIELD}` AS shipping_status,
				dn.grand_total   AS cod_amount
			FROM `tabDelivery Note` dn
			WHERE dn.docstatus = 1
				AND IFNULL(dn.`{SHIPPING_COMPANY_FIELD}`, '') != ''
				{conditions}
			ORDER BY dn.posting_date DESC
			""",
			self.filters,
			as_dict=True,
		)

		if not self.delivery_notes:
			self.data = []
			return

		dn_names = [d.delivery_note for d in self.delivery_notes]
		shipping_companies = list({d.shipping_company for d in self.delivery_notes})

		# Look-ups
		amount_received_map = self._get_amount_received(dn_names)
		advance_offset_map = self._get_advance_offsets(shipping_companies)

		# Assemble rows
		self.data = []
		for dn in self.delivery_notes:
			amount_received = flt(amount_received_map.get(dn.delivery_note, 0))
			advance_offset = flt(advance_offset_map.get(dn.shipping_company, 0))
			outstanding = flt(dn.cod_amount) - amount_received

			# Aging: days since posting for Delivered but unpaid notes
			aging = 0
			if dn.shipping_status == "Delivered" and outstanding > 0:
				aging = date_diff(today(), getdate(dn.posting_date))

			row = frappe._dict(
				delivery_note=dn.delivery_note,
				posting_date=dn.posting_date,
				customer=dn.customer,
				status=dn.status,
				shipping_status=dn.shipping_status,
				cod_amount=dn.cod_amount,
				amount_received=amount_received,
				advance_offset=advance_offset,
				outstanding_balance=outstanding,
				aging=aging,
				shipping_company=dn.shipping_company,
			)

			# ── Settlement Status filter (post-calculation) ──
			settlement = self.filters.get("settlement_status")
			if settlement and settlement != "All":
				if settlement == "Pending" and amount_received > 0:
					continue
				if settlement == "Partially Paid" and not (
					0 < amount_received < flt(dn.cod_amount)
				):
					continue
				if settlement == "Fully Paid" and outstanding > 0:
					continue

			self.data.append(row)

	# ──────────────────────────────────────────────
	# Amount Received  (DN → SI → PE Receive)
	# ──────────────────────────────────────────────
	def _get_amount_received(self, dn_names):
		"""Sum of PE (Receive) amounts linked to each DN via Sales Invoice."""
		if not dn_names:
			return {}

		placeholders = ", ".join(["%s"] * len(dn_names))

		# 1. DN → SI mapping with proportional amounts
		dn_si_data = frappe.db.sql(
			f"""
			SELECT
				sii.delivery_note,
				sii.parent        AS sales_invoice,
				SUM(sii.amount)   AS dn_share_amount,
				si.grand_total    AS si_total
			FROM `tabSales Invoice Item` sii
			INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
			WHERE sii.delivery_note IN ({placeholders})
				AND si.docstatus = 1
			GROUP BY sii.delivery_note, sii.parent
			""",
			dn_names,
			as_dict=True,
		)

		if not dn_si_data:
			return {}

		si_names = list({d.sales_invoice for d in dn_si_data})
		si_placeholders = ", ".join(["%s"] * len(si_names))

		# 2. PE allocated amounts per SI
		pe_data = frappe.db.sql(
			f"""
			SELECT
				per.reference_name      AS sales_invoice,
				SUM(per.allocated_amount) AS total_allocated
			FROM `tabPayment Entry Reference` per
			INNER JOIN `tabPayment Entry` pe ON pe.name = per.parent
			WHERE pe.docstatus = 1
				AND pe.payment_type = 'Receive'
				AND per.reference_doctype = 'Sales Invoice'
				AND per.reference_name IN ({si_placeholders})
			GROUP BY per.reference_name
			""",
			si_names,
			as_dict=True,
		)

		pe_map = {r.sales_invoice: flt(r.total_allocated) for r in pe_data}

		# 3. Distribute PE amount to DNs proportionally
		dn_amount_map = {}
		for row in dn_si_data:
			pe_amount = pe_map.get(row.sales_invoice, 0)
			if pe_amount and flt(row.si_total):
				proportion = flt(row.dn_share_amount) / flt(row.si_total)
				dn_amount_map[row.delivery_note] = (
					dn_amount_map.get(row.delivery_note, 0) + pe_amount * proportion
				)

		return dn_amount_map

	# ──────────────────────────────────────────────
	# Advance Offsets  (Internal Transfer from Wallet)
	# ──────────────────────────────────────────────
	def _get_advance_offsets(self, shipping_companies):
		"""Total Internal-Transfer PEs debiting each Shipping Company's wallet."""
		if not shipping_companies:
			return {}

		wallet_accounts = {}
		for sc in shipping_companies:
			account = frappe.db.get_value("Shipping Company", sc, "account")
			if account:
				wallet_accounts[account] = sc

		if not wallet_accounts:
			return {}

		account_list = list(wallet_accounts.keys())
		placeholders = ", ".join(["%s"] * len(account_list))

		result = frappe.db.sql(
			f"""
			SELECT
				pe.paid_from          AS wallet_account,
				SUM(pe.paid_amount)   AS total_advance
			FROM `tabPayment Entry` pe
			WHERE pe.docstatus = 1
				AND pe.payment_type = 'Internal Transfer'
				AND pe.paid_from IN ({placeholders})
			GROUP BY pe.paid_from
			""",
			account_list,
			as_dict=True,
		)

		return {
			wallet_accounts[r.wallet_account]: flt(r.total_advance)
			for r in result
			if r.wallet_account in wallet_accounts
		}

	# ──────────────────────────────────────────────
	# Wallet Balance  (GL Entry balance)
	# ──────────────────────────────────────────────
	def _get_wallet_balance(self):
		"""Current balance of the Shipping Company wallet account(s)."""
		if self.filters.get("shipping_company"):
			account = frappe.db.get_value(
				"Shipping Company", self.filters.shipping_company, "account"
			)
			accounts = [account] if account else []
		else:
			accounts = [
				a.account
				for a in frappe.get_all("Shipping Company", fields=["account"])
				if a.account
			]

		if not accounts:
			return 0

		placeholders = ", ".join(["%s"] * len(accounts))
		result = frappe.db.sql(
			f"""
			SELECT IFNULL(SUM(debit - credit), 0) AS balance
			FROM `tabGL Entry`
			WHERE account IN ({placeholders})
				AND is_cancelled = 0
			""",
			accounts,
		)

		return flt(result[0][0]) if result else 0

	# ──────────────────────────────────────────────
	# KPI Summary Ribbon
	# ──────────────────────────────────────────────
	def get_report_summary(self):
		if not self.data:
			self.report_summary = []
			return

		total_notes = len(self.data)
		delivered_notes = sum(
			1 for d in self.data if d.get("shipping_status") == "Delivered"
		)
		success_rate = (delivered_notes / total_notes * 100) if total_notes else 0

		total_exposure = sum(
			flt(d.cod_amount)
			for d in self.data
			if flt(d.outstanding_balance) > 0
		)

		pending_remittance = sum(
			flt(d.outstanding_balance)
			for d in self.data
			if d.shipping_status == "Delivered" and flt(d.outstanding_balance) > 0
		)

		wallet_balance = self._get_wallet_balance()

		self.report_summary = [
			{
				"value": total_exposure,
				"indicator": "Red" if total_exposure > 0 else "Green",
				"label": _("Total Exposure"),
				"datatype": "Currency",
			},
			{
				"value": wallet_balance,
				"indicator": "Blue",
				"label": _("Wallet Balance"),
				"datatype": "Currency",
			},
			{
				"value": flt(success_rate, 1),
				"indicator": "Green" if success_rate >= 80 else "Orange",
				"label": _("Success Rate %"),
				"datatype": "Percent",
			},
			{
				"value": pending_remittance,
				"indicator": "Orange" if pending_remittance > 0 else "Green",
				"label": _("Pending Remittance"),
				"datatype": "Currency",
			},
		]

	# ──────────────────────────────────────────────
	# Chart
	# ──────────────────────────────────────────────
	def get_chart_data(self):
		if not self.data:
			self.chart = None
			return

		status_outstanding = {}
		for row in self.data:
			status = row.get("shipping_status") or _("Not Set")
			status_outstanding[status] = (
				status_outstanding.get(status, 0) + flt(row.outstanding_balance)
			)

		self.chart = {
			"data": {
				"labels": list(status_outstanding.keys()),
				"datasets": [
					{
						"name": _("Outstanding Balance"),
						"values": list(status_outstanding.values()),
					}
				],
			},
			"type": "bar",
			"colors": ["#fc4f51"],
		}

	# ──────────────────────────────────────────────
	# SQL condition builder
	# ──────────────────────────────────────────────
	def _build_conditions(self):
		conds = []

		if self.filters.get("from_date"):
			conds.append("dn.posting_date >= %(from_date)s")

		if self.filters.get("to_date"):
			conds.append("dn.posting_date <= %(to_date)s")

		if self.filters.get("shipping_company"):
			conds.append(
				f"dn.`{SHIPPING_COMPANY_FIELD}` = %(shipping_company)s"
			)

		return (" AND " + " AND ".join(conds)) if conds else ""
