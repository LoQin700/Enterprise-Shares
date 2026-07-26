import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f'Missing patch point: {label}')
    return text.replace(old, new, 1)


def read_schema(text: str):
    match = re.search(r'{% schema %}\s*(\{.*?\})\s*{% endschema %}', text, flags=re.S)
    if not match:
        raise RuntimeError('Schema block not found')
    return match, json.loads(match.group(1))


def write_schema(text: str, match, schema: dict) -> str:
    rendered = json.dumps(schema, ensure_ascii=False, indent=2)
    return text[:match.start()] + '{% schema %}\n' + rendered + '\n{% endschema %}' + text[match.end():]


def patch_global_settings():
    path = ROOT / 'config/settings_schema.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    group = next(item for item in data if item.get('name') == '全局产品卡')
    no_info = {
        'es_mf_namespace', 'es_deadline_key', 'es_desc_key', 'es_author_key',
        'es_tags_key', 'es_location_key', 'es_author_avatar_key',
        'es_author_bio_key', 'es_author_joined_key', 'es_wishlist_enable'
    }
    for setting in group['settings']:
        if setting.get('id') in no_info:
            setting.pop('info', None)

    ids = [item.get('id') for item in group['settings']]
    insert_at = ids.index('es_hover_second_image') + 1 if 'es_hover_second_image' in ids else len(group['settings'])
    additions = [
        {
            'type': 'checkbox',
            'id': 'es_media_accent_enable',
            'label': '显示图片底部主题色条',
            'default': True
        },
        {
            'type': 'range',
            'id': 'es_media_accent_height',
            'label': '主题色条高度',
            'min': 2,
            'max': 12,
            'step': 1,
            'unit': 'px',
            'default': 6,
            'visible_if': '{{ settings.es_media_accent_enable }}'
        }
    ]
    existing = set(ids)
    for addition in reversed(additions):
        if addition['id'] not in existing:
            group['settings'].insert(insert_at, addition)

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def patch_bootstrap():
    path = ROOT / 'snippets/es-wishlist-bootstrap.liquid'
    text = path.read_text(encoding='utf-8')
    old = "    --es-card-description-size: {{ settings.es_card_description_size | default: 14 }}px;\n"
    new = old + "    --es-media-accent-height: {% if settings.es_media_accent_enable == false %}0px{% else %}{{ settings.es_media_accent_height | default: 6 }}px{% endif %};\n"
    text = replace_once(text, old, new, 'product card accent variable')
    path.write_text(text, encoding='utf-8')


def patch_product_css():
    path = ROOT / 'assets/es-project-card-overrides.css'
    text = path.read_text(encoding='utf-8')
    marker = '/* ES 20260726 card frame and media accent */'
    if marker not in text:
        text += f'''\n\n{marker}\n.es-card {{\n  border: 1px solid var(--color-border);\n  border-radius: 10px;\n  overflow: visible;\n}}\n\n.es-card:hover,\n.es-card:focus-within {{\n  border-color: var(--color-primary);\n}}\n\n.es-card__media {{\n  width: calc(100% - 10px);\n  margin: 5px 5px 0;\n  border-radius: 8px;\n}}\n\n.es-card__media::after {{\n  content: '';\n  position: absolute;\n  right: 0;\n  bottom: 0;\n  left: 0;\n  z-index: 4;\n  height: var(--es-media-accent-height, 6px);\n  border-radius: 0 0 8px 8px;\n  background: var(--color-primary);\n  pointer-events: none;\n}}\n\n.es-slider-arrow,\n.es-slider-arrow:hover:not(:disabled),\n.es-slider-arrow:focus-visible:not(:disabled),\n.es-slider-arrow:disabled {{\n  border-color: transparent !important;\n  color: var(--color-primary) !important;\n  background: transparent !important;\n}}\n\n.es-slider-arrow:hover:not(:disabled),\n.es-slider-arrow:focus-visible:not(:disabled) {{\n  color: var(--color-primary-hover) !important;\n}}\n'''
    path.write_text(text, encoding='utf-8')


