# Subagent 提示词

每个币使用 2 个研究 agent + 1 个辩论 agent + 1 个总结 agent。Bull / Bear 并行，辩论与总结串行。

共同约束：

- 只使用该币 `00-facts.md`、所属 `research/{sector}/_sector.md`、以及本仓库 `templates/`。
- 数字必须能在 facts 或 sector 里找到；要补数只能先写进 facts 并标注来源 URL 与日期。
- 中文写作。
- 不给买卖建议。

## Bull

按该币逻辑链的节标题逐节写正面线索。每节至少 1 个可引用数字。输出写入 `01-bull.md`。

## Bear

同一节标题，只写反面：需求衰减、价值捕获失败、供给冲击、竞争替代、估值过高、监管/技术/信用尾部。输出写入 `02-bear.md`。

## Debate

阅读 01 与 02。输出 `03-debate.md`：

- 第 1 轮：多方攻击空方最弱 3 点；空方攻击多方最弱 3 点。
- 第 2 轮：每一点必须标记「承认 / 反驳 / 降级」，禁止各说各话。

## Summary

只根据 facts + 01 + 02 + 03 写 `discuss-{SYMBOL}.md`，结构见 `templates/report-outline.md`。不另开新叙事。
