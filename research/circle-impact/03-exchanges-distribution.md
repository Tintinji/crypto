# Circle 交易所与分销渠道：CLARITY 程序性失败后的近端与远端影响

**研究日期：** 2026-09-16（周三，投票次日；美东盘中截稿）  
**对象：** Circle Internet Group（NYSE: CRCL）经**在线交易所及其他分销伙伴**的短/长期冲击  
**事件：** 2026-09-15 美国参议院对 H.R. 3633（Digital Asset Market Clarity Act）启动辩论的 cloture 以 **49–50** 失败（唱名第 234 号）  
**方法：** 核验 2026 年已披露的 Circle–Coinbase 合约、Coinbase / Circle 季报、OCC/财政部实施文本、DefiLlama 供给、交易所公开奖励页；**不编造投票后新合伙公告**。投票后 24 小时内，未检索到任何 CEX 宣布因该票停掉 USDC rewards 或新签/解除 Circle 分销协议。9/16 Circle 上线 Arc 主网属 Q2 财报已预告的原定日程，不是对投票的反应性合伙。

---

## 一句话结论

CLARITY 失败**没有撤销 USDC 的发行人路径**（GENIUS 仍是法），但把 Circle 最贵的增长期权——「美国现货场所成文法 + 平台奖励安全港」——再推迟至少一个政治周期。近端杀的是 **CRCL 与 COIN 的股权耦合和奖励产品不确定性**；远端决定谁能在 2028-07-18 之后把哪一种美元币卖给美国人的，是 **GENIUS 的 DASP 条款和 OCC 实施规则，不是这次唱名**。Circle 对 Coinbase 的经济联姻（平台内 USDC 储备收益 100% 归 COIN、其余约五五分成，续约至 2029）在失败后变得更「贵」：集中度风险被市场重新标价，而 Circle 自己能立刻加码的，是已经在跑的 **CPN / 支付验收 / Arc / 国际 CASP**，不是再等一条美国现货市场结构法。

---

## 1. 事件边界（先把「没变」写死）

| 项 | 核实结果 | 置信度 |
|---|---|---|
| 表决 | 2026-09-15 14:19 ET，49 赞成 / 50 反对 / 1 未投票（Coons）；Tillis 投反对以便复议 | 高 |
| GENIUS | 2025-07-18 签署，P.L. 119-27，**仍然有效** | 高 |
| 发行人付息 | 发行人「仅因持有」付息仍被禁止 | 高 |
| USDC 发行人路径 | **未被这次投票废止或降级** | 高 |
| CLARITY 本要做的 | SEC/CFTC 分权、数字商品现货交易所联邦登记、自托管/开发者保护、限制平台对稳定币余额发类存款收益 | 高 |
| 投票没有做的 | 没有让平台 rewards 在成文法上变得更违法；也没有给它法定安全港 | 高 |

官方唱名：<https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00234.htm>  
GENIUS 文本：<https://www.govinfo.gov/content/pkg/COMPS-18221/pdf/COMPS-18221.pdf>

**CLARITY 这场架的经济内核，就是「rewards vs interest」通道：** Circle 把储备收益分给 Coinbase，Coinbase 在站内对持有 USDC 的用户发 rewards（官方零售页现标 Coinbase One **3.50% APY**；2024–2026 公开口径大致落在 **3.5–4.5%**，随账户/地区/月份浮动）。银行游说要的是事前禁令；CLARITY 终稿只给财政部 18 个月监视社区银行存款外流的弱熔断。失败意味着：**成文法既没有封死这条通道，也没有保护它。** 下一战场仍是 OCC 拟议规则，而不是新的国会文本。

---

## 2. 股权已发生什么：高分销耦合，不是支付产品被废

Yahoo Finance 日线（America/New_York）：

| 标的 | 9/14 收 | 9/15 收 | 9/15 日线 | 9/15 盘中 | 9/16 盘中约 | 两日相对 9/14 |
|---|---:|---:|---:|---|---:|---:|
| **CRCL** | $97.42 | $86.30 | **−11.4%** | 低点 $84.80 | **$81.10**（−6.0%，低点 $79.15） | **−16.8%** |
| **COIN** | $191.45 | $172.11 | **−10.1%** | 低点 $168.07 = **−12.2%** | **$165.47**（−3.9%） | **−13.6%** |
| PYPL | $54.03 | $53.81 | −0.4% | — | $53.09（−1.3%） | −1.7% |
| HOOD | $114.33 | $110.45 | −3.4% | — | $104.80（−5.1%） | −8.3% |

CRCL 两日跌幅**大于** COIN，符合「发行人吃分销折价 + 奖励通道期权被减记」而不是「USDC 被禁」。PYPL 几乎不跌：市场杀的是 **Circle–Coinbase 中介联姻**，不是美元稳定币支付产品本身。

9/16 盘中 CRCL 市值约 **$221 亿**，COIN 约 **$437 亿**。

---

## 3. Circle 分销地图（2026-09 核实口径）

下图按**对 Circle 储备收益/流通量的经济权重**排列，不是按品牌知名度。投票后**没有**发现新的分销合同被公开签署或解除。

```text
USDC 流通（DefiLlama API 2026-09-16）≈ $73.7B  /  稳定币总供给 ≈ $310.9B（USDC 份额 23.7%）
                    │
     ┌──────────────┼──────────────────────────┐
     │              │                          │
 Coinbase 平台    Circle 自有平台           其余 CEX / 链上 / 支付
 ~$20B 季均       Q2 末 $12.4B              残差 ≈ $41B
 >30% 季末时点    ≈17% 流通                 国际 CASP + DeFi + 钱包 + 商户
 100% 平台内      无对 COIN 的              多数是上架/做市/验收，
 储备收益归 COIN  「100% 分成」             不是 Coinbase 式婚姻
     │              │                          │
     └──────┬───────┴──────────┬───────────────┘
            │                  │
      储备收益分成        交易/支付流量
      （Circle 成本）     （USDC 效用，不一定进 Circle 分成表）
```

