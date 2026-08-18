<h1 align="center">PurrCat Graphs Market</h1>

<p align="center">
    专为 <a href="https://github.com/PurrPod/purrcat">PurrCat</a> 构建的任务图（Graph）市场与注册表中心。
</p>

---

## 1. 简介

Graph 是 PurrCat Agent 的「任务编排中枢」，通过节点（Node）与边（Edge）描述一条完整的多步骤工作流。每个 Graph 是一个独立的 JSON 文件，包含全局变量声明、节点定义与连线关系，由运行时引擎解析并按拓扑顺序执行。

* **节点类型**：输入/输出、文件读写、模板渲染、消息卡片构建、Agent 循环、Python 执行器等。
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
    └── <graph-name>.json # 每个 graph 对应一个独立 JSON 文件
```

---

## 3. 已收录 Graph 清单

*(注：本列表由自动化流水线实时生成)*

<!-- GRAPHS:START -->
| 图名 (Install ID) | 描述 |
| :--- | :--- |
| `skill_eval` | 自动化技能沙盒盲测：支持断言级 (Assertion) 的细粒度评判与官方 grading 标准统计。 |
<!-- GRAPHS:END -->

---

## 4. 统一字段规范

每个 graph 的 JSON 文件必须包含以下顶层字段：

```json
{
  "version": "2.0",
  "name": "skill_eval",
  "description": "自动化技能沙盒盲测：支持断言级 (Assertion) 的细粒度评判与官方 grading 标准统计。",
  "global_schema": { ... },
  "nodes": [ ... ],
  "edges": [ ... ]
}
```

### 必填字段

* **`name`** (必填): 安装标识，必须与 JSON 文件名（去掉 `.json`）完全一致。
* **`description`** (必填): 一句话描述该 Graph 的用途。

### 可选字段

* **`version`**: Graph 规范版本。
* **`global_schema`**: 全局输入变量的类型声明与必填校验。
* **`nodes`**: 节点定义数组，每个节点包含 `id` / `type` / `name` / `position` / `config`。
* **`edges`**: 连边定义数组，每条边包含 `source` / `target` / `sourceHandle` / `targetHandle`。

### 命名一致性要求

**JSON 文件名（去掉 `.json`） = 文件内的 `name` 字段**

两者必须严格一致，CI 构建时会自动校验。例如 graph `skill_eval`：

```
graphs/
└── skill_eval.json      # ✅ name: "skill_eval"
```

（即 `graphs/graphs/skill_eval.json`，位于嵌套的 `graphs/` 官方目录下）

---

## 5. 收录方式

在 `graphs/` 目录下新建 `<graph-name>.json`，包含：

1. `name`：与文件名一致的图名。
2. `description`：一句话描述。
3. `global_schema` / `nodes` / `edges` 等运行时所需的图定义字段。

提交 Pull Request。CI 会自动校验：

* 文件名与 `name` 字段严格一致；
* JSON 可解析且包含 `name` 与 `description` 两个必填字段；
* `description` 不能为空。

PR 审核通过并合并后，流水线将自动把所有 graph 合并为全局注册表 `registry.json`，并重写本文档的 graph 清单。
