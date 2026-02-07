// Copyright (c) 2026, Shaqwieer and contributors
// For license information, please see license.txt

frappe.query_reports["Shipping Company Analytics"] = {
	filters: [
		{
			fieldname: "shipping_company",
			label: __("Shipping Company"),
			fieldtype: "Link",
			options: "Shipping Company",
			width: 200,
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			width: 120,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			width: 120,
		},
		{
			fieldname: "settlement_status",
			label: __("Settlement Status"),
			fieldtype: "Select",
			options: ["All", "Pending", "Partially Paid", "Fully Paid"],
			default: "All",
			width: 120,
		},
		{
			fieldname: "city",
			label: __("City"),
			fieldtype: "Link",
			options: "City",
			width: 120,
		},
	],
};