### 3.1 核心经济层（吃储备收益）

| 节点 | 角色 | 2026 已核实事实 | 对 Circle 的经济含义 | 投票后变化 |
|---|---|---|---|---|
| **Coinbase** | 主分销商 + 少数股权历史伙伴 | 2023-08-18 Collaboration Agreement；**2026-08-18 按原条款自动续约至 2029**。平台内 USDC 储备收益 **100%** 归 Coinbase；其余流通的残差储备收益约 **50/50**。Q2’26 平台内 USDC **季均 $20B**，季末占流通 **>30%**。过去一年 Coinbase 自称捕获约 **50% 的 USDC 经济学**。 | Circle Q2 分销+交易+其他成本 **$412M / 收入 $701M = 59%**；RLDC $289M、利润率 41%。Coinbase 是最大单点成本中心。 | **无新合同。** 股权 β 上升；奖励通道的法律期权被减记。 |
| **Circle 自有平台** | 直连铸造/赎回与企业账户 | Q2 末平台内 USDC **$12.4B**（同比 +106%），日加权占比 19.5%。 | 唯一不向 COIN 交「平台内 100%」的大块；提高这块才能改善 RLDC。 | 不受 CLARITY 直接打击；GENIUS 实施窗口继续。 |
| **BNY** | 储备主托管 + 铸造/赎回入口 | Q2 披露：BNY 在数字资产托管平台内增加 USDC 铸造/赎回，延续储备托管角色。 | 银行级入口，不是零售 CEX。 | 投票前已有；**未发现**投票后新公告。 |

### 3.2 交易所层（上架 / 报价货币 / 部分自办奖励）

| 节点 | 与 Circle 关系 | 奖励/促销 | 投票后 |
|---|---|---|---|
| **Coinbase** | 经济婚姻，见上 | Coinbase One 零售页标 **3.50% APY**；Business 帮助页曾写 3.35%；第三方 2026-08 摘录约 4.10%。费率按账户/地区/月份变，**9/16 无法穿透 Cloudflare 核对仪表盘实时值**。纽约居民排除。 | 未宣布下架或停奖。 |
| **Kraken** | 2025 年公开合作：扩大 USDC/EURC 流动性与产品，降低兑换费 | 官方称奖励由 **Kraken 自办忠诚计划全额出资**，不是发行人付息。Kraken+ **最高 3.75% APY**，非订阅 **1.75%**；适用于其服务的美/加/澳/英客户。 | 未发现因投票停奖。Payward 9/16 另有经 Bitnomial 为合格美国客户做许可永续的计划（待批）——这是市场结构灰区的绕行，不是 Circle 新合伙。 |
| **OKX** | 既有合作（法币兑换、X Layer 原生 USDC） | **2026-09-01/02**（投票**前**）扩大现货/杠杆/期货 USDC 市场，并上线 Circle **出资**的 USDC Margin Growth Program：每月最多 4,000 人、持仓 ≥20,000 USDC 满 17 天且交易量 >1,000 USDC，奖 100 USDC。为期最多 6 个月。 | 投票后无撤回公告。这是**交易激励**，不是 Coinbase 式「持有即 APY」。 |
| **Binance / 国际 CASP** | 上架与 USDC 交易对；**未检索到**类似 Coinbase 的储备收益婚姻披露 | 多为活动型 USDC 奖池，不是公开的储备分成合同。 | 无投票后新公告。离岸订单簿继续以 **USDT** 为报价主导。 |
| **DEX / 钱包** | Uniswap、Aave、Morpho、MetaMask 等是 Arc 生态日名单上的建设者，不是储备分成对手方 | DeFi 借贷利率不是发行人付息；GENIUS 这条路径未被新开也未被新关。 | 灰区保留；CLARITY 本想给的开发者安全港落空。 |

### 3.3 支付 / 金融科技层（流量，未必吃分成）

| 节点 | 核实 | 是否 Circle「伙伴」 |
|---|---|---|
| **Stripe** | 文档支持 Checkout/Crypto 收稳定币（USDC 轨） | **验收方**，不是披露中的储备分成婚姻。 |
| **Shopify Payments** | 原生 USDC 结账（Base / ETH / OP / Polygon / Arbitrum），合作栈为 Coinbase + Stripe；商户可做法币结算或领 Base USDC。2025-06 先推 Base。AK/NY/TX 等有限制。 | Circle 的**商户分销**，经济上更多走 Coinbase/Stripe 轨道。 |
| **PayPal PYUSD** | Paxos 发行，PayPal 分销 | **竞争对手，不是 Circle 伙伴。** |
| **CPN（Circle Payments Network）** | 2025-05 正式上线。Q2 末 trailing-30d 年化交易额 **$14.7B**（环比 +76%），入网金融机构 **175** 家（+29%）。合作走廊含 Tazapay、Triple-A（2026-03）、Alfred、Conduit、Nium 等；Circle 称网络对稳定币中性，当前结算用 USDC/EURC。 | 这是 Circle **自己能扩的分销**，不依赖 CLARITY。 |
| **Arc L1** | 2026-09-16 公共主网上线（Q2 电话会已预告）。USDC 作 gas；许可验证者含 BlackRock、DTCC、Visa、Mastercard、标旗、SBI 等。 | **预告日程，不是投票后新合伙。** 方向是支付/RWA/代理经济，降低对美国 CEX 现货法的依赖。 |
| **国际机构** | Circle–SBI 日本 JV（2025-11）；JCB、Standard Chartered 铸造/赎回、Grupo Bind（阿根廷）、Kakao 探索、Marex 用 USDC 交衍生品保证金。Circle 另获 OCC **Circle National Trust** 与 NYDFS 信托批准。 | 银行与支付轨道，GENIUS 友好。 |

