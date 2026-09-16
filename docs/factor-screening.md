# 因子筛选：方法、本样本结果与生产流程

研究笔记，**不是投资建议**。回测与筛选结果不能代表未来收益。加密资产波动极大，可能损失全部本金。

本文记录 `factorlib` 的点-in-time 筛选管线（`python3 -m factorlib screen-factors`），用 **2026-09-16** 当日拉取的真实 yfinance 行情跑通，并说明：**在这个加密+宏观设定里，筛选应当怎么做**，而不只是本样本谁赢。

---

## 1. 数据窗口、宇宙、成本、真实 vs fixture

| 项目 | 取值 |
|---|---|
| 行情窗口 | **2023-01-01 → 2026-09-16**（面板 1355 个日历日，含加密周末） |
| 目标 | BTC-USD 下一根收益（`signal_lag=1`） |
| BTC 首/末收盘 | 16,625.08 → 75,807.72（样本内约 3.6×，牛市） |
| 成本 | **15 bp** / 换手（`abs(Δposition) * 15e-4`）；买入持有只在首日扣一次 15 bp |
| OOS 段 | 最后 **126** 个面板日：**2026-05-14 → 2026-09-16** |
| IS 标签 | 远期收益必须在 OOS 开始前实现（再减 `lag+horizon` 日），避免 IS IC 吃到 OOS 收益 |
| 因子数 | **90**（宏观 + 价量 + 日历 + 资金流） |

**宇宙（全部 yfinance 成功，无 fallback、无 reused）：**

`BTC-USD`, `ETH-USD`, `SOL-USD`, `^TNX`, `2YY=F`, `^IRX`, `DX-Y.NYB`, `USDJPY=X`, `CL=F`, `BZ=F`, `GC=F`, `^GSPC`, `^NDX`, `KRW=X`, `BTC-KRW`

宏观序列约 929–963 个交易日；加密约 1355 日。宏观因子对齐后有效样本约 890–910。

**真实 vs fixture（必须分开看）：**

| 来源 | 内容 | 本样本状态 |
|---|---|---|
| yfinance OHLCV | 价、量、利率、汇率、商品、股指 | **真实下载**（2026-09-16 拉取） |
| `data/fixtures/btc_etf_flows.csv` | 现货 BTC ETF 净流入 | **样本 fixture**，非 Farside/发行商；非零日仅 54 天，且集中在 2026-07 之后 |
| `data/fixtures/fomc_cpi_2026q4.csv` | FOMC / CPI | **占位日历**（2026 年静态表，不是官方日程的完整核对） |
| `data/fixtures/hormuz_risk.csv` | 霍尔木兹风险旗标 | **静态占位**，全样本仅 **5** 天为 1 |

官方 IBIT/现货 ETF 流水不在 yfinance。在换成真实 CSV 之前，`flow_btc_etf_net` / 日历 / 霍尔木兹 **不能当 alpha**。

---

## 2. 筛选管线（无前瞻）

实现：`src/factorlib/model/screening.py`。规则在 `config/default.yaml` → `screen:`。

1. **PIT z-score**：与打分相同，扩展窗口均值/方差，只用 ≤ t 的因子值，再 clip 到 ±3。
2. **远期收益**：信号在 t 日收盘；`lag=1, h=1` 时标签是 `close[t+1]/close[t]-1`，**不用**当日收益。h=5/20 为 `close[t+h]/close[t]-1`。
3. **Rank IC**：因子 z 与远期收益的 Spearman。
4. **滚动 IC / ICIR**：窗口 63，ICIR = mean(滚动 IC) / std(滚动 IC)。阈值默认 `|ICIR_IS| ≥ 0.3`。
5. **Newey–West**：滚动 IC 均值的 HAC t 统计量；以及 `fwd ~ z` 的 OLS 斜率 HAC t。
6. **命中率**：`sign(z)==sign(fwd)`（剔除 0）。
7. **换手**：简单多空仓 `sign(z)` 的日均 `|Δpos|`。
8. **相关簇**：在 **IS 段** z 的两两相关，`|ρ|>0.7` 记入簇；筛选时保留 |ICIR| 更强的一侧。
9. **Walk-forward**：IS vs 最后 126 日 OOS 的 Spearman；入选要求 **OOS IC 与 IS 同号**。
10. **衰减**：报告 1d / 5d / 20d IC。
11. **体制诊断**（不参与默认入选）：`macro_fed_restrictive_flag` 开/关；BTC 30d RV 是否高于 **扩展中位数**（阈值本身也是 PIT）。

