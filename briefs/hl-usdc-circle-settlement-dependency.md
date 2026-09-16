# HL 对 USDC / Circle 的单点依赖：结算资产、清算冲击路径、对照 CME 与币安

**受众：** 首席合成  
**快照时点：** 2026-09-16（UTC 晚间；链上 RPC + Hyperliquid info API + DefiLlama 同步拉取）  
**立场：** 结算资产与单点依赖，不是交易观点。

---

## 一句话

Hyperliquid 的清算所把**记账单位、保证金、出入金轨道和合规开关**同时押在 Circle 的 USDC 上；匹配引擎在 USDC 被暂停/冻结后仍能继续跑，但那只是把坏账留在账本里。若 USDC 出问题，**HL 比币安更脆**——币安的主结算层是 USDT，可以把 USDC 切成卫星盘；HL 没有同量级的第二结算货币。对照 CME：CME 用美元现金 + 国债（有发剪、有违约瀑布），HL 用的是「被 Circle 可编程冻结的美元 IOU」。

---

## 1. 数字仪表盘（可复核）

### 1.1 保证金与稳定币占比

| 指标 | 数字 | 含义 | 来源 |
|---|---|---|---|
| HyperEVM 原生 USDC `totalSupply` | **62.6436 亿** | Circle 在 HyperEVM（CCTP domain 19）铸造的原生 USDC | HyperEVM RPC `totalSupply()` @ `0xb88339CB7199b77E23DB6E890353E22632Ba630f` |
| DefiLlama「Hyperliquid L1」USDC | **67.103 亿** | 链上稳定币统计口径（含 L1 记账差异） | [DefiLlama stablecoins](https://stablecoins.llama.fi) |
| HL L1 稳定币合计 | **68.255 亿** | USDC 占比 **98.3%** | 同上：USDC 67.10 / USDT 0.855 / USDe 0.087 / USDH 0.078 |
| USDC 全球流通 | **737.3 亿** | HL 是 USDC 第二大链（**9.10%**），仅次于以太坊 63.2% | DefiLlama；CoinGecko mcap ≈ $73.6B、现货 0.9997 |
| Perp 未平仓（OI，标记价） | **102.62 亿美元** | 234 个合约；BTC 29.1 / ETH 23.6 / HYPE 16.2 | `POST https://api.hyperliquid.xyz/info` `metaAndAssetCtxs` |
| 24h Perp 名义成交 | **67.57 亿美元** | 同一接口 `dayNtlVlm` | 同上 |
| CoinGecko 衍生品 OI（对照） | HL 187,349 BTC；币安期货 417,539 BTC | 量级：HL 约为币安期货 OI 的 45%（不同口径） | [Coingecko derivatives/exchanges](https://api.coingecko.com/api/v3/derivatives/exchanges) |
| HyperCore 现货 USDC 供给 | **4.511 亿**，`markPx = 1.0` | **记账单位被硬编码为 1**，不是市场价格 | info `tokenDetails` tokenId `0x6d1e7cde53ba9467b783cb7c530ce054` |
| 投资组合保证金 USDT 全局供给/借款上限 | 0.50 亿 / 0.10 亿 | 无法替代 USDC 结算层 | [HL portfolio margin docs](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/portfolio-margin.md) |
| USDC 借款上限（PM） | 10 亿供给 / 5 亿借款 | 仍以 USDC 为计价与清算货币 | 同上 |

**保证金占比结论：** 规范 Perp 是「USDC 保证金 + 多数合约 USDT 计价的 quanto」。HYPE/BTC 在投资组合保证金下 LTV 仅 0.5，USDT 上限可忽略。**清算所风险资本 ≥98% 是 Circle USDC**；其余稳定币是点缀。

### 1.2 托管与桥（真正可被冻结的美元）

| 位置 | 地址 | USDC 余额 | 控制者 | 状态（快照） |
|---|---|---|---|---|
| **CoreDepositWallet**（HyperEVM） | `0x6B9E773128f453f5c2C60935Ee2DE2CBc5390A24` | **6.0569 亿** | Circle 合约（Pausable + 代理） | `paused=false`，`isBlacklisted=false` |
| CctpForwarder（HyperEVM） | `0xb21D281DEdb17AE5B501F6AA8256fe38C4e45757` | 1.41 万 | Circle | 中转，非库存 |
| **遗留 Arbitrum 桥** | `0x2Df1c51E09aECF9cacB7bc98cB1742757f163dF7` | **4.5118 亿** | HL 验证者 2/3 热签 | 未暂停、未拉黑 |
| Arbitrum `CctpExtension` | `0xA95d9c1F655341597C94393fDdc30cf3c08E4fcE` | 0.77 万 | Circle | 瞬时库存 |
| DefiLlama 协议 TVL | Arb **4.507 亿** + HL L1 **62.07 亿** = **66.58 亿** | 口径混了 HyperEVM DeFi + 桥 | [DefiLlama Hyperliquid](https://defillama.com/protocol/hyperliquid) |

**拆账（避免把 DeFi TVL 当成保证金）：**

- HyperEVM 上 62.64 亿原生 USDC 里，**只有 6.06 亿锁在 CoreDepositWallet**，对应 Circle 文档所说：「HyperCore 余额是协议记账，原生 USDC 留在 CoreDepositWallet」。
- 遗留 Arb 桥 4.51 亿与 HyperCore 现货 USDC `totalSupply` 4.51 亿几乎 1:1。这强烈暗示：**旧桥仍在给一截 HyperCore USDC 做托管，CCTP 默认入金走 Perp（`destinationDex=0`）**。
- **HyperCore 可被 Circle/验证者直接卡住的结算库存 ≈ 6.06 + 4.51 = 10.57 亿 USDC。**
- 其余约 **56.6 亿** 在 HyperEVM 钱包/DeFi，数分钟内可打进清算所，也可经 CCTP 逃离。它不是保证金，但是**挤兑燃料**。

### 1.3 清算缓冲区（相对 OI 极薄）

| 组件 | 地址 | 权益 | 相对 102.6 亿 OI |
|---|---|---|---|
| HLP（协议金库） | `0xdfc24b077bc1425ad1dea75bcb6f8158e10df303` | **1.875 亿 USDC** | 1.83% |
| HLP Liquidator 子策略 | `0x2e3d94f0562703b25c83308a05046ddaf9a8dd14` | **100 万美元** | 0.01% |
| Liquidator 历史 PnL | allTimePnl ≈ **+4352 万** | 说明常态有利润，但**当前库存被抽回母金库** | info `vaultDetails` |
| HLP 锁定期 | 最近一次入金后 **4 天** | 挤兑时金库资本抽不走，也补不进来 | [HL protocol vaults](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/vaults/protocol-vaults) |

真·偿付不变量不是 HLP，是 **ADL**（账户权益转负时，按盈利×杠杆排序，把对手方在前一标记价强平）。HLP 只是订单簿之后的回止，不是 CME 式担保基金。

### 1.4 AQAv2：把协议收入也绑上 Circle / Coinbase

- Circle = **技术部署方**（铸造、赎回、CCTP）；Coinbase = **资金部署方**（储备收益分成）。各押 **50 万 HYPE**（快照价 78.36，合计约 **7836 万 USD** 可罚没）。
- 对照 67 亿 USDC 和 103 亿 OI，罚没金是**象征性对齐**，不是偿付能力。
- USDH 已退出主舞台（DefiLlama 仅 781 万），稳定币竞赛的结果是 **USDC 成为事实标准**，不是多币均衡。

来源：[HL AQAv2](https://hyperliquid.xyz/article/aqav2)、[Circle 博文](https://www.circle.com/blog/circle-expands-support-for-usdc-on-hyperliquid)、[Coinbase 博文](https://www.coinbase.com/en-ca/blog/coinbase-and-hyperliquid-aligning-markets-on-hyperliquid-to-usdc)、[HL AQA 文档](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/aligned-quote-assets.md)。

---

## 2. 依赖拓扑：谁能关掉哪一扇门

```
用户 USDC（Arb / ETH / Sol / …）
        │  CCTP burn（TokenMessengerV2 / CctpExtension / V2 relayer）
        │  Circle Iris 见证 → HyperEVM mint
        ▼
HyperEVM 原生 USDC  0xb883…630f     ◄── Circle：pause / blacklist / masterMinter
        │  CoreDepositWallet.deposit(amount, dex)
        ▼
CoreDepositWallet  0x6b9e…0a24     ◄── Circle：pause、owner、proxy upgrade
        │  CoreWriter 预编译（记账，不是转 ERC20）
        ▼
HyperCore 清算所 USDC 额度（Perp dex=0 或 Spot dex=uint32.max）
        │  订单簿清算 → HLP Liquidator → ADL
        │
        ├── 提现回 HyperEVM：system address 调 wallet.transfer()（仍要 USDC 未暂停、钱包未拉黑）
        └── 跨链提现：wallet.coreReceiveWithData → TokenMessengerV2.depositForBurnWithHook
```

**关键合约角色（HyperEVM，链上读值）：**

| 角色 | 地址 |
|---|---|
| CoreDepositWallet owner | `0x438aa6cea4d8a153c35c6bd1e4b6adcfdf869eac` |
| CoreDepositWallet pauser | `0x2da340fde4087c8ad0848ed3f980549fde4f0a59` |
| Proxy admin | `0x8e66c6ac847f06b9502fa2512435a62005f5fb92` |
| 实现 | `0x7537af00779cc053a696e47ebd451b5bc4790da3` |
| USDC owner | `0xb5653bf26797d3271dabf31c616fa2b7b216a053` |
| USDC pauser | `0xebf40e28db4c373d1d73f11fd1926574f618bc9e` |

源码：[circlefin/hyperevm-circle-contracts `CoreDepositWallet.sol`](https://github.com/circlefin/hyperevm-circle-contracts/blob/master/src/CoreDepositWallet.sol)。版权头就是 Circle Internet Group。合约 `Pausable + Rescuable + Initializable`。`_rescueERC20` **禁止救援 USDC 本体**（`Cannot rescue token`），Circle 不能用 rescue 直接掏空保证金；**冻结用的是 USDC.blacklist 和 pause**。

`depositFor` 显式 `require(!token.isBlacklisted(recipient))`。跨链出金路径强制走 `tokenMessenger.depositForBurnWithHook`，且 `whenNotPaused`。

遗留桥仍是验证者托管：[HL docs USDC / Bridge2](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/usdc) — 热验证者权重 **2/3** 签名才能在 Arb 放行提现。迁移到 CCTP 是在**用 Circle 单点换掉验证者桥单点**。

---

## 3. 三条冲击路径（对清算，不是对 PR）

官方清算机：[Liquidations](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/liquidations) → 订单簿市价（>10 万 USDC 先砍 20%，30 秒冷却后全平）→ 权益 < 维持保证金的 2/3 由 HLP liquidator 接手 → 账户转负则 [ADL](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/auto-deleveraging)。标记价三要素中位数，**含币安/OKX/Bybit 权重 3/2/2**（[robust price indices](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/robust-price-indices)）。

合约规格写死：[quanto](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/contract-specifications.md) — 「**不应用 USDC/USDT 汇率**，USDT 计价的 PnL 用 USDC 记账」。

### 路径 A — 脱钩（USDC 不再是 1 美元）

历史锚：2023-03-11 SVB，USDC 现货曾至约 **0.87**。

| 机制 | 实际行为 | 清算后果 |
|---|---|---|
| HyperCore USDC 标记 | `markPx = 1.0` 硬钉 | **抵押品不按市值减记**。账户在「假美元」下仍满足维持保证金 |
| Quanto | BTC 预言机 ≈ USDT，盈亏记 USDC，不乘汇率 | USDC=0.87 时，HL 多头按 USDT 涨幅记账、提现只能拿贬值 USDC → **对 USDT 盘出现系统性基差**：空 HL / 多币安 USDT-M |
| 投资组合保证金里的 `USDT_USDC_oracle` | `1 / HL_spot_oracle_price(USDC)` | 若现货预言机也钉在 1，PM 同样不减记 |
| 加密资产价格 | 标记价吃 CEX | 脱钩若引发 BTC/ETH 崩盘，HL **仍按 CEX 价强平**。这是唯一会立刻点火的通道 |
| 订单簿清算 | 用 USDC 买/卖合约 | 流动性是「假 1 美元」的 USDC。外部做市商拒绝用真美元补货 → 价差炸开、回止/ADL |
| 挤兑 | 56.6 亿 HyperEVM 浮存 + 10.6 亿锁定 | 能跑的走 CCTP；跑不掉的在 HL 内用 1.00 记账交易。HLP 4 天锁仓，**1.88 亿回止 vs 103 亿 OI** |
| 隐藏资不抵债 | 清算所资产是 USDC，负债是「1 美元记账的盈利」 | 若 USDC=0.87，**约 13% 的美元偿付缺口**写在所有赢家身上，直到提现/ADL 实现 |

**这不是「不爆仓所以更安全」。这是把爆仓从保证金引擎推迟到提现与对手方。** 赢家拿到的是脱钩币；输家用脱钩币少赔了真美元。ADL 在前一标记价成交，标记价本身仍按 USDT 世界定价，结算却用烂 USDC。

### 路径 B — 黑名单

Circle FiatToken 的 `blacklist` 冻结该地址的转入、转出、授权。与全局 pause 不同，是**定点手术**。

| 被拉黑对象 | HyperCore 匹配 | 入金 | 出金 | 清算 |
|---|---|---|---|---|
| 用户 EOA（尚未入金） | 无余额 | `transferFrom` 失败 | n/a | 无 |
| 用户 EOA（USDC 已在 CoreDepositWallet，HyperCore 有额度） | **仍可交易**（记账不走 ERC20） | 不能再补保证金 | `wallet.transfer` 到该地址失败；CCTP mint 到被拉黑地址失败 | **可被清算，但用户无法补保** → 被动穿仓概率上升 |
| **CoreDepositWallet 本身** | 账本仍在 | 任何 `transfer` 进钱包失败 | 任何 `transfer`/burn 出钱包失败 | **整座清算所变成封闭岛**：内部强平、ADL 继续，**10.6 亿锁定 USDC 变成不可移动的冻结物** |
| CctpForwarder / TokenMessenger | 已在岛内的仓位不受影响 | 跨链入金断 | 跨链出金断 | 同上，范围限于轨道 |

`depositFor` 在合约层就会拒收被拉黑收款人。合规上这是 Circle 的产品能力；对 HL 则是 **清算所托管地址可被发行方单方面关进小黑屋**。CME 的结算银行做不到「把清算所保证金账户从美元体系里抹掉」而不走法院。

### 路径 C — 暂停（三层独立开关）

1. **USDC.pause（链级）**：该链所有 transfer / approve / mint / burn 停。HyperEVM 一暂停，CoreDepositWallet 的 `transferFrom`、CCTP mint/burn 全停。`balanceOf` 仍可读。来源：[USDC pause 机制](https://chainscorelabs.com/protocol/circle-usdc/implementation-and-integration-patterns/pause-and-unpause-mechanics)。
2. **CoreDepositWallet.pause（门级）**：只关 HyperEVM↔HyperCore 的门。HyperEVM DeFi 仍可转 USDC，但**补保/提现/跨链出金**停。Owner 还能 `disableDex` 关掉 Perp 或 Spot 入金。
3. **CCTP pause（TokenMessenger / MessageTransmitter / TokenMinter）**：跨链 burn/mint/见证停。岛内（HyperEVM↔HyperCore）若 wallet 未暂停仍可动。Iris 见证掉线等价于 CCTP 停。来源：[L2BEAT CCTP v2](https://l2beat.com/interop/protocols/cctpv2)、Circle TokenMessenger 角色。

**清算在暂停下的真实状态：**

- 引擎不断电。维持保证金仍按标记价扫。用户**无法追加保证金**。
- 高杠杆仓位一旦价格朝不利方向跳，只能被订单簿/HLP/ADL 处理。这是「暂停出金 + 继续强平」的组合，比两边都停更狠。
- HLP 无法吸收新 USDC；Liquidator 套筒只有 100 万。大缺口直接 ADL。
- 遗留 Arb 桥是**平行逃生舱**（4.51 亿），但它自己是验证者桥，且正在被弃用。CCTP 暂停时旧桥可能仍工作——直到也被弃用或 USDC-on-Arb 被暂停。

---

## 4. 对照 CME：美元现金 + 国债，不是可编程 IOU

| 维度 | CME Clearing | Hyperliquid |
|---|---|---|
| 计价货币 | 美元（主权货币） | USDC 记账单位（`markPx=1`） |
| 保证金资产 | **美元现金** + 美债（T-bills 0–1y 发剪 **0.5%**；notes/bonds 按久期 1–8%） | 规范 Perp：**100% USDC**；PM 下 HYPE/BTC LTV 50% |
| 现金最低软约束 | 美元保证金的 **30% 须是美元现金**，否则额外费 | 无「真美元」桶 |
| 硬限额 | 现金与美债 **无硬顶**；股票/ETF/金等有硬顶 | USDC 无发剪；USDT 在 PM 里被小帽卡住 |
| 谁能冻结抵押品 | 法院 / OFAC / 结算银行合规，不是代币 `pause()` | Circle `pauser` 一笔交易 |
| 加密作为保证金 | 不在可接受清单；BTC/ETH 期货是**现金结算** | 标的和保证金都在链上，标的还吃 CEX 价 |
| 违约瀑布 | 会员保证金 → 会员担保基金 → CME 出资 → 评估权 | 订单簿 → HLP（1.88 亿）→ **ADL 对手方** |
| 会员结构 | FCM / 清算会员，资本与风险限额 | 钱包即账户，无会员资本垫层 |
| 监管 | CFTC DCO，Reg 39.13(g) 要求保证金资产「信用/市场/流动性风险最小」并定期评估发剪 | 无对等约束 |

来源：[CME Acceptable Collateral](https://www.cmegroup.com/solutions/clearing/financial-and-collateral-management/acceptable-collateral.html)、[Hard Dollar Limits](https://www.cmegroup.com/solutions/clearing/financial-and-collateral-management/hard-dollar-limits.html)、[Cash interest / 30% USD cash](https://www.cmegroup.com/solutions/clearing/financial-and-collateral-management/cash-interest-rates-and-non-cash-collateral-fees.html)、[加密期货 FAQ（现金结算）](https://www.cmegroup.com/articles/faqs/frequently-asked-questions-cryptocurrency-futures.html)。

**结构差异一句话：** CME 的抵押品是「美联储负债 + 财政部负债」，发剪的是利率风险；HL 的抵押品是「Circle 对银行准备金/T-bill 的份额 + 可编程冻结权」。USDC 的储备可能也是国债，但**中间多了一个可 pause/blacklist 的公司，且 HL 对这张代币 0 发剪**。

---

## 5. 若 USDC 出问题：HL 比币安更脆还是更强？

### 结论：在 USDC 事件上，HL 更脆。在「交易所自身爆雷」上，HL 更强。不要把两件事加总成一个分数。

### 5.1 币安的结算结构（对照）

- 主盘仍是 **USDT-M**。2026-09-01 PoR：USDT 用户净负债 **323.08 亿**，钱包 332.48 亿，覆盖率 102.91%。来源：[Gate/Foresight 转述 Binance Sep PoR](https://www.gate.com/news/detail/binance-september-proof-of-reserves-btc-eth-and-usdt-at-10016-10000-and-24082668)。
- 2026-08-01 PoR：USDT ≈ 329 亿（103.62%），**USDC 覆盖率 107.64%**（绝对额未进 9 月头条）。来源：[CryptoBriefing Aug PoR](https://cryptobriefing.com/binance-proof-of-reserves-august-2026/)。
- 2026-01-03 起增加 USDC 保证金 BTC/ETH 等合约，并有 Multi-Asset（USDT/USDC/BTC/ETH/BNB 带发剪）。来源：[Binance USDC-M 上线报道](https://rfq.news/options-trading/binance-standardizes-collateral-with-usdc-margined-btc-eth-derivatives-launch/)、[Multi-Asset 说明](https://j-binance.com/en/a/what-is-binance-multi-asset-mode-and-what-are-its-benefits)。
- 8 月衍生品成交币安 **1.67 万亿美元**（47.7% 份额）。来源：[WuBlockchain Aug 2026](https://wublock.substack.com/p/august-2026-exchange-derivatives)。
- 保险基金/SAFU 与可调发剪、可停 USDC 充提、可关 USDC-M、可把用户账户冻结——**开关在交易所，不在 Circle 独占**。

USDT 在 HL 上只有 **0.855 亿**（DefiLlama），是币安 USDT 负债的 **0.26%**。HL 没有「切到 Tether 盘继续开」的能力。

### 5.2 场景对照表

| 冲击 | Hyperliquid | 币安 | 谁更脆 |
|---|---|---|---|
| USDC 脱钩至 0.87 | 抵押品不减记；quanto 制造 vs USDT-M 的基差；提现挤兑；ADL 用烂币结算赢家 | 可对 USDC 发剪/隔离 USDC-M；USDT-M 与保险基金继续 | **HL** |
| Circle 暂停 HyperEVM USDC | 岛内继续撮合+强平，无法补保/出金 | 热钱包同链 USDC 同样转不出，但 USDT 轨道仍在 | **HL**（没有第二轨） |
| 拉黑 CoreDepositWallet | 10.6 亿锁定冻结，账本变成 IOU | 热钱包被拉黑可换地址；用户负债在中心化账本，可改兑付资产 | **HL**（托管地址公开且唯一） |
| 拉黑单个用户 | 已入金的 HyperCore 额度仍可交易（比 CEX 更抗「针对地址」） | 直接冻账户 | **币安更弱于定点冻用户；HL 更弱于冻公共金库** |
| CCTP / Iris 停 | 跨链进出停；岛内+旧桥（若仍开） | 本就不是 CCTP 清算所 | 平手偏 HL（进出金依赖 CCTP） |
| 加密大跌（与稳定币无关） | 标记价跟币安；清算吃自己的簿+HLP+ADL | 更深的簿、更大的保险基金、125x 但多资产 | 币安簿更深；HL 杠杆上限更低（BTC 40x vs 125x） |
| 交易所/运营方盗用 | 链上可见；CoreDepositWallet 不能 rescue USDC | 中心化账本，PoR 是时点快照 | **HL 更强** |
| 验证者作恶（旧桥） | 仍锁 4.51 亿 | n/a | HL 特有残差 |

### 5.3 反射性（常被漏掉）

HL 的标记价**显式依赖币安**。USDC 危机里：

1. 币安用 USDT 继续定价 BTC；
2. HL 用该价格强平 USDC 保证金账户；
3. HL 赢家无法把 USDC 兑成 USDT；
4. 外部 MM 撤出 HL 簿；
5. 清算滑点 → HLP → ADL。

币安是 HL 的**价格主源**，却不是 HL 的结算资产。这是单点依赖的放大器。

### 5.4 为什么「链上」在这一题上帮不上忙

- 透明让你**看见** 6.06 亿在 CoreDepositWallet，不能让它在 `blacklist(wallet)` 之后再转出来。
- 「HyperCore 不断电」会被误读成稳健。对清算来说，不断电 + 不能补保 = **单向绞肉机**。
- 把验证者桥换成 CCTP，降低了「HL 验证者卷走 50 亿」的旧风险，**抬高了 Circle 合规/事故风险**。这是有意识的取舍，不是升级成无风险。

---

## 6. 给首席的判断与监测

**判断：** 把 HL 当「链上 CME」在结算资产这一层不成立。CME 的单位是美元，抵押是现金+国债。HL 的单位是 USDC，出入金是 CCTP，托管金库是 Circle 可暂停合约。**USDC 出事，HL 比币安脆；HL 自己出事，HL 比币安强。** 当前协议选择（AQAv2、USDH 退场、旧桥弃用）是在**主动提高 Circle 集中度**。

**不可对冲的三件事：** (1) Circle 拉黑/暂停 CoreDepositWallet；(2) USDC 脱钩而 HL 仍按 1 记账；(3) 币安价格活着、HL 美元死了，造成 quanto 基差 + ADL。

**可监测触发器：**

1. `USDC.paused()` / `CoreDepositWallet.paused()` / `isBlacklisted(CoreDepositWallet)`（HyperEVM + Arbitrum）。
2. CoreDepositWallet 余额相对 HyperCore 入金的缺口（backing hole）。
3. Arb 桥余额下降 vs CCTP 占比（单点迁移进度）。
4. HLP 权益 / OI；Liquidator 套筒是否仍被抽到 ~100 万。
5. HyperCore USDC `markPx` 是否仍锁 1.0；USDT0/USDH 现货相对脱钩。
6. HL BTC 标记 vs 币安 BTCUSDT 基差（quanto 压力表）。
7. CCTP Fast Transfer 失败率 / Iris 延迟。

**不是建议：** 做空 HYPE、切换仓位、或「应该发自己的稳定币」。那是另一张备忘录。本题只回答依赖与冲击路径。

---

## 7. 来源（按层）

**链上 / API（2026-09-16）：**  
HyperEVM RPC `https://rpc.hyperliquid.xyz/evm`；Arbitrum `https://arbitrum-one.public.blastapi.io`；`https://api.hyperliquid.xyz/info`（`spotMeta`、`tokenDetails`、`metaAndAssetCtxs`、`vaultDetails`、`clearinghouseState`）；DefiLlama `protocol/hyperliquid`、`protocol/hyperliquid-bridge`、`stablecoins.llama.fi`；CoinGecko `coins/usd-coin`、`derivatives/exchanges`。

**官方文档：**  
Circle [CCTP on HyperCore](https://developers.circle.com/cctp/concepts/cctp-on-hypercore)、[HyperCore 地址](https://developers.circle.com/cctp/references/hypercore-contract-addresses)、[CoreDepositWallet 接口](https://developers.circle.com/cctp/references/coredepositwallet-contract-interface)；源码 [CoreDepositWallet.sol](https://github.com/circlefin/hyperevm-circle-contracts/blob/master/src/CoreDepositWallet.sol)。  
HL：[合约规格](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/contract-specifications.md)、[清算](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/liquidations)、[ADL](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/auto-deleveraging)、[标记价](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/robust-price-indices)、[预言机](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/oracle)、[PM](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/portfolio-margin.md)、[AQA](https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/aligned-quote-assets.md)、[USDC/旧桥](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/usdc)、[AQAv2](https://hyperliquid.xyz/article/aqav2)。  
CME：上文抵押品 / 硬限额 / 现金政策 / 加密 FAQ。  
Chainstack：[Bridging USDC](https://docs.chainstack.com/docs/hyperliquid-bridging-usdc)。

**二级：** Circle / Coinbase AQA 博文；L2BEAT CCTP；ChainScore USDC pause；Binance PoR 转述；WuBlockchain 成交；HypurrScan CoreDepositWallet 页（交叉验证余额量级）。