### 3.4 稳定币供给对照（DefiLlama，2026-09-16）

| 资产 | 流通 / 市值 | 占总供给 | 在交易所分销中的位置 |
|---|---:|---:|---|
| **USDT** | **$183.3B** | **58.9%** | 离岸 CEX / Tron 报价之王；美国 DASP 2028 大限下的问题币。 |
| **USDC** | **$73.7B** | **23.7%** | 合规美元主币；美国 CEX 与支付的默认选择。 |
| 稳定币合计（API `peggedAssets`） | **$310.9B** | 100% | 网页端「稳定币」看板约 $304B（口径略窄，USDT 主导 60%）；与用户给出的 ~$311B 对齐的是 API 全口径。 |
| USD1（WLFI / BitGo 发行） | $4.36B | 1.4% | 政治敏感；交易所上架但不是 Circle 伙伴。 |
| USDG | $3.22B | 1.0% | 部分交易所（含 Kraken）给比 USDC 更高的自办奖励。 |
| **PYUSD** | $2.79B | 0.9% | PayPal 封闭生态 + 部分 CEX。 |
| BUIDL（BlackRock 通证化现金） | $2.69B | 0.9% | 基金，不是支付稳定币；拟上 Arc。 |
| Circle USYC | $2.55B | 0.8% | Circle 自己的收益产品，和 USDC 支付币分轨。 |
| **RLUSD** | $2.35B | 0.8% | Ripple/NY 信托轨道；XRPL + ETH。 |
| **USAT / USA₮** | **$184M** | 0.06% | Tether+Anchorage 的美国平行产品；Kraken/OKX/Bybit 有盘，**体量可忽略**。 |

网页看板：<https://defillama.com/stablecoins>  
USDT：<https://defillama.com/stablecoin/tether>  
USDC：<https://defillama.com/stablecoin/usd-coin>  
USAT：<https://defillama.com/stablecoin/usat>（$184.1M）

---

## 4. Circle–Coinbase 经济婚姻：投票后的集中度风险

### 4.1 合同长什么样（已续约，不是谈判中）

2023-08-18 协议在 Centre 解散后把 Circle 定为唯一发行人，Coinbase 拿少数股权 + 分销权。**2026-08-18 进入第一个三年续约期，条款不变，锁到 2029。** Circle CEO Jeremy Allaire 在 8/5 季报会上确认；Coinbase CFO Alesia Haas 此前已说双方满足自动续约条件。

公开结构（多家对已提交协议的解读，方向一致）：

- 平台内（Coinbase 产品中的 USDC）：储备收益 **100% → Coinbase**。
- 其余流通：扣除 Circle 发行人留存与其他伙伴后，残差约 **50/50**。
- 续约期内 Circle 多了两把「慢杠杆」：产品支持门槛（60 天补救）与转售门槛（90 天补救）；发出排除通知后，Coinbase 对受影响现金流仍最多再享 **12 个月**。这不是能在一个季度内改分成的开关。

来源：  
<https://cryptoslate.com/circles-renewed-coinbase-deal-creates-two-ways-to-challenge-coinbases-usdc-payouts-but-neither-works-quickly/>  
<https://stablecoininsider.org/circle-coinbase-usdc-agreement-renewal-2029/>  
<https://finance.yahoo.com/markets/crypto/articles/coinbase-circle-partnership-renew-same-173903843.html>

### 4.2 数字有多集中

Coinbase Q2’26（截至 2026-06-30）：

| 指标 | 数字 | 出处 |
|---|---|---|
| 订阅与服务收入 | **$555M**，占净收入 **48%** | Coinbase Q2’26 业绩稿 / 8-K |
| 其中稳定币收入 | **$292M** | 同上；被利率下降与**站外**余额下滑部分抵消 |
| 平台内 USDC | 季均 **$20B** ATH；季末 **>30%** 流通 | 同上。Circle 季末流通 $73.3B，故 $20B 是季均、>30% 是时点，**不要直接相除** |
| 全球现货份额 | 10.3% ATH | 同上 |
| 「USDC 经济学」占比 | 过去一年约 **50%** | Coinbase 自己的表述 |
| 稳定币交易量叙事 | 市场 YTD >$37T，其中 **79%** 来自 USDC + Coinbase partner stables（相对 2024 全年 51%） | 同上 |

Circle Q2’26：

| 指标 | 数字 |
|---|---|
| 季末 / 季均流通 | $73.3B / $76.5B |
| 链上交易量 | $14.8T（同比 +151%） |
| 收入与储备收益 | $701M（储备收益 $668M，回报率 3.5%，−66bp） |
| 分销+交易+其他成本 | **$412M**（同比 +1%，几乎全是分销付款） |
| RLDC / 利润率 | $289M / **41%** |
| 2024 / 2025 分销开支（二手汇总） | 付给分销体系约 $9.08 亿（2024，约 54% 收入）、$14 亿（2025，约 51% 收入）——其中 Coinbase 是最大头 |

Coinbase 稿：<https://investor.coinbase.com/news/news-details/2026/Coinbase-Q2-Earnings-Everything-Exchange-Drives-3rd-Consecutive-Quarter-of-Record-Crypto-Trading-Volume-Market-Share-Revenue-Diversification-and-Resilience/default.aspx>  
业绩页 PDF：<https://s27.q4cdn.com/397450999/files/doc_financials/2026/q2/Q2-26-Earnings-Deck.pdf>  
Circle 稿：<https://www.circle.com/pressroom/circle-reports-second-quarter-2026-results>  
10-Q：<https://www.sec.gov/Archives/edgar/data/1876042/000187604226000246/augustepr-circle_q22026f.htm>

### 4.3 投票之后，集中度风险怎么变

**合同没变，折现率变了。**

