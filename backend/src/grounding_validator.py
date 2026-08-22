"""Grounding Validator: Prevents physical, regulatory, economic, and temporal hallucinations."""
from typing import Dict, List, Any, Optional
from datetime import datetime
from src.utils import logger

REGULATORY_TIMELINES = {
    "medical_class_iii": {"min_years": 5.0, "estimated_compliance_usd": 45_000_000, "agency": "FDA PMA / CE MDR"},
    "medical_class_ii": {"min_years": 2.0, "estimated_compliance_usd": 6_000_000, "agency": "FDA 510(k)"},
    "aviation_avionics": {"min_years": 4.0, "estimated_compliance_usd": 25_000_000, "agency": "FAA Part 23/25 / EASA"},
    "automotive_safety": {"min_years": 2.5, "estimated_compliance_usd": 12_000_000, "agency": "ISO 26262 / UNECE"},
    "consumer_hardware": {"min_years": 0.8, "estimated_compliance_usd": 350_000, "agency": "FCC / CE / RoHS"},
    "enterprise_software": {"min_years": 0.3, "estimated_compliance_usd": 80_000, "agency": "SOC2 / HIPAA / GDPR"}
}

PHYSICAL_BOUNDS = {
    "chemical_battery_wh_per_kg_max": 800.0,
    "consumer_mems_power_microwatts_min": 5.0,
    "speed_of_light_latency_floor_ms": 0.001
}

class GroundingValidator:
    """Rigorous validator checking physical, regulatory, economic, and temporal feasibility."""
    
    def validate_invention(self, blueprint: Dict[str, Any], current_year: int = 2026) -> Dict[str, Any]:
        """
        Run multi-layer grounding audit.
        Returns:
            {
                "valid": bool,
                "feasibility_score": float,
                "passed_checks": int,
                "total_checks": int,
                "violations": List[str],
                "warnings": List[str],
                "regulatory_clearance_year": int
            }
        """
        violations = []
        warnings = []
        target_year = blueprint.get("target_market_year", current_year + 2)
        years_available = max(0.5, target_year - current_year)
        
        # 1. Physics & Thermodynamics Check
        spec = blueprint.get("technical_spec_summary", "").lower()
        if any(w in spec for w in ["perpetual", "teleportation", "free energy", "anti-gravity propulsion", "faster than light"]):
            violations.append("Physics showstopper: Concept asserts unproven or impossible physical mechanisms.")
        
        # 2. Regulatory Timeline Check
        category = blueprint.get("regulatory_category", "consumer_hardware")
        if category in REGULATORY_TIMELINES:
            reg = REGULATORY_TIMELINES[category]
            if years_available < reg["min_years"]:
                violations.append(
                    f"Regulatory barrier: Category '{category}' mandates ~{reg['min_years']} years certification ({reg['agency']}), but target launch is in {years_available} years."
                )
            elif years_available < reg["min_years"] * 1.3:
                warnings.append(f"Tight regulatory runway for {reg['agency']} certification.")
        
        # 3. Unit Economics Check
        econ = blueprint.get("unit_economics", {})
        margin = econ.get("gross_margin_pct", 65)
        if margin < 20:
            violations.append(f"Economic infeasibility: Gross margin of {margin}% is below sustainable venture/hardware threshold (>= 25%).")
        elif margin < 40:
            warnings.append(f"Moderate gross margin ({margin}%); sensitive to supply chain volatility.")
        
        # 4. Temporal TRL Progression Check
        is_hardware = blueprint.get("is_hardware", True)
        trl_rate = 1.0 if is_hardware else 2.0  # TRL levels per year
        trl_curr = blueprint.get("trl_current", 7)
        trl_req = blueprint.get("trl_required", 9)
        needed_years = (trl_req - trl_curr) / trl_rate
        if needed_years > years_available:
            violations.append(f"Temporal risk: TRL progression from TRL {trl_curr} to TRL {trl_req} requires ~{needed_years:.1f} years, exceeding horizon window.")
        
        total_checks = 4
        passed = max(0, total_checks - len(violations))
        feasibility_score = round(passed / float(total_checks), 2)
        if warnings and feasibility_score > 0.6:
            feasibility_score = round(feasibility_score - 0.05 * len(warnings), 2)
        
        reg_years = REGULATORY_TIMELINES.get(category, {}).get("min_years", 1.0)
        clearance_year = current_year + int(reg_years + 0.5)
        
        return {
            "valid": len(violations) == 0,
            "feasibility_score": feasibility_score,
            "passed_checks": passed,
            "total_checks": total_checks,
            "violations": violations,
            "warnings": warnings,
            "regulatory_clearance_year": max(target_year, clearance_year)
        }

grounding_validator = GroundingValidator()
