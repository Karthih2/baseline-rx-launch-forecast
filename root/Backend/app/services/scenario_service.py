"""Scenario handling using the supplied Stage-8 reference behavior."""
from typing import Dict, Tuple


def _speed_multiplier(value) -> float:
    if isinstance(value, str):
        mapping = {"Fast": 1.10, "Normal": 1.00, "Slow": 0.90}
        key = value.strip().title()
        if key not in mapping:
            raise ValueError(
                f"Unrecognized adoption_speed_multiplier '{value}'. "
                "Use Fast, Normal or Slow, or provide a numeric multiplier."
            )
        return mapping[key]
    return float(value)


def normalize_scenario_assumptions(raw: Dict[str, Dict]) -> Dict[str, Dict]:
    """Support both the original backend numeric contract and the Stage-8
    reference file's market_size_adjustment_pct + Fast/Normal/Slow format.
    """
    result = {}
    for name, cfg in raw.items():
        if "market_size_adjustment_pct" in cfg:
            ceiling_mult = 1.0 + float(cfg["market_size_adjustment_pct"]) / 100.0
        else:
            ceiling_mult = float(cfg.get("market_size_multiplier", 1.0))
        speed_mult = _speed_multiplier(cfg.get("adoption_speed_multiplier", 1.0))
        result[name] = {
            "ceiling_mult": ceiling_mult,
            "speed_mult": speed_mult,
            "raw_assumptions": dict(cfg),
        }
    return result


def build_scenario_results(
    known_monthly,
    analog_weighted_curve,
    horizon_months,
    base_p,
    base_q,
    base_m,
    base_calibration_factor,
    base_weight,
    scenario_assumptions: Dict[str, Dict],
):
    from app.services.bass_model_service import build_scenario_forecast

    normalized = normalize_scenario_assumptions(scenario_assumptions)
    results = {}
    for scenario, adj in normalized.items():
        forecast, params = build_scenario_forecast(
            known_monthly,
            analog_weighted_curve,
            horizon_months,
            base_p,
            base_q,
            base_m,
            base_calibration_factor,
            base_weight,
            ceiling_mult=adj["ceiling_mult"],
            speed_mult=adj["speed_mult"],
        )
        results[scenario] = {
            "forecast": forecast.tolist(),
            "params": params,
            "ceiling_mult": adj["ceiling_mult"],
            "speed_mult": adj["speed_mult"],
            "raw_assumptions": adj["raw_assumptions"],
        }
    return results
