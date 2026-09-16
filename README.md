# crypto

市值前 100 加密资产的对抗辩论备忘库。快照按 CoinGecko 原样收录（含稳定币、代币化基金），不先做「可投资筛选」。

## 怎么读

1. [universe/sectors.md](universe/sectors.md) — 赛道分组与覆盖清单
2. [research/_index.md](research/_index.md) — 总目录与完成状态
3. 每个赛道先读 `research/{sector}/_sector.md`，再读单币
4. 单币目录：`research/{sector}/discuss-{SYMBOL}/`

```text
discuss-SYMBOL/
  00-facts.md        统一量化事实包（多空必须引用）
  01-bull.md         正面线索（逻辑链逐节）
  02-bear.md         反面论据（同一节标题）
  03-debate.md       两轮交锋
  discuss-SYMBOL.md  总结稿（对外主文件）
```

方法论与提示词：[templates/logic-chains.md](templates/logic-chains.md)、[templates/report-outline.md](templates/report-outline.md)、[templates/agent-prompts.md](templates/agent-prompts.md)。

重建快照：`python3 scripts/build_universe.py`（依赖 `/tmp` 下已拉取的 CoinGecko / DefiLlama JSON）。

## 数据截止

当前宇宙快照见 `universe/top100.json` 的 `snapshot_utc`。价格与市值来自 CoinGecko `/coins/markets`；TVL、费用、稳定币流通来自 DefiLlama。对不上的字段写「未知」，辩论中不得补造。

研究备忘，非投资建议。
