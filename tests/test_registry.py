from factorlib.macro.compute import register_macro_specs
from factorlib.pricevolume.compute import register_pv_specs
from factorlib.registry import list_factor_ids, list_factors


REQUIRED = {
    "macro_us10y_chg",
    "macro_dxy_ret_20d",
    "macro_oil_ret_20d",
    "macro_fed_restrictive_flag",
    "px_btc_dist_365dma",
    "px_btc_dist_200dma",
    "px_btc_rv_30d",
    "flow_btc_etf_net",
    "px_ethbtc_ret_20d",
    "px_btc_dominance_proxy",
    "px_btc_mom_20",
    "px_eth_mom_20",
    "px_sol_mom_20",
    "cal_fomc_flag",
    "cal_cpi_flag",
}


def test_registry_lists_required_factors():
    register_macro_specs()
    register_pv_specs()
    ids = set(list_factor_ids())
    missing = REQUIRED - ids
    assert not missing, f"missing factor ids: {sorted(missing)}"
    assert len(ids) >= 40
    cats = {s.category for s in list_factors()}
    assert {"macro", "pricevolume", "flow", "calendar"} <= cats