1. **收入相关性被市场定价。** 9/15 CRCL −11.4% vs COIN −10.1%，9/16 继续更深。这不是「USDC 要被禁」，而是市场把 Circle 的近端自由现金流看成 **Coinbase 零售余额 × 美债收益率 × 分成公式**，再叠加「奖励通道可能被 OCC 咬」的久期。
2. **Circle 短期无法改婚姻。** 续约刚生效四周；排除条款有 60–90 天补救 + 最长 12 个月尾款。想靠「减少给 COIN 的分成」对冲这次投票，**2026 年内做不到**。
3. **Coinbase 的激励是继续推 USDC，不是改推 PYUSD/USDT。** 平台内每 1 美元 USDC，储备收益全部留在 COIN；换成竞品会直接打 $292M 这一条。只要 OCC 规则未终稿，理性交易所会**继续促销**，同时律师准备 rebuttal 卷宗。
4. **对 Circle 股东的不对称：** 平台内余额涨，COIN 吃 100% 收益、Circle 只拿到「流通增长」的残差；平台内余额跌，Circle 的分销成本短期下不来（合同在），流通与叙事一起受伤。这是典型的**上凸给伙伴、下凸给发行人**。
5. **唯一结构性减压阀**是把流通赶到 Circle 自有平台、CPN、银行铸造口和 Arc——Q2 自有平台 $12.4B 已在涨，但还远小于 Coinbase 的 $20B 季均。

**判断（中置信）：** 投票把「2026–27 靠美国 CEX 再挖一个 Coinbase 级伙伴」的概率下调，把「必须忍受与 COIN 的 50% 经济学分成直到 2029」的概率上调。集中度风险从或有变成基线。

---

## 5. 交易所还会不会推 USDC rewards？OCC 悬顶 vs 没有新成文法

### 5.1 法律分层（不要混在一起）

| 层级 | 状态（2026-09-16） | 对「持有即奖」的含义 |
|---|---|---|
| **GENIUS 成文法** | 有效。禁的是**发行人**就「仅因持有」付息 | Coinbase / Kraken / PayPal 把支付标成 **platform rewards** 的字面空间还在。 |
| **CLARITY** | cloture 失败；本会期再凑 60 票概率低 | **既没有法定安全港，也没有法定禁令。** 银行要的事前禁令没写成法。 |
| **OCC NPRM** | 2026-02-25，Bulletin 2026-3，**尚未终稿** | 拟议 **可反驳推定**：若 PPSI 与关联方/「相关第三方」有付息安排，且该方再向持有人付息，则视为发行人违规。「相关第三方」宽到「作为服务向持有人付息的人」以及白标品牌方——**字面能套住 Circle–Coinbase**。发行人可用书面证据反驳。商户折扣、与非关联方分润的白标不在禁令核心。 |
| **财政部 DASP 规则** | 2026-08-18 联邦公报提案，澄清「向美国人 offer/sell」 | 管的是 2028 年谁能卖哪种币，**不直接管 APY**。 |

OCC：<https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-3.html>  
律师解读（推定如何咬 Coinbase）：<https://www.ashurstperkinscoie.com/en/insights/stablecoin-interest-yield-and-rewards-occ-proposes-sweeping-regulations-under-the-genius-act/>  
<https://www.forbes.com/sites/digital-assets/2026/05/20/the-genius-act-stablecoin-yield-ban-has-a-coinbase-shaped-hole/>  
财政部提案：<https://www.federalregister.gov/documents/2026/08/18/2026-16796/genius-act-regulations-on-payment-stablecoin-issuance-offer-and-sale>

GENIUS 对 OCC 监管对象的生效日：2025-07-18 起算 **18 个月（2027-01-18）** 与「终稿后 120 天」之较早者。DASP 对美国人 offer/sell 非 PPSI 币的禁止日是 **2028-07-18**。

### 5.2 当前公开奖励（能核实的）

| 平台 | 产品形态 | 最近公开数字 | 谁出钱 | 9/16 核实限制 |
|---|---|---|---|---|
| Coinbase One | 持有 USDC 得奖励 | 官网 **3.50% APY** | 经济上来自 Circle 储备分成后由 Coinbase 发放 | Cloudflare 挡了帮助页；**不能声称这是每一账户的实时值**。历史区间 3.5–4.5% 仍成立。 |
| Coinbase Business | 同上 | 帮助页曾写 **3.35%** | 同上 | 可能滞后。 |
| Kraken | 自办忠诚 | 1.75% / Kraken+ **3.75%** | **Kraken 自费**（官方如此表述） | OCC「相关第三方」是否咬自费忠诚，比咬储备分成更弱，但仍有解释空间。 |
| OKX | 持仓+交易任务 | 100 USDC / 月（高门槛） | **Circle 出资** | 更像市场费，不像存款利息；OCC 文本主要打「solely for holding」。 |
| PayPal / PYUSD | 平台内收益（历史产品） | 未在本稿核对 9/16 实时 APY | PayPal 体系 | 竞品，用来对照「平台奖」行业惯例仍在。 |

Coinbase USDC 页：<https://www.coinbase.com/usdc>  
帮助中心（结构）：<https://help.coinbase.com/en/coinbase/coinbase-staking/rewards/usd-coin-rewards-faq>  
Kraken：<https://support.kraken.com/articles/stablecoin-rewards>  
OKX 活动（投票前）：<https://www.okx.com/en-us/learn/usdc-trade-and-earn>

### 5.3 会不会停？

**基线判断：近端不会系统性停，但会「律师化」和「任务化」。**

