// Add Shopify Excel import button to Sales Order form
frappe.ui.form.on('Sales Order', {
	refresh(frm) {
		// if (!frm.client) return;
		
		frm.add_custom_button(__('Import Shopify Customers'), function() {
			const d = new frappe.ui.Dialog({
				title: __('Import Shopify Customer Data (Excel)'),
				fields: [
					{ fieldname: 'file', fieldtype: 'Attach', label: __('Excel File (.xlsx or .csv)'), reqd: true },
				],
				primary_action_label: __('Upload & Sync'),
				primary_action(values) {
					d.hide();
					frappe.show_progress(__('Syncing customers'), 0, 0, __('Uploading file'));
					frappe.call({
						method: 'ecommerce_integrations.ecommerce_integrations.controllers.shopify_sync.sync_customers_from_excel',
						args: { file_url: values.file },
						freeze: true,
						callback(r) {
							frappe.hide_progress();
							if (r.exc) {
								frappe.msgprint({
									title: __('Error'),
									message: r.exc,
									indicator: 'red'
								});
								return;
							}
							const data = r.message || {};
							let msg = __('Sync complete. Updated {0} orders.', [data.updated || 0]);
							if (data.skipped) msg += ' ' + __('Skipped {0} rows.', [data.skipped]);
							frappe.msgprint(msg);
							if (data.errors && data.errors.length) {
								const details = data.errors.slice(0, 10).map(e => `${e.row}: ${e.error}`).join('\n');
								frappe.msgprint({title: __('Some rows failed'), message: details, indicator: 'orange'});
							}
						}
					});
				}
			});
			d.show();
		});
	}
});
