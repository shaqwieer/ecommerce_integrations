// Copyright (c) 2021, Frappe and contributors
// For license information, please see LICENSE

frappe.query_reports["Shipping Company Analytics"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "shipping_company",
			label: __("Shipping Company"),
			fieldtype: "Link",
			options: "Shipping Company",
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
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
		},
	],
	onload: function (report) {
		// Add custom formatting
		report.page.add_inner_button(__("Export to Excel"), function () {
			var filters = report.get_filter_values();
			window.open(
				`/api/method/frappe.desk.query_report.export_query?` +
					`report_name=${encodeURIComponent(report.report_name)}&` +
					`file_format_type=Excel&` +
					`filters=${encodeURIComponent(JSON.stringify(filters))}`
			);
		});
	},
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname === "shipping_status") {
			if (value) {
				var color_map = {
					Pending: "#ffa00a",
					"In Transit": "#7cd6fd",
					"Out for Delivery": "#743ee2",
					Delivered: "#28a745",
					Returned: "#dc3545",
					Lost: "#6c757d",
				};
				var color = color_map[value] || "#6c757d";
				value = `<span style="color: ${color}; font-weight: bold;">${value}</span>`;
			}
		}

		if (data.bold) {
			value = `<strong>${value}</strong>`;
		}

		return value;
	},
};