- **停的触发器**是 OCC **终稿**把 Circle–Coinbase 结构写成难以反驳的违法，或执法行动，而不是 9/15 唱名。唱名没有增加违法性。
- **Coinbase 的期望损失函数**偏向继续发奖：奖励是把零售现金冻在站内、支撑 $20B 余额和 $292M 稳定币收入的获客工具。没有成文法安全港，他们会准备 rebuttal（强调奖励来自平台服务、用户可交易/提现、不是发行人直接付息），而不是先下线产品。
- **Kraken 自费模式**在 OCC 文本下比「发行人资助」更可辩护，可能成为其他美国 CEX 的预案。
- **Circle 出资的持有型奖励**（若被认定 solely for holding）比 OKX 这种「持仓+交易」任务更危险。预期分销会从「纯 APY」滑向 **交易量 / 支付 / 订阅捆绑**。
- **未发现** 9/15–9/16 有交易所因投票宣布暂停 USDC rewards。

**对 Circle：** 奖励通道继续存在 → Coinbase 仍有动力囤 USDC → 近端流通不见得塌。但通道变成**可撤销的行政解释**，CRCL 的倍数里要永久扣一笔政策溢价。若 OCC 终稿咬死「发行人资助的第三方奖励」，受伤顺序是：Coinbase 零售 APY → 平台内余额 → Circle 流通与叙事；Circle 的分销合同成本不会同比例下降。

---

## 6. 其他 CEX / DEX / 钱包 / 金融科技：会被迫出海还是加码支付（CPN）？

**短答案：不是二选一，是「美国现货 TAM 冻结 → 把增量预算从『再找一个美国 Coinbase』转到已经能签约的支付网与国际 CASP」。** Circle 的发行人执照不需要 CLARITY；它需要 CLARITY 的是**美国现货场所把更多交易对、经纪、做市做大**，从而抬升 USDC 作为报价货币的美国份额。

### 6.1 美国市场结构灰区对分销的真实约束

- CFTC **仍无**全面现货加密商品的制定法授权——这正是 CLARITY 要给、行政机关给不了的东西。
- 美国 CEX 继续靠 Atkins/Selig 行政解释过日子；新资产上架、银行级分销、经纪定义保持可撤销。
- 这**不阻止** Stripe/Shopify 收 USDC，也**不阻止** Circle 当 PPSI 铸造。它阻止的是「美国零售现货活动台阶式上台」这种 Circle 在 IPO 叙事里用过的 β。

### 6.2 出海：本来就在做，投票只是去掉「2026 年可以少做一点」的借口

已核实、且均在投票**之前**或与投票无关：

- **OKX** 9/1–9/2 扩 USDC 交易与 Circle 出资活动。
- **Kraken** 2025 合作 + 自办奖励；国际盘仍是其基本盘。
- **欧盟 MiCA**：过渡期已于 2026-07-01 结束；持牌 CASP 是 USDC（EMT）相对 USDT 的规则书红利。美国市场结构再拖，**欧洲持牌所**更可能把合规美元默认成 USDC。
- **日本**：Circle–SBI JV；2026-06 外币合规稳定币分销已通。
- **香港 / 阿联酋 / 新加坡**：牌照与机构代币化窗口，不替代美国零售，但能接住「先在海外上新」的交易流。

**未发现** Circle 在 9/15 后宣布新的离岸交易所独家。把「失败 → 明天签约 Binance 分成」写成事实，是编造。

### 6.3 支付（CPN / 商户 / Arc）：这是 Circle 自己控制的方向盘

| 信号 | 数字 / 事实 | 与 CLARITY 的关系 |
|---|---|---|
| CPN 规模 | T30 年化 **$14.7B**，175 家 FI（Q2 末） | 不依赖现货市场结构法 |
| 商户验收 | Shopify 原生 USDC；Stripe Crypto | 靠 GENIUS + 卡组织/收单，不靠 CLARITY |
| 银行入口 | BNY 铸造/赎回、标旗一体兑换、Nium 190+ 国家出金 | 银行分销继续 |
| Arc | 9/16 主网，USDC gas，传统金融验证者 | **8/5 已预告**；是把结算层从「借 CEX 的链」迁到「自己的链」 |
| Agent / x402 | Circle 称 99.3% 的 x402 代理支付体积用 USDC | 与美国现货法弱相关 |

**判断（中高置信）：** 管理团队的理性反应是 **双加码支付 + 国际 CASP**，而不是等 2027 年再赌一条市场结构法。约束是：支付增量（CPN $14.7B 年化）相对 USDC **$14.8T** 的季链上量仍是小数；近端 P&L 还是储备收益减去 Coinbase 分成。出海能抬流通，但抬不到立刻替换 $20B Coinbase 余额的程度。

---

## 7. 交易所上的竞争代币

投票**没有**改变这些币的发行人资格；它改变的是「美国 CEX 还要不要把营销预算押在需要市场结构法的山寨交易对上」。稳定币货架竞争是 GENIUS 轨道。

| 代币 | 发行人 / 结构 | 供给（9/16） | 交易所角色 | 对 USDC 的近端威胁 | 2028 DASP 含义 |
|---|---|---|---|---|---|
| **USDT** | Tether Ltd（离岸） | $183.3B | 全球 CEX 报价货币、Tron 主导 | **高（离岸）**，美国零售盘已弱 | 若不能成 PPSI/合格 FPSI，**2028-07-18 后美国 DASP 不得向美国人 offer/sell** |
| **USAT / USA₮** | **Anchorage Digital Bank, N.A.** 发行；Tether 出品牌与技术；Cantor 管储备。**2026-01-27** 上线，专为 GENIUS 美国市场。Tether 官方强调 Tether Operations **不是**发行人 | **$184M** | Kraken / OKX / Bybit 等有盘，日量极小 | **近端可忽略**（是 USDC 的 0.25%） | 这是 Tether 的美国合规楔子；8 个月未做大，说明「有牌 ≠ 有分销」 |
| **PYUSD** | Paxos Trust；PayPal 分销 | $2.79B | PayPal/Venmo 封闭 + 部分 CEX | 支付结账竞争，不是 CEX 报价竞争 | 走 PPSI 路径的竞品；**不是 Circle 伙伴** |
| **RLUSD** | Ripple 体系 / NY 信托轨道 | $2.35B（近一月 +30% 量级，波动大） | XRPL 原生 + ETH；部分 CEX | 跨境/XRPL 利基 | 若维持州/联邦合格，2028 可留在美国货架 |
| **USD1** | **BitGo** 铸造托管，WLFI 持品牌 | $4.36B | 多家 CEX 已上架 | 供给已是 PYUSD 的 1.6 倍，但政治/伦理风险与 CLARITY 失败同源 | PPSI 地位仍被第三方登记处标为不清；2028 是真正的闸门 |
| **USDG** | Global Dollar | $3.22B | 部分所给高于 USDC 的自办 APY | 奖励货架竞争 | 视发行人牌照 |
| **银行币 / 存款代币** | JPM Coin（JPMD，Base，机构客户）；Citi Token Services；sofiUSD（SoFi Bank，2025-12，FDIC 银行稳定币） | 公开 CEX **基本不上架** | 批发支付、链上存款 | **不抢 CEX 报价**，抢的是企业司库与支付 | GENIUS 把银行存款排除在「支付稳定币」定义外；走的是银行法，可付息 |
| 通证化现金 | BUIDL、USYC、USDY | 各 $2–3B | 基金/RWA，不是现货报价货币 | 抢的是「想要收益的机构美元」，不是零售交易垫资 | 证券法轨道，不靠 CLARITY |