入选权重：`sign(IC_IS) * |ICIR_IS|`（`weight_scheme: icir`）。合成仍走原来的 `tanh(Σ w z / ‖w‖₁)`，**不是**截面回归拟合的 alpha。

可选加固（默认关闭，生产应打开）：

- `min_unique`：稀疏 0/1 旗标的 ICIR 会被 4–5 个事件吹爆（本样本霍尔木兹 ICIR_IS = −10.1，有效点 88）。
- `exclude_ids`：在真实 ETF/日历接入前排除 fixture。
- `turnover_penalty` + `turnover_cap`：惩罚日换手过高的噪声腿。

---

## 3. 本样本：按 ICIR / OOS IC 的两端

说明：1 日 Rank IC 的量级大多在 **|IC| < 0.06**。ICIR 大，经常只表示「滚动 IC 几乎常负、波动又小」，**不等于**经济上可交易。

### 3.1 |ICIR_IS| 最高（含未入选）

| 因子 | ICIR_IS | IC_IS | IC_OOS | IC 1d | IC 5d | IC 20d | 同号 | 入选？ |
|---|---:|---:|---:|---:|---:|---:|---|---|
| macro_hormuz_risk_flag | −10.07 | −0.27 | −0.16 | −0.17 | −0.33 | +0.03 | 是 | 是（fixture，n=88） |
| px_btc_dist_200dma | −1.61 | +0.03 | −0.06 | +0.03 | +0.04 | +0.06 | 否 | 否 |
| px_btc_vpt | −1.57 | +0.00 | −0.24 | +0.01 | +0.01 | −0.04 | 否 | 否 |
| px_btc_dist_365dma | −1.54 | +0.01 | −0.04 | +0.01 | −0.00 | −0.02 | 否 | 否 |
| px_btc_mom_60 | −1.54 | +0.01 | −0.11 | +0.00 | −0.02 | −0.01 | 否 | 否 |
| px_eth_vpt | −1.43 | −0.02 | −0.15 | −0.01 | −0.05 | −0.11 | 是 | 是 |
| px_eth_dist_365dma | −1.36 | −0.04 | −0.02 | −0.03 | −0.12 | −0.22 | 是 | 否（与 VPT 冗余） |
| cal_fomc_flag | +1.29 | −0.06 | −0.14 | −0.08 | −0.07 | −0.21 | 是 | 是（占位日历） |
| px_btc_mom_20 | −1.20 | −0.01 | +0.03 | −0.01 | +0.00 | +0.09 | 否 | 否 |
| px_btc_rsi_14 | −1.18 | +0.00 | +0.02 | +0.01 | +0.02 | +0.06 | 是 | 是 |

### 3.2 OOS IC 两端（最后 126 日）

OOS 最正：`px_sol_breakout_20` +0.16、`px_ethbtc_ret_20d` +0.14（但 IS 异号）、`px_btc_breakout_20` +0.12（IS 异号）。

OOS 最负：`px_btc_vpt` −0.24、`macro_2s10s` −0.23（IS 异号）、`macro_dxy_ret_20d` −0.19（同号，入选）。

**解读：** 2026-05–09 这一段 OOS 很短，单因子 OOS IC ±0.15 很容易是噪声。用「OOS 同号」当入选条件，会把这段 OOS **部分信息泄漏进选股**，筛选组合的全样本回测 **不是** 干净的样本外。

### 3.3 默认规则入选的 17 个因子

