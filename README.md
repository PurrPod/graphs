<h1 align="center">PurrCat Graphs Market</h1>

<p align="center">
    专为 <a href="https://github.com/PurrPod/purrcat">PurrCat</a> 构建的任务图（Graph）市场与注册表中心。
</p>

---

## 1. 简介

Graph 是 PurrCat Agent 的「任务编排中枢」，通过节点（Node）与边（Edge）描述一条完整的多步骤工作流。每个 Graph 是一个**独立文件夹**，内含 `graph.json`（全局变量声明、节点定义与连线关系）与可选 `asset/`（看板等静态资源），由运行时引擎解析并按拓扑顺序执行。

* **单元结构**：`<graph-name>/` 文件夹，含 `graph.json` + `asset/`。
* **节点类型**：输入/输出、文件读写、模板渲染、消息卡片构建、命令执行、自定义输入、Agent 循环等。
* **连线**：通过 `edges` 描述节点之间的数据流向，支持 `sourceHandle` / `targetHandle` 进行字段级映射。

---

## 2. 仓库架构设计

```text
graphs/
├── .github/workflows/   # CI/CD 自动化构建流水线
├── scripts/             # 注册表构建与校验脚本
├── registry.json        # 全局注册表 (由 Action 自动生成)
├── README.md            # 说明文档与 Graph 列表 (由 Action 自动更新)
│
└── graphs/              # 官方 graph (源码直接在本仓库维护)
    └── <graph-name>/    # 每个 graph 对应一个独立文件夹
        ├── graph.json   # graph 定义 (必需)
        └── asset/       # 静态资源：看板 html 等 (可选)
```

---

## 3. 已收录 Graph 清单

*(注：本列表由自动化流水线实时生成)*

<!-- GRAPHS:START -->
| 图名 (Install ID) | 描述 |
| :--- | :--- |
| `skill_eval` | [正在调试适配新架构]自动化技能沙盒盲测：支持断言级 (Assertion) 的细粒度评判与官方 grading 标准统计。 |
| `trading` | [正在调试适配新架构]股票操作分析 |
<!-- GRAPHS:END -->

---

## 4. 统一字段规范

每个 graph 文件夹内的 `graph.json` 必须包含以下顶层字段：

```json
{
  "version": "2.0",
  "name": "skill_eval",
  "description": "Automated blind skill evaluation in a sandbox: supports fine-grained assertion-level grading and statistics against official grading standards.",
  "description-zh": "自动化技能沙盒盲测：支持断言级 (Assertion) 的细粒度评判与官方 grading 标准统计。",
  "global_schema": { ... },
  "nodes": [ ... ],
  "edges": [ ... ],
  "dashboard": "purrcat://graph/skill_eval/asset/dashboard.html"
}
```

### 必填字段

* **`name`** (必填): 安装标识，必须与所在文件夹名完全一致。
* **`description`** (必填): 英文描述，一句话描述该 Graph 的用途。
* **`description-zh`** (必填): 中文描述，用于市场中文展示。

### 可选字段

* **`version`**: Graph 规范版本。
* **`global_schema`**: 全局输入变量的类型声明与必填校验。
* **`nodes`**: 节点定义数组，每个节点包含 `id` / `type` / `name` / `position` / `config`。
* **`edges`**: 连边定义数组，每条边包含 `source` / `target` / `sourceHandle` / `targetHandle`。
* **`dashboard`**: 看板地址（uri 或 url）。支持单个字符串，或多看板数组 `[{ "name": "...", "url": "..." }]`；指向 `asset/` 下的 html 时用 `purrcat://graph/{name}/asset/{file}`。

### 命名一致性要求

**文件夹名 = 文件内的 `name` 字段**

两者必须严格一致，CI 构建时会自动校验。例如 graph `skill_eval`：

```
graphs/
└── skill_eval/
    ├── graph.json       # ✅ name: "skill_eval"
    └── asset/           # (可选) 看板等静态资源
```

---

## 5. 收录方式

在 `graphs/` 目录下新建 `<graph-name>/graph.json`（可含 `asset/`），包含：

1. `name`：与所在文件夹名一致的图名。
2. `description` / `description-zh`：英文与中文描述。
3. `global_schema` / `nodes` / `edges` 等运行时所需的图定义字段。
4. （可选）`dashboard`：看板 uri/url，或归档到 `asset/` 下的 html。

提交 Pull Request。CI 会自动校验：

* 文件夹名与 `name` 字段严格一致；
* `graph.json` 可解析且包含 `name`、`description` 与 `description-zh` 三个必填字段；
* `description` 与 `description-zh` 不能为空。

PR 审核通过并合并后，流水线将自动扫描 `graphs/` 下的 graph 文件夹（含 `asset/*` 资源清单）合并为全局注册表 `registry.json`，并重写本文档的 graph 清单。
