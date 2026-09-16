# 市值前 100 赛道分组

快照：`2026-09-16T21:13:43Z`。来源：CoinGecko 市值排序原样 100 个，不剔除稳定币/包装资产/代币化基金。

本轮快照中 **没有** stETH/WBTC/WETH 等 LST/包装资产进入前 100，故 `lst-wrapped` 为空，目录仍保留。
代币化国债/信贷/黄金数量已单独成 `rwa` 赛道，不再塞进 `other`。

## stables — 稳定币

默认逻辑链：`B`。数量：16

| 排名 | 符号 | 名称 | MC | 目录 |
|---:|---|---|---|---|
| 3 | USDT | Tether | $183.31B | `research/stables/discuss-USDT/` |
| 6 | USDC | USDC | $73.61B | `research/stables/discuss-USDC/` |
| 13 | USDS | USDS | $9.57B | `research/stables/discuss-USDS/` |
| 21 | USDE | Ethena USDe | $4.73B | `research/stables/discuss-USDE/` |
| 22 | DAI | Dai | $4.58B | `research/stables/discuss-DAI/` |
| 24 | USD1 | USD1 | $4.34B | `research/stables/discuss-USD1/` |
| 30 | USDG | Global Dollar | $3.28B | `research/stables/discuss-USDG/` |
| 35 | PYUSD | PayPal USD | $2.82B | `research/stables/discuss-PYUSD/` |
| 42 | RLUSD | Ripple USD | $2.34B | `research/stables/discuss-RLUSD/` |
| 54 | USDD | USDD | $1.51B | `research/stables/discuss-USDD/` |
| 60 | U | United Stables | $1.38B | `research/stables/discuss-U/` |
| 61 | USDGO | USDGO | $1.38B | `research/stables/discuss-USDGO/` |
| 63 | USDF | Falcon USD | $1.34B | `research/stables/discuss-USDF/` |
| 67 | BFUSD | BFUSD | $1.32B | `research/stables/discuss-BFUSD/` |
| 89 | GHO | GHO | $698.03M | `research/stables/discuss-GHO/` |
| 99 | USD0 | Usual USD | $547.03M | `research/stables/discuss-USD0/` |

## btc-soverign — BTC 主权资产

默认逻辑链：`A`。数量：1

| 排名 | 符号 | 名称 | MC | 目录 |
|---:|---|---|---|---|
| 1 | BTC | Bitcoin | $1.53T | `research/btc-soverign/discuss-BTC/` |

## l1 — 智能合约 L1

默认逻辑链：`A`。数量：21

| 排名 | 符号 | 名称 | MC | 目录 |
|---:|---|---|---|---|
| 2 | ETH | Ethereum | $294.18B | `research/l1/discuss-ETH/` |
| 7 | SOL | Solana | $57.91B | `research/l1/discuss-SOL/` |
| 8 | TRX | TRON | $31.89B | `research/l1/discuss-TRX/` |
| 19 | ADA | Cardano | $7.32B | `research/l1/discuss-ADA/` |
| 27 | CC | Canton | $3.80B | `research/l1/discuss-CC/` |
| 28 | GRAM | Gram (prev. Toncoin) | $3.65B | `research/l1/discuss-GRAM/` |
| 29 | NEAR | NEAR Protocol | $3.38B | `research/l1/discuss-NEAR/` |
| 31 | AVAX | Avalanche | $3.27B | `research/l1/discuss-AVAX/` |
| 33 | SUI | Sui | $2.91B | `research/l1/discuss-SUI/` |
| 51 | DOT | Polkadot | $1.72B | `research/l1/discuss-DOT/` |
| 59 | ICP | Internet Computer | $1.41B | `research/l1/discuss-ICP/` |
| 68 | ETC | Ethereum Classic | $1.15B | `research/l1/discuss-ETC/` |
| 76 | PI | Pi Network | $948.80M | `research/l1/discuss-PI/` |
| 78 | KAS | Kaspa | $903.06M | `research/l1/discuss-KAS/` |
| 80 | ATOM | Cosmos Hub | $798.94M | `research/l1/discuss-ATOM/` |
| 81 | ALGO | Algorand | $795.30M | `research/l1/discuss-ALGO/` |
| 91 | FIL | Filecoin | $667.01M | `research/l1/discuss-FIL/` |
| 94 | VET | VeChain | $608.83M | `research/l1/discuss-VET/` |
| 97 | FLR | Flare | $552.61M | `research/l1/discuss-FLR/` |
| 98 | XDC | XDC Network | $548.56M | `research/l1/discuss-XDC/` |
| 100 | INJ | Injective | $541.74M | `research/l1/discuss-INJ/` |

