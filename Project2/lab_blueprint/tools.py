"""Deterministic regulatory calculators and read-only data/policy tools for AeroGlobal FlightOps.

All functions use clear docstrings, explicit type hints, and default values where appropriate so
Google ADK builds accurate tool schemas automatically (Core Guide §1.2).
"""

from typing import Any

# Contracted hub lodging caps (A01, A04b, INC-882914)
HUB_HOTEL_CAPS: dict[str, dict[str, Any]] = {
    "ORD": {"cap": 140.0, "currency": "USD", "property": "O'Hare Contracted Airport Partner Hotel", "shuttle": True},
    "DFW": {"cap": 120.0, "currency": "USD", "property": "DFW Contracted Airport Partner Hotel", "shuttle": True},
    "LHR": {"cap": 150.0, "currency": "EUR", "property": "Heathrow Contracted Airport Partner Hotel", "shuttle": True},
}

# Meal stipends by loyalty tier (A01, A04b)
TIER_MEAL_STIPENDS_USD: dict[str, float] = {
    "EXECUTIVE_PLATINUM": 65.0,
    "PLATINUM_PRO": 40.0,
    "GOLD": 40.0,
    "SILVER": 40.0,
    "GENERAL": 40.0,
}

# Statutory constants (CoC v2024.4, EU261 2025, Montreal Convention 1999, US DOT 14 CFR Part 260)
MONTREAL_BAGGAGE_CAP_SDR: int = 1288
SDR_TO_USD_RATE: float = 1.32764  # 1,288 SDR ~= $1,710.00 USD (I-250 / A04b)
MONTREAL_BAGGAGE_CAP_USD: float = 1710.0
US_DOMESTIC_BAGGAGE_CAP_USD: float = 3800.0  # Active CoC v2024.4 (never 2022's $3,500)
HUMAN_ESCALATION_CLAIM_THRESHOLD_USD: float = 2500.0
FRAUD_SCORE_ESCALATION_THRESHOLD: float = 0.75
FDP_ALERT_THRESHOLD_MINUTES: int = 30


def evaluate_jurisdiction(
    origin_iata: str,
    destination_iata: str,
    carrier_jurisdiction: str = "US",
    itinerary_type: str = "INTERNATIONAL",
) -> dict[str, Any]:
    """Determines applicable regulatory regimes and precedence for a flight itinerary.

    Args:
        origin_iata: 3-letter IATA airport code of departure (e.g., 'LHR', 'ORD', 'LAX').
        destination_iata: 3-letter IATA airport code of arrival (e.g., 'JFK', 'DFW', 'HND').
        carrier_jurisdiction: Operating carrier home jurisdiction ('EU', 'UK', 'US').
        itinerary_type: 'DOMESTIC' or 'INTERNATIONAL'.

    Returns:
        Dictionary with ordered 'regimes', 'baggage_regime', 'active_coc_version', and 'rule_id'.
    """
    origin = origin_iata.strip().upper()
    dest = destination_iata.strip().upper()
    itin = itinerary_type.strip().upper()
    eu_uk_airports = {"LHR", "LGW", "MAN", "EDI", "CDG", "FRA", "AMS", "MAD", "FCO", "MUC", "DUB"}
    uk_airports = {"LHR", "LGW", "MAN", "EDI"}

    regimes: list[str] = []
    if origin in uk_airports or carrier_jurisdiction.upper() == "UK":
        regimes.append("UK261")
    if origin in eu_uk_airports or carrier_jurisdiction.upper() == "EU":
        regimes.append("EU261")
    if origin in {"ORD", "DFW", "JFK", "LAX", "SFO", "ATL", "MIA"} or dest in {"ORD", "DFW", "JFK", "LAX", "SFO", "ATL", "MIA"}:
        regimes.append("US_DOT_PART_260")

    baggage_regime = "MONTREAL_1999" if itin == "INTERNATIONAL" or origin != dest and (origin not in {"ORD", "DFW", "JFK", "LAX"} or dest not in {"ORD", "DFW", "JFK", "LAX"}) else "US_DOT_14CFR254"
    if origin in {"LAX", "JFK", "ORD", "DFW"} and dest in {"LAX", "JFK", "ORD", "DFW"} and itin == "DOMESTIC":
        baggage_regime = "US_DOT_14CFR254"

    return {
        "origin_iata": origin,
        "destination_iata": dest,
        "regimes": regimes,
        "baggage_regime": baggage_regime,
        "active_coc_version": "2024.4",
        "rule_id": "JURISDICTION-PRECEDENCE-2025",
        "rule_owner": "Rachel Sterling (VP Aviation Compliance & Legal)",
    }