def patch_header_row():
    path = ROOT / 'snippets/header-row.liquid'
    text = path.read_text(encoding='utf-8')
    old = """    assign item_row = settings[row_key] | default: 'top'\n    assign item_column = settings[column_key] | default: 'left'\n\n    case item\n      when 'actions'\n        assign item_column = 'right'\n    endcase\n"""
    new = """    assign item_row = settings[row_key] | default: 'top'\n    assign item_column = settings[column_key] | default: 'left'\n\n    if settings.es_kickstarter_layout\n      case item\n        when 'logo'\n          assign item_row = 'top'\n          assign item_column = 'left'\n        when 'search'\n          assign item_row = 'top'\n          assign item_column = 'center'\n        when 'menu'\n          assign item_row = 'bottom'\n          assign item_column = 'center'\n        when 'actions'\n          assign item_row = 'top'\n          assign item_column = 'right'\n        when 'localization'\n          assign item_row = 'top'\n          assign item_column = 'right'\n      endcase\n    else\n      case item\n        when 'actions'\n          assign item_column = 'right'\n      endcase\n    endif\n"""
    text = replace_once(text, old, new, 'header row custom layout')
    path.write_text(text, encoding='utf-8')


def patch_header_section():
    path = ROOT / 'sections/header.liquid'
    text = path.read_text(encoding='utf-8')

    old_search = """  capture search\n    render 'search', style: search_style, class: search_class, display_style: section.settings.actions_display_style\n  endcapture\n"""
    new_search = """  capture search\n    if section.settings.es_full_search\n      render 'es-header-search', placeholder: section.settings.es_search_placeholder\n    else\n      render 'search', style: search_style, class: search_class, display_style: section.settings.actions_display_style\n    endif\n  endcapture\n"""
    text = replace_once(text, old_search, new_search, 'full header search')

    old_tag = """  data-theme-color=\"rgb({{ section.settings.color_scheme_top.settings.background.rgb }})\"\n"""
    new_tag = old_tag + """  data-es-kickstarter-layout=\"{{ section.settings.es_kickstarter_layout }}\"\n"""
    text = replace_once(text, old_tag, new_tag, 'header data attribute')

    old_style = """    --color-scheme-bottom-row: rgba({{ section.settings.color_scheme_bottom.settings.background.rgba }});\n"""
    new_style = old_style + """    --es-header-search-max-width: {{ section.settings.es_search_max_width | default: 840 }}px;\n    --es-mobile-menu-font-size: {{ section.settings.es_mobile_menu_font_size | default: 16 }}px;\n"""
    text = replace_once(text, old_style, new_style, 'header css variables')

    old_assets = """<script\n  src=\"{{ 'header.js' | asset_url }}\"\n  type=\"module\"\n></script>\n"""
    new_assets = """{{ 'es-header.css' | asset_url | stylesheet_tag }}\n<script src=\"{{ 'es-header.js' | asset_url }}\" defer=\"defer\"></script>\n\n""" + old_assets
    text = replace_once(text, old_assets, new_assets, 'header assets')

    match, schema = read_schema(text)
    settings = schema['settings']
    ids = [item.get('id') for item in settings]

    def add_after(anchor_id, item):
        nonlocal settings, ids
        if item['id'] in ids:
            return
        index = ids.index(anchor_id) + 1
        settings.insert(index, item)
        ids.insert(index, item['id'])

    add_after('menu_row', {
        'type': 'range', 'id': 'es_mobile_menu_font_size', 'label': '手机端菜单字号',
        'min': 12, 'max': 24, 'step': 1, 'unit': 'px', 'default': 16
    })
    add_after('show_search', {
        'type': 'checkbox', 'id': 'es_kickstarter_layout', 'label': '启用双层分类导航', 'default': True
    })
    add_after('es_kickstarter_layout', {
        'type': 'checkbox', 'id': 'es_full_search', 'label': '桌面端显示完整搜索框', 'default': True
    })
    add_after('es_full_search', {
        'type': 'text', 'id': 'es_search_placeholder', 'label': '搜索框预设文案',
        'default': 'Search projects, creators, and categories'
    })
    add_after('es_search_placeholder', {
        'type': 'range', 'id': 'es_search_max_width', 'label': '搜索框最大宽度',
        'min': 360, 'max': 1000, 'step': 20, 'unit': 'px', 'default': 840
    })

    search_position = next(item for item in settings if item.get('id') == 'search_position')
    if not any(option.get('value') == 'center' for option in search_position['options']):
        search_position['options'].insert(1, {'value': 'center', 'label': '居中'})

    text = write_schema(text, match, schema)
    path.write_text(text, encoding='utf-8')