Tether USAT 官方：<https://tether.io/news/tether-announces-the-launch-of-usat-the-federally-regulated-dollar-backed-stablecoin-made-in-america/>  
JPMD：<https://www.jpmorgan.com/kinexys/jpm-coin>

**货架结论：** 美国 CEX 的合规美元默认值仍是 USDC。USDT 继续赢离岸深度。USAT 证明 Tether 接受「美国要另开一只币」，但 8 个月 $184M 说明 **Anchorage 牌照填不满 Coinbase 式分销坑**。PYUSD/RLUSD/USD1 是货架噪音，不是 Q3 流通的替代者。银行币在批发，不在订单簿。CLARITY 失败**没有**把这些竞品突然送进美国零售 CEX 的默认位——默认位仍受 GENIUS + 平台自身合规委员会约束。

---

## 8. 上市 / 交易量 β：灰区会不会在供给稳住时打掉 USDC 交易份额？

**会打「美国现货相关」的交易份额，不一定打全球供给，更不一定打 Circle 披露的链上量。必须拆三层。**

### 8.1 三层口径

| 口径 | 最近数字 | 对 CLARITY 的弹性 | 含义 |
|---|---|---|---|
| **供给 / 流通** | USDC $73.7B，较 Q2 末 $73.3B 基本持平；网页端近 7 日约 **−1.3%** | 低–中。供给由储备收益、支付浮存、CEX 垫资共同决定 | 投票不是赎回事件；近周供给走平/微降，更像风险偏好与利率，而不是「USDC 被禁」 |
| **链上转账量** | Circle Q2 **$14.8T**（+151% YoY）；含跨链、DeFi、支付、铸造销毁，**≠ CEX 现货量** | 中。一部分是 Base/代理/CPN，一部分是交易垫资 | 供给稳住时，链上量仍可以因 DeFi/支付上涨或因 CEX 降温下跌 |
| **CEX 现货报价份额** | Coinbase 全球现货份额 10.3%；离岸主簿仍是 USDT | **高。** 这是最吃市场结构法的一层 | 美国现货继续灰区 → 美国站 USDC 交易对、经纪、新上币配对的 TAM 被冻结 |

Coinbase 自己的「79% 稳定币交易量来自 USDC + partner stables」是**全市场链上/交易混合叙事**，不能直接读成「美国 CEX 现货份额」。USDC 在 Base（Coinbase L2）、Shopify、x402 上的份额，对 CLARITY 的 β 低于「SOL/XRP 新交易对的报价货币」。

### 8.2 传导机制（判断）

```text
美国现货保持灰区
  ├─ 美国 CEX 现货量 / 新上币 放缓
  │     └─ 平台内交易垫资需求 ↓ → Coinbase 站内 USDC 余额的「交易性」部分承压
  │           └─ 但奖励 APY 仍在 → 「储蓄性」余额可能对冲
  ├─ 离岸永续 / 国际 CASP 留住全球零售
  │     └─ 报价货币继续偏 USDT（Tron ~$94B 稳定币，USDT 占绝对主导）
  │           └─ USDC 全球 CEX 交易份额不一定跟供给份额走
  └─ 支付 / CPN / Shopify / Arc / 代理支付
        └─ 与现货法弱相关，支撑链上量与「效用叙事」
```

**因此：供给稳住 + 美国现货灰区，完全可以同时发生「USDC 流通不变、美国 CEX 相关交易份额下滑、离岸 USDT 报价份额上升」。** Circle 的 P&L 近端看储备（流通 × 利率 − 分成），所以供给稳住就能撑住收入；被打的是 **增长期权和 Coinbase 站内余额结构**。若站内「交易性」USDC 被「奖励性」替换，Coinbase 更高兴（100% 吃收益），Circle 只是没得到交易爆发带来的增量流通。

9/15 美国现货 BTC ETF 净流出约 $4.50 亿、期货多头清算约 $5.7 亿，是活动收缩的脉冲，不是稳定币挤兑。DefiLlama 近 30 日总稳定币供给仍约 +1%。

### 8.3 对 Circle 交易份额的工作假设

| 情景 | 美国现货活动 | USDC 供给 | USDC「交易份额」（CEX 报价） | Circle 近端 P&L |
|---|---|---|---|---|
| 基线（本研究权重最高） | 灰区、温和偏低 | 走平至随利率缓降 | 美国盘弱、全球盘被 USDT 咬 | 储备收益仍在；倍数压缩 |
| 偏熊 | 监管叙事 + 利率再紧，CEX 量再下一台阶 | 微降 | 离岸 USDT 份额再升 | 流通小降 × 分成刚性 |
| 偏牛 | 行政解释维持、支付与 Arc 补上活动 | 走平/微升 | 交易份额与供给脱钩，支付份额升 | 收入稳，叙事从「CEX 货币」转向「互联网美元」 |