`macro_hormuz_risk_flag`, `px_eth_vpt`, `cal_fomc_flag`, `px_btc_rsi_14`, `px_btc_resid_mom`, `px_eth_dollar_vol`, `cal_cpi_flag`, `macro_brent_ret_20d`, `macro_dxy_ret_20d`, `px_eth_ret_1d`, `x_btc_us10y_corr_60d`, `px_sol_breakout_20`, `px_sol_vol_z_20`, `px_eth_breakout_20`, `px_btc_rv_cc_20`, `px_eth_liq_proxy`, `macro_us10y_chg`

剔除原因计数：OOS 异号 36、ICIR 不足 27、相关冗余 10。

---

## 4. 默认权重因子：谁活下来，谁是冗余

`config/default.yaml` 里 19 个叙事权重，对照本样本筛选：

| 默认因子 | 默认权重 | 本样本命运 | 说明 |
|---|---:|---|---|
| px_btc_mom_20 / mom_60 | +0.15 / +0.10 | **OOS 异号** | 趋势在 2023–26 牛市 IS 弱、OOS 翻号 |
| px_btc_dist_200dma / 365dma | +0.10 / +0.12 | **OOS 异号** | 二者 IS 相关 **0.97**，只该留一条；本样本两条都没过同号 |
| px_btc_rv_30d | −0.08 | ICIR 不足（0.05） | 与 `px_btc_rv_cc_20` 相关 0.88 |
| px_btc_breakout_20 | +0.08 | OOS 异号 | OOS IC +0.12，IS 接近 0 |
| px_btc_vol_z_20 | +0.05 | ICIR 不足；换手 0.63 | 噪声腿 |
| px_ethbtc_ret_20d | +0.06 | OOS 异号 | OOS 反而最强之一（+0.14） |
| px_btc_dominance_proxy | +0.05 | OOS 异号 | 全样本 1d IC +0.05，20d IC +0.14，值得用更长视野再验 |
| **macro_dxy_ret_20d** | −0.08 | **存活** | IS/OOS 皆负；限制性体制下 IC 更负（−0.06 vs +0.01） |
| **macro_us10y_chg** | −0.07 | **存活** | IC 为正，入选权重符号与默认**相反**（默认做空利率变动） |
| macro_fed_restrictive_flag | −0.05 | ICIR 不足 | 体制旗标本身几乎不预测次日收益 |
| macro_oil_ret_20d | +0.03 | **冗余** | 与 Brent 相关 **0.995**，保留 `macro_brent_ret_20d` |
| macro_gold_ret_20d | +0.04 | ICIR 不足 | |
| x_btc_spx_corr_20d | −0.04 | OOS 异号 | |
| x_btc_dxy_corr_20d | −0.04 | ICIR 不足 | |
| flow_btc_etf_net | +0.12 | ICIR 不足 | fixture，有效点 77，非零 54 |
| **cal_fomc_flag / cal_cpi_flag** | −0.02 | **存活（不可信）** | 占位日历；FOMC 仅 17 天为 1 |

**200dma vs 365dma：** 相关 0.97，叙事上同是「周期位置」，筛选必须去重。本样本两条都因 OOS 翻号被丢，说明均线距离在这段牛市里不是稳定的次日预测器。

**oil vs WTI vs Brent：** `oil–WTI 0.996`，`oil–Brent 0.995`，`WTI–Brent 0.983`。三条是同一条油价风险。默认同时写 `macro_oil_ret_20d` 是重复暴露；筛选正确留下 Brent（|ICIR| 略高）。高波动体制下油价 1d IC = −0.14，低波动接近 0——**混合 IC 会稀释体制效应**。

其它明显簇：`spx` vs `ndx` 20d 收益 0.93；`btc/eth` 200/365dma 与 VPT/成交额 0.72–0.91（慢变量共趋势）；`mom_20` 与 `rsi` / `dist_ma_20` 0.85+。

---

## 5. 组合回测：默认 vs 等权 vs 筛选 vs 买入持有

成本 15 bp，扩展 z-score，`signal_lag=1`，n=1354。

