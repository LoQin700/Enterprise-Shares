from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    file = ROOT / path
    text = file.read_text(encoding='utf-8')
    if old not in text:
        raise RuntimeError(f'Pattern not found in {path}: {old[:80]}')
    file.write_text(text.replace(old, new, 1), encoding='utf-8')


replace_once(
    'blocks/_es-header-mega-item.liquid',
    "  assign menu_title = block.settings.menu_title | strip\n-%}",
    "  assign menu_title = block.settings.menu_title | strip\n  assign card_ratio = settings.es_card_ratio | default: '16/9'\n-%}",
)
replace_once(
    'blocks/_es-header-mega-item.liquid',
    "image_ratio: settings.es_card_ratio | default: '16/9'",
    "image_ratio: card_ratio",
)

replace_once(
    'blocks/_product-card.liquid',
    "  if settings.es_cards_enable == false\n    assign es_cards_enabled = false\n  endif\n-%}",
    "  if settings.es_cards_enable == false\n    assign es_cards_enabled = false\n  endif\n  assign card_ratio = settings.es_card_ratio | default: '16/9'\n-%}",
)
replace_once(
    'blocks/_product-card.liquid',
    "image_ratio: settings.es_card_ratio | default: '16/9'",
    "image_ratio: card_ratio",
)

replace_once(
    'sections/enterprise-shares-header.liquid',
    "  if header_logo == blank\n    assign header_logo = settings.logo\n  endif\n-%}",
    "  if header_logo == blank\n    assign header_logo = settings.logo\n  endif\n  assign card_ratio = settings.es_card_ratio | default: '16/9'\n-%}",
)
replace_once(
    'sections/enterprise-shares-header.liquid',
    "image_ratio: settings.es_card_ratio | default: '16/9'",
    "image_ratio: card_ratio",
)

replace_once(
    'sections/es-main-author.liquid',
    "  assign author_joined = author[joined_key].value\n-%}",
    "  assign author_joined = author[joined_key].value\n  assign card_ratio = settings.es_card_ratio | default: '16/9'\n-%}",
)
replace_once(
    'sections/es-main-author.liquid',
    "image_ratio: settings.es_card_ratio | default: '16/9'",
    "image_ratio: card_ratio",
)

replace_once(
    'sections/es-product-recommendation-carousel.liquid',
    "  if view_all_url == blank and section.settings.source == 'collection' and recommended_collection != blank\n    assign view_all_url = recommended_collection.url\n  endif\n-%}",
    "  if view_all_url == blank and section.settings.source == 'collection' and recommended_collection != blank\n    assign view_all_url = recommended_collection.url\n  endif\n  assign card_ratio = settings.es_card_ratio | default: '16/9'\n-%}",
)
replace_once(
    'sections/es-product-recommendation-carousel.liquid',
    "image_ratio: settings.es_card_ratio | default: '16/9'",
    "image_ratio: card_ratio",
)