---

## 9. 短期 vs 长期

### 9.1 短期（到 2026 年底 / 中期选举）

| 主题 | 判断 | 置信度 |
|---|---|---|
| **与 COIN 的股权相关** | 维持高相关。CRCL 是「COIN 稳定币条线 + 奖励法律期权 + 美国分销久期」的杠杆多头。9/15–16 已实证：同方向、Circle 更深。PYPL 对照说明不是稳定币产品被废。 | 高 |
| **奖励产品** | 不会因唱名下线。不确定性来自 OCC 终稿时点与措辞，不是来自 49–50。预期文案更律师化、更多「交易/订阅捆绑」。 | 中高 |
| **分销合同** | 2026-08-18 续约锁死到 2029，近端改不了分成。 | 高 |
| **流通** | 不是挤兑；7 日微降与风险偏好一致。Q3 流通更看利率与 CEX 余额，不看唱名本身。 | 中高 |
| **Arc / CPN** | 按既定产品日历推进；把它们写成「投票后战略转向」是叙事，不是新事实。 | 高（日程）/ 中（是否加速） |
| **竞品** | USAT/PYUSD/RLUSD 不会因这次投票突然吃掉美国 CEX 默认位。 | 中高 |

### 9.2 长期（到 2028 DASP 大限及以后）

GENIUS §3：自颁布满三年（**2028-07-18**）起，DASP（交易所、托管、经纪等）向美国人 offer/sell 支付稳定币，须为 **PPSI** 所发；对外国发行人另有 section 18 的技术能力与对等安排要求。财政部 2026-08 提案把「向美国人招揽/广告」明确算 offer。

<https://www.sullcrom.com/insights/memo/2026/August/Treasury-Department-Proposes-Rules-Clarifying-GENIUS-Act-Prohibitions>

| 长期问题 | 谁决定 | CLARITY 失败改了什么 | 对 Circle 的含义 |
|---|---|---|---|
| **谁能向美国人分销哪一种币** | GENIUS + 财政部/OCC 实施，**不是 CLARITY** | **几乎没改。** 2028 货架清洗日程还在 | USDC 作为最干净的非银行 PPSI 候选之一，反而更依赖把 Circle National Trust / 州合格走完。USDT 全球币面临「美国货架出局或迁到 USAT」。 |
| **谁能在美国开现货交易所、上新、做经纪** | 本该是 CLARITY；现为行政解释 | **这是真正被推迟的。** 2027 若分裂国会，立法接近冰冻 | Circle 的「美国 CEX 交易 β」久期拉长；支付/Arc/国际 CASP 的相对权重上升。 |
| **平台奖励是否永久合法** | OCC 终稿 + 可能的 2027–28 国会再战 | 失去 2026 年把「交易型激励 vs 持有型利息」写进成文法的窗口 | 最坏情况：发行人资助的 APY 被推定违法 → Coinbase 改自费或改任务奖励 → 站内余额逻辑重写。Circle 流通不一定崩，**经济学可能更差或更好**（分成对象若减少奖励，余额结构会变）。 |
| **银行币** | 银行法，可付息 | 不受 CLARITY 失败阻碍 | 批发支付的长期对手是 JPMD/Citi/TCH，不是 USDT。 |
| **DASP 定义是否咬 DEX 前端** | GENIUS 对自托管/协议有排除；CLARITY 本想再写控制测试 | 前端/界面是否构成经纪，灰区原样保留 | DEX 分销继续，但是律师风险最高的一层。 |

**长期基准情景（研究权重，非交易指令）：** 2028 年美国人在持牌 DASP 上能买的支付稳定币，短名单是 **USDC、PYUSD、合格银行稳定币、USAT（若 Anchorage 路径站稳）、或许 RLUSD/USD1（若 PPSI 落袋）**。USDT 全球币大概率退出美国零售货架。Circle 赢的是**合规货架**，不是自动赢流通——流通仍要靠支付效用和（被削弱的）CEX 垫资。CLARITY 失败让「货架赢了但美国交易活动没做大」成为更可能的组合。

---

## 10. 综合：短长对照表

| | **短期（周–两个季度）** | **长期（2027–2028+）** |
|---|---|---|
| **核心冲击** | CRCL–COIN 股权耦合；奖励通道从「快要写成法」变成「只剩 OCC 解释」 | 2028 DASP 货架谁留下；美国现货场所是否永远没有成文法 |
| **Circle–Coinbase** | 合同锁死，集中度被标成风险溢价 | 2029 再谈判时，Circle 的筹码取决于自有平台/CPN/Arc 是否已替代一部分 $20B |
| **Rewards** | 大所继续发，文案更谨慎 | 若 OCC 收紧，APY 迁到自费、任务、订阅；DeFi 与离岸承接一部分「要收益」的余额 |
| **其他分销** | OKX/Kraken/Shopify/CPN 按原计划 | 国际 CASP + 支付网成为增量主战场；不是因为投票创造了新激励，而是拿走了 2026 上岸立法 |
| **竞品** | 货架无突变；USAT 仍是小品 | USDT 美国出局风险是 Circle 的结构性尾部利好；银行币抢批发 |
| **交易量 β** | 美国现货灰区 → USDC 的 CEX 交易份额弱于供给 | 「供给稳、美国交易份额不涨」可以成为稳态 |
| **P&L** | 储备收益 − 分成仍在；杀的是倍数 | 利率下行 + 分成刚性是比 CLARITY 更持久的基本面；政策只决定分子有没有第二增长曲线 |

---

## 11. 监测清单（分销专用）

