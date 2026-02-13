// Copyright (c) 2026, Shaqwieer and contributors
// For license information, please see license.txt

frappe.query_reports["Shipping Company Orders"] = {
	onload: function (report) {
		report.page.set_title_sub("");
		// Visually distinguish chart type as "switch chart" (display only) not a filter
		setTimeout(() => {
			const $chart_field = report.page.page_form.find('[data-fieldname="chart_type"]');
			if ($chart_field.length) {
				const $wrapper = $chart_field.closest(".form-group, .frappe-control");
				$wrapper.addClass("chart-switch-field");
				$wrapper
					.find(".control-label, .page-control-label")
					.first()
					.before(
						'<span class="fa fa-line-chart text-muted" style="margin-right: 4px;" title="' +
							__("Display mode — does not filter data") +
							'"></span>'
					);
				$wrapper.css({
					"border-left": "3px solid var(--primary)",
					"padding-left": "8px",
					"margin-top": "8px",
				});
			}
		}, 500);
	},
	filters: [
		{
			fieldname: "is_return",
			label: __("Is Return"),
			fieldtype: "Select",
			options: [
				{ value: "All", label: __("All") },
				{ value: "Return", label: __("Return") },
				{ value: "No Return", label: __("No Return") },
			],
			default: "All",
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
		// {
		// 	fieldname: "shipping_status",
		// 	label: __("Shipping Status"),
		// 	fieldtype: "Select",
		// 	options: [
		// 		"",
		// 		"Pending",
		// 		"In Transit",
		// 		"Out for Delivery",
		// 		"Delivered",
		// 		"Returned",
		// 		"Lost",
		// 	],
		// },
		// Chart view selector — display only, does not filter data
		{
			fieldname: "chart_type",
			label: __("Switch Chart"),
			fieldtype: "Select",
			options: [
				{ value: "shipping_company", label: __("By Shipping Company") },
				{ value: "payment_status", label: __("By Payment Status") },
				{ value: "return_vs_sales", label: __("Return vs Sales") },
				{ value: "amount_by_company", label: __("Amount by Shipping Company") },
			],
			default: "shipping_company",
		},
	],
};