| 组合 | CAGR | 波动 | Sharpe | 最大回撤 | 命中率 |
|---|---:|---:|---:|---:|---:|
| 默认 `model.weights` | −3.09% | 18.59% | −0.08 | −39.87% | 44.42% |
| 全体因子等权 | −3.53% | 14.23% | −0.18 | −33.32% | 45.84% |
| 筛选（ICIR 加权，17 个） | **+4.65%** | 8.35% | **0.59** | −13.75% | 46.89% |
| BTC 买入持有 | **+50.47%** | 46.63% | **1.11** | −53.06% | 50.15% |

同一管道、排除 fixture + `min_unique=10` + 换手上限后，入选剩下 9 个（VPT / RSI / 残差动量 / ETH 成交额 / DXY / BTC–10Y 相关 / SOL·ETH 突破 / BTC 20d RV），筛选组合变为 **CAGR −1.27%，Sharpe 0.04**——「战胜默认」几乎消失。

**结论（对本样本诚实）：**

- 默认叙事权重在 2023–2026 的 BTC 上是亏损的低暴露多空，不是「错过了牛市」的全仓多。
- 买入持有完胜所有 z-score 组合。这是牛市 + 组合被 tanh 压在 ±1、再扣 15 bp 换手的必然结果，**不是**筛选失效的反证，也 **不是** 该改去 All-in BTC 的建议。
- 宽松规则下筛选 Sharpe 0.59，很大一部分来自 **稀疏 fixture 旗标** 和 **用了 OOS 同号**。不能当成可上线的 alpha。

---

## 6. 这种设定下，筛选应当怎么做

### 6.1 PIT / 禁止前瞻

- 因子变换、z-score、体制阈值只用 ≤ t。
- 标签必须是 **信号之后** 的收益；日历/ETF 只能用当时已发布的值。
- IS 统计量的最后几天，远期窗口不能跨进 OOS。
- 相关去重用 IS 相关，不用全样本相关。
- 动态再筛选（每月重选）时，ICIR 本身也要等到标签实现后才能用——否则滚动 IC 是偷看未来收益。

### 6.2 多重检验与过拟合

90 个因子 × 约 3.7 年加密日频，独立检验很少（簇里高度相关）。即便每日 IC 为 0，也会有若干条 |ICIR| > 0.3、OOS 偶然同号。

本样本入选 17/90 ≈ 19%。用「OOS 同号」当硬门，名义上像确认，实际是 **第二层数据挖掘**（你在 90 次投币里挑「两段同号」）。

建议：

- 先按经济叙事 **预注册** 假设（DXY↑ → 风险资产↓），再看 IC 符号是否符合，而不是从 90 列里捞 ICIR。
- 报告 FDR / Bonferroni：例如 90 次检验、5% 双侧，单次 |t| 门槛远高于 2。
- 相关簇按 **一条代表** 计一次检验（油、均线、VPT 各算 1，不算 3）。
- 禁止把筛选权重再在同一段上调参（本库的 ICIR 加权已经是一层拟合）。

### 6.3 体制 vs 混合 IC

2023–2026 大部分时间 10Y > 4%（限制性），混合 IC ≈ 限制性 IC。油价、DXY 在高波动/限制性下更负，低波动接近 0。**只报全样本 IC 会得到一条「略负」的油价因子，丢掉「风险off 时油价冲击才有信息」的结构。**

生产上应：限制性 / 非限制性、高 RV / 低 RV 分表；入选要求 **目标体制内** IS/OOS 同号，而不是池化同号。

### 6.4 为什么「BTC 次日 IC」是弱目标，还该看什么

