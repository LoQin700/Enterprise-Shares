# Theme integration

## Included theme files

- `snippets/es-project-product-card.liquid`: global project-style product card
- `snippets/es-product-card-router.liquid`: global enable/disable router
- `snippets/es-product-media.liquid`: video hover playback and second-image hover
- `snippets/es-author-popover.liquid`: author hover card
- `snippets/es-wishlist-button.liquid`: bookmark button
- `sections/es-featured-recommended-products.liquid`: left featured product + right 2×2 paginated recommendations
- `sections/es-wishlist-page.liquid`: dedicated saved-products page
- `sections/es-main-author.liquid`: author page and filtered author products
- `templates/page.enterprise-wishlist.json`: wishlist page template
- `templates/metaobject/project_author.json`: author metaobject template
- `templates/product.es-card.liquid`: card fragment used by the wishlist page

## Global product-card takeover

The repository includes common adapters:

- `snippets/card-product.liquid` for Dawn-style themes
- `snippets/product-card.liquid` for common custom themes
- `snippets/product-card-1.liquid` for themes that use numbered product-card snippets

A Shopify theme can use any snippet name, so true global takeover requires one integration point in the target theme's shared product-card snippet. Use this pattern while preserving the original card as the `else` branch:

```liquid
{% if settings.es_cards_enable %}
  {% render 'es-project-product-card', product: product, variant: 'compact', image_ratio: '16/9' %}
{% else %}
  <!-- Keep the theme's original product-card markup here. -->
{% endif %}
```

Once this shared snippet is connected, Collection pages, featured collections, search results, related products, and other sections that already use the shared snippet are all controlled by the global switch.

## Theme settings

If merging into an existing theme, copy the object from `config/settings_schema.json` into the existing `settings_schema.json` array. Do not replace the theme's existing settings.

## Wishlist page

1. Create a Shopify page named `Saved products` or `Wishlist`.
2. Assign template `page.enterprise-wishlist`.
3. Add the page to the header or account navigation.

Guest customers use `localStorage`. Logged-in customers merge local items with the customer metafield through the app proxy.

## Author pages

1. Create the `project_author` Metaobject definition.
2. Enable Metaobject Web pages.
3. Assign template `metaobject.project_author` if Shopify does not assign it automatically.
4. Create an automated collection for each author and connect it through `projects_collection`.

## Media behavior

- First media is a Shopify-hosted video: muted autoplay starts on card Hover/focus and resets on exit.
- First media is an image: Hover switches to the second product image.
- External video embeds render normally; reliable Hover playback requires provider-specific APIs and is not forced.
