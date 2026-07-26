from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly 1 match, found {count}")
    return text.replace(old, new, 1)


# 1) Product template: use carousel and disable zoom.
product_path = ROOT / "templates/product.json"
product = product_path.read_text(encoding="utf-8")
product = replace_once(product, '"media_presentation": "grid"', '"media_presentation": "carousel"', "media presentation")
product = replace_once(product, '"media_columns": "two"', '"media_columns": "one"', "media columns")
product = replace_once(product, '"icons_style": "none"', '"icons_style": "arrow"', "media icons")
product = replace_once(product, '"zoom": true', '"zoom": false', "media zoom")
product_path.write_text(product, encoding="utf-8")


# 2) Product media: eagerly load only the first item and lazy-load the rest.
media_path = ROOT / "snippets/product-media-gallery-content.liquid"
media = media_path.read_text(encoding="utf-8")

old_children = """          {%- liquid
              if needs_both_sizes and forloop.first
                assign media_sizes = sizes_single
              else
                assign media_sizes = sizes
              endif
          -%}
          {% if block_settings.aspect_ratio != 'adapt' and block_settings.constrain_to_viewport %}
            <div
              class=\"product-media-constraint-wrapper\">
              {%- render 'product-media', media: media, sizes: media_sizes, is_main_product_media: forloop.first -%}
            </div>
          {% else %}
            {%- render 'product-media', media: media, sizes: media_sizes, is_main_product_media: forloop.first -%}
          {% endif %}"""

new_children = """          {%- liquid
              if needs_both_sizes and forloop.first
                assign media_sizes = sizes_single
              else
                assign media_sizes = sizes
              endif
              assign media_loading = 'lazy'
              if forloop.first
                assign media_loading = 'eager'
              endif
          -%}
          {% if block_settings.aspect_ratio != 'adapt' and block_settings.constrain_to_viewport %}
            <div
              class=\"product-media-constraint-wrapper\">
              {%- render 'product-media', media: media, sizes: media_sizes, loading: media_loading, is_main_product_media: forloop.first -%}
            </div>
          {% else %}
            {%- render 'product-media', media: media, sizes: media_sizes, loading: media_loading, is_main_product_media: forloop.first -%}
          {% endif %}"""
media = replace_once(media, old_children, new_children, "carousel media loading")

old_grid = """            {%- liquid
              if needs_both_sizes and forloop.first
                assign media_sizes = sizes_single
              else
                assign media_sizes = sizes
              endif
            -%}
            {% if block_settings.aspect_ratio != 'adapt' and block_settings.constrain_to_viewport %}
              <div class=\"product-media-constraint-wrapper\">
                {%- render 'product-media', media: media, sizes: media_sizes, is_main_product_media: forloop.first -%}
              </div>
            {% else %}
              {%- render 'product-media', media: media, sizes: media_sizes, is_main_product_media: forloop.first -%}
            {% endif %}"""

new_grid = """            {%- liquid
              if needs_both_sizes and forloop.first
                assign media_sizes = sizes_single
              else
                assign media_sizes = sizes
              endif
              assign media_loading = 'lazy'
              if forloop.first
                assign media_loading = 'eager'
              endif
            -%}
            {% if block_settings.aspect_ratio != 'adapt' and block_settings.constrain_to_viewport %}
              <div class=\"product-media-constraint-wrapper\">
                {%- render 'product-media', media: media, sizes: media_sizes, loading: media_loading, is_main_product_media: forloop.first -%}
              </div>
            {% else %}
              {%- render 'product-media', media: media, sizes: media_sizes, loading: media_loading, is_main_product_media: forloop.first -%}
            {% endif %}"""
media = replace_once(media, old_grid, new_grid, "grid media loading")
media_path.write_text(media, encoding="utf-8")


# 3) Product tabs: reuse the FAQ parsing done in the first pass.
tabs_path = ROOT / "sections/es-product-project-tabs.liquid"
tabs = tabs_path.read_text(encoding="utf-8")

nav_faq_pattern = re.compile(
    r"(\{%- when 'faq' -%\}\n\s*\{%- liquid\n)"
    r"\s*assign faq_markup = block\.settings\.faq_source\n"
    r"\s*assign faq_serialized = faq_markup \| replace: '</li>', '.*?'\n"
    r"\s*assign faq_items = faq_serialized \| split: '.*?'\n"
    r"\s*assign faq_count = 0\n"
    r"\s*for faq_item in faq_items\n"
    r"\s*assign faq_text = faq_item \| strip_html \| strip\n"
    r"\s*if faq_text != blank\n"
    r"\s*assign faq_count = faq_count \| plus: 1\n"
    r"\s*endif\n"
    r"\s*endfor\n"
    r"(\s*assign tab_id = 'faq-' \| append: block\.id\n\s*-?%\})",
    re.S,
)

tabs, nav_count = nav_faq_pattern.subn(r"\1                  \2", tabs, count=1)
if nav_count != 1:
    raise RuntimeError(f"FAQ nav optimization: expected 1 match, found {nav_count}")

body_faq_pattern = re.compile(
    r"(\{%- when 'faq' -%\}\n\s*\{%- liquid\n)"
    r"\s*assign faq_markup = block\.settings\.faq_source\n"
    r"\s*assign faq_serialized = faq_markup \| replace: '</li>', '.*?'\n"
    r"\s*assign faq_items = faq_serialized \| split: '.*?'\n"
    r"\s*assign faq_count = 0\n"
    r"\s*for faq_item in faq_items\n"
    r"\s*assign faq_text = faq_item \| strip_html \| strip\n"
    r"\s*if faq_text != blank\n"
    r"\s*assign faq_count = faq_count \| plus: 1\n"
    r"\s*endif\n"
    r"\s*endfor\n"
    r"(\s*assign tab_id = 'faq-' \| append: block\.id\n\s*-?%\})",
    re.S,
)

tabs, body_count = body_faq_pattern.subn(r"\1                \2", tabs, count=1)
if body_count != 1:
    raise RuntimeError(f"FAQ body optimization: expected 1 match, found {body_count}")

# Remove author project collection access from the product page.
tabs = tabs.replace("                assign creator_projects = blank\n                assign creator_project_count = 0\n", "", 1)
tabs = tabs.replace("                  assign creator_projects = creator.projects_collection.value\n", "", 1)
collection_logic = """                  if creator_projects != blank
                    if creator_projects.products_count != blank
                      assign creator_project_count = creator_projects.products_count
                    elsif creator_projects.size != blank
                      assign creator_project_count = creator_projects.size
                    endif
                  endif
"""
if collection_logic not in tabs:
    raise RuntimeError("Creator collection logic not found")
tabs = tabs.replace(collection_logic, "", 1)

stats_block = """                      <div class=\"es-project-creator__stats\">
                        <div class=\"es-project-creator__stat\">
                          <strong>{{ creator_project_count }}</strong>
                          <span>{% if creator_project_count == 1 %}created project{% else %}created projects{% endif %}</span>
                        </div>
                        {%- if creator_joined != blank -%}
                          <div class=\"es-project-creator__stat\">
                            <strong>{{ creator_joined | date: '%B %Y' }}</strong>
                            <span>account created</span>
                          </div>
                        {%- endif -%}
                      </div>

"""
if stats_block not in tabs:
    raise RuntimeError("Creator stats block not found")
tabs = tabs.replace(stats_block, "", 1)

tabs_path.write_text(tabs, encoding="utf-8")

print("Product-page performance optimizations applied successfully.")
