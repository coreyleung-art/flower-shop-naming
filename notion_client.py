#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notion API Client for Flower Shop Naming Database
用于从 Notion 加载花店命名数据库

Usage:
    python3 notion_client.py --test          # 测试连接
    python3 notion_client.py --setup        # 创建旧版数据库并迁移数据
    python3 notion_client.py --rebuild      # 重建统一产品数据库（新结构）
    python3 notion_client.py --fetch        # 从Notion获取数据
    python3 notion_client.py --add-missing  # 添加缺失的数据
"""

import json
import os
import sys
import requests
from pathlib import Path

# Notion API 配置
# 从环境变量获取 Notion Token
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
if not NOTION_TOKEN:
    raise ValueError("NOTION_TOKEN environment variable is required")
NOTION_VERSION = "2022-06-28"
NOTION_API_BASE = "https://api.notion.com/v1"

# 父页面 ID - 花店业务系统
PARENT_PAGE_ID = "33bdaacb-e017-80f7-9273-e27cda616c14"

# 数据库名称
DB_NAMES = {
    "categories": "花材分类关键词",
    "species": "种属映射",
    "colors": "颜色映射",
    "products": "统一产品库"
}

# 数据库 Schema 定义
DATABASE_SCHEMAS = {
    "categories": {
        "Category": {"name": "Category", "type": "title"},
        "Keywords": {"name": "Keywords", "type": "multi_select"},
        "Priority": {"name": "Priority", "type": "number"}
    },
    "species": {
        "Product": {"name": "Product", "type": "title"},
        "Species": {"name": "Species", "type": "rich_text"},
        "Category": {"name": "Category", "type": "select"}
    },
    "colors": {
        "Original": {"name": "Original", "type": "title"},
        "Standard": {"name": "Standard", "type": "rich_text"}
    }
}

# 统一产品数据库 Schema（新版）
PRODUCT_DB_SCHEMA = {
    "Product": {"name": "Product", "type": "title"},
    "Original Keywords": {"name": "Original Keywords", "type": "multi_select"},
    "Category": {"name": "Category", "type": "select"},
    "Variety Type": {"name": "Variety Type", "type": "rich_text"},
    "Species": {"name": "Species", "type": "rich_text"},
    "Spec": {"name": "Spec", "type": "rich_text"},
    "Color": {"name": "Color", "type": "rich_text"},
    "Unit": {"name": "Unit", "type": "rich_text"},
    "Notes": {"name": "Notes", "type": "rich_text"}
}


def notion_headers():
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json"
    }


def test_connection():
    """测试 Notion API 连接"""
    print("🔍 测试 Notion API 连接...")
    response = requests.get(
        f"{NOTION_API_BASE}/users/me",
        headers=notion_headers()
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ 连接成功!")
        print(f"   用户: {data.get('name')}")
        print(f"   类型: {data.get('type')}")
        if data.get('bot'):
            print(f"   工作空间: {data['bot'].get('workspace_name')}")
        return True
    else:
        print(f"❌ 连接失败: {response.status_code}")
        print(f"   {response.text}")
        return False


def create_database(db_key: str, schema: dict) -> str:
    """在父页面创建数据库"""
    print(f"📦 创建数据库: {DB_NAMES[db_key]}...")

    # 构建属性 schema
    properties = {}
    for prop_name, prop_config in schema.items():
        prop_type = prop_config["type"]
        if prop_type == "title":
            properties[prop_name] = {"title": {}}
        elif prop_type == "rich_text":
            properties[prop_name] = {"rich_text": {}}
        elif prop_type == "multi_select":
            properties[prop_name] = {"multi_select": {"options": []}}
        elif prop_type == "select":
            properties[prop_name] = {"select": {"options": []}}
        elif prop_type == "number":
            properties[prop_name] = {"number": {"format": "number"}}

    payload = {
        "parent": {
            "type": "page_id",
            "page_id": PARENT_PAGE_ID
        },
        "title": [
            {
                "type": "text",
                "text": {"content": DB_NAMES[db_key]}
            }
        ],
        "properties": properties
    }

    response = requests.post(
        f"{NOTION_API_BASE}/databases",
        headers=notion_headers(),
        json=payload
    )

    if response.status_code == 200:
        db = response.json()
        db_id = db["id"]
        print(f"   ✅ 创建成功! ID: {db_id}")
        return db_id
    else:
        print(f"   ❌ 创建失败: {response.status_code}")
        print(f"   {response.text}")
        return None


def add_page_to_database(database_id: str, properties: dict) -> bool:
    """添加页面到数据库"""
    payload = {
        "parent": {"database_id": database_id},
        "properties": properties
    }

    response = requests.post(
        f"{NOTION_API_BASE}/pages",
        headers=notion_headers(),
        json=payload
    )

    if response.status_code != 200:
        print(f"       错误: {response.status_code} - {response.text[:100]}")

    return response.status_code == 200


def add_category_to_notion(database_id: str, category: str, keywords: list, priority: int):
    """添加单个分类到 Notion 数据库"""
    properties = {
        "Category": {
            "title": [{"text": {"content": category}}]
        },
        "Keywords": {
            "multi_select": [{"name": k} for k in keywords]
        },
        "Priority": {
            "number": priority
        }
    }

    payload = {
        "parent": {"database_id": database_id},
        "properties": properties
    }

    response = requests.post(
        f"{NOTION_API_BASE}/pages",
        headers=notion_headers(),
        json=payload
    )

    if response.status_code == 200:
        print(f"   ✅ {category}: {len(keywords)} 个关键词")
        return True
    else:
        print(f"   ❌ {category}: 添加失败 ({response.status_code})")
        return False


def add_missing_categories():
    """添加缺失的分类到 Notion"""
    config_file = get_config_file()
    if not config_file.exists():
        print("❌ 配置文件不存在")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 导入数据
    from item_naming_cli import CATEGORY_KEYWORDS

    print("\n📝 添加缺失的分类...")

    # 检查现有分类
    existing = query_database(config["categories_db_id"])
    existing_categories = set()
    for page in existing:
        props = page.get("properties", {})
        category_name = props.get("Category", {}).get("title", [{}])[0].get("text", {}).get("content", "")
        if category_name:
            existing_categories.add(category_name)

    print(f"   已有分类: {len(existing_categories)} 个")

    # 添加缺失的分类
    priority = len(existing_categories) + 1
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category not in existing_categories:
            add_category_to_notion(config["categories_db_id"], category, keywords, priority)
            priority += 1


def add_missing_species():
    """添加缺失的种属映射到 Notion（覆盖花材和非花材）"""
    config_file = get_config_file()
    if not config_file.exists():
        print("❌ 配置文件不存在")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 导入数据
    from item_naming_cli import SPECIES_CATEGORY, PRODUCT_TYPE_MAPPING, CATEGORY_TO_NOTION_CATEGORY

    print("\n📝 添加缺失的种属映射...")

    # 检查现有种属映射
    existing = query_database(config["species_db_id"])
    existing_products = set()
    for page in existing:
        props = page.get("properties", {})
        product_name = props.get("Product", {}).get("title", [{}])[0].get("text", {}).get("content", "")
        if product_name:
            existing_products.add(product_name)

    print(f"   已有映射: {len(existing_products)} 条")

    # 1. 同步花材种属映射（SPECIES_CATEGORY）
    print("   [花材]")
    added_count = 0
    for product, species in SPECIES_CATEGORY.items():
        if product not in existing_products:
            properties = {
                "Product": {
                    "title": [{"text": {"content": product}}]
                },
                "Species": {
                    "rich_text": [{"text": {"content": species}}]
                },
                "Category": {
                    "select": {"name": "花材"}
                }
            }
            if add_page_to_database(config["species_db_id"], properties):
                added_count += 1
                print(f"   ✅ {product}: {species}")
                existing_products.add(product)  # 避免重复添加

    print(f"   花材完成! 新增 {added_count} 条")

    # 2. 同步非花材产品类型映射（PRODUCT_TYPE_MAPPING）
    print("   [非花材]")
    nonflower_count = 0
    for product, product_type in PRODUCT_TYPE_MAPPING.items():
        if product not in existing_products:
            # 确定 Notion 分类
            notion_cat = "其他"
            for cat, notion_cat_val in CATEGORY_TO_NOTION_CATEGORY.items():
                # 检查该产品属于哪个本地品类
                from item_naming_cli import CATEGORY_KEYWORDS
                if cat in CATEGORY_KEYWORDS and product in CATEGORY_KEYWORDS[cat]:
                    notion_cat = notion_cat_val
                    break

            properties = {
                "Product": {
                    "title": [{"text": {"content": product}}]
                },
                "Species": {
                    "rich_text": [{"text": {"content": product_type}}]
                },
                "Category": {
                    "select": {"name": notion_cat}
                }
            }
            if add_page_to_database(config["species_db_id"], properties):
                nonflower_count += 1
                print(f"   ✅ {product}: {product_type} ({notion_cat})")
                existing_products.add(product)  # 避免重复添加

    print(f"   非花材完成! 新增 {nonflower_count} 条")
    print(f"   总计: {added_count + nonflower_count} 条")


def add_missing_colors():
    """添加缺失的颜色映射到 Notion"""
    config_file = get_config_file()
    if not config_file.exists():
        print("❌ 配置文件不存在")
        return

    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 导入数据
    from item_naming_cli import COLOR_MAPPING

    print("\n📝 添加缺失的颜色映射...")

    # 检查现有颜色映射
    existing = query_database(config["colors_db_id"])
    existing_originals = set()
    for page in existing:
        props = page.get("properties", {})
        original_name = props.get("Original", {}).get("title", [{}])[0].get("text", {}).get("content", "")
        if original_name:
            existing_originals.add(original_name)

    print(f"   已有映射: {len(existing_originals)} 条")

    # 添加缺失的映射
    added_count = 0
    for original, standard in COLOR_MAPPING.items():
        if original not in existing_originals:
            properties = {
                "Original": {
                    "title": [{"text": {"content": original}}]
                },
                "Standard": {
                    "rich_text": [{"text": {"content": standard}}]
                }
            }
            if add_page_to_database(config["colors_db_id"], properties):
                added_count += 1
                print(f"   ✅ {original}: {standard}")

    print(f"   完成! 新增 {added_count} 条映射")


def populate_categories_db(database_id: str):
    """填充花材分类关键词数据库"""
    print(f"\n📝 填充花材分类关键词数据库...")

    # 延迟导入避免循环依赖
    from item_naming_cli import CATEGORY_KEYWORDS

    priority = 1
    for category, keywords in CATEGORY_KEYWORDS.items():
        properties = {
            "Category": {
                "title": [{"text": {"content": category}}]
            },
            "Keywords": {
                "multi_select": [{"name": k} for k in keywords]
            },
            "Priority": {
                "number": priority
            }
        }

        if add_page_to_database(database_id, properties):
            print(f"   ✅ {category}: {len(keywords)} 个关键词")
        else:
            print(f"   ❌ {category}: 添加失败")

        priority += 1

    print(f"   完成! 共 {priority - 1} 个分类")


def populate_species_db(database_id: str):
    """填充种属映射数据库"""
    print(f"\n📝 填充种属映射数据库...")

    from item_naming_cli import SPECIES_CATEGORY

    count = 0
    for product, species in SPECIES_CATEGORY.items():
        properties = {
            "Product": {
                "title": [{"text": {"content": product}}]
            },
            "Species": {
                "rich_text": [{"text": {"content": species}}]
            },
            "Category": {
                "select": {"name": "通用"}
            }
        }

        if add_page_to_database(database_id, properties):
            count += 1
        else:
            print(f"   ❌ {product}: 添加失败")

    print(f"   完成! 共 {count} 条映射")


def populate_colors_db(database_id: str):
    """填充颜色映射数据库"""
    print(f"\n📝 填充颜色映射数据库...")

    from item_naming_cli import COLOR_MAPPING

    count = 0
    for original, standard in COLOR_MAPPING.items():
        properties = {
            "Original": {
                "title": [{"text": {"content": original}}]
            },
            "Standard": {
                "rich_text": [{"text": {"content": standard}}]
            }
        }

        if add_page_to_database(database_id, properties):
            count += 1
        else:
            print(f"   ❌ {original}: 添加失败")

    print(f"   完成! 共 {count} 条映射")


def populate_products_db(database_id: str):
    """填充统一产品数据库（从 STANDARD_PRODUCTS）"""
    from item_naming_cli import STANDARD_PRODUCTS
    import time

    print(f"\n📝 填充统一产品数据库 (共 {len(STANDARD_PRODUCTS)} 个产品)...")
    print("   提示: 此过程可能需要几分钟，请耐心等待...")

    count = 0
    total = len(STANDARD_PRODUCTS)
    for i, product_data in enumerate(STANDARD_PRODUCTS):
        properties = {
            "Product": {
                "title": [{"text": {"content": product_data['product']}}]
            },
            "Original Keywords": {
                "multi_select": [{"name": kw} for kw in product_data['original_keywords']]
            },
            "Category": {
                "select": {"name": product_data['category']}
            },
            "Variety Type": {
                "rich_text": [{"text": {"content": product_data['variety_type']}}] if product_data['variety_type'] else []
            },
            "Species": {
                "rich_text": [{"text": {"content": product_data['species']}}] if product_data['species'] else []
            },
            "Spec": {
                "rich_text": [{"text": {"content": product_data['spec']}}] if product_data['spec'] else []
            },
            "Color": {
                "rich_text": [{"text": {"content": ','.join(product_data['common_colors'])}}] if product_data['common_colors'] else []
            },
            "Unit": {
                "rich_text": [{"text": {"content": product_data['unit']}}] if product_data['unit'] else []
            },
            "Notes": {
                "rich_text": [{"text": {"content": product_data['notes']}}] if product_data['notes'] else []
            }
        }

        # 添加小延迟避免速率限制
        if i > 0 and i % 50 == 0:
            time.sleep(0.5)

        if add_page_to_database(database_id, properties):
            count += 1
            if count % 50 == 0:
                print(f"   进度: {count}/{total} ({count*100//total}%)")
        else:
            print(f"   ❌ {product_data['product']}: 添加失败")

    print(f"   完成! 共 {count} 条产品")
    return count


def query_database(database_id: str, page_size: int = 100) -> list:
    """查询数据库所有页面"""
    print(f"   查询数据库 {database_id}...")

    results = []
    has_more = True
    start_cursor = None

    while has_more:
        payload = {"page_size": min(page_size, 100)}
        if start_cursor:
            payload["start_cursor"] = start_cursor

        response = requests.post(
            f"{NOTION_API_BASE}/databases/{database_id}/query",
            headers=notion_headers(),
            json=payload
        )

        if response.status_code != 200:
            print(f"   ❌ 查询失败: {response.status_code}")
            break

        data = response.json()
        results.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor")

    print(f"   获取到 {len(results)} 条记录")
    return results


def save_to_cache(data: dict, cache_file: str):
    """保存到本地缓存"""
    cache_path = Path(cache_file)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"💾 已保存到缓存: {cache_file}")


def load_from_cache(cache_file: str) -> dict:
    """从本地缓存加载"""
    cache_path = Path(cache_file)

    if not cache_path.exists():
        return None

    with open(cache_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_cache_file() -> Path:
    """获取缓存文件路径"""
    return Path(__file__).parent / "notion_cache.json"


def get_config_file() -> Path:
    """获取配置文件路径"""
    return Path(__file__).parent / "notion_config.json"


def load_data(use_cache: bool = True, force_refresh: bool = False) -> dict:
    """加载数据（优先从缓存，缓存不存在或强制刷新时从 Notion 获取）

    Args:
        use_cache: 是否使用缓存
        force_refresh: 是否强制从 Notion 刷新

    Returns:
        dict: 包含 categories, species, colors 的字典
    """
    cache_file = get_cache_file()
    config_file = get_config_file()

    # 尝试从缓存加载
    if use_cache and not force_refresh:
        cached = load_from_cache(str(cache_file))
        if cached:
            print(f"📦 从缓存加载数据: {cache_file}")
            return cached

    # 检查配置文件
    if not config_file.exists():
        print("⚠️ Notion 配置文件不存在，请先运行: python3 notion_client.py --setup")
        return None

    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 从 Notion 获取
    data = fetch_all_from_notion(
        config["categories_db_id"],
        config["species_db_id"],
        config["colors_db_id"]
    )

    # 保存到缓存
    save_to_cache(data, str(cache_file))

    return data


def fetch_all_from_notion(categories_db_id: str, species_db_id: str, colors_db_id: str) -> dict:
    """从 Notion 获取所有数据"""
    print("\n📥 从 Notion 获取数据...")

    # 获取分类关键词
    category_pages = query_database(categories_db_id)
    categories = {}
    for page in category_pages:
        props = page.get("properties", {})
        category_name = props.get("Category", {}).get("title", [{}])[0].get("text", {}).get("content", "")
        keywords = [k.get("name") for k in props.get("Keywords", {}).get("multi_select", [])]
        if category_name:
            categories[category_name] = keywords

    # 获取种属映射
    species_pages = query_database(species_db_id)
    species = {}
    for page in species_pages:
        props = page.get("properties", {})
        product = props.get("Product", {}).get("title", [{}])[0].get("text", {}).get("content", "")
        species_name = props.get("Species", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
        if product:
            species[product] = species_name

    # 获取颜色映射
    color_pages = query_database(colors_db_id)
    colors = {}
    for page in color_pages:
        props = page.get("properties", {})
        original = props.get("Original", {}).get("title", [{}])[0].get("text", {}).get("content", "")
        standard = props.get("Standard", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
        if original:
            colors[original] = standard

    return {
        "categories": categories,
        "species": species,
        "colors": colors
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]

    if command == "--test":
        test_connection()

    elif command == "--setup":
        if not test_connection():
            return

        print("\n" + "="*50)
        print("🚀 开始创建 Notion 数据库...")
        print("="*50)

        # 创建数据库
        db_ids = {}
        for db_key in ["categories", "species", "colors"]:
            db_id = create_database(db_key, DATABASE_SCHEMAS[db_key])
            if db_id:
                db_ids[db_key] = db_id
            else:
                print(f"❌ 数据库 {DB_NAMES[db_key]} 创建失败，退出")
                return

        print("\n" + "="*50)
        print("📊 开始迁移数据...")
        print("="*50)

        # 填充数据
        populate_categories_db(db_ids["categories"])
        populate_species_db(db_ids["species"])
        populate_colors_db(db_ids["colors"])

        # 保存数据库 ID
        config = {
            "categories_db_id": db_ids["categories"],
            "species_db_id": db_ids["species"],
            "colors_db_id": db_ids["colors"]
        }

        config_file = Path(__file__).parent / "notion_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 数据库创建和数据迁移完成!")
        print(f"📁 配置已保存到: {config_file}")
        print(f"\n数据库 ID:")
        for key, db_id in db_ids.items():
            print(f"   {DB_NAMES[key]}: {db_id}")

    elif command == "--fetch":
        config_file = Path(__file__).parent / "notion_config.json"

        if not config_file.exists():
            print("❌ 配置文件不存在，请先运行 --setup")
            return

        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        data = fetch_all_from_notion(
            config["categories_db_id"],
            config["species_db_id"],
            config["colors_db_id"]
        )

        cache_file = Path(__file__).parent / "notion_cache.json"
        save_to_cache(data, str(cache_file))

        print(f"\n✅ 数据获取完成!")

    elif command == "--add-missing":
        add_missing_categories()
        add_missing_species()
        add_missing_colors()

    elif command == "--rebuild":
        """重建统一产品数据库"""
        if not test_connection():
            return

        print("\n" + "="*50)
        print("🚀 开始重建统一产品数据库...")
        print("="*50)

        # 创建新数据库
        db_id = create_database("products", PRODUCT_DB_SCHEMA)
        if not db_id:
            print("❌ 数据库创建失败")
            return

        print("\n" + "="*50)
        print("📊 开始迁移数据...")
        print("="*50)

        # 填充数据
        populate_products_db(db_id)

        # 保存数据库 ID
        config = {
            "products_db_id": db_id,
            # 保留旧数据库 ID 以便兼容
            "categories_db_id": "",
            "species_db_id": "",
            "colors_db_id": ""
        }

        config_file = Path(__file__).parent / "notion_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 统一产品数据库创建和数据迁移完成!")
        print(f"📁 配置已保存到: {config_file}")
        print(f"\n新数据库 ID:")
        print(f"   统一产品库: {db_id}")
        print(f"\n💡 提示: 旧数据库需要手动在 Notion 中删除")

    else:
        print(f"❌ 未知命令: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