1. **次日收益噪声极大**（本样本 BTC 年化波动 ~47%）。真实 1d IC=0.02 在 900 点上仍难与运气区分；本样本多数叙事因子 1d |IC| < 0.03。
2. **5d / 20d** 更接近宏观与均线的信息半衰期：油 5d IC ≈ −0.11，主导权代理 20d IC ≈ +0.14，FOMC 旗标 20d IC ≈ −0.21（仍受 fixture 污染）。衰减表应作为主报告，而不是附录。
3. **波动调整标签**：`fwd / σ_t` 或下一根的 Sharpe 贡献，避免高波动日主宰 Spearman。
4. **ETF 资金流的同期泄漏**：若 CSV 的 t 日净流入其实是 t 日盘中/收盘后才完整可知，拿它预测 t→t+1 可能仍偏乐观；拿它解释 **当日** BTC 收益则几乎一定泄漏。正确做法：流入只与 **下一交易日** 对齐，缺失填 0、禁止 ffill。本库已这样对齐，但 fixture 本身不是真流入。
5. **经济检验优于 IC 排名**：符号是否符合叙事、换手是否可执行、相关簇是否只留一条、体制内是否稳定。

### 6.5 推荐生产流程

```
研究假设（预注册）
  → IS 筛选（PIT z、ICIR、去相关、换手、min_unique、排除 fixture）
    → 冻结权重与代码
      → 新时间段 OOS 确认（筛选过程不再改阈值）
        → paper（本库 paper-order，小名义）
          → 极小现货 live（双重闸门 + 风控）
```

不要：在同一 2023–2026 上筛完再把筛选组合的全样本 Sharpe 当 OOS。  
不要：把 z-score 线性组合当成优化过的预测模型。  
不要：在 ETF/日历仍是 fixture 时，让它们进入实盘权重。

配置建议（写入 `screen:` 后重跑）：

```yaml
icir_threshold: 0.3
oos_days: 126
corr_threshold: 0.7
min_unique: 10
turnover_penalty: true
turnover_cap: 0.35
exclude_ids:
  - macro_hormuz_risk_flag
  - cal_fomc_flag
  - cal_cpi_flag
  - flow_btc_etf_net
```

接入真实 Farside/发行商 CSV 与官方日历后，再让 flow/calendar 重新进入研究池。

---

## 7. 局限（请当成本文的一部分）

- **只有一段样本**：2023-01 → 2026-09，主旋律是 ETF 现货上市后的加密牛市 + 限制性利率。没有熊市、没有 QE 重启、没有 2022 类去杠杆。
- **ETF / FOMC / 霍尔木兹是 fixture**。宽松筛选会把它们选进来，并抬高组合回测。
- **z-score 加权不是拟合 alpha**。没有截面、没有中性化、没有对 BTC beta 做残差。
- **OOS 同号入选污染了「筛选组合」全样本指标**。上表 Sharpe 0.59 不能当样本外成绩。
- **90 因子短样本**：多重检验未做正式 FDR；相关簇 >100 对。
- **加密日历 vs 宏观交易日** 混在同一面板，周末宏观为 NaN，IC 样本长度不一致。
- 无 API key、无实盘下单；本文数字仅用于复现研究管道。

---

## 8. 复现命令

```bash
cd /workspace
python3 -m pip install -e ".[dev]"

# 真实行情（不要加 --offline；单票失败时会保留已有 parquet，而不是覆盖成合成数据）
python3 -m factorlib ingest

python3 -m factorlib compute-factors

# 默认权重回测
python3 -m factorlib backtest

# 筛选 + 四组对比（默认 / 全因子等权 / 筛选 / 买入持有）
python3 -m factorlib screen-factors

# 只筛不回测
python3 -m factorlib screen-factors --skip-backtest

# 更严的生产向参数
python3 -m factorlib screen-factors --turnover-penalty --icir-threshold 0.3
```

产出（git 忽略数据文件，报告以本文为准）：

- `data/backtests/factor_screen/factor_metrics.csv`
- `data/backtests/factor_screen/corr_matrix.csv`
- `data/backtests/factor_screen/selected.json`
- `data/backtests/factor_screen/clusters.json`
- `data/backtests/factor_screen/comparison.json`
- `data/backtests/equity.csv`（默认权重）

测试：`python3 -m pytest`（筛选用例覆盖：远期收益不对齐当日、滚动 IC/z-score 不受未来冲击、入选 ID ⊆ 注册表、相关簇丢弱者、`min_unique`、CLI smoke）。
