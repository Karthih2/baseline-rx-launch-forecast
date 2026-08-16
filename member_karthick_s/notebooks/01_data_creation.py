"""
generate_datasets.py
=====================
Generates the three raw-input-layer datasets for the forecasting pipeline,
per the "Dataset Creation" spec:

  1. Analog / Historical Drug Dataset  -> 35 drugs x (12 static features + 36-month Rx curve)
  2. New Drug Dataset                  -> 1 drug  x (12 static features + 18-26 weekly early Rx points)
  3. Scenario Assumptions Dataset      -> 3 rows   (Bull / Base / Bear)

Design notes
------------
- Static features are drawn from realistic, diverse categorical/numeric pools
  (no near-duplicate rows) using a fixed RNG seed for reproducibility.
- Monthly Rx curves are NOT random noise. Each curve is a logistic ("Bass-like")
  S-curve whose CEILING and SPEED are derived from that drug's own static
  features, so later "analog similarity" logic is meaningful:
      ceiling (peak penetration) shrinks with competitive_density,
          payer_restrictiveness, and higher price_tier; grows with
          special_designation and larger market_size.
      speed (time-to-ramp) increases with promotional_intensity and
          eases with route of administration (oral/topical adopted faster
          than injectable/IV) and lower payer_restrictiveness.
  A small amount of multiplicative noise is layered on top so curves look
  like real Rx data rather than a perfect mathematical curve.
- The new drug's early_rx uses the SAME generative model, just sliced to the
  first N weeks (early ramp only) -- this is the "time grain" locked to
  weekly, per the spec's recommendation for the new drug.
- Output: three JSON files (list-of-documents, Mongo-import-ready) written to
  ./output/. An optional --mongo-uri flag will additionally load them into
  MongoDB collections (analog_drugs, new_drug, scenario_assumptions) if
  pymongo is installed and a URI is supplied.

Usage
-----
    python generate_datasets.py --seed 42 --outdir ./output
    python generate_datasets.py --seed 42 --mongo-uri "mongodb://localhost:27017" --db forecasting_raw
"""

import argparse
import json
import math
import os
import random
from pathlib import Path

# --------------------------------------------------------------------------
# Reference pools (diverse, realistic categorical values)
# --------------------------------------------------------------------------

MECHANISMS = [
    "GLP-1 agonist", "SGLT2 inhibitor", "JAK inhibitor", "PD-1 inhibitor",
    "PCSK9 inhibitor", "IL-17 inhibitor", "TNF-alpha inhibitor",
    "Factor Xa inhibitor", "Tyrosine kinase inhibitor", "Dopamine agonist",
    "Beta-2 agonist", "Proton pump inhibitor", "ACE inhibitor",
    "CGRP antagonist", "Anti-CD20 monoclonal antibody", "DPP-4 inhibitor",
    "Sodium channel blocker", "mTOR inhibitor", "Integrin antagonist",
    "Complement C5 inhibitor",
]

ROUTES = ["Oral", "Injectable", "Subcutaneous", "Intravenous", "Topical", "Inhaled"]

# relative "adoption friction" by route (higher = slower ramp)
ROUTE_FRICTION = {
    "Oral": 0.0, "Topical": 0.0, "Inhaled": 0.05,
    "Subcutaneous": 0.10, "Injectable": 0.15, "Intravenous": 0.25,
}

SPECIALTIES = [
    "Primary Care", "Endocrinology", "Oncology", "Rheumatology", "Neurology",
    "Cardiology", "Dermatology", "Gastroenterology", "Pulmonology", "Psychiatry",
    "Nephrology", "Hematology",
]

QUARTERS = ["Q1", "Q2", "Q3", "Q4"]

# syllable pools for synthetic, non-trademark-colliding drug brand names
NAME_PREFIX = ["Xel", "Nuro", "Vyn", "Zora", "Halo", "Kyn", "Bren", "Solix",
               "Trex", "Amara", "Onyx", "Perin", "Lumis", "Cala", "Draval",
               "Ferro", "Glim", "Ixara", "Jovex", "Kestra"]
NAME_SUFFIX = ["vara", "tide", "zumab", "prel", "dine", "tinib", "mune",
               "cort", "sera", "flux", "gene", "para", "xen", "lith", "via"]


def make_drug_name(rng, used):
    while True:
        name = rng.choice(NAME_PREFIX) + rng.choice(NAME_SUFFIX)
        if name not in used:
            used.add(name)
            return name.capitalize()


# --------------------------------------------------------------------------
# Static feature generation (12 fields, shared schema for analog + new drug)
# --------------------------------------------------------------------------

