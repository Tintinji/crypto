# factorlib — 宏观 + 价量因子库与实盘执行骨架

研究工具，**不是投资建议**。回测与纸面单不能代表未来收益。实盘会亏钱。默认只跑 **paper**。

把先前对 BTC 周期叙事（美联储路径、ETF 资金流、DXY、10Y、原油/霍尔木兹、365 日均线、ETF 成本带、韩溢价等）编码成**可复现、无前瞻**的因子，而不是交易口号。

## 架构

```
ingest (yfinance / 离线合成) 
    → data/ohlcv/*.parquet
compute-factors
    → data/factors/panel.parquet
score / backtest
    → data/scores/  data/backtests/
paper-order (默认) 或 live-order (双重闸门)
    → logs/orders.jsonl
```

| 模块 | 路径 | 职责 |
|---|---|---|
| 数据 | `src/factorlib/data/` | YAML 配置、yfinance 包装、日历、ETF CSV、合成备援、parquet 存储 |
| 宏观 | `src/factorlib/macro/` | 利率 / FX / 商品 / 股指 / 相关 / 日历 / 资金流 |
| 价量 | `src/factorlib/pricevolume/` | BTC/ETH/SOL 收益、动量、波动、流动性 |
| 模型 | `src/factorlib/model/` | FactorStore、时序 z-score 合成、扩展窗口回测 |
| 风控 | `src/factorlib/risk/` | 名义、持仓、日亏、点差、KILL 开关 |
| 执行 | `src/factorlib/execution/` | PaperAdapter（无网络）/ ccxt 实盘 |
| CLI | `src/factorlib/cli/` | `ingest` → `compute-factors` → `score` → `paper-order` |

所有滚动窗口只用 **t 及之前** 的 bar。回测默认 `signal_lag=1`（收盘信号，下一根成交）。

## 安装

Python 3.11+。

```bash
cd /workspace
python3 -m pip install -e ".[dev]"
# 或
python3 -m pip install -r requirements.txt
```

## Paper 端到端（默认、安全）

```bash
# 1) 拉行情。Yahoo 失败时自动写入确定性离线 OHLCV，保证链路可跑
python -m factorlib ingest
# 纯离线（不碰网络）：
python -m factorlib ingest --offline

# 2) 算因子面板
python -m factorlib compute-factors

# 3) 合成分数（tanh 后落在 -1..1，即目标仓位）
python -m factorlib score

# 4) 纸面单：按分数 * default_notional_usd 下单，写入 logs/orders.jsonl
python -m factorlib paper-order

# 可选：扩展窗口 + 15bp 成本回测
python -m factorlib backtest

# 因子目录
python -m factorlib list-factors
```

配置：`config/default.yaml`（宇宙、回看期、权重、风控上限）。

## 如何打开实盘（默认关闭）

实盘路径是完整的（ccxt：`binance` / `bybit` / `okx`），但被**两道硬闸**挡住：

1. 环境变量 `LIVE_TRADING=1`（必须正好是 `1`）
2. CLI 显式 `--i-understand-live`

另外还要：

- `EXCHANGE_ID`、`EXCHANGE_API_KEY`、`EXCHANGE_SECRET`（OKX 可能还要 `EXCHANGE_PASSWORD`）
- 风控闸：单笔名义、持仓、日亏、点差
- 未触发 kill：仓库根目录存在 `KILL` 文件，或 `KILL_SWITCH=1` → **拒绝新单**

```bash
export LIVE_TRADING=1
export EXCHANGE_ID=binance
export EXCHANGE_API_KEY=...
export EXCHANGE_SECRET=...
# 可选：EXCHANGE_PASSWORD=  EXCHANGE_SANDBOX=1  EXCHANGE_MARKET_TYPE=spot
python -m factorlib live-order --i-understand-live
```

**永远不要把密钥写进代码或提交到 git。** 参考 `.env.example`。

默认 **现货 + 小名义**（`default_notional_usd: 50`）。若坚持合约：必须 isolated，杠杆上限 **1–2x**（配置 `leverage_cap`，超过 2 会被 CLI 拒绝）。

支持 `market` / `limit`；交易所支持时传 `reduceOnly`。

## 叙事 → 因子 ID

