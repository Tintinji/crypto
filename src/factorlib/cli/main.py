"""Dry-run CLI: ingest → compute-factors → score → paper-order / live-order / backtest."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Any

from factorlib.data.config import load_config
from factorlib.data.store import read_ohlcv, scores_dir, write_frame, write_ohlcv
from factorlib.data.synthetic import seed_offline_universe
from factorlib.data.yahoo import download_ohlcv
from factorlib.execution.router import (
    build_adapter,
    execute_intent,
    gate_from_cfg,
    live_enabled,
    score_to_intent,
)
from factorlib.model.backtest import run_backtest
from factorlib.model.factor_store import FactorStore
from factorlib.model.metrics import format_metrics
from factorlib.model.scoring import latest_score, score_panel
from factorlib.model.screening import (
    ScreenConfig,
    format_metrics_table,
    persist_screen,
    run_comparison_backtests,
    run_screen,
)
from factorlib.paths import REPO_ROOT
from factorlib.registry import factor_catalog
from factorlib.risk.gates import kill_switch_active

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("factorlib")


def _all_tickers(cfg: dict) -> list[str]:
    uni = cfg.get("universe") or {}
    crypto = list(uni.get("crypto") or [])
    macro = list((uni.get("macro") or {}).values())
    # unique, preserve order
    seen: set[str] = set()
    out: list[str] = []
    for t in crypto + macro:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def cmd_ingest(cfg: dict, args: argparse.Namespace) -> int:
    start = args.start or (cfg.get("ingest") or {}).get("start") or "2023-01-01"
    end = args.end or (cfg.get("ingest") or {}).get("end")
    offline = args.offline or (cfg.get("ingest") or {}).get("offline_fallback", True)
    tickers = _all_tickers(cfg)
    if args.offline:
        seed_offline_universe(tickers, persist=True)
        print(json.dumps({"ok": tickers, "failed": [], "source": "offline_synthetic"}))
        return 0
    ok, failed, reused, fallback = [], [], [], []
    for t in tickers:
        df = download_ohlcv(t, start=start, end=end)
        if df is not None and not df.empty:
            write_ohlcv(t, df)
            ok.append(t)
            logger.info("ingest %s rows=%d last=%.4f", t, len(df), float(df["close"].iloc[-1]))
            continue
        try:
            existing = read_ohlcv(t)
        except FileNotFoundError:
            existing = None
        if existing is not None and not existing.empty:
            reused.append(t)
            ok.append(t)
            logger.warning("yfinance missed %s — keeping existing OHLCV rows=%d", t, len(existing))
            continue
        failed.append(t)
    if failed and offline:
        logger.warning("yfinance missed %s — seeding deterministic offline OHLCV", failed)
        seed_offline_universe(failed, persist=True)
        fallback = list(failed)
        ok.extend(failed)
        failed = []
    print(
        json.dumps(
            {
                "ok": ok,
                "failed": failed,
                "reused": reused,
                "fallback": fallback,
                "source": "yfinance+fallback" if (offline and fallback) else "yfinance",
            }
        )
    )
    return 0 if ok else 1


def cmd_compute_factors(cfg: dict, _args: argparse.Namespace) -> int:
    store = FactorStore(cfg)
    panel = store.compute()
    if panel.empty:
        print("no factor panel — run ingest first", file=sys.stderr)
        return 1
    path = store.persist(panel)
    print(json.dumps({"rows": int(len(panel)), "cols": int(panel.shape[1]), "path": str(path)}))
    return 0


def _scores(cfg: dict):
    store = FactorStore(cfg)
    panel = store.load()
    model = cfg.get("model") or {}
    scores = score_panel(
        panel,
        model.get("weights") or {},
        window=int(model.get("zscore_window", 126)),
        min_periods=int(model.get("zscore_min_periods", 20)),
        expanding=bool(model.get("expanding", True)),
        z_clip=float(model.get("z_clip", 3.0)),
    )
    return store, panel, scores


def cmd_score(cfg: dict, _args: argparse.Namespace) -> int:
    _store, _panel, scores = _scores(cfg)
    path = write_frame(scores.to_frame(), scores_dir() / "score.parquet")
    scores.to_csv(scores_dir() / "score.csv")
    ts, val = latest_score(scores)
    print(json.dumps({"asof": str(ts.date()), "score": val, "path": str(path)}))
    return 0


def _last_crypto_price(cfg: dict, yf_ticker: str, ccxt_symbol: str) -> float:
    try:
        df = read_ohlcv(yf_ticker)
        return float(df["close"].iloc[-1])
    except FileNotFoundError:
        return 0.0


def _place(cfg: dict, *, mode: str, understand_live: bool = False) -> int:
    exec_cfg = cfg.get("execution") or {}
    if mode == "live":
        if not live_enabled():
            print("refused: live mode requires env LIVE_TRADING=1", file=sys.stderr)
            return 2
        if not understand_live:
            print("refused: pass --i-understand-live", file=sys.stderr)
            return 2
        if (exec_cfg.get("market_type") or "spot") != "spot":
            lev = float(exec_cfg.get("leverage_cap", 1))
            if lev > 2:
                print("refused: futures leverage_cap must be 1–2", file=sys.stderr)
                return 2

    if kill_switch_active((cfg.get("risk") or {}).get("kill_switch_file", "KILL")):
        print("refused: kill switch active", file=sys.stderr)
        return 3

    _store, _panel, scores = _scores(cfg)
    ts, val = latest_score(scores)
    symbol = exec_cfg.get("symbol", "BTC/USDT")
    yf_ticker = (cfg.get("model") or {}).get("target_symbol", "BTC-USD")
    last = _last_crypto_price(cfg, yf_ticker, symbol)
    if last <= 0:
        print("no last price — run ingest", file=sys.stderr)
        return 1

    adapter = build_adapter(cfg, mode=mode, last_prices={symbol: last, yf_ticker: last})
    gate = gate_from_cfg(cfg)
    intent = score_to_intent(
        val,
        symbol=symbol,
        last_price=last,
        default_notional_usd=float(exec_cfg.get("default_notional_usd", 50)),
        order_type=exec_cfg.get("order_type", "market"),
        limit_offset_bps=float(exec_cfg.get("limit_offset_bps", 5)),
        reduce_only=bool(exec_cfg.get("reduce_only", False)),
        mode=mode,
    )
    result = execute_intent(adapter, gate, intent)
    payload: dict[str, Any] = {
        "mode": mode,
        "asof": str(ts.date()),
        "score": val,
        "intent": intent.to_dict(),
        "ok": result.ok,
        "status": result.status,
        "order_id": result.exchange_order_id,
        "error": result.error,
        "disclaimer": "research only — not financial advice; live trading can lose money",
    }
    print(json.dumps(payload, default=str))
    return 0 if result.ok else 4


def cmd_paper_order(cfg: dict, _args: argparse.Namespace) -> int:
    return _place(cfg, mode="paper")


def cmd_live_order(cfg: dict, args: argparse.Namespace) -> int:
    return _place(cfg, mode="live", understand_live=bool(args.i_understand_live))


def cmd_backtest(cfg: dict, _args: argparse.Namespace) -> int:
    store = FactorStore(cfg)
    panel = store.load()
    model = cfg.get("model") or {}
    target = model.get("target_symbol", "BTC-USD")
    close = read_ohlcv(target)["close"]
    _eq, metrics = run_backtest(
        panel,
        close,
        model.get("weights") or {},
        cost_bps=float(model.get("cost_bps", 15)),
        signal_lag=int(model.get("signal_lag", 1)),
        zscore_window=int(model.get("zscore_window", 126)),
        zscore_min_periods=int(model.get("zscore_min_periods", 20)),
        expanding=bool(model.get("expanding", True)),
        z_clip=float(model.get("z_clip", 3.0)),
    )
    print(format_metrics(metrics))
    print(json.dumps(metrics, indent=2))
    return 0


def cmd_screen_factors(cfg: dict, args: argparse.Namespace) -> int:
    store = FactorStore(cfg)
    try:
        panel = store.load()
    except FileNotFoundError:
        print("no factor panel — run compute-factors first", file=sys.stderr)
        return 1
    if panel.empty:
        print("empty factor panel — run compute-factors first", file=sys.stderr)
        return 1
    model = cfg.get("model") or {}
    target = model.get("target_symbol", "BTC-USD")
    close = read_ohlcv(target)["close"]
    scfg = ScreenConfig.from_cfg(cfg)
    if args.oos_days is not None:
        scfg.oos_days = int(args.oos_days)
    if args.icir_threshold is not None:
        scfg.icir_threshold = float(args.icir_threshold)
    if args.corr_threshold is not None:
        scfg.corr_threshold = float(args.corr_threshold)
    if args.weight_scheme:
        scfg.weight_scheme = str(args.weight_scheme)
    if args.turnover_penalty:
        scfg.turnover_penalty = True

    result = run_screen(panel, close, scfg, registry_ids=store.factor_ids())
    dest = persist_screen(result)
    print("research only — not financial advice")
    print(json.dumps({"split": result.split, "n_factors": int(len(result.metrics)), "n_selected": len(result.selected), "selected": result.selected, "path": str(dest)}, indent=2))
    print("\n=== top 12 by |ICIR_IS| ===")
    ranked = result.metrics.reindex(result.metrics["icir_is"].abs().sort_values(ascending=False).index)
    print(format_metrics_table(ranked.head(12)))
    print("\n=== bottom 8 by ICIR_IS ===")
    print(format_metrics_table(result.metrics.sort_values("icir_is", na_position="first").head(8)))
    print(f"\n=== selected ({len(result.selected)}) weights={result.weights} ===")
    if not args.skip_backtest:
        comparison = run_comparison_backtests(
            panel,
            close,
            default_weights=model.get("weights") or {},
            screened_weights=result.weights,
            cfg=scfg,
            persist=True,
            out_dir=dest,
        )
        result.comparison = comparison
        print("\n=== comparison (cost_bps=%.1f) ===" % scfg.cost_bps)
        for name, met in comparison.items():
            if "cagr" in met:
                print(f"{name:12s}  {format_metrics(met)}")
        print(json.dumps({k: v for k, v in comparison.items()}, indent=2, default=str))
    return 0


def cmd_list_factors(_cfg: dict, _args: argparse.Namespace) -> int:
    from factorlib.macro.compute import register_macro_specs
    from factorlib.pricevolume.compute import register_pv_specs

    register_macro_specs()
    register_pv_specs()
    print(json.dumps(factor_catalog(), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="factorlib",
        description="Macro + price/volume factors, scores, paper/live orders. Research only.",
    )
    p.add_argument("--config", default=str(REPO_ROOT / "config" / "default.yaml"))
    sub = p.add_subparsers(dest="cmd", required=True)

    ing = sub.add_parser("ingest", help="Download OHLCV (yfinance) with offline fallback")
    ing.add_argument("--start", default=None)
    ing.add_argument("--end", default=None)
    ing.add_argument("--offline", action="store_true", help="Skip Yahoo; seed synthetic OHLCV")
    ing.set_defaults(func=cmd_ingest)

    cf = sub.add_parser("compute-factors", help="Build and persist factor panel")
    cf.set_defaults(func=cmd_compute_factors)

    sc = sub.add_parser("score", help="Z-score combo → position target")
    sc.set_defaults(func=cmd_score)

    po = sub.add_parser("paper-order", help="Size a paper order from latest score (default, safe)")
    po.set_defaults(func=cmd_paper_order)

    lo = sub.add_parser("live-order", help="Live order — refused unless LIVE_TRADING=1 and flag")
    lo.add_argument(
        "--i-understand-live",
        action="store_true",
        help="Acknowledge that live orders can lose real money",
    )
    lo.set_defaults(func=cmd_live_order)

    bt = sub.add_parser("backtest", help="Expanding-window walk-forward with costs")
    bt.set_defaults(func=cmd_backtest)

    lf = sub.add_parser("list-factors", help="Print factor catalog")
    lf.set_defaults(func=cmd_list_factors)

    sf = sub.add_parser(
        "screen-factors",
        help="PIT factor screen (IC/ICIR/clusters/OOS) + screened-weight backtest",
    )
    sf.add_argument("--oos-days", type=int, default=None)
    sf.add_argument("--icir-threshold", type=float, default=None)
    sf.add_argument("--corr-threshold", type=float, default=None)
    sf.add_argument("--weight-scheme", choices=["icir", "equal_risk", "equal"], default=None)
    sf.add_argument("--turnover-penalty", action="store_true")
    sf.add_argument("--skip-backtest", action="store_true")
    sf.set_defaults(func=cmd_screen_factors)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    cfg = load_config(args.config)
    return int(args.func(cfg, args))