def patch_header_menu():
    path = ROOT / 'blocks/_header-menu.liquid'
    text = path.read_text(encoding='utf-8')
    old_top = """{% liquid\n  assign block_settings = block.settings\n%}\n"""
    new_top = """{% liquid\n  assign block_settings = block.settings\n%}\n{% capture es_mega_configs %}{% content_for 'blocks' %}{% endcapture %}\n"""
    text = replace_once(text, old_top, new_top, 'mega child block capture')

    old_inner = """      </div>\n\n      <script\n        src=\"{{ 'header-menu.js' | asset_url }}\"\n"""
    new_inner = """      </div>\n      <div class=\"es-mega-configs\" hidden>{{ es_mega_configs }}</div>\n\n      <script\n        src=\"{{ 'header-menu.js' | asset_url }}\"\n"""
    text = replace_once(text, old_inner, new_inner, 'mega configs markup')

    match, schema = read_schema(text)
    schema['blocks'] = [{'type': '_es-header-mega-item'}]
    remove_ids = {
        'menu_style', 'featured_products_aspect_ratio',
        'featured_collections_aspect_ratio', 'image_border_radius'
    }
    schema['settings'] = [item for item in schema['settings'] if item.get('id') not in remove_ids and item.get('content') != 't:content.submenu_feature']
    text = write_schema(text, match, schema)
    path.write_text(text, encoding='utf-8')


def patch_installer():
    path = ROOT / 'scripts/install_es_feature.py'
    text = path.read_text(encoding='utf-8')
    text = text.replace("{'type': 'checkbox', 'id': 'es_hover_second_image', 'label': 'Hover 显示第二张图片', 'default': False},\n", "{'type': 'checkbox', 'id': 'es_hover_second_image', 'label': 'Hover 显示第二张图片', 'default': False},\n            {'type': 'checkbox', 'id': 'es_media_accent_enable', 'label': '显示图片底部主题色条', 'default': True},\n            {'type': 'range', 'id': 'es_media_accent_height', 'label': '主题色条高度', 'min': 2, 'max': 12, 'step': 1, 'unit': 'px', 'default': 6, 'visible_if': '{{ settings.es_media_accent_enable }}'},\n")
    for fragment in [
        ", 'info': '填写 Shopify 产品元字段的命名空间，建议保持 custom。'",
        ", 'info': '类型必须为“日期和时间”；前台根据当前时间自动计算剩余天数、小时或分钟。'",
        ", 'info': '建议使用多行文本；重点商品常显，推荐商品 Hover 时显示。'",
        ", 'info': '类型为 Metaobject 引用，并关联 project_author 作者元对象。'",
        ", 'info': '建议使用单行文本列表；如果导入值包含分号或逗号，前台会自动拆分为独立标签。'",
        ", 'info': '可选；使用单行文本，作为卡片补充标签显示。'"
    ]:
        text = text.replace(fragment, '')
    path.write_text(text, encoding='utf-8')


def main():
    patch_global_settings()
    patch_bootstrap()
    patch_product_css()
    patch_header_row()
    patch_header_section()
    patch_header_menu()
    patch_installer()


if __name__ == '__main__':
    main()