| 研究叙事 | 因子 ID | 说明 |
|---|---|---|
| 美债 10Y / 联储路径 | `macro_us10y_level` `macro_us10y_chg` | ^TNX，CBOE×10 会自动 /10 |
| 2Y / 13 周 / 联储基金代理 | `macro_us2y_*` `macro_us13w_level` `macro_fed_funds_proxy` | 2Y 用 `2YY=F`，缺省则跳过 |
| 2s10s 曲线 | `macro_2s10s` | 10Y − 2Y |
| 限制性政策 | `macro_fed_restrictive_flag` | 10Y > 4% |
| 美元 DXY | `macro_dxy_level` `macro_dxy_ret_20d` | DX-Y.NYB |
| 美元兑日元 | `macro_usdjpy_ret_20d` | USDJPY=X |
| 原油 / 霍尔木兹 | `macro_wti_ret_20d` `macro_brent_ret_20d` `macro_oil_ret_20d` `macro_hormuz_risk_flag` | 油价来自期货；霍尔木兹是静态 CSV 旗标 |
| 黄金 | `macro_gold_ret_20d` | GC=F |
| 美股风险偏好 | `macro_spx_ret_20d` `macro_ndx_ret_20d` | ^GSPC / ^NDX |
| BTC 相对 200/365 日均线 | `px_btc_dist_200dma` `px_btc_dist_365dma` | close/SMA − 1 |
| BTC 已实现波动 | `px_btc_rv_30d` `px_btc_rv_90d` | 年化 close-to-close |
| BTC–SPX/GOLD/DXY/10Y 相关 | `x_btc_spx_corr_*` `x_btc_gold_corr_*` `x_btc_dxy_corr_*` `x_btc_us10y_corr_*` | 20/60 日收益相关 |
| FOMC / CPI | `cal_fomc_flag` `cal_cpi_flag` | `data/fixtures/fomc_cpi_2026q4.csv`（占位日历） |
| IBIT / 现货 BTC ETF 净流入 | `flow_btc_etf_net` | **仅 CSV**。官方流不在 yfinance。接入 Farside / SoSoValue / 发行商文件 |
| ETH/BTC | `px_ethbtc_ret_20d` | |
| BTC 主导权代理 | `px_btc_dominance_proxy` | 供应×价格 / (BTC+ETH+SOL)，非 CMC 官方 |
| 韩溢价 | `px_korea_premium` | BTC-KRW / (BTC-USD×USDKRW) − 1 |
| 价量（三币） | `px_{btc,eth,sol}_*` | 动量 5/20/60、RSI、成交量 z、VPT、Parkinson、Vol-of-vol、ATR、突破、volume/ATR |

ETF **成本带**没有公开稳定 API：把持仓成本/份额 CSV 接进 `etf_flows` 加载器即可扩展，不要从网页硬刮。

## 如何加一个因子

1. 在 `src/factorlib/factors/math.py` 写**只使用 ≤ t** 的变换（或直接用已有函数）。
2. 在 `macro/compute.py` 或 `pricevolume/compute.py` 的 `register_*_specs()` 里加 `FactorSpec`（`id / description / unit / horizon / category / narrative`）。
3. 在对应 `compute_*` 里写入一列，列名 = `id`。
4. （可选）把权重加到 `config/default.yaml` → `model.weights`。
5. 补一条无前瞻测试：全样本 `t` 的值必须等于只用 `[:t]` 重算的值。

单位与默认视野写在 `FactorSpec.unit` / `horizon`（`1d` / `5d` / `20d` / `60d`）。

## 数据说明

- **行情**：优先 yfinance；全部包在 try/except。失败且 `offline_fallback: true` 时写入确定性合成序列（可跑通链路，**不能**当真实研究）。
- **ETF 官方流**：需要你自己的 CSV（Farside / SoSoValue / 发行商）。样本：`data/fixtures/btc_etf_flows.csv`。缺日填 0，不前向填充旧流入。
- **日历**：2026 年 FOMC/CPI 静态表，请换成官方日程。
- 产出：`data/factors/panel.parquet`（无 pyarrow 则退回 CSV）。

## 风控硬闸

下任何新单前：

- `|notional| ≤ max_notional_usd`
- `|position after| ≤ max_position_usd`
- `daily pnl > −max_daily_loss_usd`
- `spread_bps ≤ max_spread_bps`
- 杠杆 ≤ `leverage_cap`（现货 = 1）
- 无 `KILL` / `KILL_SWITCH=1`

意图与成交追加写入 `logs/orders.jsonl`。

## 测试

```bash
python -m pytest
```

覆盖：因子无前瞻、风控拒单、paper 不碰网络、注册表列出因子、实盘 CLI 拒跑。

## 免责声明

本仓库仅供研究与工程演示。不构成买卖建议。加密资产波动极大，实盘可能损失全部本金。先跑 paper，再用交易所沙盒，最后才考虑极小名义的现货。
