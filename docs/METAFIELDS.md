# Shopify 元字段与 Metaobject 设置

主题设置中的命名已预填。你可以在 **Online Store → Themes → Customize → Theme settings → 全局产品卡** 中手动修改命名空间和 Key；修改后，代码会按新名称读取数据。

## 1. 产品元字段

统一在 **Settings → Custom data → Products** 创建一次定义。之后所有产品后台都会显示这些字段，不需要在每个商品系列里重复创建。

| 显示名称 | Namespace and key | 类型 | 必填 | 用途 |
|---|---|---|---|---|
| Project deadline | `custom.project_deadline` | Date and time | 是 | 当前时间到截至时间的自动倒数 |
| Card description | `custom.card_description` | Multi-line text | 建议 | 左侧重点卡常显；右侧卡 Hover 时显示 |
| Author | `custom.author` | Metaobject reference → `project_author` | 建议 | 关联作者头像、名称、简介和作者页面 |
| Card tags | `custom.card_tags` | List of single line text | 可选 | 产品卡标签，最多显示 3 个 |
| Card location | `custom.card_location` | Single line text | 可选 | 地区或附加标签 |

### 命名说明

- Namespace 建议固定为 `custom`。
- Key 可在主题全局设置中手动修改。
- 截至时间必须使用 **Date and time**，不要使用普通文本。
- 每个产品的数据值仍需分别填写；这里只是全局创建一次字段定义。

## 2. 作者 Metaobject

在 **Settings → Custom data → Metaobjects** 创建定义：

- Name: `Project author`
- Type: `project_author`
- 启用 Web pages，以便生成作者详情页。

字段如下：

| 显示名称 | Key | 类型 | 必填 | 用途 |
|---|---|---|---|---|
| Display name | `display_name` | Single line text | 是 | 作者名称 |
| Avatar | `avatar` | File（仅图片） | 建议 | 产品卡作者头像 |
| Bio | `bio` | Rich text 或 Multi-line text | 建议 | Hover 作者简介和作者页面介绍 |
| Projects collection | `projects_collection` | Collection reference | 是 | 作者产品数量和作者详情页产品列表 |
| Joined date | `joined_date` | Date | 可选 | 作者加入日期 |

## 3. 作者产品自动归类

Shopify Liquid 不能高效地在前台反向扫描全店产品，因此使用智能商品系列维护作者项目关系：

1. 给每位作者建立一个自动商品系列，例如 `Projects by Alice`。
2. 自动条件设置为：产品元字段 `custom.author` 等于该作者 Metaobject。
3. 回到作者 Metaobject，把 `projects_collection` 关联到这个自动商品系列。
4. 以后新产品只需填写 `custom.author`，系统会自动进入该作者商品系列。

产品卡 Hover 作者资料时只显示作者信息和项目数量，不列出产品名称。点击作者进入作者页面后，展示该作者的全部产品。

## 4. 登录客户收藏元字段

同步应用使用客户元字段：

- Namespace: `enterprise_shares`
- Key: `wishlist`
- Type: `json`
- Value: 产品 Handle 数组，例如 `["product-a","product-b"]`

该值由 `wishlist-sync-app` 自动读写，不需要人工维护。
