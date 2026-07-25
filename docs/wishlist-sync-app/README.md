# Wishlist sync app

This lightweight app proxy keeps bookmark collections after a customer logs in and across devices.

## What it does

- Verifies Shopify App Proxy signatures.
- Uses `logged_in_customer_id` supplied by Shopify.
- Reads and writes `enterprise_shares.wishlist` on the matching customer.
- Stores a JSON array of product handles.
- Rejects anonymous requests and requests from another shop.

## Shopify setup

1. Create a custom app in the Shopify Dev Dashboard or Partner Dashboard.
2. Grant `read_customers`, `write_customers`, and `write_app_proxy`.
3. Configure the App Proxy:
   - Prefix: `apps`
   - Subpath: `enterprise-wishlist`
   - Proxy URL: `/proxy/wishlist` on the deployed app
4. Create an Admin API access token for the store.
5. Copy `.env.example` to `.env` and set all values.
6. Deploy the Node service to a public HTTPS host.
7. Keep the theme setting `收藏同步 App Proxy 路径` as `/apps/enterprise-wishlist`.

## Run locally

```bash
npm install
npm run dev
```

Node.js 20 or newer is required.

## Data protection

Customer data access can be subject to Shopify protected customer data requirements. Request only the scopes needed for wishlist synchronization and keep the Admin API token server-side.