def compute_eu261_compensation(
    distance_km: float,
    arrival_delay_min: int,
    is_carrier_controllable: bool,
    disruption_code: str = "",
    regime: str = "EU261",
) -> dict[str, Any]:
    """Computes deterministic EU261/UK261 statutory cash compensation and Right to Care.

    Under CJEU Wallentin-Hermann and van der Lans precedents, technical defects (e.g., APU fault)
    and crew shortages are ALWAYS carrier-controllable, never extraordinary circumstances.

    Args:
        distance_km: Great-circle route distance in kilometers.
        arrival_delay_min: Actual arrival delay at final destination in minutes.
        is_carrier_controllable: Operational controllability flag from flight record.
        disruption_code: Optional disruption reason/code (e.g., 'APU_FAULT', 'CREW_TIMEOUT', 'WEATHER').
        regime: 'EU261' or 'UK261'.

    Returns:
        Dictionary containing statutory cash compensation amount, currency, right_to_care, and rule metadata.
    """
    code_upper = disruption_code.upper()
    technical_or_crew = any(tok in code_upper for tok in ("APU", "MECH", "TECH", "DEFECT", "CREW", "FDP", "FAULT"))
    controllable = bool(is_carrier_controllable or technical_or_crew)

    # Right to care (meals, hotel if overnight, ground transfer) is ALWAYS unconditional under EU261 Art. 9
    right_to_care_eligible = arrival_delay_min >= 120

    if not controllable or arrival_delay_min < 180:
        return {
            "eligible_for_cash_compensation": False,
            "amount": 0.0,
            "currency": "GBP" if regime.upper() == "UK261" else "EUR",
            "uk261_equivalent_gbp": 0.0,
            "eu261_equivalent_eur": 0.0,
            "is_carrier_controllable": controllable,
            "right_to_care_unconditional": right_to_care_eligible,
            "rule_id": "EU261-ART7-NONE",
            "rule_owner": "Rachel Sterling (VP Aviation Compliance & Legal)",
            "rationale": (
                "Arrival delay under 180 minutes."
                if arrival_delay_min < 180
                else "Extraordinary weather/ATC circumstances outside carrier control; cash compensation exempt, but Right to Care (meals, contracted hotel, transfers) remains unconditional."
            ),
        }

    if distance_km <= 1500:
        eur_amount, gbp_amount, band = 250.0, 220.0, "SHORT_HAUL_LE_1500KM"
    elif distance_km <= 3500:
        eur_amount, gbp_amount, band = 400.0, 350.0, "MEDIUM_HAUL_1501_3500KM"
    else:
        # > 3,500 km: 50% reduction applies if arrival delay is between 180 and 239 minutes
        if arrival_delay_min < 240:
            eur_amount, gbp_amount, band = 300.0, 260.0, "LONG_HAUL_GT_3500KM_3H_TO_4H"
        else:
            eur_amount, gbp_amount, band = 600.0, 520.0, "LONG_HAUL_GT_3500KM_GE_4H"

    use_gbp = regime.upper() == "UK261"
    return {
        "eligible_for_cash_compensation": True,
        "amount": gbp_amount if use_gbp else eur_amount,
        "currency": "GBP" if use_gbp else "EUR",
        "eu261_equivalent_eur": eur_amount,
        "uk261_equivalent_gbp": gbp_amount,
        "distance_band": band,
        "is_carrier_controllable": True,
        "right_to_care_unconditional": True,
        "rule_id": f"EU261-{band}",
        "rule_owner": "Rachel Sterling (VP Aviation Compliance & Legal)",
        "rationale": (
            f"Route {distance_km:.0f} km ({band}) with {arrival_delay_min} min arrival delay; "
            "carrier-controllable under CJEU Wallentin-Hermann (technical/crew faults never extraordinary)."
        ),
    }


