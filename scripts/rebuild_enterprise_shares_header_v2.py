import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NATIVE_REF = "3223fe342a7be1186de21fc871e671a43c4b30df"


def git_show(path: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"{NATIVE_REF}:{path}"],
        cwd=ROOT,
        text=True,
    )


def read_json_with_preamble(path: Path):
    text = path.read_text(encoding="utf-8")
    start = text.find("{")
    return text[:start], json.loads(text[start:])


def write_json_with_preamble(path: Path, preamble: str, data) -> None:
    path.write_text(
        preamble + json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


CUSTOM_HEADER = r'''{%- liquid
  assign header_menu = section.settings.menu
  assign header_logo = section.settings.logo
  if header_logo == blank
    assign header_logo = settings.logo
  endif
-%}

<div class="section-background color-{{ section.settings.color_scheme }}"></div>
<section
  id="EnterpriseSharesHeader-{{ section.id }}"
  class="esh color-{{ section.settings.color_scheme }}{% if section.settings.sticky_header %} esh--sticky{% endif %}"
  style="--esh-search-width: {{ section.settings.search_max_width }}px; --esh-logo-width: {{ section.settings.logo_width }}px; --esh-logo-width-mobile: {{ section.settings.logo_width_mobile }}px; --esh-mobile-menu-size: {{ section.settings.mobile_menu_font_size }}px; --esh-padding-y: {{ section.settings.padding_y }}px;"
>
  <div class="esh__top section section--{{ section.settings.section_width }}">
    <details class="esh__mobile-menu">
      <summary class="esh__icon-button" aria-label="Open menu">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
      </summary>
      <div class="esh__mobile-panel color-{{ section.settings.menu_color_scheme }}">
        <nav aria-label="Mobile navigation">
          <ul class="esh__mobile-list" role="list">
            {%- for link in header_menu.links -%}
              <li>
                {%- if link.links != blank -%}
                  <details>
                    <summary class="esh__mobile-link esh__mobile-link--parent">
                      <span>{{ link.title }}</span>
                      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 7 7-7 7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    </summary>
                    <ul class="esh__mobile-submenu" role="list">
                      <li><a href="{{ link.url }}">{{ link.title }}</a></li>
                      {%- for child_link in link.links -%}
                        <li><a href="{{ child_link.url }}">{{ child_link.title }}</a></li>
                      {%- endfor -%}
                    </ul>
                  </details>
                {%- else -%}
                  <a class="esh__mobile-link" href="{{ link.url }}">{{ link.title }}</a>
                {%- endif -%}
              </li>
            {%- endfor -%}
          </ul>
        </nav>
      </div>
    </details>

    <a class="esh__logo" href="{{ routes.root_url }}" aria-label="{{ shop.name | escape }}">
      {%- if header_logo != blank -%}
        {{ header_logo | image_url: width: 600 | image_tag: loading: 'eager', widths: '120,180,240,360,480,600', alt: shop.name }}
      {%- else -%}
        <span>{{ shop.name }}</span>
      {%- endif -%}
    </a>

    {%- if section.settings.show_search -%}
      <search-button class="esh__search">
        <button type="button" class="esh__search-button" on:click="#search-modal/showDialog" aria-label="{{ section.settings.search_placeholder | escape }}" aria-haspopup="dialog">
          <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="m16.5 16.5 4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
          <span>{{ section.settings.search_placeholder }}</span>
        </button>
      </search-button>
      <search-button class="esh__mobile-search">
        <button type="button" class="esh__icon-button" on:click="#search-modal/showDialog" aria-label="{{ section.settings.search_placeholder | escape }}" aria-haspopup="dialog">
          <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="m16.5 16.5 4 4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
        </button>
      </search-button>
    {%- endif -%}

    <div class="esh__actions">
      {% render 'header-actions', display_style: 'icon', section: section %}
    </div>
  </div>

  <div class="esh__nav-row color-{{ section.settings.menu_color_scheme }}">
    <nav class="esh__nav section section--{{ section.settings.section_width }}" aria-label="Primary navigation">
      <ul class="esh__nav-list" role="list">
        {%- for link in header_menu.links -%}
          {%- liquid
            assign menu_position = forloop.index
            assign link_key = link.title | strip | downcase
            assign mega_block = blank

            for block in section.blocks
              assign block_key = block.settings.menu_title | strip | downcase
              if block_key != blank and block_key == link_key
                assign mega_block = block
                break
              endif
            endfor

            if mega_block == blank
              for block in section.blocks
                if block.settings.menu_title == blank and forloop.index == menu_position
                  assign mega_block = block
                  break
                endif
              endfor
            endif

            assign featured_product = blank
            if mega_block != blank and mega_block.settings.show_featured
              assign featured_product = mega_block.settings.product
            endif
          -%}
          <li class="esh__nav-item{% if link.links != blank or featured_product != blank %} esh__nav-item--mega{% endif %}">
            <a class="esh__nav-link" href="{{ link.url }}">{{ link.title }}</a>
            {%- if link.links != blank or featured_product != blank -%}
              <div class="esh__mega color-{{ section.settings.menu_color_scheme }}">
                <div class="esh__mega-inner section section--{{ section.settings.section_width }}">
                  <div class="esh__mega-categories">
                    <a class="esh__mega-title" href="{{ link.url }}">
                      <span>{{ link.title }}</span>
                      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 5 7 7-7 7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    </a>
                    {%- if link.links != blank -%}
                      <div class="esh__mega-links">
                        {%- for child_link in link.links -%}
                          <a href="{{ child_link.url }}">{{ child_link.title }}</a>
                        {%- endfor -%}
                      </div>
                    {%- endif -%}
                  </div>
                  {%- if featured_product != blank -%}
                    <aside class="esh__mega-featured" {{ mega_block.shopify_attributes }}>
                      <div class="esh__mega-label">{{ mega_block.settings.label | default: 'Featured project' }}</div>
                      {% render 'es-project-product-card', product: featured_product, variant: 'mega', image_ratio: settings.es_card_ratio | default: '16/9' %}
                    </aside>
                  {%- endif -%}
                </div>
              </div>
            {%- endif -%}
          </li>
        {%- endfor -%}
      </ul>
    </nav>
  </div>
</section>

{% stylesheet %}
  .esh { position: relative; z-index: 40; width: 100%; font-family: var(--font-body--family); background: var(--color-background); }
  .esh--sticky { position: sticky; top: 0; }
  .esh__top { display: grid; grid-template-columns: max-content minmax(280px, var(--esh-search-width)) max-content; align-items: center; justify-content: space-between; gap: 28px; min-height: 82px; padding-block: var(--esh-padding-y); }
  .esh__logo { display: inline-flex; width: min(var(--esh-logo-width), 100%); align-items: center; color: var(--color-foreground-heading); font-family: var(--font-heading--family); font-size: 1.45rem; font-weight: var(--font-heading--weight); line-height: 1; text-decoration: none; }
  .esh__logo img { display: block; width: 100%; height: auto; }
  .esh__search { display: flex; width: 100%; }
  .esh__search-button { display: flex; width: 100%; min-height: 54px; align-items: center; gap: 14px; padding: 0 18px; border: 1px solid var(--color-border); border-radius: var(--style-border-radius-inputs, 8px); color: rgb(var(--color-foreground-rgb) / 0.6); background: var(--color-background); box-shadow: 0 8px 22px rgb(var(--color-shadow-rgb) / 0.08); font: inherit; text-align: left; cursor: text; }
  .esh__search-button svg, .esh__icon-button svg, .esh__mobile-link svg, .esh__mega-title svg { width: 22px; height: 22px; flex: 0 0 auto; }
  .esh__search-button span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .esh__actions { display: flex; align-items: center; justify-content: flex-end; }
  .esh__nav-row { position: relative; border-top: 1px solid var(--color-border); border-bottom: 1px solid var(--color-border); background: var(--color-background); }
  .esh__nav { position: relative; }
  .esh__nav-list { display: flex; align-items: center; justify-content: center; gap: 24px; min-height: 56px; margin: 0; padding: 0; list-style: none; }
  .esh__nav-item { position: static; }
  .esh__nav-link { display: inline-flex; align-items: center; min-height: 56px; color: var(--color-foreground); font-size: 1rem; line-height: 1; text-decoration: none; white-space: nowrap; }
  .esh__nav-link:hover, .esh__nav-link:focus-visible, .esh__nav-item:focus-within > .esh__nav-link { color: var(--color-primary); text-decoration: underline; text-underline-offset: 5px; }
  .esh__mega { position: absolute; top: 100%; right: 0; left: 0; z-index: 60; visibility: hidden; border-bottom: 1px solid var(--color-border); background: var(--color-background); box-shadow: 0 16px 28px rgb(var(--color-shadow-rgb) / 0.1); opacity: 0; transform: translateY(6px); transition: opacity 160ms ease, transform 160ms ease, visibility 160ms ease; }
  .esh__nav-item:hover .esh__mega, .esh__nav-item:focus-within .esh__mega { visibility: visible; opacity: 1; transform: translateY(0); }
  .esh__mega-inner { display: grid; grid-template-columns: minmax(0, 1fr) minmax(280px, 34%); gap: 48px; padding-block: 30px 36px; }
  .esh__mega-categories { min-width: 0; padding-right: 44px; border-right: 1px solid var(--color-border); }
  .esh__mega-title { display: inline-flex; align-items: center; gap: 8px; margin-bottom: 24px; color: var(--color-foreground-heading); font-family: var(--font-heading--family); font-size: 1.55rem; font-weight: var(--font-heading--weight); line-height: 1.2; text-decoration: none; }
  .esh__mega-links { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px 28px; }
  .esh__mega-links a { color: var(--color-foreground); font-size: 1rem; line-height: 1.35; text-decoration: none; }
  .esh__mega-links a:hover, .esh__mega-links a:focus-visible { color: var(--color-primary); }
  .esh__mega-featured { min-width: 0; }
  .esh__mega-label { margin-bottom: 16px; color: rgb(var(--color-foreground-rgb) / 0.68); font-size: 1rem; }
  .esh__mega-featured .es-card__description, .esh__mega-featured .es-card__chips, .esh__mega-featured .es-card__extra { display: none !important; }
  .esh__mobile-menu, .esh__mobile-search { display: none; }
  .esh__icon-button { display: inline-flex; width: 42px; height: 42px; align-items: center; justify-content: center; padding: 0; border: 0; color: var(--color-foreground); background: transparent; cursor: pointer; }

  @media screen and (max-width: 989px) and (min-width: 750px) {
    .esh__top { grid-template-columns: max-content minmax(240px, 1fr) max-content; gap: 18px; }
    .esh__mega-inner { grid-template-columns: minmax(0, 1fr) 280px; gap: 28px; }
    .esh__mega-links { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  }

  @media screen and (max-width: 749px) {
    .esh__top { display: flex; min-height: 64px; gap: 6px; padding-block: 8px; }
    .esh__mobile-menu { display: block; order: 1; }
    .esh__logo { order: 2; width: min(var(--esh-logo-width-mobile), 100%); margin-right: auto; }
    .esh__search, .esh__nav-row { display: none; }
    .esh__mobile-search { display: block; order: 3; }
    .esh__actions { order: 4; }
    .esh__mobile-menu > summary, .esh__mobile-link--parent { list-style: none; }
    .esh__mobile-menu > summary::-webkit-details-marker, .esh__mobile-link--parent::-webkit-details-marker { display: none; }
    .esh__mobile-panel { position: absolute; top: 100%; right: 0; left: 0; z-index: 80; max-height: calc(100vh - 64px); overflow-y: auto; border-top: 1px solid var(--color-border); border-bottom: 1px solid var(--color-border); background: var(--color-background); box-shadow: 0 14px 30px rgb(var(--color-shadow-rgb) / 0.12); }
    .esh__mobile-list, .esh__mobile-submenu { margin: 0; padding: 0; list-style: none; }
    .esh__mobile-list { padding: 12px 20px 24px; }
    .esh__mobile-link, .esh__mobile-submenu a { display: flex; width: 100%; align-items: center; justify-content: space-between; padding: 14px 0; color: var(--color-foreground); font-family: var(--font-body--family); font-size: var(--esh-mobile-menu-size); line-height: 1.3; text-decoration: none; }
    .esh__mobile-link--parent { cursor: pointer; }
    .esh__mobile-submenu { padding: 0 0 8px 18px; }
    .esh__mobile-submenu a { padding-block: 10px; font-size: calc(var(--esh-mobile-menu-size) - 1px); opacity: 0.82; }
  }
{% endstylesheet %}

{% schema %}
{
  "name": "Enterprise Shares Header",
  "tag": "section",
  "class": "section-enterprise-shares-header",
  "limit": 1,
  "enabled_on": { "groups": ["header"] },
  "settings": [
    { "type": "image_picker", "id": "logo", "label": "Logo" },
    { "type": "range", "id": "logo_width", "label": "电脑端 Logo 宽度", "min": 80, "max": 280, "step": 10, "unit": "px", "default": 180 },
    { "type": "range", "id": "logo_width_mobile", "label": "手机端 Logo 宽度", "min": 70, "max": 200, "step": 10, "unit": "px", "default": 120 },
    { "type": "link_list", "id": "menu", "label": "主菜单", "default": "main-menu" },
    { "type": "color_scheme", "id": "color_scheme", "label": "顶部颜色方案", "default": "scheme-1" },
    { "type": "color_scheme", "id": "menu_color_scheme", "label": "菜单和 Mega Menu 颜色方案", "default": "scheme-1" },
    { "type": "select", "id": "section_width", "label": "内容宽度", "default": "page-width", "options": [{ "value": "page-width", "label": "页面宽度" }, { "value": "full-width", "label": "全宽" }] },
    { "type": "checkbox", "id": "show_search", "label": "显示完整搜索框", "default": true },
    { "type": "text", "id": "search_placeholder", "label": "搜索框预设文案", "default": "Search projects, creators, and categories" },
    { "type": "range", "id": "search_max_width", "label": "搜索框最大宽度", "min": 360, "max": 1000, "step": 20, "unit": "px", "default": 840 },
    { "type": "range", "id": "mobile_menu_font_size", "label": "手机端菜单字号", "min": 12, "max": 24, "step": 1, "unit": "px", "default": 16 },
    { "type": "range", "id": "padding_y", "label": "顶部栏上下内间距", "min": 8, "max": 32, "step": 2, "unit": "px", "default": 16 },
    { "type": "checkbox", "id": "sticky_header", "label": "启用 Sticky Header", "default": true }
  ],
  "blocks": [
    {
      "type": "mega_menu",
      "name": "一级菜单推荐项目",
      "settings": [
        { "type": "text", "id": "menu_title", "label": "对应一级菜单名称", "info": "填写与主菜单完全一致的名称；留空时按 Block 顺序匹配一级菜单。" },
        { "type": "checkbox", "id": "show_featured", "label": "显示推荐项目", "default": true },
        { "type": "text", "id": "label", "label": "推荐项目标题", "default": "Featured project" },
        { "type": "product", "id": "product", "label": "推荐产品" }
      ]
    }
  ],
  "max_blocks": 20,
  "presets": [{ "name": "Enterprise Shares Header" }]
}
{% endschema %}
'''


def restore_native_header() -> None:
    (ROOT / "sections/header.liquid").write_text(git_show("sections/header.liquid"), encoding="utf-8")
    (ROOT / "blocks/_header-menu.liquid").write_text(git_show("blocks/_header-menu.liquid"), encoding="utf-8")


def create_custom_header() -> None:
    (ROOT / "sections/enterprise-shares-header.liquid").write_text(CUSTOM_HEADER, encoding="utf-8")


def patch_header_group() -> None:
    native = git_show("sections/header-group.json")
    start = native.find("{")
    preamble = native[:start]
    group = json.loads(native[start:])

    blocks = {}
    block_order = []
    for index in range(1, 4):
        block_id = f"enterprise_mega_{index}"
        blocks[block_id] = {
            "type": "mega_menu",
            "settings": {
                "menu_title": "",
                "show_featured": True,
                "label": "Featured project",
                "product": "",
            },
        }
        block_order.append(block_id)

    custom_id = "enterprise_shares_header"
    group["sections"][custom_id] = {
        "type": "enterprise-shares-header",
        "blocks": blocks,
        "block_order": block_order,
        "name": "Enterprise Shares Header",
        "settings": {
            "logo_width": 180,
            "logo_width_mobile": 120,
            "menu": "main-menu",
            "color_scheme": "scheme-1",
            "menu_color_scheme": "scheme-1",
            "section_width": "page-width",
            "show_search": True,
            "search_placeholder": "Search projects, creators, and categories",
            "search_max_width": 840,
            "mobile_menu_font_size": 16,
            "padding_y": 16,
            "sticky_header": True,
        },
    }

    group["order"] = [item for item in group.get("order", []) if item != "header_section"] + [custom_id]
    write_json_with_preamble(ROOT / "sections/header-group.json", preamble, group)


def patch_product_card_schema() -> None:
    path = ROOT / "config/settings_schema.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    card_group = next(item for item in data if item.get("name") == "全局产品卡")
    settings = card_group["settings"]

    added_ids = {
        "es_media_accent_color",
        "es_card_content_padding_y",
        "es_card_content_padding_y_mobile",
    }
    settings[:] = [item for item in settings if item.get("id") not in added_ids]

    height_index = next(i for i, item in enumerate(settings) if item.get("id") == "es_media_accent_height")
    settings.insert(
        height_index + 1,
        {
            "type": "color",
            "id": "es_media_accent_color",
            "label": "图片底部主题色条颜色",
            "default": "#00c875",
        },
    )

    size_index = next(i for i, item in enumerate(settings) if item.get("id") == "es_card_description_size")
    settings[size_index + 1:size_index + 1] = [
        {
            "type": "range",
            "id": "es_card_content_padding_y",
            "label": "产品卡内容上下内间距",
            "min": 12,
            "max": 32,
            "step": 1,
            "unit": "px",
            "default": 20,
        },
        {
            "type": "range",
            "id": "es_card_content_padding_y_mobile",
            "label": "手机端产品卡内容上下内间距",
            "min": 8,
            "max": 24,
            "step": 1,
            "unit": "px",
            "default": 14,
        },
    ]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def patch_settings_data() -> None:
    path = ROOT / "config/settings_data.json"
    preamble, data = read_json_with_preamble(path)
    current = data.setdefault("current", {})
    current.update(
        {
            "es_media_accent_enable": current.get("es_media_accent_enable", True),
            "es_media_accent_height": current.get("es_media_accent_height", 6),
            "es_media_accent_color": current.get("es_media_accent_color", "#00c875"),
            "es_card_content_padding_y": current.get("es_card_content_padding_y", 20),
            "es_card_content_padding_y_mobile": current.get("es_card_content_padding_y_mobile", 14),
        }
    )
    write_json_with_preamble(path, preamble, data)


def patch_runtime_variables() -> None:
    path = ROOT / "snippets/es-wishlist-bootstrap.liquid"
    text = path.read_text(encoding="utf-8")
    anchor = "    --es-media-accent-height: {% if settings.es_media_accent_enable == false %}0px{% else %}{{ settings.es_media_accent_height | default: 6 }}px{% endif %};"
    replacement = anchor + "\n" + "    --es-media-accent-color: {{ settings.es_media_accent_color | default: '#00c875' }};\n" + "    --es-card-content-padding-y: {{ settings.es_card_content_padding_y | default: 20 }}px;\n" + "    --es-card-content-padding-y-mobile: {{ settings.es_card_content_padding_y_mobile | default: 14 }}px;"
    if "--es-media-accent-color:" in text:
        lines = [line for line in text.splitlines() if "--es-media-accent-color:" not in line and "--es-card-content-padding-y:" not in line and "--es-card-content-padding-y-mobile:" not in line]
        text = "\n".join(lines) + "\n"
    if anchor not in text:
        raise RuntimeError("Runtime variable anchor not found")
    path.write_text(text.replace(anchor, replacement, 1), encoding="utf-8")


def patch_product_card_css() -> None:
    path = ROOT / "assets/es-project-card-overrides.css"
    css = path.read_text(encoding="utf-8")
    marker = "/* ES 20260726 card frame and media accent */"
    if marker in css:
        css = css.split(marker)[0].rstrip() + "\n\n"
    css += r'''/* ES 20260726 card frame and media accent */
.es-card {
  border: 1px solid transparent;
  border-radius: 10px;
  overflow: visible;
  background: var(--color-background);
  box-shadow: none;
}

.es-card:hover,
.es-card:focus-within {
  border-color: var(--color-border);
  box-shadow: none;
}

.es-card__media {
  width: calc(100% - 10px);
  margin: 5px 5px 0;
  border-radius: 8px;
}

.es-card__media-link {
  position: relative;
  overflow: hidden;
  border-radius: inherit;
}

.es-card__media-link::after {
  content: '';
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 20;
  display: block;
  height: var(--es-media-accent-height, 6px);
  border-radius: 0 0 8px 8px;
  background-color: var(--es-media-accent-color, #00c875);
  pointer-events: none;
}

.es-card__content {
  padding-top: var(--es-card-content-padding-y, 20px);
  padding-bottom: var(--es-card-content-padding-y, 20px);
}

.es-featured-section .es-slider-arrow,
.es-featured-section .es-slider-arrow:hover:not(:disabled),
.es-featured-section .es-slider-arrow:focus-visible:not(:disabled),
.es-featured-section .es-slider-arrow:disabled,
.es-product-carousel .es-slider-arrow,
.es-product-carousel .es-slider-arrow:hover:not(:disabled),
.es-product-carousel .es-slider-arrow:focus-visible:not(:disabled),
.es-product-carousel .es-slider-arrow:disabled {
  width: 28px !important;
  height: 28px !important;
  padding: 0 !important;
  border: 0 !important;
  border-radius: 0 !important;
  color: var(--color-primary) !important;
  background: transparent !important;
  box-shadow: none !important;
}

.es-featured-section .es-slider-arrow:hover:not(:disabled),
.es-featured-section .es-slider-arrow:focus-visible:not(:disabled),
.es-product-carousel .es-slider-arrow:hover:not(:disabled),
.es-product-carousel .es-slider-arrow:focus-visible:not(:disabled) {
  color: var(--color-primary-hover) !important;
}

@media screen and (max-width: 749px) {
  .es-card__content,
  .es-recommended-mobile .es-card__content {
    padding-top: var(--es-card-content-padding-y-mobile, 14px);
    padding-bottom: var(--es-card-content-padding-y-mobile, 14px);
  }
}
'''
    path.write_text(css, encoding="utf-8")


def main() -> None:
    restore_native_header()
    create_custom_header()
    patch_header_group()
    patch_product_card_schema()
    patch_settings_data()
    patch_runtime_variables()
    patch_product_card_css()


if __name__ == "__main__":
    main()
