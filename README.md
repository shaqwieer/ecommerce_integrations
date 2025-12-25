
### Currently supported integrations:

- Shopify - [User documentation](https://docs.erpnext.com/docs/v13/user/manual/en/erpnext_integration/shopify_integration)

### Development setup

- Enable developer mode.
- If you want to use a tunnel for local development. Set `localtunnel_url` parameter in your site_config file with ngrok / localtunnel URL. This will be used in most places to register webhooks. Likewise, use this parameter wherever you're sending current site URL to integrations in development mode.
