"""Technology Capability Graph & 2026-2030+ Horizon Interpolator."""
from typing import Dict, List, Any, Optional
from datetime import datetime
from src.utils import logger

TECH_CAPABILITIES: Dict[str, Dict[str, Dict[str, Any]]] = {
    "edge_ai_silicon": {
        "2024": {"tops_per_watt": 2.5, "chip_cost_usd": 65.0, "quantization_bits": 4, "trl": 7},
        "2026": {"tops_per_watt": 8.0, "chip_cost_usd": 38.0, "quantization_bits": 2, "trl": 8},
        "2027": {"tops_per_watt": 18.0, "chip_cost_usd": 24.0, "quantization_bits": 1.5, "trl": 8},
        "2028": {"tops_per_watt": 45.0, "chip_cost_usd": 15.0, "quantization_bits": 1, "trl": 9},
        "2030": {"tops_per_watt": 120.0, "chip_cost_usd": 8.0, "quantization_bits": 1, "trl": 9}
    },
    "battery_energy_density": {
        "2024": {"wh_per_kg": 270, "cost_per_kwh_usd": 139, "cycle_life": 1200, "solid_state_trl": 4},
        "2026": {"wh_per_kg": 340, "cost_per_kwh_usd": 98, "cycle_life": 2200, "solid_state_trl": 6},
        "2027": {"wh_per_kg": 390, "cost_per_kwh_usd": 82, "cycle_life": 2800, "solid_state_trl": 7},
        "2028": {"wh_per_kg": 460, "cost_per_kwh_usd": 68, "cycle_life": 3800, "solid_state_trl": 8},
        "2030": {"wh_per_kg": 600, "cost_per_kwh_usd": 45, "cycle_life": 5000, "solid_state_trl": 9}
    },
    "slm_local_inference": {
        "2024": {"tokens_per_sec_mobile": 25, "ram_footprint_mb": 2200, "reasoning_benchmark_pct": 68},
        "2026": {"tokens_per_sec_mobile": 90, "ram_footprint_mb": 650, "reasoning_benchmark_pct": 84},
        "2027": {"tokens_per_sec_mobile": 180, "ram_footprint_mb": 380, "reasoning_benchmark_pct": 91},
        "2028": {"tokens_per_sec_mobile": 350, "ram_footprint_mb": 190, "reasoning_benchmark_pct": 96},
        "2030": {"tokens_per_sec_mobile": 900, "ram_footprint_mb": 80, "reasoning_benchmark_pct": 98}
    },
    "ambient_biometric_sensing": {
        "2024": {"spatial_resolution_mm": 15.0, "power_draw_microwatts": 1800, "continuous_tracking_hours": 12},
        "2026": {"spatial_resolution_mm": 4.0, "power_draw_microwatts": 450, "continuous_tracking_hours": 72},
        "2027": {"spatial_resolution_mm": 1.8, "power_draw_microwatts": 180, "continuous_tracking_hours": 240},
        "2028": {"spatial_resolution_mm": 0.8, "power_draw_microwatts": 60, "continuous_tracking_hours": 720},
        "2030": {"spatial_resolution_mm": 0.2, "power_draw_microwatts": 15, "continuous_tracking_hours": 8760}
    }
}

class TechCapabilityGraph:
    """Manages multi-year technology capabilities with linear and exponential interpolation."""
    
    def __init__(self):
        self.capabilities = TECH_CAPABILITIES
    
    def get_capability(self, tech_key: str, year: int = 2027) -> Dict[str, Any]:
        """Get or linearly interpolate capability metrics for a given year."""
        if tech_key not in self.capabilities:
            return {"error": f"Unknown technology: {tech_key}"}
        
        tech_data = self.capabilities[tech_key]
        year_str = str(year)
        if year_str in tech_data:
            return dict(tech_data[year_str])
        
        years = sorted([int(y) for y in tech_data.keys()])
        if year <= years[0]:
            return dict(tech_data[str(years[0])])
        if year >= years[-1]:
            return dict(tech_data[str(years[-1])])
        
        # Interpolate between closest years
        for i in range(len(years) - 1):
            y1, y2 = years[i], years[i+1]
            if y1 <= year <= y2:
                fraction = (year - y1) / float(y2 - y1)
                d1 = tech_data[str(y1)]
                d2 = tech_data[str(y2)]
                interpolated = {}
                for k, v in d1.items():
                    if isinstance(v, (int, float)) and k in d2:
                        v2 = d2[k]
                        interpolated[k] = round(v + fraction * (v2 - v), 2)
                    else:
                        interpolated[k] = v2 if fraction > 0.5 else v
                return interpolated
        return dict(tech_data[str(years[0])])
    
    def check_feasibility(self, tech_key: str, metric_name: str, target_value: float, year: int = 2027) -> Dict[str, Any]:
        """Check whether a requested performance metric is feasible in the given year."""
        cap = self.get_capability(tech_key, year)
        if metric_name not in cap:
            return {"feasible": True, "note": f"Metric {metric_name} not constrained"}
        
        actual = cap[metric_name]
        # For costs, resolution, footprint: lower is better
        is_cost_or_footprint = any(x in metric_name for x in ["cost", "resolution", "footprint", "draw", "bits"])
        feasible = (actual <= target_value) if is_cost_or_footprint else (actual >= target_value)
        
        return {
            "technology": tech_key,
            "metric": metric_name,
            "target_required": target_value,
            "projected_for_year": actual,
            "year": year,
            "feasible": feasible,
            "recommendation": "Ready for production" if feasible else f"Requires technological maturation; projected to hit target closer to 2028-2030."
        }

tech_capability_graph = TechCapabilityGraph()
