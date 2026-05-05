# OpenAlex 定时论文检索

这个工作流把“定时触发”“Reviewer 判断研究缺口”和“Executor 执行检索”分开。

当前推荐两段式：

1. 如果定时任务由 Codex 唤醒，Codex 先分析 `research-wiki/` 和最近运行记录，把审阅结论写入 `lit-watch/codex_reviewer_direction.md`。
2. ARIS 读取这个审阅结论，只负责执行 `openalex-search` 检索、导出和整理。

这种方式避免 ARIS 在内部再调用一层 Reviewer 模型，职责更清楚。

传统 ARIS 内部审阅模式仍然可用：

1. 外部调度器定时运行 `scripts/aris_openalex_lit_watch.py`。
2. 脚本读取 `research-wiki/` 中的 `query_pack.md`、`gap_map.md`、`index.md` 和最近日志。
3. 如果没有配置 `reviewer_direction_file`，ARIS 先调用 `LlmReview`，让审阅模型判断当前还缺哪方面研究。
4. Executor 模型读取审阅结果，再调用 `openalex-search` skill。
5. Executor 生成可复现的 OpenAlex query-plan JSON。
6. 先 dry-run 检查每条检索式命中量，再收紧检索式并导出结果。
7. 结果写入 `lit-watch/runs/<timestamp>-<topic>/`，并更新 `research-wiki/`。

## 手动运行一轮

在仓库根目录运行：

```bash
python3 scripts/aris_openalex_lit_watch.py \
  --config configs/openalex_lit_watch.example.json
```

如果只想看 ARIS 将收到的 prompt，不真正调用模型：

```bash
python3 scripts/aris_openalex_lit_watch.py \
  --config configs/openalex_lit_watch.example.json \
  --print-prompt
```

如果要使用“Codex 审阅，ARIS 执行”的方式，先让 Codex 或人工更新：

```text
lit-watch/codex_reviewer_direction.md
```

然后运行：

```bash
python3 scripts/aris_openalex_lit_watch.py \
  --config configs/llm_industry_lit_watch.json
```

如果想固定一个方向：

```bash
python3 scripts/aris_openalex_lit_watch.py \
  --topic "physics-informed neural networks adaptive sampling" \
  --lookback-days 90
```

## 输出位置

每次运行会创建一个目录：

```text
lit-watch/runs/<timestamp>-<topic>/
  prompt.md
  watch_manifest.json
  reviewer_direction.md
  aris.stdout.txt
  aris.stderr.txt
  openalex_queries.json
  openalex/
    manifest.json
    query_counts.csv
    all_results_deduped.csv
    all_results_deduped.jsonl
  SUMMARY.md
```

其中最重要的是：

- `openalex_queries.json`：本轮真实使用的检索式。
- `reviewer_direction.md`：Reviewer 对当前知识库的审查结论，以及建议补充的研究方向。
- `openalex/query_counts.csv`：每条检索式的命中量。
- `openalex/all_results_deduped.csv`：去重后的论文元数据。
- `SUMMARY.md`：Reviewer 建议、Executor 执行方式、本轮检索整理和下一步建议。

## macOS cron 示例

先确认绝对路径：

```bash
pwd
which python3
```

然后编辑 crontab：

```bash
crontab -e
```

每天凌晨 3 点运行一轮：

```cron
0 3 * * * cd "/Users/zhuyingqin/Documents/New project/Auto-claude-code-research-in-sleep" && /opt/homebrew/bin/python3 scripts/aris_openalex_lit_watch.py --config configs/openalex_lit_watch.example.json >> lit-watch/cron.log 2>&1
```

## 配置说明

配置文件在 `configs/openalex_lit_watch.example.json`：

- `topic`: 为 `null` 时，ARIS 会根据 `research-wiki` 自动选择方向；填字符串时，会以该方向为锚点。
- `lookback_days`: 默认只检索最近 30 天的新论文。
- `max_results_per_query`: 默认每条检索式最多导出 300 条，避免定时任务一次拉太多。设为 `0` 表示完整导出所有匹配结果。
- `permission_mode`: 默认为 `danger-full-access`，因为 OpenAlex 导出需要运行 Python 脚本并写入结果目录。
- `allowed_tools`: 限制 ARIS 本轮可用工具。Codex 审阅模式通常只需要 `Skill`、文件读写、检索和 `bash`；ARIS 内部审阅模式才需要加入 `LlmReview`。
- `reviewer_direction_file`: 可选。设置后表示 Reviewer 步骤已由 Codex 或人工完成，ARIS 不再调用 `LlmReview`，只执行检索和整理。

## OpenAlex 要求

检索必须先经过 Reviewer 审查，再通过 `openalex-search` skill 使用显式 query-plan JSON。常见结构：

```json
{
  "project": "example",
  "shared": {
    "filter": "from_publication_date:2026-03-28,to_publication_date:2026-04-27,type:article,language:en,is_retracted:false,is_paratext:false",
    "sort": "relevance_score:desc"
  },
  "queries": [
    {
      "name": "core_topic",
      "search": "\"physics-informed neural network\" \"adaptive sampling\""
    },
    {
      "name": "precise_title_abstract",
      "filter": "title_and_abstract.search:physics-informed neural network,title_and_abstract.search:adaptive sampling"
    }
  ]
}
```

如果你有 `OPENALEX_API_KEY` 或 `OPENALEX_MAILTO`，可以在 shell 环境中设置，导出脚本会自动读取。
