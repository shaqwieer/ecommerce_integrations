// Copyright (c) 2026, Shaqwieer and contributors
// For license information, please see license.txt

frappe.query_reports["Shipping Company Orders"] = {
	onload: function (report) {
		report.page.set_title_sub("");
	},
	filters: [
		{
			fieldname: "chart_type",
			label: __("Chart Type"),
			fieldtype: "Select",
			options: [
				{ value: "shipping_company", label: __("By Shipping Company") },
				{ value: "payment_status", label: __("By Payment Status") },
			],
			default: "shipping_company",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
			reqd: 1,
		},
		{
			fieldname: "city",
			label: __("City"),
			fieldtype: "Link",
			options: "City",
		},
		{
			fieldname: "shipping_company",
			label: __("Shipping Company"),
			fieldtype: "Link",
			options: "Shipping Company",
		},
		{
			fieldname: "delivery_note_status",
			label: __("Delivery Note Status"),
			fieldtype: "Select",
			options: [
				{ value: "", label: __("All") },
				{ value: "Submitted", label: __("Submitted") },
				{ value: "Draft", label: __("Draft") },
				{ value: "Cancelled", label: __("Cancelled") },
				{ value: "To Bill", label: __("To Bill") },
			],
			default: "Submitted",
		},
		{
			fieldname: "shipping_status",
			label: __("Shipping Status"),
			fieldtype: "Select",
			options: [
				"",
				"Pending",
				"In Transit",
				"Out for Delivery",
				"Delivered",
				"Returned",
				"Lost",
			],
		},
	],
};