def compute_dot_part260_refund(
    itinerary_type: str,
    delay_min: int,
    is_cancelled: bool,
    alternative_declined: bool,
    bag_delay_hours: float = 0.0,
    bag_fee_paid_usd: float = 0.0,
    payment_method: str = "CREDIT_CARD",
) -> dict[str, Any]:
    """Computes US DOT 14 CFR Part 260 automatic ticket and baggage-fee refund eligibility.

    Args:
        itinerary_type: 'DOMESTIC' or 'INTERNATIONAL'.
        delay_min: Flight delay in minutes.
        is_cancelled: True if flight was cancelled.
        alternative_declined: True if passenger declined rebooking/alternative transportation.
        bag_delay_hours: Hours baggage was delayed after arrival.
        bag_fee_paid_usd: Ancillary checked-baggage fee paid in USD.
        payment_method: 'CREDIT_CARD' (7 business days) or 'CASH'/'OTHER' (20 calendar days).

    Returns:
        Dictionary with ticket refund status, baggage fee refund amount, statutory deadline, and rule ID.
    """
    itin = itinerary_type.strip().upper()
    sig_delay_threshold_min = 180 if itin == "DOMESTIC" else 360
    fare_refund_due = bool((is_cancelled or delay_min > sig_delay_threshold_min) and alternative_declined)

    # DOT baggage delay threshold: > 12h domestic; > 15h international (conservative trigger for 15-30h band)
    bag_threshold_hours = 12.0 if itin == "DOMESTIC" else 15.0
    bag_fee_refund_due = bool(bag_delay_hours > bag_threshold_hours and bag_fee_paid_usd > 0)
    bag_fee_refund_usd = round(bag_fee_paid_usd, 2) if bag_fee_refund_due else 0.0

    due_days = "7 business days" if payment_method.strip().upper() == "CREDIT_CARD" else "20 calendar days"

    return {
        "fare_refund_due": fare_refund_due,
        "bag_fee_refund_due": bag_fee_refund_due,
        "bag_fee_refund_usd": bag_fee_refund_usd,
        "refund_timeline": due_days,
        "rule_id": "DOT-14CFR260-AUTO-REFUND",
        "rule_owner": "Rachel Sterling (VP Aviation Compliance & Legal)",
        "active_coc_version": "2024.4",
    }