def generate_static_features(rng, drug_id, drug_name):
    return {
        "drug_id": drug_id,
        "drug_name": drug_name,
        "mechanism_of_action": rng.choice(MECHANISMS),
        "route_of_administration": rng.choice(ROUTES),
        "target_specialty": rng.choice(SPECIALTIES),
        "market_size": int(rng.uniform(200_000, 3_000_000)),
        "competitive_density": rng.randint(1, 5),
        "payer_restrictiveness": rng.randint(1, 5),
        "launch_quarter": rng.choice(QUARTERS),
        "promotional_intensity": rng.randint(1, 5),
        "special_designation": rng.random() < 0.15,   # ~15% get orphan/breakthrough-style boost
        "price_tier": rng.randint(1, 5),
    }


# --------------------------------------------------------------------------
# Curve model: static features -> Bass-like logistic S-curve
# --------------------------------------------------------------------------

def curve_params(features):
    """Derive (ceiling_fraction, speed_k, inflection_t) from static features."""
    cd = features["competitive_density"]
    pr = features["payer_restrictiveness"]
    pi = features["promotional_intensity"]
    price = features["price_tier"]
    special = features["special_designation"]
    route_friction = ROUTE_FRICTION[features["route_of_administration"]]

    # Ceiling: fraction of market_size that becomes the plateau Rx level
    ceiling = 0.22
    ceiling -= 0.025 * (cd - 3)        # more competitors -> lower ceiling
    ceiling -= 0.02 * (pr - 3)         # stricter payers -> lower ceiling
    ceiling -= 0.015 * (price - 3)     # pricier -> slightly lower ceiling
    ceiling += 0.06 if special else 0  # special designation -> boost
    ceiling = min(max(ceiling, 0.04), 0.42)

    # Speed: how quickly the curve climbs (logistic steepness)
    speed = 0.16
    speed += 0.03 * (pi - 3)           # more promo -> faster ramp
    speed -= 0.02 * (pr - 3)           # stricter payers -> slower ramp
    speed -= route_friction            # harder-to-administer routes -> slower
    speed = min(max(speed, 0.06), 0.32)

    # Inflection point (month/week where curve is at 50% of ceiling)
    inflection = 18 - 10 * (speed - 0.16) / 0.16
    inflection = min(max(inflection, 6), 22)

    return ceiling, speed, inflection


def logistic_curve(n_points, ceiling_value, speed, inflection, rng, noise_sd=0.04):
    """Generate an n_points-long logistic S-curve with light multiplicative noise."""
    values = []
    for t in range(1, n_points + 1):
        frac = 1 / (1 + math.exp(-speed * (t - inflection)))
        noisy_frac = frac * (1 + rng.gauss(0, noise_sd))
        val = max(0, ceiling_value * noisy_frac)
        values.append(val)
    return values


def generate_rx_curve(rng, features, months=36):
    ceiling_frac, speed, inflection = curve_params(features)
    ceiling_value = features["market_size"] * ceiling_frac
    raw = logistic_curve(months, ceiling_value, speed, inflection, rng)
    return [{"month": i + 1, "rx": int(round(v))} for i, v in enumerate(raw)]


def generate_early_rx_weekly(rng, features, n_weeks):
    """Early weekly Rx for the new drug — same model, weekly grain, ramp-only slice."""
    ceiling_frac, speed, inflection = curve_params(features)
    ceiling_value = features["market_size"] * ceiling_frac
    # convert monthly-scale speed/inflection to a weekly grain (~4.3 weeks/month)
    weekly_speed = speed / 4.3
    weekly_inflection = inflection * 4.3
    raw = logistic_curve(n_weeks, ceiling_value, weekly_speed, weekly_inflection, rng, noise_sd=0.06)
    return [{"week": i + 1, "rx": int(round(v))} for i, v in enumerate(raw)]


# --------------------------------------------------------------------------
# Dataset builders
# --------------------------------------------------------------------------

def build_analog_dataset(rng, n_drugs=35, months=36):
    used_names = set()
    drugs = []
    for i in range(1, n_drugs + 1):
        drug_id = f"ANL_{i:03d}"
        name = make_drug_name(rng, used_names)
        features = generate_static_features(rng, drug_id, name)
        features["rx_curve"] = generate_rx_curve(rng, features, months=months)
        drugs.append(features)
    return drugs


def build_new_drug_dataset(rng, n_weeks=22):
    used_names = set()
    drug_id = "NEW_001"
    name = "New Drug X " + make_drug_name(rng, used_names)
    features = generate_static_features(rng, drug_id, name)
    features["early_rx"] = generate_early_rx_weekly(rng, features, n_weeks)
    return features


