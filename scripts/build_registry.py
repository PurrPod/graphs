#!/usr/bin/env python3
"""构建 graphs 的 registry.json 并同步 README.md

目录约定:
  graphs/<graph-name>/graph.json   graph 定义（必需）
  graphs/<graph-name>/asset/...    graph 附带资源（可选）
  每个 graph 是一个独立文件夹，registry 记录完整文件清单供客户端整目录下载

统一字段: name / description (英文) / description-zh (中文)  (graph 文件本身的其它字段如 nodes/edges 等由运行时解析，不进入注册表)
"""
import json
import os
import sys

REGISTRY_FILE = "registry.json"
README_FILE = "README.md"
REPO_URL = "https://github.com/PurrPod/graphs"

GRAPHS_DIR = "graphs"

REQUIRED_FIELDS = ("name", "description", "description-zh")


def fail(msg):
    print(f"[Error] {msg}")
    sys.exit(1)


def load_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        fail(f"无法读取或解析 {filepath}: {e}")


def list_graph_files(graph_dir):
    """列出 graph 文件夹内全部文件的相对路径（含 graph.json 与 asset/*），按路径排序"""
    rels = []
    for root, _dirs, files in os.walk(graph_dir):
        for fn in files:
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, graph_dir).replace(os.sep, "/")
            rels.append(rel)
    return sorted(rels)


def validate_entry(graph_dir, entry, expected_name):
    """校验单个 graph 条目"""
    graph_json = os.path.join(graph_dir, "graph.json")
    if not isinstance(entry, dict):
        fail(f"[{graph_json}] 内容必须是一个 JSON 对象")

    for field in REQUIRED_FIELDS:
        if field not in entry:
            fail(f"[{graph_json}] 缺少必填字段 '{field}'")

    # 校验 1: name 必须与文件夹名一致
    name = str(entry.get("name", "")).strip()
    if not name:
        fail(f"[{graph_json}] 'name' 不能为空")
    if name != expected_name:
        fail(f"[{graph_json}] 'name' ('{name}') 必须与文件夹名 ('{expected_name}') 一致")

    # 校验 2: description / description-zh 不能为空
    if not str(entry.get("description", "")).strip():
        fail(f"[{graph_json}] 'description' 不能为空")
    if not str(entry.get("description-zh", "")).strip():
        fail(f"[{graph_json}] 'description-zh' 不能为空")


def normalize(entry, graph_name, files):
    """输出为统一的注册表条目，仅保留约定的字段"""
    return {
        "name": entry["name"],
        "description": entry["description"],
        "description-zh": entry["description-zh"],
        "graph-link": f"{REPO_URL}/tree/main/{GRAPHS_DIR}/{graph_name}",
        "files": files,
    }


def scan_graphs():
    """扫描 graphs/ 下的 graph 文件夹（每个文件夹必须含 graph.json）"""
    entries = []
    if not os.path.isdir(GRAPHS_DIR):
        return entries

    for item in sorted(os.listdir(GRAPHS_DIR)):
        graph_dir = os.path.join(GRAPHS_DIR, item)
        if item.startswith(".") or not os.path.isdir(graph_dir):
            continue

        graph_json = os.path.join(graph_dir, "graph.json")
        if not os.path.isfile(graph_json):
            fail(f"[{graph_dir}] 缺少 graph.json")

        entry = load_json(graph_json)
        validate_entry(graph_dir, entry, item)
        entries.append((item, normalize(entry, item, list_graph_files(graph_dir))))
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
        desc = str(info["description-zh"]).replace("|", "\\|")
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
        "version": "3.0",
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
