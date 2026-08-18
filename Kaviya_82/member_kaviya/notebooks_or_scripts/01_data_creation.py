import json
import random
import numpy as np

# ============================================================
# 1. SETTINGS
# ============================================================

random.seed(42)
np.random.seed(42)

NUM_ANALOG_DRUGS = 35
RX_MONTHS = 36
EARLY_RX_WEEKS = 22


# ============================================================
# 2. POSSIBLE VALUES
# ============================================================

mechanisms = [
    "SGLT2 inhibitor",
    "PCSK9 inhibitor",
    "Tyrosine kinase inhibitor",
    "DPP-4 inhibitor",
    "ACE inhibitor",
    "CGRP antagonist",
    "Integrin antagonist",
    "Dopamine agonist",
    "Anti-CD20 monoclonal antibody",
    "Complement C5 inhibitor",
    "Beta-2 agonist",
    "Proton pump inhibitor"
]

routes = [
    "Oral",
    "Injectable",
    "Intravenous",
    "Inhaled",
    "Topical",
    "Subcutaneous"
]

specialties = [
    "Oncology",
    "Gastroenterology",
    "Dermatology",
    "Neurology",
    "Hematology",
    "Rheumatology",
    "Endocrinology",
    "Cardiology",
    "Primary Care"
]

launch_quarters = ["Q1", "Q2", "Q3", "Q4"]


# ============================================================
# 3. FUNCTION TO GENERATE RX CURVE
# ============================================================

def generate_rx_curve(months=36):
    """
    Generate a realistic prescription curve.
    RX generally increases over time with some random variation.
    """

    starting_rx = random.randint(10000, 70000)

    growth_rate = random.uniform(0.04, 0.12)

    rx_curve = []

    current_rx = starting_rx

    for month in range(1, months + 1):

        # Growth
        current_rx = current_rx * (1 + growth_rate)

        # Random noise
        noise = random.uniform(0.90, 1.10)

        rx_value = int(current_rx * noise)

        rx_curve.append({
            "month": month,
            "rx": rx_value
        })

    return rx_curve


# ============================================================
# 4. GENERATE ANALOG DRUG DATA
# ============================================================

analog_drugs = []

for i in range(1, NUM_ANALOG_DRUGS + 1):

    drug = {
        "drug_id": f"ANL_{i:03d}",

        "drug_name": f"DrugAnalog_{i}",

        "mechanism_of_action": random.choice(mechanisms),

        "route_of_administration": random.choice(routes),

        "target_specialty": random.choice(specialties),

        "market_size": random.randint(
            200000,
            3000000
        ),

        "competitive_density": random.randint(
            1,
            5
        ),

        "payer_restrictiveness": random.randint(
            1,
            5
        ),

        "launch_quarter": random.choice(
            launch_quarters
        ),

        "promotional_intensity": random.randint(
            1,
            5
        ),

        "special_designation": random.choice(
            [True, False]
        ),

        "price_tier": random.randint(
            1,
            5
        ),

        "rx_curve": generate_rx_curve(
            RX_MONTHS
        )
    }

    analog_drugs.append(drug)


# ============================================================
# 5. SAVE ANALOG DRUG DATA
# ============================================================

with open(
    "analog_drugs_generated.json",
    "w"
) as f:

    json.dump(
        analog_drugs,
        f,
        indent=2
    )


print(
    f"Created {NUM_ANALOG_DRUGS} analog drugs"
)


# ============================================================
# 6. GENERATE NEW DRUG DATA
# ============================================================

new_drug = {

    "drug_id": "NEW_001",

    "drug_name": "New Drug X Calatinib",

    "mechanism_of_action": random.choice(
        mechanisms
    ),

    "route_of_administration": random.choice(
        routes
    ),

    "target_specialty": random.choice(
        specialties
    ),

    "market_size": random.randint(
        500000,
        2000000
    ),

    "competitive_density": random.randint(
        1,
        5
    ),

    "payer_restrictiveness": random.randint(
        1,
        5
    ),

    "launch_quarter": random.choice(
        launch_quarters
    ),

    "promotional_intensity": random.randint(
        1,
        5
    ),

    "special_designation": random.choice(
        [True, False]
    ),

    "price_tier": random.randint(
        1,
        5
    ),

    "early_rx": []
}


# ============================================================
# 7. GENERATE EARLY RX DATA
# ============================================================

starting_rx = random.randint(
    10000,
    20000
)

current_rx = starting_rx

for week in range(1, EARLY_RX_WEEKS + 1):

    growth = random.uniform(
        0.01,
        0.08
    )

    current_rx = current_rx * (
        1 + growth
    )

    noise = random.uniform(
        0.90,
        1.10
    )

    rx_value = int(
        current_rx * noise
    )

    new_drug["early_rx"].append({

        "week": week,

        "rx": rx_value

    })


# ============================================================
# 8. SAVE NEW DRUG DATA
# ============================================================

with open(
    "new_drug_generated.json",
    "w"
) as f:

    json.dump(
        new_drug,
        f,
        indent=2
    )


print(
    "New drug data created"
)


# ============================================================
# 9. CREATE SCENARIO ASSUMPTIONS
# ============================================================

scenario_assumptions = [

    {
        "scenario_id": "Bull",

        "market_size_adjustment_pct": 15,

        "peak_penetration_ceiling": "High",

        "adoption_speed_multiplier": "Fast",

        "competitive_entry_flag": False,

        "payer_access_trend": "Improving",

        "promotional_spend_trend": "Ramping"
    },

    {
        "scenario_id": "Base",

        "market_size_adjustment_pct": 0,

        "peak_penetration_ceiling":
            "Analog-implied midpoint",

        "adoption_speed_multiplier": "Normal",

        "competitive_entry_flag": None,

        "payer_access_trend": "Static",

        "promotional_spend_trend": "Sustained"
    },

    {
        "scenario_id": "Bear",

        "market_size_adjustment_pct": -15,

        "peak_penetration_ceiling": "Low",

        "adoption_speed_multiplier": "Slow",

        "competitive_entry_flag": True,

        "payer_access_trend": "Worsening",

        "promotional_spend_trend": "Tapering"
    }
]


# ============================================================
# 10. SAVE SCENARIO DATA
# ============================================================

with open(
    "scenario_assumptions_generated.json",
    "w"
) as f:

    json.dump(
        scenario_assumptions,
        f,
        indent=2
    )


print(
    "Scenario assumptions created"
)

print("\nData creation completed successfully!")