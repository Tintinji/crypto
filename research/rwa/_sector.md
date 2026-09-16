# 赛道：RWA / 代币化基金与实物

快照：`2026-09-16T21:13:43Z`。13 个标的，合计 MC **$41.7B**。逻辑链 **D**。FIGR_HELOC 独占 **$22.7B**。

## 这个市场在卖什么

RWA 卖的是 **把传统金融现金流搬到链上的份额**：国债、回购、AAA CLO、HELOC、黄金、VC 基金份额。买方要的是：

- 现金管理替代（BUIDL、USYC、USDY、USTB、JTRSY、EUTBL、EURSAFO）
- 黄金链上代理（XAUT、PAXG）
- 信贷风险溢价（FIGR_HELOC、JAAA）
- 协议治理/费用（ONDO）
- 基金 LP 份额（BCAP）

价格应贴近 **NAV / 本金**，不是成长股曲线。CoinGecko 把它们排进「加密市值」会造成虚假的「第 9 大加密货币」观感——FIGR_HELOC 约 $1.01，是贷款本金代币，不是风险资产贝塔。

## 分层

| 组 | 标的 | 定价锚 |
|---|---|---|
| 现金与 T-bill | BUIDL、USYC、USDY、USTB、JTRSY、EUTBL、EURSAFO | NAV、赎回 T+、牌照 |
| 黄金 | XAUT、PAXG | 金价 × 盎司托管，折溢价 |
| 信贷 | FIGR_HELOC、JAAA | 信用利差、逾期、提前还款 |
| 协议代币 | ONDO | 发行与分发费用，不是 NAV |
| 基金份额 | BCAP | PE/VC NAV，流动性折价 |

USYC Llama 价 **1.137**、USDY **1.143**，说明它们是 **计息份额**（净值累积），不是 $1 稳定币。分析时用份额变化和 NAV，不用「涨了 14%」。

## 拥挤点

- 把 RWA 算进加密市值会扭曲「山寨季」统计。本仓库单独成赛道就是为了避免和 SOL 比涨跌。
- 代币化国债的护城河几乎不在链上，而在 **发行方牌照 + 经纪商分发**。BlackRock BUIDL 的分发强于大多数 crypto-native 发行人。
- FIGR_HELOC 的 $22B 依赖 CoinGecko 对 Provenance 资产的供给认定；二级流动性是否匹配市值，是空方第一刀。
- 利率下行压缩现金管理产品的名义收益，但增加债券/信贷份额的价格。

## 单币写作要求

稳定币赛道的 USDT/USDC 是现金管理产品的竞品。ONDO 用链 A 的费用逻辑，其它用 NAV/信用逻辑。禁止给 FIGR_HELOC 写「突破前高」式加密研报。
