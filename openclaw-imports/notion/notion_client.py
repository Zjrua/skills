#!/usr/bin/env python3
"""
Notion API Client for OpenClaw
支持页面、数据库、搜索等核心操作
"""

import os
import json
import sys
import re
from typing import Optional, Dict, List, Any

try:
    from notion_client import Client
except ImportError:
    print("Error: notion-client not installed. Run: pip install notion-client")
    sys.exit(1)


class NotionHelper:
    """Notion 操作辅助类"""

    def __init__(self, token: Optional[str] = None):
        token = token or os.getenv("NOTION_TOKEN")
        if not token:
            raise ValueError("NOTION_TOKEN environment variable not set")
        self.client = Client(auth=token)

    @staticmethod
    def extract_page_id(url_or_id: str) -> str:
        """从 URL 或原始 ID 中提取 Page ID"""
        # Notion ID 格式：32 个字符，可能带连字符
        pattern = r'([a-f0-9]{32})'
        match = re.search(pattern, url_or_id.lower().replace('-', ''))
        if match:
            return match.group(1)
        return url_or_id

    def get_page(self, page_id: str) -> Dict[str, Any]:
        """获取页面信息"""
        clean_id = self.extract_page_id(page_id)
        return self.client.pages.retrieve(page_id=clean_id)

    def get_page_content(self, page_id: str) -> List[Dict[str, Any]]:
        """获取页面的所有子块（递归）"""
        clean_id = self.extract_page_id(page_id)
        blocks = self.client.blocks.children.list(block_id=clean_id)
        return blocks.get("results", [])

    def format_page_text(self, page_id: str) -> str:
        """将页面内容格式化为纯文本"""
        page = self.get_page(page_id)
        title = self._get_page_title(page)
        blocks = self.get_page_content(page_id)

        lines = [f"# {title}", ""]

        for block in blocks:
            lines.append(self._format_block(block))

        return "\n".join(lines)

    def _get_page_title(self, page: Dict[str, Any]) -> str:
        """从页面属性中提取标题"""
        property_obj = page.get("properties", {})
        title_property = property_obj.get("title", property_obj.get("Name", {}))

        if title_property.get("type") == "title":
            title_array = title_property.get("title", [])
            if title_array:
                return title_array[0].get("plain_text", "")

        return "Untitled"

    def _format_block(self, block: Dict[str, Any]) -> str:
        """格式化单个块内容"""
        block_type = block.get("type", "")
        content = block.get(block_type, {})

        if block_type == "paragraph":
            return content.get("rich_text", [{}])[0].get("plain_text", "")
        elif block_type == "heading_1":
            text = content.get("rich_text", [{}])[0].get("plain_text", "")
            return f"# {text}"
        elif block_type == "heading_2":
            text = content.get("rich_text", [{}])[0].get("plain_text", "")
            return f"## {text}"
        elif block_type == "heading_3":
            text = content.get("rich_text", [{}])[0].get("plain_text", "")
            return f"### {text}"
        elif block_type == "bulleted_list_item":
            text = content.get("rich_text", [{}])[0].get("plain_text", "")
            return f"- {text}"
        elif block_type == "numbered_list_item":
            text = content.get("rich_text", [{}])[0].get("plain_text", "")
            return f"1. {text}"
        elif block_type == "to_do":
            text = content.get("rich_text", [{}])[0].get("plain_text", "")
            checked = content.get("checked", False)
            status = "x" if checked else " "
            return f"- [{status}] {text}"
        elif block_type == "code":
            text = content.get("rich_text", [{}])[0].get("plain_text", "")
            return f"```\n{text}\n```"
        elif block_type == "divider":
            return "---"
        else:
            return f"[{block_type}]"

    def create_page(self, parent_id: str, title: str, properties: Optional[Dict] = None) -> Dict[str, Any]:
        """在指定父级下创建新页面"""
        clean_parent = self.extract_page_id(parent_id)
        page_data = {
            "parent": {
                "page_id": clean_parent
            },
            "properties": {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            }
        }

        if properties:
            page_data["properties"].update(properties)

        return self.client.pages.create(**page_data)

    def update_page_properties(self, page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """更新页面属性"""
        clean_id = self.extract_page_id(page_id)
        return self.client.pages.update(page_id=clean_id, properties=properties)

    def query_database(self, database_id: str, filter_conditions: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """查询数据库"""
        clean_id = self.extract_page_id(database_id)
        query_params = {"database_id": clean_id}

        if filter_conditions:
            query_params["filter"] = filter_conditions

        result = self.client.databases.query(**query_params)
        return result.get("results", [])

    def create_database_record(self, database_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """在数据库中创建新记录"""
        clean_id = self.extract_page_id(database_id)
        return self.client.pages.create(
            parent={"database_id": clean_id},
            properties=properties
        )

    def search(self, query: str) -> List[Dict[str, Any]]:
        """在工作空间中搜索"""
        result = self.client.search(query=query)
        return result.get("results", [])

    def delete_page(self, page_id: str) -> Dict[str, Any]:
        """删除页面（归档）"""
        clean_id = self.extract_page_id(page_id)
        return self.client.pages.update(page_id=clean_id, archived=True)


def main():
    """CLI 接口"""
    if len(sys.argv) < 2:
        print("Usage: notion_client.py <command> [args...]")
        print("Commands:")
        print("  get <page_id>      - Get page content as text")
        print("  search <query>     - Search workspace")
        print("  list <database_id> - List database records")
        sys.exit(1)

    try:
        client = NotionHelper()
        command = sys.argv[1]

        if command == "get":
            if len(sys.argv) < 3:
                print("Error: page_id required")
                sys.exit(1)
            page_id = sys.argv[2]
            print(client.format_page_text(page_id))

        elif command == "search":
            if len(sys.argv) < 3:
                print("Error: query required")
                sys.exit(1)
            query = sys.argv[2]
            results = client.search(query)
            print(json.dumps(results, indent=2, ensure_ascii=False))

        elif command == "list":
            if len(sys.argv) < 3:
                print("Error: database_id required")
                sys.exit(1)
            database_id = sys.argv[2]
            records = client.query_database(database_id)
            print(json.dumps(records, indent=2, ensure_ascii=False))

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