def build_scenario_assumptions():
    return [
        {
            "scenario_id": "Bull",
            "market_size_adjustment_pct": 15,
            "peak_penetration_ceiling": "High",
            "adoption_speed_multiplier": "Fast",
            "competitive_entry_flag": False,
            "payer_access_trend": "Improving",
            "promotional_spend_trend": "Ramping",
        },
        {
            "scenario_id": "Base",
            "market_size_adjustment_pct": 0,
            "peak_penetration_ceiling": "Analog-implied midpoint",
            "adoption_speed_multiplier": "Normal",
            "competitive_entry_flag": None,
            "payer_access_trend": "Static",
            "promotional_spend_trend": "Sustained",
        },
        {
            "scenario_id": "Bear",
            "market_size_adjustment_pct": -15,
            "peak_penetration_ceiling": "Low",
            "adoption_speed_multiplier": "Slow",
            "competitive_entry_flag": True,
            "payer_access_trend": "Worsening",
            "promotional_spend_trend": "Tapering",
        },
    ]


# --------------------------------------------------------------------------
# Optional MongoDB load
# --------------------------------------------------------------------------

def load_to_mongo(mongo_uri, db_name, analog, new_drug, scenarios):
    try:
        from pymongo import MongoClient
    except ImportError:
        print("pymongo not installed — skipping MongoDB load. `pip install pymongo` to enable it.")
        return
    client = MongoClient(mongo_uri)
    db = client[db_name]

    db.analog_drugs.delete_many({})
    db.analog_drugs.insert_many(analog)

    db.new_drug.delete_many({})
    db.new_drug.insert_one(new_drug)

    db.scenario_assumptions.delete_many({})
    db.scenario_assumptions.insert_many(scenarios)

    print(f"Loaded into MongoDB db='{db_name}': "
          f"analog_drugs({len(analog)}), new_drug(1), scenario_assumptions({len(scenarios)})")


# --------------------------------------------------------------------------
# Exit-criteria self-check
# --------------------------------------------------------------------------

def run_exit_criteria_checks(analog, new_drug, scenarios):
    checks = []
    checks.append(("35 analog drugs generated", len(analog) == 35))
    checks.append(("Each analog drug has 12 static features + rx_curve",
                    all(len(d) == 13 for d in analog)))  # 12 static + rx_curve key
    checks.append(("Each analog rx_curve has 36 months",
                    all(len(d["rx_curve"]) == 36 for d in analog)))
    checks.append(("New drug has 12 static features + early_rx",
                    len(new_drug) == 13))
    checks.append(("New drug early_rx has 18-26 weekly points",
                    18 <= len(new_drug["early_rx"]) <= 26))
    checks.append(("3 scenario rows with 6 assumption fields each",
                    len(scenarios) == 3 and all(len(s) == 7 for s in scenarios)))  # 6 fields + scenario_id
    checks.append(("All Drug IDs unique and joinable (Table A <-> Table B)",
                    len({d["drug_id"] for d in analog}) == 35))

    print("\nExit Criteria Check")
    print("-" * 60)
    all_pass = True
    for label, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {label}")
        all_pass = all_pass and ok
    print("-" * 60)
    print("ALL CHECKS PASSED" if all_pass else "SOME CHECKS FAILED")
    return all_pass


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate analog, new-drug, and scenario datasets.")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed for reproducibility.")
    parser.add_argument("--outdir", type=str, default="./output", help="Directory to write JSON files.")
    parser.add_argument("--n-analogs", type=int, default=35, help="Number of analog drugs.")
    parser.add_argument("--months", type=int, default=36, help="Months in each analog Rx curve.")
    parser.add_argument("--early-weeks", type=int, default=22, help="Weeks of early Rx for the new drug (18-26).")
    parser.add_argument("--mongo-uri", type=str, default=None, help="Optional MongoDB URI to load results into.")
    parser.add_argument("--db", type=str, default="forecasting_raw", help="MongoDB database name.")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    analog = build_analog_dataset(rng, n_drugs=args.n_analogs, months=args.months)
    new_drug = build_new_drug_dataset(rng, n_weeks=args.early_weeks)
    scenarios = build_scenario_assumptions()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    with open(outdir / "analog_drugs.json", "w") as f:
        json.dump(analog, f, indent=2)
    with open(outdir / "new_drug.json", "w") as f:
        json.dump(new_drug, f, indent=2)
    with open(outdir / "scenario_assumptions.json", "w") as f:
        json.dump(scenarios, f, indent=2)

    print(f"Wrote {len(analog)} analog drugs, 1 new drug, {len(scenarios)} scenarios to '{outdir}/'")

    run_exit_criteria_checks(analog, new_drug, scenarios)

    if args.mongo_uri:
        load_to_mongo(args.mongo_uri, args.db, analog, new_drug, scenarios)


if __name__ == "__main__":
    main()