def compute_baggage_liability(
    itinerary_type: str,
    claim_amount_usd: float,
    has_special_declaration: bool = False,
    declared_value_usd: float = 0.0,
) -> dict[str, Any]:
    """Computes statutory baggage liability cap under Montreal Convention (1,288 SDR) or US DOT ($3,800).

    Never uses the superseded 2022 Contract of Carriage cap ($3,500).

    Args:
        itinerary_type: 'INTERNATIONAL' (Montreal Convention) or 'DOMESTIC' (US 14 CFR Part 254 / CoC v2024.4).
        claim_amount_usd: Passenger's claimed baggage expense in USD.
        has_special_declaration: True if passenger made a special declaration of interest at check-in.
        declared_value_usd: Declared value in USD if has_special_declaration is True.

    Returns:
        Dictionary with applicable regime, cap in SDR/USD, authorized payable amount in USD, and active CoC version.
    """
    itin = itinerary_type.strip().upper()
    if itin == "INTERNATIONAL":
        cap_usd = declared_value_usd if (has_special_declaration and declared_value_usd > MONTREAL_BAGGAGE_CAP_USD) else MONTREAL_BAGGAGE_CAP_USD
        payable_usd = round(min(claim_amount_usd, cap_usd), 2)
        return {
            "regime": "MONTREAL_CONVENTION_1999",
            "cap_sdr": MONTREAL_BAGGAGE_CAP_SDR,
            "cap_usd": round(cap_usd, 2),
            "claimed_usd": round(claim_amount_usd, 2),
            "authorized_payable_usd": payable_usd,
            "active_coc_version": "2024.4",
            "rule_id": "MONTREAL-ART19-22-1288SDR",
            "rule_owner": "Rachel Sterling (VP Aviation Compliance & Legal)",
        }

    cap_usd = declared_value_usd if (has_special_declaration and declared_value_usd > US_DOMESTIC_BAGGAGE_CAP_USD) else US_DOMESTIC_BAGGAGE_CAP_USD
    payable_usd = round(min(claim_amount_usd, cap_usd), 2)
    return {
        "regime": "US_DOT_14CFR254_COC_2024_4",
        "cap_sdr": None,
        "cap_usd": round(cap_usd, 2),
        "claimed_usd": round(claim_amount_usd, 2),
        "authorized_payable_usd": payable_usd,
        "active_coc_version": "2024.4",
        "rule_id": "US-DOT-254-COC-2024.4-3800USD",
        "rule_owner": "Rachel Sterling (VP Aviation Compliance & Legal)",
    }


def check_crew_fdp_alert(
    flight_id: str,
    remaining_fdp_minutes: int,
    hub_iata: str = "ORD",
    data_age_seconds: int = 10,
) -> dict[str, Any]:
    """Evaluates FAA 14 CFR Part 117 Flight Duty Period (FDP) margin and triggers dispatch alert if < 30 min.

    Args:
        flight_id: Flight identifier (e.g., 'AG-884').
        remaining_fdp_minutes: Remaining legal Flight Duty Period in minutes before timeout.
        hub_iata: Hub airport IATA code (e.g., 'ORD', 'DFW', 'LHR').
        data_age_seconds: Staleness of the crew feed in seconds (must be <= 60s).

    Returns:
        Dictionary indicating whether a Part 117 alert is triggered, staleness status, and action required.
    """
    stale_feed = data_age_seconds > 60
    alert_triggered = remaining_fdp_minutes < FDP_ALERT_THRESHOLD_MINUTES
    return {
        "flight_id": flight_id.strip().upper(),
        "hub_iata": hub_iata.strip().upper(),
        "remaining_fdp_minutes": remaining_fdp_minutes,
        "fdp_alert_triggered": alert_triggered,
        "stale_feed_warning": stale_feed,
        "severity": "SEV_1_CRITICAL" if alert_triggered else "NORMAL",
        "rule_id": "FAA-14CFR117-FDP-30MIN",
        "rule_owner": "Tomas Morales (Chief Flight Dispatcher)",
        "recommended_action": (
            "ALERT NOC DISPATCH IMMEDIATELY: Crew FDP < 30 min; query SABRE CrewTrac for hub relief crew."
            if alert_triggered
            else "Crew within legal Part 117 FDP margin."
        ),
    }


