#!/usr/bin/env python3
"""Build universe snapshot, sector map, and per-coin 00-facts.md files."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
SNAPSHOT_DAY = SNAPSHOT[:10]

# gecko_id -> (sector, asset_type, chain_framework)
# framework: A native, B stables, C wrapped/lst, D rwa/par instruments
CLASSIFY: dict[str, tuple[str, str, str]] = {
    "bitcoin": ("btc-soverign", "native", "A"),
    "ethereum": ("l1", "native", "A"),
    "tether": ("stables", "stable", "B"),
    "binancecoin": ("cex-exchange", "exchange", "A"),
    "ripple": ("payments-settlement", "native", "A"),
    "usd-coin": ("stables", "stable", "B"),
    "solana": ("l1", "native", "A"),
    "tron": ("l1", "native", "A"),
    "figure-heloc": ("rwa", "rwa", "D"),
    "zcash": ("other", "native", "A"),
    "hyperliquid": ("defi", "native", "A"),
    "dogecoin": ("meme", "meme", "A"),
    "usds": ("stables", "stable", "B"),
    "rain": ("defi", "native", "A"),
    "monero": ("other", "native", "A"),
    "whitebit": ("cex-exchange", "exchange", "A"),
    "chainlink": ("defi", "native", "A"),
    "leo-token": ("cex-exchange", "exchange", "A"),
    "cardano": ("l1", "native", "A"),
    "stellar": ("payments-settlement", "native", "A"),
    "ethena-usde": ("stables", "stable", "B"),
    "dai": ("stables", "stable", "B"),
    "bitcoin-cash": ("payments-settlement", "native", "A"),
    "usd1-wlfi": ("stables", "stable", "B"),
    "uniswap": ("defi", "native", "A"),
    "litecoin": ("payments-settlement", "native", "A"),
    "canton-network": ("l1", "native", "A"),
    "the-open-network": ("l1", "native", "A"),
    "near": ("l1", "native", "A"),
    "global-dollar": ("stables", "stable", "B"),
    "avalanche-2": ("l1", "native", "A"),
    "hedera-hashgraph": ("payments-settlement", "native", "A"),
    "sui": ("l1", "native", "A"),
    "shiba-inu": ("meme", "meme", "A"),
    "paypal-usd": ("stables", "stable", "B"),
    "crypto-com-chain": ("cex-exchange", "exchange", "A"),
    "blackrock-usd-institutional-digital-liquidity-fund": ("rwa", "rwa", "D"),
    "tether-gold": ("rwa", "rwa", "D"),
    "hashnote-usyc": ("rwa", "rwa", "D"),
    "memecore": ("meme", "meme", "A"),
    "bittensor": ("ai-infra", "native", "A"),
    "ripple-usd": ("stables", "stable", "B"),
    "okb": ("cex-exchange", "exchange", "A"),
    "ondo-us-dollar-yield": ("rwa", "rwa", "D"),
    "bitway": ("defi", "native", "A"),
    "aster-2": ("defi", "native", "A"),
    "pax-gold": ("rwa", "rwa", "D"),
    "mantle": ("l2-scaling", "native", "A"),
    "world-liberty-financial": ("other", "native", "A"),
    "aave": ("defi", "native", "A"),
    "polkadot": ("l1", "native", "A"),
    "pump-fun": ("defi", "native", "A"),
    "ondo-finance": ("rwa", "native", "A"),
    "usdd": ("stables", "stable", "B"),
    "htx-dao": ("cex-exchange", "exchange", "A"),
    "ethena": ("defi", "native", "A"),
    "morpho": ("defi", "native", "A"),
    "pepe": ("meme", "meme", "A"),
    "internet-computer": ("l1", "native", "A"),
    "united-stables": ("stables", "stable", "B"),
    "usdgo": ("stables", "stable", "B"),
    "spiko-amundi-overnight-swap-fund-eur": ("rwa", "rwa", "D"),
    "falcon-finance": ("stables", "stable", "B"),
    "worldcoin-wld": ("ai-infra", "native", "A"),
    "bitget-token": ("cex-exchange", "exchange", "A"),
    "sky": ("defi", "native", "A"),
    "bfusd": ("stables", "stable", "B"),
    "ethereum-classic": ("l1", "native", "A"),
    "lighter": ("defi", "native", "A"),
    "venice-token": ("ai-infra", "native", "A"),
    "arbitrum": ("l2-scaling", "native", "A"),
    "polygon-ecosystem-token": ("l2-scaling", "native", "A"),
    "gatechain-token": ("cex-exchange", "exchange", "A"),
    "blockchain-capital": ("rwa", "rwa", "D"),
    "just": ("defi", "native", "A"),
    "pi-network": ("l1", "native", "A"),
    "kucoin-shares": ("cex-exchange", "exchange", "A"),
    "kaspa": ("l1", "native", "A"),
    "quant-network": ("payments-settlement", "native", "A"),
    "cosmos": ("l1", "native", "A"),
    "algorand": ("l1", "native", "A"),
    "eutbl": ("rwa", "rwa", "D"),
    "nexo": ("cex-exchange", "exchange", "A"),
    "janus-henderson-anemoy-aaa-clo-fund": ("rwa", "rwa", "D"),
    "superstate-short-duration-us-government-securities-fund-ustb": ("rwa", "rwa", "D"),
    "jupiter-exchange-solana": ("defi", "native", "A"),
    "pancakeswap-token": ("defi", "native", "A"),
    "dash": ("other", "native", "A"),
    "gho": ("stables", "stable", "B"),
    "render-token": ("ai-infra", "native", "A"),
    "filecoin": ("l1", "native", "A"),
    "janus-henderson-anemoy-treasury-fund": ("rwa", "rwa", "D"),
    "stable-2": ("l2-scaling", "native", "A"),
    "vechain": ("l1", "native", "A"),
    "beldex": ("other", "native", "A"),
    "ether-fi": ("defi", "native", "A"),
    "flare-networks": ("l1", "native", "A"),
    "xdce-crowd-sale": ("l1", "native", "A"),
    "usual-usd": ("stables", "stable", "B"),
    "injective-protocol": ("l1", "native", "A"),
}

SECTOR_META = {
    "stables": ("稳定币", "B"),
    "btc-soverign": ("BTC 主权资产", "A"),
    "l1": ("智能合约 L1", "A"),
    "lst-wrapped": ("LST / 包装资产", "C"),
    "l2-scaling": ("L2 / 扩展层", "A"),
    "cex-exchange": ("交易所平台币", "A"),
    "defi": ("DeFi", "A"),
    "payments-settlement": ("支付与结算", "A"),
    "ai-infra": ("AI / 基础设施", "A"),
    "meme": ("Meme / 文化币", "A"),
    "rwa": ("RWA / 代币化基金与实物", "D"),
    "other": ("其他（隐私、发行主体等）", "A"),
}

# Aggregate DefiLlama protocol families by parentProtocol / explicit slugs.
PROTOCOL_TVL_RULES: dict[str, list[str]] = {
    "aave": ["Aave V1", "Aave V2", "Aave V3", "Aave V4", "Aave Horizon RWA", "Aave Aptos", "Aave Arc"],
    "uniswap": ["Uniswap V1", "Uniswap V2", "Uniswap V3", "Uniswap V4"],
    "morpho": ["Morpho Blue", "Morpho Midnight"],
    "hyperliquid": ["Hyperliquid Bridge", "Hyperliquid HLP", "Hyperliquid Spot Orderbook"],
    "ethena": ["Ethena USDe", "Ethena USDtb", "Ethena tsUSDe"],
    "ether-fi": ["ether.fi Stake", "ether.fi Liquid"],
    "sky": ["Sky Lending"],
    "ondo-finance": ["Ondo Global Markets"],
    "pump-fun": ["PumpSwap"],
    "aster-2": ["Aster Bridge", "Aster USDF", "Aster asBNB"],
    "lighter": ["Lighter Bridge", "Lighter Robinhood Perps"],
    "just": ["JustLend V1", "JustLend V2"],
    "pancakeswap-token": ["PancakeSwap AMM", "PancakeSwap AMM V3", "PancakeSwap Infinity", "PancakeSwap StableSwap"],
    "jupiter-exchange-solana": [
        "Jupiter Lend",
        "Jupiter Perpetual Exchange",
        "Jupiter Staked SOL",
        "Jupiter Lend DEX",
        "Jupiter Offerbook",
    ],
    "rain": ["Rain"],
    "bitway": ["Bitway Earn"],
    "nexo": ["Nexo"],
}

FEE_PARENT: dict[str, str] = {
    "uniswap": "parent#uniswap",
    "aave": "parent#aave",
    "hyperliquid": "parent#hyperliquid",
    "ether-fi": "parent#ether-fi",
    "ethena": "parent#ethena",
    "ethena-usde": "parent#ethena",
    "morpho": "parent#morpho",
    "jupiter-exchange-solana": "parent#jupiter",
    "pancakeswap-token": "parent#pancakeswap",
    "sky": "parent#maker",
    "ondo-finance": "parent#ondo-finance",
    "ondo-us-dollar-yield": "parent#ondo-finance",
    "pump-fun": "parent#pump",
    "aster-2": "parent#astherus",
    "lighter": "parent#lighter",
    "chainlink": "parent#chainlink",
    "just": "parent#justlend",
    "rain": "parent#rain",
}

# Only the canonical L1/L2 row — do not sum every ETH-gas L2 onto ETH.
CHAIN_TVL_NAME: dict[str, str] = {
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "solana": "Solana",
    "binancecoin": "BSC",
    "tron": "Tron",
    "arbitrum": "Arbitrum",
    "hyperliquid": "Hyperliquid L1",
    "polygon-ecosystem-token": "Polygon",
    "avalanche-2": "Avalanche",
    "sui": "Sui",
    "stellar": "Stellar",
    "cardano": "Cardano",
    "the-open-network": "TON",
    "near": "Near",
    "mantle": "Mantle",
    "bittensor": "Bittensor",
    "ripple": "XRPL",
    "stable-2": "Stable",
    "worldcoin-wld": "World Chain",
    "algorand": "Algorand",
    "hedera-hashgraph": "Hedera",
    "internet-computer": "ICP",
    "injective-protocol": "Injective",
    "canton-network": "Canton",
    "filecoin": "Filecoin",
    "xdce-crowd-sale": "XDC",
    "dogecoin": "Doge",
    "vechain": "VeChain",
    "litecoin": "Litecoin",
    "cosmos": "CosmosHub",
    "dash": "Dash",
    "ethereum-classic": "EthereumClassic",
    "zcash": "Zcash",
    "flare-networks": "Flare",
    "crypto-com-chain": "Cronos",
    "okb": "X Layer",
    "bitget-token": "Morph",
    "gatechain-token": "GateLayer",
    "kucoin-shares": "KCC",
    "bitcoin-cash": "Bitcoincash",
}

CHAIN_FEE_NAME: dict[str, str] = {
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "solana": "Solana",
    "binancecoin": "BSC",
    "tron": "Tron",
    "arbitrum": "Arbitrum",
    "hyperliquid": "Hyperliquid L1",
    "polygon-ecosystem-token": "Polygon",
    "avalanche-2": "Avalanche",
    "sui": "Sui",
    "cardano": "Cardano",
    "the-open-network": "TON",
    "near": "Near",
    "mantle": "Mantle",
    "bittensor": "Bittensor",
    "ripple": "XRPL",
    "stable-2": "Stable",
    "worldcoin-wld": "World Chain",
    "algorand": "Algorand",
    "hedera-hashgraph": "Hedera",
    "internet-computer": "ICP",
    "injective-protocol": "Injective",
    "canton-network": "Canton",
    "monero": "Monero",
    "filecoin": "Filecoin",
    "xdce-crowd-sale": "XDC",
    "dogecoin": "Doge",
    "vechain": "VeChain",
    "litecoin": "Litecoin",
    "cosmos": "CosmosHub",
    "dash": "Dash",
    "ethereum-classic": "EthereumClassic",
    "zcash": "Zcash",
    "flare-networks": "Flare",
    "crypto-com-chain": "Cronos",
}

CEX_AUM_NAME: dict[str, str] = {
    "binancecoin": "Binance CEX",
    "okb": "OKX",
    "gatechain-token": "Gate",
    "bitget-token": "Bitget",
    "htx-dao": "HTX",
    "kucoin-shares": "KuCoin",
    "nexo": "Nexo",
    "whitebit": "WhiteBIT",
    "leo-token": "Bitfinex",
    "crypto-com-chain": "Crypto.com",
}


def fmt_num(x: float | None, digits: int = 2) -> str:
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "未知"
    ax = abs(x)
    sign = "-" if x < 0 else ""
    if ax >= 1e12:
        return f"{sign}${ax/1e12:.2f}T"
    if ax >= 1e9:
        return f"{sign}${ax/1e9:.2f}B"
    if ax >= 1e6:
        return f"{sign}${ax/1e6:.2f}M"
    if ax >= 1e3:
        return f"{sign}${ax/1e3:.2f}K"
    return f"{sign}${ax:.{digits}f}"


def fmt_raw(x: float | None, digits: int = 2) -> str:
    if x is None:
        return "未知"
    ax = abs(x)
    sign = "-" if x < 0 else ""
    if ax >= 1e12:
        return f"{sign}{ax/1e12:.2f}T"
    if ax >= 1e9:
        return f"{sign}{ax/1e9:.2f}B"
    if ax >= 1e6:
        return f"{sign}{ax/1e6:.2f}M"
    if ax >= 1e3:
        return f"{sign}{ax/1e3:.2f}K"
    return f"{sign}{ax:.{digits}f}"


def fmt_pct(x: float | None) -> str:
    if x is None:
        return "未知"
    return f"{x:+.2f}%"


def fmt_ratio(x: float | None) -> str:
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "未知"
    return f"{x:.2f}x"


def pct_change(coin: float | None, btc: float | None) -> float | None:
    if coin is None or btc is None:
        return None
    den = 1.0 + btc / 100.0
    if den == 0:
        return None
    return ((1.0 + coin / 100.0) / den - 1.0) * 100.0


def load_json(path: Path):
    return json.loads(path.read_text())


def dir_name(symbol: str, gecko_id: str, used: set[str]) -> str:
    base = f"discuss-{symbol}"
    if base not in used:
        used.add(base)
        return base
    alt = f"discuss-{symbol}-{gecko_id}"
    used.add(alt)
    return alt


def main() -> None:
    markets = load_json(Path("/tmp/top100.json"))
    protocols = load_json(Path("/tmp/llama_protocols.json"))
    fees = load_json(Path("/tmp/llama_fees.json"))
    revenue = load_json(Path("/tmp/llama_revenue.json"))
    stables = load_json(Path("/tmp/llama_stables.json"))
    chains = load_json(Path("/tmp/llama_chains.json"))

    proto_by_name = {p["name"]: p for p in protocols}
    proto_by_gecko = defaultdict(list)
    for p in protocols:
        if p.get("gecko_id"):
            proto_by_gecko[p["gecko_id"]].append(p)
    cex_by_name = {p["name"]: p for p in protocols if p.get("category") == "CEX"}

    chains_by_gecko: dict[str, list] = defaultdict(list)
    for ch in chains:
        gid = ch.get("gecko_id") or ch.get("gasTokenGeckoId")
        if gid:
            chains_by_gecko[gid].append(ch)

    fee_by_parent: dict[str, list] = defaultdict(list)
    fee_by_slug = {}
    fee_by_name = {}
    for p in fees.get("protocols") or []:
        fee_by_slug[p.get("slug")] = p
        fee_by_name[p.get("name")] = p
        parent = p.get("parentProtocol")
        if parent:
            fee_by_parent[parent].append(p)

    rev_by_parent: dict[str, list] = defaultdict(list)
    rev_by_name = {}
    for p in revenue.get("protocols") or []:
        rev_by_name[p.get("name")] = p
        parent = p.get("parentProtocol")
        if parent:
            rev_by_parent[parent].append(p)

    stable_by_gecko = {s["gecko_id"]: s for s in stables.get("peggedAssets") or [] if s.get("gecko_id")}

    btc = next(c for c in markets if c["id"] == "bitcoin")
    btc_ret = {
        "7d": btc.get("price_change_percentage_7d_in_currency"),
        "30d": btc.get("price_change_percentage_30d_in_currency"),
        "1y": btc.get("price_change_percentage_1y_in_currency"),
        "24h": btc.get("price_change_percentage_24h_in_currency") or btc.get("price_change_percentage_24h"),
    }

    used_dirs: set[str] = set()
    records = []
    missing = []
    for coin in markets:
        gid = coin["id"]
        if gid not in CLASSIFY:
            missing.append(gid)
            CLASSIFY[gid] = ("other", "native", "A")
        sector, asset_type, framework = CLASSIFY[gid]
        symbol = coin["symbol"].upper()
        dname = dir_name(symbol, gid, used_dirs)

        price = coin.get("current_price")
        mc = coin.get("market_cap")
        fdv = coin.get("fully_diluted_valuation")
        vol = coin.get("total_volume")
        circ = coin.get("circulating_supply")
        total = coin.get("total_supply")
        mx = coin.get("max_supply")
        mc_fdv = (mc / fdv) if mc and fdv else None
        vol_mc = (vol / mc) if mc and vol else None

        ret24 = coin.get("price_change_percentage_24h_in_currency") or coin.get("price_change_percentage_24h")
        ret7 = coin.get("price_change_percentage_7d_in_currency")
        ret30 = coin.get("price_change_percentage_30d_in_currency")
        ret1y = coin.get("price_change_percentage_1y_in_currency")

        # Chain TVL: canonical row only
        chain_tvl = None
        chain_names = []
        want_chain = CHAIN_TVL_NAME.get(gid)
        if want_chain:
            for ch in chains:
                if ch.get("name") == want_chain:
                    chain_tvl = ch.get("tvl")
                    chain_names.append(f"{ch.get('name')}={fmt_num(chain_tvl)}")
                    break

        # Protocol family TVL
        proto_tvl = None
        proto_names = []
        for name in PROTOCOL_TVL_RULES.get(gid, []):
            p = proto_by_name.get(name)
            if p and p.get("tvl") is not None:
                proto_tvl = (proto_tvl or 0) + p["tvl"]
                proto_names.append(f"{name}={fmt_num(p['tvl'])}")
        if proto_tvl is None:
            # fallback: gecko_id protocols with real tvl, skip CEX/chain placeholders
            skip_cats = {"Chain", "Canonical Bridge", "Foundation"}
            for p in proto_by_gecko.get(gid, []):
                if p.get("category") in skip_cats:
                    continue
                if p.get("tvl"):
                    proto_tvl = (proto_tvl or 0) + p["tvl"]
                    proto_names.append(f"{p['name']}={fmt_num(p['tvl'])}")

        cex_aum = None
        cex_name = CEX_AUM_NAME.get(gid)
        if cex_name and cex_name in cex_by_name:
            cex_aum = cex_by_name[cex_name].get("tvl")
        elif cex_name:
            # fuzzy
            for p in protocols:
                if p.get("category") == "CEX" and p["name"].lower() == cex_name.lower():
                    cex_aum = p.get("tvl")

        # Fees: protocol parent + chain
        fee_30d = fee_1y = fee_ann = None
        fee_notes = []
        parent = FEE_PARENT.get(gid)
        if parent:
            bucket = fee_by_parent.get(parent, [])
            if bucket:
                fee_30d = sum((x.get("total30d") or 0) for x in bucket)
                fee_1y = sum((x.get("total1y") or 0) for x in bucket)
                fee_ann = sum((x.get("annualized1y") or 0) for x in bucket)
                fee_notes.append(f"协议家族 {parent}（{len(bucket)} 条）")
        chain_fee_name = CHAIN_FEE_NAME.get(gid)
        chain_fee_30d = chain_fee_1y = chain_fee_ann = None
        if chain_fee_name and chain_fee_name in fee_by_name:
            cf = fee_by_name[chain_fee_name]
            if cf.get("protocolType") == "chain" or True:
                chain_fee_30d = cf.get("total30d")
                chain_fee_1y = cf.get("total1y")
                chain_fee_ann = cf.get("annualized1y")
                fee_notes.append(f"链费用 {chain_fee_name}")

        rev_30d = rev_1y = None
        if parent:
            rb = rev_by_parent.get(parent, [])
            if rb:
                rev_30d = sum((x.get("total30d") or 0) for x in rb)
                rev_1y = sum((x.get("total1y") or 0) for x in rb)

        tvl_for_ratio = proto_tvl if proto_tvl else chain_tvl
        tvl_label = "protocol" if proto_tvl else ("chain" if chain_tvl else None)
        mc_tvl = (mc / tvl_for_ratio) if mc and tvl_for_ratio else None
        fdv_fee = None
        fee_for_val = fee_ann or (fee_30d * 12 if fee_30d else None)
        if fee_for_val is None and chain_fee_ann:
            fee_for_val = chain_fee_ann
        if fdv and fee_for_val:
            fdv_fee = fdv / fee_for_val

        stable = stable_by_gecko.get(gid)
        llama_circ = None
        llama_peg = None
        llama_price = None
        if stable:
            circ_obj = stable.get("circulating") or {}
            llama_circ = next(iter(circ_obj.values()), None)
            llama_peg = stable.get("pegMechanism") or stable.get("pegType")
            llama_price = stable.get("price")

        rec = {
            "rank": coin.get("market_cap_rank"),
            "id": gid,
            "symbol": symbol,
            "name": coin.get("name"),
            "dir": dname,
            "sector": sector,
            "asset_type": asset_type,
            "framework": framework,
            "price": price,
            "market_cap": mc,
            "fdv": fdv,
            "volume_24h": vol,
            "circulating_supply": circ,
            "total_supply": total,
            "max_supply": mx,
            "mc_fdv": mc_fdv,
            "vol_mc": vol_mc,
            "ret_24h": ret24,
            "ret_7d": ret7,
            "ret_30d": ret30,
            "ret_1y": ret1y,
            "vs_btc_7d": pct_change(ret7, btc_ret["7d"]),
            "vs_btc_30d": pct_change(ret30, btc_ret["30d"]),
            "vs_btc_1y": pct_change(ret1y, btc_ret["1y"]),
            "ath": coin.get("ath"),
            "ath_change_percentage": coin.get("ath_change_percentage"),
            "atl": coin.get("atl"),
            "chain_tvl": chain_tvl,
            "chain_tvl_notes": chain_names,
            "protocol_tvl": proto_tvl,
            "protocol_tvl_notes": proto_names,
            "cex_aum": cex_aum,
            "tvl_used": tvl_for_ratio,
            "tvl_used_kind": tvl_label,
            "mc_tvl": mc_tvl,
            "fee_30d": fee_30d,
            "fee_1y": fee_1y,
            "fee_ann": fee_ann,
            "chain_fee_30d": chain_fee_30d,
            "chain_fee_1y": chain_fee_1y,
            "chain_fee_ann": chain_fee_ann,
            "rev_30d": rev_30d,
            "rev_1y": rev_1y,
            "fdv_fee": fdv_fee,
            "llama_stable_circ": llama_circ,
            "llama_peg": llama_peg,
            "llama_stable_price": llama_price,
            "image": coin.get("image"),
            "last_updated": coin.get("last_updated"),
            "homepage_guess": None,
        }
        records.append(rec)

        sector_dir = ROOT / "research" / sector / dname
        sector_dir.mkdir(parents=True, exist_ok=True)
        facts = render_facts(rec, btc_ret)
        (sector_dir / "00-facts.md").write_text(facts)

    if missing:
        print("UNCLASSIFIED", missing)

    universe = {
        "snapshot_utc": SNAPSHOT,
        "source": "CoinGecko /coins/markets + DefiLlama protocols/fees/stablecoins/chains",
        "btc_returns": btc_ret,
        "count": len(records),
        "coins": records,
    }
    (ROOT / "universe" / "top100.json").write_text(json.dumps(universe, indent=2, ensure_ascii=False))
    (ROOT / "universe" / "sectors.md").write_text(render_sectors(records))
    (ROOT / "research" / "_index.md").write_text(render_index(records))
    print(f"wrote {len(records)} facts, snapshot {SNAPSHOT}")
    by_sec = defaultdict(int)
    for r in records:
        by_sec[r["sector"]] += 1
    for k, v in sorted(by_sec.items(), key=lambda kv: -kv[1]):
        print(f"  {k}: {v}")


def render_facts(r: dict, btc_ret: dict) -> str:
    unlock = "未知（公开 API 未提供已验证解锁日历，辩论中不得编造具体解锁美元金额）"
    lines = [
        f"# 事实包 {r['symbol']} / {r['name']}",
        "",
        f"- 快照时点（UTC）：`{SNAPSHOT}`",
        f"- CoinGecko id：`{r['id']}`",
        f"- 市值排名：`#{r['rank']}`",
        f"- 赛道：`{r['sector']}`",
        f"- 资产类型：`{r['asset_type']}`",
        f"- 逻辑链：`{r['framework']}`",
        f"- 价格来源：CoinGecko markets；TVL/费用来源：DefiLlama（能对上才写）",
        "",
        "## 市值与供给",
        "",
        "| 指标 | 数值 |",
        "|---|---|",
        f"| 价格 | {fmt_num(r['price'], 6) if r['price'] is not None and r['price'] < 1 else fmt_num(r['price'])} |",
        f"| 流通市值 MC | {fmt_num(r['market_cap'])} |",
        f"| 完全稀释估值 FDV | {fmt_num(r['fdv'])} |",
        f"| MC/FDV | {('%.2f' % r['mc_fdv']) if r['mc_fdv'] is not None else '未知'} |",
        f"| 24h 成交额 | {fmt_num(r['volume_24h'])} |",
        f"| 成交额/MC | {('%.2f%%' % (r['vol_mc']*100)) if r['vol_mc'] is not None else '未知'} |",
        f"| 流通供给 | {fmt_raw(r['circulating_supply'], 0)} |",
        f"| 总供给 | {fmt_raw(r['total_supply'], 0)} |",
        f"| 最大供给 | {fmt_raw(r['max_supply'], 0)} |",
        f"| ATH | {fmt_num(r['ath'], 6) if r['ath'] is not None and r['ath'] < 1 else fmt_num(r['ath'])}（距 ATH {fmt_pct(r['ath_change_percentage'])}） |",
        f"| ATL | {fmt_num(r['atl'], 6) if r['atl'] is not None and r['atl'] < 1 else fmt_num(r['atl'])} |",
        "",
        "## 收益与相对 BTC",
        "",
        f"BTC 同期：24h {fmt_pct(btc_ret['24h'])} / 7d {fmt_pct(btc_ret['7d'])} / 30d {fmt_pct(btc_ret['30d'])} / 1y {fmt_pct(btc_ret['1y'])}",
        "",
        "| 区间 | 本币 | 相对 BTC |",
        "|---|---|---|",
        f"| 24h | {fmt_pct(r['ret_24h'])} | — |",
        f"| 7d | {fmt_pct(r['ret_7d'])} | {fmt_pct(r['vs_btc_7d'])} |",
        f"| 30d | {fmt_pct(r['ret_30d'])} | {fmt_pct(r['vs_btc_30d'])} |",
        f"| 1y | {fmt_pct(r['ret_1y'])} | {fmt_pct(r['vs_btc_1y'])} |",
        "",
        "## TVL / 托管 / 稳定币流通",
        "",
        "| 指标 | 数值 | 备注 |",
        "|---|---|---|",
        f"| 链上 DeFi TVL（DefiLlama chain） | {fmt_num(r['chain_tvl'])} | {', '.join(r['chain_tvl_notes']) or '无 chain 匹配'} |",
        f"| 协议家族 TVL | {fmt_num(r['protocol_tvl'])} | {', '.join(r['protocol_tvl_notes']) or '无协议家族匹配'} |",
        f"| CEX 托管 AUM（若适用） | {fmt_num(r['cex_aum'])} | 这是交易所托管资产，不是协议收入，不能当 MC/TVL 主锚 |",
        f"| 本报告用于 MC/TVL 的 TVL | {fmt_num(r['tvl_used'])} | kind=`{r['tvl_used_kind'] or '无'}` |",
        f"| MC/TVL | {fmt_ratio(r['mc_tvl'])} | TVL 缺失则为未知 |",
        f"| Llama 稳定币流通 | {fmt_num(r['llama_stable_circ'])} | peg=`{r['llama_peg'] or 'n/a'}`；Llama 价={r['llama_stable_price'] if r['llama_stable_price'] is not None else 'n/a'} |",
        "",
        "## 费用与收入",
        "",
        "| 指标 | 数值 |",
        "|---|---|",
        f"| 协议家族费用 30d | {fmt_num(r['fee_30d'])} |",
        f"| 协议家族费用 1y | {fmt_num(r['fee_1y'])} |",
        f"| 协议家族费用年化 | {fmt_num(r['fee_ann'])} |",
        f"| 链费用 30d | {fmt_num(r['chain_fee_30d'])} |",
        f"| 链费用 1y | {fmt_num(r['chain_fee_1y'])} |",
        f"| 链费用年化 | {fmt_num(r['chain_fee_ann'])} |",
        f"| 协议收入 30d（Llama type=revenue） | {fmt_num(r['rev_30d'])} |",
        f"| 协议收入 1y | {fmt_num(r['rev_1y'])} |",
        f"| FDV / 年化费用 | {fmt_ratio(r['fdv_fee'])} | 优先用协议家族年化费用，否则用链费用年化 |",
        "",
        "## 解锁",
        "",
        f"- {unlock}",
        "",
        "## 使用规则",
        "",
        "- 多空双方必须引用本文件数字；不得另写一套市值/TVL。",
        "- 空单元格或「未知」不得补成具体数字。",
        "- CEX AUM 只能用于讨论托管规模，不能当成协议 TVL。",
        "- 稳定币价格偏离 1 美元时，用 Llama 价与 CoinGecko 价对照，不要把市值波动自动解释成「成长」。",
        "",
        "研究备忘，非投资建议。",
        "",
    ]
    return "\n".join(lines)


def render_sectors(records: list[dict]) -> str:
    by = defaultdict(list)
    for r in records:
        by[r["sector"]].append(r)
    order = [
        "stables",
        "btc-soverign",
        "l1",
        "lst-wrapped",
        "l2-scaling",
        "cex-exchange",
        "defi",
        "payments-settlement",
        "ai-infra",
        "meme",
        "rwa",
        "other",
    ]
    lines = [
        f"# 市值前 100 赛道分组",
        "",
        f"快照：`{SNAPSHOT}`。来源：CoinGecko 市值排序原样 100 个，不剔除稳定币/包装资产/代币化基金。",
        "",
        "本轮快照中 **没有** stETH/WBTC/WETH 等 LST/包装资产进入前 100，故 `lst-wrapped` 为空，目录仍保留。",
        "代币化国债/信贷/黄金数量已单独成 `rwa` 赛道，不再塞进 `other`。",
        "",
    ]
    for sec in order:
        title, fw = SECTOR_META[sec]
        coins = sorted(by.get(sec, []), key=lambda x: x["rank"] or 999)
        lines.append(f"## {sec} — {title}")
        lines.append("")
        lines.append(f"默认逻辑链：`{fw}`。数量：{len(coins)}")
        lines.append("")
        if not coins:
            lines.append("_本快照无标的。_")
            lines.append("")
            continue
        lines.append("| 排名 | 符号 | 名称 | MC | 目录 |")
        lines.append("|---:|---|---|---|---|")
        for r in coins:
            lines.append(
                f"| {r['rank']} | {r['symbol']} | {r['name']} | {fmt_num(r['market_cap'])} | `research/{sec}/{r['dir']}/` |"
            )
        lines.append("")
    lines.append("## 分类备注")
    lines.append("")
    lines.append("- BNB / CRO 等同时是 L1 与交易所币：按价值捕获主锚放入 `cex-exchange`。")
    lines.append("- Hyperliquid 自有 L1，但费用与叙事在永续 DEX，放入 `defi`。")
    lines.append("- TON 在 CoinGecko 现显示为 Gram (prev. Toncoin)，目录用 `discuss-GRAM`。")
    lines.append("- MemeCore 同时是 L1 与 meme，按主导叙事放入 `meme`。")
    lines.append("- ONDO 是 RWA 协议代币，USDY 是其美元收益产品，都在 `rwa`。")
    lines.append("")
    return "\n".join(lines)


def render_index(records: list[dict]) -> str:
    by = defaultdict(list)
    for r in records:
        by[r["sector"]].append(r)
    lines = [
        "# 研究总目录",
        "",
        f"数据快照：`{SNAPSHOT}`。每个币目录内：`00-facts.md` → `01-bull.md` → `02-bear.md` → `03-debate.md` → `discuss-SYMBOL.md`。",
        "",
        "净判断列在各币最终稿完成后回填。",
        "",
    ]
    for sec, (title, _) in SECTOR_META.items():
        coins = sorted(by.get(sec, []), key=lambda x: x["rank"] or 999)
        lines.append(f"## {title} (`{sec}`)")
        lines.append("")
        if not coins:
            lines.append("_本快照无标的。_")
            lines.append("")
            continue
        for r in coins:
            status = "facts-only"
            lines.append(
                f"- [ ] `#{r['rank']}` **{r['symbol']}** {r['name']} — `{r['dir']}` — {status}"
            )
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