1. OCC NPRM 终稿是否保留「相关第三方」可反驳推定，以及 Circle/Coinbase 是否提交公开 comment 的后续。
2. Coinbase / Kraken 奖励页 APY 与条款是否在无预告下下调或改为任务制。
3. Coinbase 下季「Average USDC Held in Coinbase Products」是否从 $20B 回落（交易性余额 vs 奖励性余额）。
4. Circle 下季分销成本 / RLDC：分成刚性下流通若降，利润率先受伤。
5. CPN 年化量与入网 FI 是否继续环比增长（支付是否真能补 CEX β）。
6. USAT 流通是否还在 $2 亿附近，或出现美国 DASP 规模化上架。
7. 2028 准备：Circle National Trust 是否开始管储备；USDT 是否宣布美国 FPSI/互惠路径。
8. 11/3 中期后参议院银行委员会主席归属（Warren 情景对 OCC 终稿偏鹰）。

---

## 12. 来源、分叉、置信度

### 主要 URL

- 参议院唱名：<https://www.senate.gov/legislative/LIS/roll_call_votes/vote1192/vote_119_2_00234.htm>
- GENIUS（P.L. 119-27）：<https://www.govinfo.gov/content/pkg/COMPS-18221/pdf/COMPS-18221.pdf>
- OCC Bulletin 2026-3（2026-02-25）：<https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-3.html>
- 财政部 DASP 提案（2026-08-18）：<https://www.federalregister.gov/documents/2026/08/18/2026-16796/genius-act-regulations-on-payment-stablecoin-issuance-offer-and-sale>
- Circle Q2’26：<https://www.circle.com/pressroom/circle-reports-second-quarter-2026-results>
- Circle 10-Q 索引：<https://www.sec.gov/Archives/edgar/data/1876042/000187604226000246/augustepr-circle_q22026f.htm>
- Coinbase Q2’26 稿：<https://investor.coinbase.com/news/news-details/2026/Coinbase-Q2-Earnings-Everything-Exchange-Drives-3rd-Consecutive-Quarter-of-Record-Crypto-Trading-Volume-Market-Share-Revenue-Diversification-and-Resilience/default.aspx>
- Coinbase Q2 deck：<https://s27.q4cdn.com/397450999/files/doc_financials/2026/q2/Q2-26-Earnings-Deck.pdf>
- Coinbase USDC 奖励页：<https://www.coinbase.com/usdc>
- Kraken 稳定币奖励：<https://support.kraken.com/articles/stablecoin-rewards>
- Kraken–Circle 2025 合作：<https://investor.circle.com/news/news-details/2025/Kraken-and-Circle-Partner-to-Accelerate-Global-Access-and-Utility-of-USDC-and-EURC/default.aspx>
- OKX–Circle 2026-09-02 扩交易（投票前）：<https://crypto.news/circle-expands-usdc-trading-reach-across-okx-markets/>
- CPN：<https://www.circle.com/cpn>
- Shopify USDC：<https://help.shopify.com/en/manual/payments/shopify-payments/local-payment-methods/usdc-payments>
- Arc 主网（预告后的原定上线）：<https://www.circle.com/pressroom/circle-launches-arc-mainnet-an-economic-operating-system-for-the-internet>
- Tether USAT：<https://tether.io/news/tether-announces-the-launch-of-usat-the-federally-regulated-dollar-backed-stablecoin-made-in-america/>
- DefiLlama 稳定币：<https://defillama.com/stablecoins>
- JPMD：<https://www.jpmorgan.com/kinexys/jpm-coin>

### 口径分叉（不调和）

- 稳定币「总量」：DefiLlama **网页看板 ~$304B** vs **API 全口径 ~$310.9B**。USDT $183.3B、USDC $73.7B 在两套口径里一致；差额来自网页是否计入部分通证化基金/收益币。本稿主表用 API，以便与「~$311B」对齐。
- Coinbase「$20B」是**季均**，「>30%」是**季末时点**，与 Circle $73.3B 季末流通不可直接相除。
- Coinbase One 3.50% 是营销页；8 月三方摘录 ~4.10%、Business 3.35% 并存。**9/16 未登录账户，不声称单一实时 APY。**
- 2024–2025 Circle「付给 Coinbase $9.08 亿 / $14 亿」来自对披露的二手加总，方向正确，精确分项以 10-K/10-Q 为准。
- Arc 主网恰在投票次日：时间重合，**因果不是「因失败而发布」**——8/5 已宣布 9/16。

### 未覆盖 / 未编造

- 投票后新的交易所分销合同、停奖公告：**检索未发现，故不写。**
- X/社交原帖抽样：本环境未做。
- 个性化交易建议：无。
- USDC 在 Binance 的未披露分成：没有主文件就不写「婚姻」。

### 置信度汇总

| 模块 | 置信度 |
|---|---|
| 唱名、GENIUS 仍有效、USDC 发行人路径未被废 | **高** |
| Coinbase/Circle Q2 数字、8/18 续约、分成结构方向 | **高** |
| 供给份额（USDT 58.9% / USDC 23.7% / 总 $310.9B） | **高**（API 时点） |
| USAT 1 月上线、现流通 ~$184M | **高** |
| 9/15–16 CRCL/COIN 价格与相对 PYPL | **高** |
| 当前 Coinbase 单一实时 APY | **中**（页标 3.50%，账户层未验证） |
| OCC 终稿是否咬死 Circle–Coinbase | **中低**（提案在，终稿未出） |
| 「支付能补上 CEX β」的幅度 | **中** |
| 2028 货架短名单的具体构成 | **中**（法已写，牌照尚未全部落袋） |
| 2027 国会控制权 | **中低** |

**总判断：** 分销分析的硬事实（合同、季报、供给、OCC 文本、价格）高置信；「交易所会不会停奖」和「支付能否替代 CEX 交易 β」是机制判断，标为中。失败对 Circle 的交易所通道是 **倍数和久期事件，不是执照事件**。