def compute_right_to_care(
    hub_iata: str,
    loyalty_tier: str = "GENERAL",
    is_overnight: bool = True,
    active_waiver_id: str = "",
    fare_bucket: str = "STANDARD",
) -> dict[str, Any]:
    """Computes contracted airport hotel cap, meal stipend by loyalty tier, and weather-waiver exemptions.

    Enforces CON-10: off-contract hotels and uncapped reimbursements are strictly prohibited.

    Args:
        hub_iata: Hub airport IATA code ('ORD', 'DFW', 'LHR').
        loyalty_tier: Passenger loyalty tier ('EXECUTIVE_PLATINUM', 'PLATINUM_PRO', 'GOLD', 'SILVER', 'GENERAL').
        is_overnight: True if stranded overnight requiring lodging.
        active_waiver_id: Optional active executive weather waiver ID (e.g., 'WAIVER-2025-Q1-ORION').
        fare_bucket: Booking fare class (e.g., 'B_BUCKET' / 'BASIC_ECONOMY' or 'STANDARD').

    Returns:
        Dictionary with contracted hotel cap, meal stipend, and waiver fee/fare-difference exemptions.
    """
    hub = hub_iata.strip().upper()
    tier = loyalty_tier.strip().upper().replace(" ", "_")
    bucket = fare_bucket.strip().upper().replace(" ", "_")

    hotel_info = HUB_HOTEL_CAPS.get(
        hub,
        {"cap": 120.0, "currency": "USD", "property": f"{hub} Contracted Partner Hotel", "shuttle": True},
    )
    meal_stipend_usd = TIER_MEAL_STIPENDS_USD.get(tier, 40.0)
    waiver_active = bool(active_waiver_id.strip())
    is_basic_econ = bucket in {"B", "B_BUCKET", "BASIC_ECONOMY"}

    return {
        "hub_iata": hub,
        "lodging_eligible": is_overnight or (waiver_active and tier != "GENERAL"),
        "contracted_property": hotel_info["property"],
        "hotel_nightly_cap": hotel_info["cap"],
        "hotel_currency": hotel_info["currency"],
        "ground_transfer_included": hotel_info["shuttle"],
        "meal_stipend_per_day_usd": meal_stipend_usd,
        "change_fee_waived": waiver_active,
        "fare_difference_waived": waiver_active and is_basic_econ or waiver_active,
        "off_contract_reimbursement_allowed": False,
        "active_coc_version": "2024.4",
        "rule_id": "CARE-AND-WAIVER-2025-Q1",
        "rule_owner": "Elena Rostova (Director NOC)",
    }


def check_escalation(
    claim_amount_usd: float,
    loyalty_tier: str = "GENERAL",
    is_medical_emergency: bool = False,
    fraud_dispute_risk_score: float = 0.0,
    is_churn_risk: bool = False,
) -> dict[str, Any]:
    """Deterministically evaluates whether a case must be escalated to a human specialist (FR-16).

    Escalates when claim > $2,500 (on claimed amount per CFL-15), medical emergency,
    Executive Platinum churn risk, or high fraud_dispute_risk_score.

    Args:
        claim_amount_usd: Amount claimed by the passenger in USD.
        loyalty_tier: Passenger loyalty tier.
        is_medical_emergency: True if passenger reported a medical emergency.
        fraud_dispute_risk_score: Risk score between 0.0 and 1.0 (or 0 to 100 normalized).
        is_churn_risk: True if flagged as high churn risk.

    Returns:
        Dictionary with 'escalate' boolean and list of 'reasons'.
    """
    reasons: list[str] = []
    tier = loyalty_tier.strip().upper().replace(" ", "_")
    normalized_fraud = fraud_dispute_risk_score / 100.0 if fraud_dispute_risk_score > 1.0 else fraud_dispute_risk_score

    if claim_amount_usd > HUMAN_ESCALATION_CLAIM_THRESHOLD_USD:
        reasons.append(f"CLAIM_EXCEEDS_2500_USD (${claim_amount_usd:.2f})")
    if is_medical_emergency:
        reasons.append("MEDICAL_EMERGENCY")
    if tier == "EXECUTIVE_PLATINUM" and (is_churn_risk or claim_amount_usd >= 1000.0):
        reasons.append("EXECUTIVE_PLATINUM_CHURN_RISK")
    if normalized_fraud >= FRAUD_SCORE_ESCALATION_THRESHOLD:
        reasons.append(f"HIGH_FRAUD_DISPUTE_RISK_SCORE ({normalized_fraud:.2f})")

    return {
        "escalate": len(reasons) > 0,
        "reasons": reasons,
        "rule_id": "HITL-ESCALATION-FR16",
        "rule_owner": "Rachel Sterling (VP Aviation Compliance & Legal)",
    }
