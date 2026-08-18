#!/usr/bin/env python3
"""构建 graphs 的 registry.json 并同步 README.md

目录约定:
  graphs/<graph-name>.json   每个 graph 对应一个独立 JSON 文件

统一字段: name / description  (graph 文件本身的其它字段如 nodes/edges 等由运行时解析，不进入注册表)
"""
import json
import os
import sys

REGISTRY_FILE = "registry.json"
README_FILE = "README.md"
REPO_URL = "https://github.com/PurrPod/graphs"

GRAPHS_DIR = "graphs"

REQUIRED_FIELDS = ("name", "description")


def fail(msg):
    print(f"[Error] {msg}")
    sys.exit(1)


def load_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        fail(f"无法读取或解析 {filepath}: {e}")


def validate_entry(filepath, entry, expected_name):
    """校验单个 graph 条目"""
    if not isinstance(entry, dict):
        fail(f"[{filepath}] 内容必须是一个 JSON 对象")

    for field in REQUIRED_FIELDS:
        if field not in entry:
            fail(f"[{filepath}] 缺少必填字段 '{field}'")

    # 校验 1: name 必须与文件名 (去掉 .json) 一致
    name = str(entry.get("name", "")).strip()
    if not name:
        fail(f"[{filepath}] 'name' 不能为空")
    if name != expected_name:
        fail(f"[{filepath}] 'name' ('{name}') 必须与文件名 ('{expected_name}') 一致")

    # 校验 2: description 不能为空
    if not str(entry.get("description", "")).strip():
        fail(f"[{filepath}] 'description' 不能为空")


def normalize(entry, filename):
    """输出为统一的注册表条目，仅保留约定的字段"""
    return {
        "name": entry["name"],
        "description": entry["description"],
        "graph-link": f"{REPO_URL}/blob/main/{GRAPHS_DIR}/{filename}",
    }


def scan_graphs():
    """扫描 graphs/ 下的 graph JSON 文件"""
    entries = []
    if not os.path.isdir(GRAPHS_DIR):
        return entries

    for item in sorted(os.listdir(GRAPHS_DIR)):
        if item.startswith(".") or not item.endswith(".json"):
            continue
        filepath = os.path.join(GRAPHS_DIR, item)
        if not os.path.isfile(filepath):
            continue

        expected_name = item[: -len(".json")]
        entry = load_json(filepath)
        validate_entry(filepath, entry, expected_name)
        entries.append((expected_name, normalize(entry, item)))
    return entries


def generate_markdown_table(entries):
    """生成 Markdown 格式表格"""
    lines = [
        "| 图名 (Install ID) | 描述 |",
        "| :--- | :--- |",
    ]

    if not entries:
        lines.append("| *(虚位以待)* | 期待您的收录！ |")
        return "\n".join(lines) + "\n"

    for short_id, info in sorted(entries):
        name = info["name"]
        desc = str(info["description"]).replace("|", "\\|")
        lines.append(f"| `{name}` | {desc} |")

    return "\n".join(lines) + "\n"


def replace_between_tags(text, start_tag, end_tag, new_content):
    """将文本中 start_tag 与 end_tag 之间的内容替换为 new_content"""
    start_idx = text.find(start_tag)
    end_idx = text.find(end_tag)
    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        head = text[: start_idx + len(start_tag)]
        tail = text[end_idx:]
        return f"{head}\n{new_content}{tail}"
    return text


def update_readme(entries):
    """回写更新 README.md 中的表格"""
    if not os.path.exists(README_FILE):
        return
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    content = replace_between_tags(
        content, "<!-- GRAPHS:START -->", "<!-- GRAPHS:END -->",
        generate_markdown_table(entries),
    )

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    print(f"扫描 {GRAPHS_DIR}/ 下的 graph ...")
    entries = scan_graphs()

    # 校验: 不允许同名 graph
    names = [name for name, _ in entries]
    duplicates = sorted({n for n in names if names.count(n) > 1})
    if duplicates:
        fail(f"存在同名 graph: {', '.join(duplicates)}")

    registry = {
        "version": "2.0",
        "repository": REPO_URL,
        "graphs": [info for _, info in entries],
    }

    print(f"生成 {REGISTRY_FILE} ...")
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("更新 README.md ...")
    update_readme(entries)

    print(f"构建与校验完成！共 {len(entries)} 个 graph。")


if __name__ == "__main__":
    main()
