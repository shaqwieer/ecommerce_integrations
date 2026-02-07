import frappe

from ecommerce_integrations.ecommerce_integrations.doctype.shipping_company.shipping_company import (
	setup_custom_fields_on_begining,
)
from ecommerce_integrations.shopify.constants import SETTING_DOCTYPE


def execute():
	setup_custom_fields_on_begining()