## lst-wrapped — LST / 包装资产

默认逻辑链：`C`。数量：0

_本快照无标的。_

## l2-scaling — L2 / 扩展层

默认逻辑链：`A`。数量：4

| 排名 | 符号 | 名称 | MC | 目录 |
|---:|---|---|---|---|
| 48 | MNT | Mantle | $1.82B | `research/l2-scaling/discuss-MNT/` |
| 71 | ARB | Arbitrum | $1.10B | `research/l2-scaling/discuss-ARB/` |
| 72 | POL | POL (ex-MATIC) | $1.00B | `research/l2-scaling/discuss-POL/` |
| 93 | STABLE | ​​Stable | $637.33M | `research/l2-scaling/discuss-STABLE/` |

## cex-exchange — 交易所平台币

默认逻辑链：`A`。数量：10

| 排名 | 符号 | 名称 | MC | 目录 |
|---:|---|---|---|---|
| 4 | BNB | BNB | $95.89B | `research/cex-exchange/discuss-BNB/` |
| 16 | WBT | WhiteBIT Coin | $9.21B | `research/cex-exchange/discuss-WBT/` |
| 18 | LEO | LEO Token | $8.14B | `research/cex-exchange/discuss-LEO/` |
| 36 | CRO | Cronos | $2.79B | `research/cex-exchange/discuss-CRO/` |
| 43 | OKB | OKB | $2.32B | `research/cex-exchange/discuss-OKB/` |
| 55 | HTX | HTX DAO | $1.50B | `research/cex-exchange/discuss-HTX/` |
| 65 | BGB | Bitget Token | $1.33B | `research/cex-exchange/discuss-BGB/` |
| 73 | GT | Gate | $989.15M | `research/cex-exchange/discuss-GT/` |
| 77 | KCS | KuCoin | $941.00M | `research/cex-exchange/discuss-KCS/` |
| 83 | NEXO | NEXO | $791.51M | `research/cex-exchange/discuss-NEXO/` |

## defi — DeFi

默认逻辑链：`A`。数量：16

| 排名 | 符号 | 名称 | MC | 目录 |
|---:|---|---|---|---|
| 11 | HYPE | Hyperliquid | $17.47B | `research/defi/discuss-HYPE/` |
| 14 | RAIN | Rain | $9.26B | `research/defi/discuss-RAIN/` |
| 17 | LINK | Chainlink | $8.22B | `research/defi/discuss-LINK/` |
| 25 | UNI | Uniswap | $4.04B | `research/defi/discuss-UNI/` |
| 45 | BTW | Bitway | $1.98B | `research/defi/discuss-BTW/` |
| 46 | ASTER | Aster | $1.87B | `research/defi/discuss-ASTER/` |
| 50 | AAVE | Aave | $1.81B | `research/defi/discuss-AAVE/` |
| 52 | PUMP | Pump.fun | $1.72B | `research/defi/discuss-PUMP/` |
| 56 | ENA | Ethena | $1.49B | `research/defi/discuss-ENA/` |
| 57 | MORPHO | Morpho | $1.45B | `research/defi/discuss-MORPHO/` |
| 66 | SKY | Sky | $1.33B | `research/defi/discuss-SKY/` |
| 69 | LIT | Lighter | $1.14B | `research/defi/discuss-LIT/` |
| 75 | JST | JUST | $956.36M | `research/defi/discuss-JST/` |
| 86 | JUP | Jupiter | $721.19M | `research/defi/discuss-JUP/` |
| 87 | CAKE | PancakeSwap | $719.70M | `research/defi/discuss-CAKE/` |
| 96 | ETHFI | Ether.fi | $566.81M | `research/defi/discuss-ETHFI/` |

## payments-settlement — 支付与结算

默认逻辑链：`A`。数量：6

| 排名 | 符号 | 名称 | MC | 目录 |
|---:|---|---|---|---|
| 5 | XRP | XRP | $81.75B | `research/payments-settlement/discuss-XRP/` |
| 20 | XLM | Stellar | $6.38B | `research/payments-settlement/discuss-XLM/` |
| 23 | BCH | Bitcoin Cash | $4.39B | `research/payments-settlement/discuss-BCH/` |
| 26 | LTC | Litecoin | $3.98B | `research/payments-settlement/discuss-LTC/` |
| 32 | HBAR | Hedera | $3.22B | `research/payments-settlement/discuss-HBAR/` |
| 79 | QNT | Quant | $879.59M | `research/payments-settlement/discuss-QNT/` |

