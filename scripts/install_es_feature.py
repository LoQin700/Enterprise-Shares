import base64
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def extract_bundle() -> None:
    chunks = sorted((ROOT / 'scripts').glob('es_feature_bundle.*'))
    if not chunks:
        if not (ROOT / 'snippets/es-project-product-card.liquid').exists():
            raise RuntimeError('Feature bundle chunks are missing')
        return

    encoded = ''.join(path.read_text(encoding='utf-8').strip() for path in chunks)
    archive = ROOT / 'scripts/es_feature_bundle.tar.gz'
    archive.write_bytes(base64.b64decode(encoded))

    with tarfile.open(archive, 'r:gz') as bundle:
        for member in bundle.getmembers():
            target = (ROOT / member.name).resolve()
            if ROOT not in target.parents and target != ROOT:
                raise RuntimeError(f'Unsafe bundle member: {member.name}')
        bundle.extractall(ROOT)

    archive.unlink()
    for path in chunks:
        path.unlink()


def patch_settings() -> None:
    path = ROOT / 'config/settings_schema.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    group = {
        'name': '全局产品卡',
        'settings': [
            {'type': 'checkbox', 'id': 'es_cards_enable', 'label': '启用自定义产品卡', 'default': True, 'info': '开启后，Horizon 的全局商品卡 Block 会统一使用本套项目卡样式。'},
            {'type': 'select', 'id': 'es_card_ratio', 'label': '全局产品卡图片比例', 'default': '16/9', 'options': [
                {'value': '1/1', 'label': '1:1 正方形'},
                {'value': '4/3', 'label': '4:3 横图'},
                {'value': '3/2', 'label': '3:2 横图'},
                {'value': '16/9', 'label': '16:9 宽屏'},
                {'value': '4/5', 'label': '4:5 竖图'},
                {'value': '3/4', 'label': '3:4 竖图'}
            ], 'info': '统一用于集合页、搜索页、相关商品、重点商品与推荐轮播中的产品卡图片。'},
            {'type': 'header', 'content': '产品元字段命名'},
            {'type': 'text', 'id': 'es_mf_namespace', 'label': '元字段命名空间', 'default': 'custom', 'info': '填写 Shopify 产品元字段的命名空间，建议保持 custom。'},
            {'type': 'text', 'id': 'es_deadline_key', 'label': '截至时间字段 Key', 'default': 'project_deadline', 'info': '类型必须为“日期和时间”；前台根据当前时间自动计算剩余天数、小时或分钟。'},
            {'type': 'text', 'id': 'es_desc_key', 'label': '卡片简介字段 Key', 'default': 'card_description', 'info': '建议使用多行文本；重点商品常显，推荐商品 Hover 时显示。'},
            {'type': 'text', 'id': 'es_author_key', 'label': '作者关联字段 Key', 'default': 'author', 'info': '类型为 Metaobject 引用，并关联 project_author 作者元对象。'},
            {'type': 'text', 'id': 'es_tags_key', 'label': '卡片标签字段 Key', 'default': 'card_tags', 'info': '建议使用单行文本列表；如果导入值包含分号或逗号，前台会自动拆分为独立标签。'},
            {'type': 'text', 'id': 'es_location_key', 'label': '地区字段 Key', 'default': 'card_location', 'info': '可选；使用单行文本，作为卡片补充标签显示。'},
            {'type': 'header', 'content': '作者 Metaobject 字段命名'},
            {'type': 'text', 'id': 'es_author_name_key', 'label': '作者名称字段 Key', 'default': 'display_name', 'info': '作者元对象中的名称字段。'},
            {'type': 'text', 'id': 'es_author_avatar_key', 'label': '作者头像字段 Key', 'default': 'avatar'},
            {'type': 'text', 'id': 'es_author_bio_key', 'label': '作者简介字段 Key', 'default': 'bio'},
            {'type': 'text', 'id': 'es_author_collection_key', 'label': '作者商品集合字段 Key', 'default': 'projects_collection', 'info': '类型为商品系列引用；关联按作者自动归类的智能商品系列，用于项目数量和作者页面。'},
            {'type': 'text', 'id': 'es_author_joined_key', 'label': '作者加入日期字段 Key', 'default': 'joined_date'},
            {'type': 'header', 'content': '显示与收藏'},
            {'type': 'range', 'id': 'es_card_title_size', 'label': '产品标题字号', 'min': 12, 'max': 40, 'step': 1, 'unit': 'px', 'default': 16},
            {'type': 'range', 'id': 'es_card_description_size', 'label': '产品正文与信息字号', 'min': 10, 'max': 24, 'step': 1, 'unit': 'px', 'default': 14},
            {'type': 'checkbox', 'id': 'es_hover_second_image', 'label': 'Hover 显示第二张图片', 'default': False},
            {'type': 'checkbox', 'id': 'es_show_price', 'label': '产品卡显示价格', 'default': False},
            {'type': 'text', 'id': 'es_ended_text', 'label': '截至后的文案', 'default': 'Ended'},
            {'type': 'checkbox', 'id': 'es_wishlist_enable', 'label': '启用书签收藏', 'default': True}
        ]
    }
    existing = next((item for item in data if item.get('name') == group['name']), None)
    if existing is None:
        data.append(group)
    else:
        existing.clear()
        existing.update(group)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def patch_layout() -> None:
    path = ROOT / 'layout/theme.liquid'
    text = path.read_text(encoding='utf-8')
    marker = "    {%- render 'color-schemes' -%}\n"
    addition = marker + "    {%- render 'es-wishlist-bootstrap' -%}\n"
    if "render 'es-wishlist-bootstrap'" not in text:
        if marker not in text:
            raise RuntimeError('Could not find theme head integration point')
        text = text.replace(marker, addition, 1)
        path.write_text(text, encoding='utf-8')


def patch_horizon_product_block() -> None:
    path = ROOT / 'blocks/_product-card.liquid'
    text = path.read_text(encoding='utf-8')
    if "render 'es-project-product-card'" in text:
        return
    old = """{% liquid
  assign product = closest.product
-%}

{% capture children %}
  {% content_for 'blocks', closest.product: product %}
{% endcapture %}

{% render 'product-card', children: children, product: product %}
"""
    new = """{% liquid
  assign product = closest.product
  assign es_cards_enabled = true
  if settings.es_cards_enable == false
    assign es_cards_enabled = false
  endif
-%}

{% if es_cards_enabled and product != blank %}
  {% render 'es-project-product-card', product: product, variant: 'compact', image_ratio: settings.es_card_ratio | default: '16/9', shopify_attributes: block.shopify_attributes %}
{% else %}
  {% capture children %}
    {% content_for 'blocks', closest.product: product %}
  {% endcapture %}

  {% render 'product-card', children: children, product: product %}
{% endif %}
"""
    if old not in text:
        raise RuntimeError('Could not find Horizon product-card block integration point')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')


def patch_card_attributes() -> None:
    path = ROOT / 'snippets/es-project-product-card.liquid'
    text = path.read_text(encoding='utf-8')
    old = '<article class="es-card es-card--{{ card_variant }}" data-es-product-card data-product-handle="{{ product.handle | escape }}">'
    new = '<article class="es-card es-card--{{ card_variant }}" data-es-product-card data-product-handle="{{ product.handle | escape }}" {{ shopify_attributes }}>'
    if old in text:
        path.write_text(text.replace(old, new, 1), encoding='utf-8')


def main() -> None:
    extract_bundle()
    patch_settings()
    patch_layout()
    patch_horizon_product_block()
    patch_card_attributes()


if __name__ == '__main__':
    main()
