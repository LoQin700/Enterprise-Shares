# Enterprise Shares Shopify product-card system

This repository contains a reusable Shopify implementation for:

- A global project-style product card with a theme-level enable switch
- Product metafield names editable in global theme settings
- Deadline countdown calculated from the current time
- Author Metaobject avatar, bio popover, project count, and author page
- First-video Hover playback and second-image Hover switching
- Left featured product plus right 2×2 paginated recommendation carousel
- Bookmark icon in the product-information top-right corner
- A dedicated wishlist page
- Guest browser persistence and logged-in customer cross-device synchronization

## Setup order

1. Read `docs/METAFIELDS.md` and create the product metafields and `project_author` Metaobject.
2. Merge the theme files and settings using `docs/INTEGRATION.md`.
3. Create the wishlist page using `page.enterprise-wishlist`.
4. Deploy `wishlist-sync-app` to enable logged-in account synchronization.

The repository started without an existing Shopify theme, so the shared product-card integration point must be connected once when the target theme is added. The included adapters cover common snippet names.