## ai-infra — AI / 基础设施

默认逻辑链：`A`。数量：4

| 排名 | 符号 | 名称 | MC | 目录 |
|---:|---|---|---|---|
| 41 | TAO | Bittensor | $2.49B | `research/ai-infra/discuss-TAO/` |
| 64 | WLD | Worldcoin | $1.33B | `research/ai-infra/discuss-WLD/` |
| 70 | VVV | Venice Token | $1.12B | `research/ai-infra/discuss-VVV/` |
| 90 | RENDER | Render | $692.01M | `research/ai-infra/discuss-RENDER/` |

## meme — Meme / 文化币

默认逻辑链：`A`。数量：4

| 排名 | 符号 | 名称 | MC | 目录 |
|---:|---|---|---|---|
| 12 | DOGE | Dogecoin | $12.57B | `research/meme/discuss-DOGE/` |
| 34 | SHIB | Shiba Inu | $2.89B | `research/meme/discuss-SHIB/` |
| 40 | M | MemeCore | $2.55B | `research/meme/discuss-M/` |
| 58 | PEPE | Pepe | $1.42B | `research/meme/discuss-PEPE/` |

## rwa — RWA / 代币化基金与实物

默认逻辑链：`D`。数量：13

| 排名 | 符号 | 名称 | MC | 目录 |
|---:|---|---|---|---|
| 9 | FIGR_HELOC | Figure Heloc | $22.69B | `research/rwa/discuss-FIGR_HELOC/` |
| 37 | BUIDL | BlackRock USD Institutional Digital Liquidity Fund | $2.70B | `research/rwa/discuss-BUIDL/` |
| 38 | XAUT | Tether Gold | $2.66B | `research/rwa/discuss-XAUT/` |
| 39 | USYC | Circle USYC | $2.56B | `research/rwa/discuss-USYC/` |
| 44 | USDY | Ondo US Dollar Yield | $2.23B | `research/rwa/discuss-USDY/` |
| 47 | PAXG | PAX Gold | $1.86B | `research/rwa/discuss-PAXG/` |
| 53 | ONDO | Ondo | $1.66B | `research/rwa/discuss-ONDO/` |
| 62 | EURSAFO | Spiko Amundi Overnight Swap Fund (EUR) | $1.37B | `research/rwa/discuss-EURSAFO/` |
| 74 | BCAP | Blockchain Capital | $970.80M | `research/rwa/discuss-BCAP/` |
| 82 | EUTBL | Spiko EU T-Bills Money Market Fund | $792.40M | `research/rwa/discuss-EUTBL/` |
| 84 | JAAA | Janus Henderson Anemoy AAA CLO Fund | $774.91M | `research/rwa/discuss-JAAA/` |
| 85 | USTB | Invesco Short Duration US Government Securities Fund | $739.50M | `research/rwa/discuss-USTB/` |
| 92 | JTRSY | Janus Henderson Anemoy Treasury Fund | $650.17M | `research/rwa/discuss-JTRSY/` |

## other — 其他（隐私、发行主体等）

默认逻辑链：`A`。数量：5

| 排名 | 符号 | 名称 | MC | 目录 |
|---:|---|---|---|---|
| 10 | ZEC | Zcash | $22.38B | `research/other/discuss-ZEC/` |
| 15 | XMR | Monero | $9.24B | `research/other/discuss-XMR/` |
| 49 | WLFI | World Liberty Financial | $1.82B | `research/other/discuss-WLFI/` |
| 88 | DASH | Dash | $710.92M | `research/other/discuss-DASH/` |
| 95 | BDX | Beldex | $597.74M | `research/other/discuss-BDX/` |

## 分类备注

- BNB / CRO 等同时是 L1 与交易所币：按价值捕获主锚放入 `cex-exchange`。
- Hyperliquid 自有 L1，但费用与叙事在永续 DEX，放入 `defi`。
- TON 在 CoinGecko 现显示为 Gram (prev. Toncoin)，目录用 `discuss-GRAM`。
- MemeCore 同时是 L1 与 meme，按主导叙事放入 `meme`。
- ONDO 是 RWA 协议代币，USDY 是其美元收益产品，都在 `rwa`。
