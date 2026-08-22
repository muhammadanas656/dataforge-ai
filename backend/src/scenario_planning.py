"""Multi-scenario planning with Monte Carlo simulation for business viability analysis."""
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from src.utils import logger

class ScenarioPlanner:
    """Generates and simulates business scenarios with Monte Carlo analysis."""
    
    def __init__(self, n_simulations: int = 1000):
        self.n_simulations = n_simulations
    
    def generate_scenarios(
        self,
        niche: str,
        base_assumptions: Dict,
        category: str = "E-Commerce"
    ) -> Dict:
        logger.info(f"[scenarios] Generating scenarios for '{niche}'")
        
        base_units = base_assumptions.get('units_per_month', 100)
        base_price = base_assumptions.get('price_usd', 50.0)
        base_cogs = base_assumptions.get('cogs_usd', 20.0)
        base_cac = base_assumptions.get('cac_usd', 15.0)
        base_conversion = base_assumptions.get('conversion_rate', 0.02)
        fixed_costs = base_assumptions.get('fixed_costs_monthly', 2000.0)
        
        category_multipliers = {
            'E-Commerce': {'volume': 1.0, 'cac': 1.0, 'conversion': 1.0},
            'AI & SaaS': {'volume': 0.7, 'cac': 1.5, 'conversion': 1.2},
            'Health & Wellness': {'volume': 1.2, 'cac': 1.3, 'conversion': 0.9},
            'Creator Economy': {'volume': 1.5, 'cac': 0.8, 'conversion': 1.1},
            'Home & Gadgets': {'volume': 1.1, 'cac': 1.1, 'conversion': 1.0}
        }
        cat_mult = category_multipliers.get(category, category_multipliers['E-Commerce'])
        
        scenarios = {
            'conservative': {
                'name': 'Conservative',
                'description': 'Low volume, high CAC, slow growth',
                'units_per_month': max(10, int(base_units * 0.5 * cat_mult['volume'])),
                'price_usd': round(base_price * 0.9, 2),
                'cogs_usd': round(base_cogs * 1.1, 2),
                'cac_usd': round(base_cac * 1.5 * cat_mult['cac'], 2),
                'conversion_rate': round(base_conversion * 0.7 * cat_mult['conversion'], 3),
                'growth_rate_monthly': 0.02,
                'breakeven_months': None
            },
            'base': {
                'name': 'Base Case',
                'description': 'Expected performance based on market analysis',
                'units_per_month': max(20, int(base_units * cat_mult['volume'])),
                'price_usd': round(base_price, 2),
                'cogs_usd': round(base_cogs, 2),
                'cac_usd': round(base_cac * cat_mult['cac'], 2),
                'conversion_rate': round(base_conversion * cat_mult['conversion'], 3),
                'growth_rate_monthly': 0.08,
                'breakeven_months': None
            },
            'aggressive': {
                'name': 'Aggressive',
                'description': 'High volume, low CAC, viral growth',
                'units_per_month': max(40, int(base_units * 2.0 * cat_mult['volume'])),
                'price_usd': round(base_price * 1.1, 2),
                'cogs_usd': round(base_cogs * 0.9, 2),
                'cac_usd': round(base_cac * 0.75 * cat_mult['cac'], 2),
                'conversion_rate': round(base_conversion * 1.3 * cat_mult['conversion'], 3),
                'growth_rate_monthly': 0.15,
                'breakeven_months': None
            }
        }
        
        for k, s in scenarios.items():
            s['breakeven_months'] = self._calculate_breakeven(s, fixed_costs)
            
        monte_carlo = self._run_monte_carlo(scenarios['base'], fixed_costs, n_months=12)
        recommendations = self._generate_recommendations(scenarios, monte_carlo)
        
        return {
            'niche': niche,
            'category': category,
            'scenarios': scenarios,
            'monte_carlo': monte_carlo,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_breakeven(self, scenario: Dict, fixed_costs: float) -> Optional[int]:
        try:
            margin_per_unit = scenario['price_usd'] - scenario['cogs_usd'] - scenario['cac_usd']
            if margin_per_unit <= 0:
                return None
            monthly_contribution = margin_per_unit * scenario['units_per_month']
            if monthly_contribution <= 0:
                return None
            months = int(np.ceil(fixed_costs / max(1.0, monthly_contribution)))
            return min(months, 36)
        except Exception:
            return None
    
    def _run_monte_carlo(self, base_scenario: Dict, fixed_costs: float, n_months: int = 12) -> Dict:
        try:
            monthly_profits = []
            cumulative_profits = []
            
            for _ in range(self.n_simulations):
                units = max(1.0, np.random.normal(base_scenario['units_per_month'], base_scenario['units_per_month'] * 0.3))
                cac = max(1.0, np.random.normal(base_scenario['cac_usd'], base_scenario['cac_usd'] * 0.2))
                
                rev = units * base_scenario['price_usd']
                cogs = units * base_scenario['cogs_usd']
                mktg = units * cac
                net = (rev - cogs - mktg) - fixed_costs
                monthly_profits.append(net)
                
                cum = 0.0
                for m in range(n_months):
                    growth = (1 + base_scenario['growth_rate_monthly']) ** m
                    m_units = units * growth
                    m_net = (m_units * base_scenario['price_usd']) - (m_units * base_scenario['cogs_usd']) - (m_units * cac) - fixed_costs
                    cum += m_net
                cumulative_profits.append(cum)
                
            m_arr = np.array(monthly_profits)
            c_arr = np.array(cumulative_profits)
            
            return {
                'n_simulations': self.n_simulations,
                'monthly_profit': {
                    'mean': float(round(np.mean(m_arr), 1)),
                    'median': float(round(np.median(m_arr), 1)),
                    'std': float(round(np.std(m_arr), 1)),
                    'p10': float(round(np.percentile(m_arr, 10), 1)),
                    'p50': float(round(np.percentile(m_arr, 50), 1)),
                    'p90': float(round(np.percentile(m_arr, 90), 1)),
                    'min': float(round(np.min(m_arr), 1)),
                    'max': float(round(np.max(m_arr), 1))
                },
                'cumulative_profit_12mo': {
                    'p10': float(round(np.percentile(c_arr, 10), 1)),
                    'p50': float(round(np.percentile(c_arr, 50), 1)),
                    'p90': float(round(np.percentile(c_arr, 90), 1))
                },
                'probability_of_profit': float(round(np.mean(m_arr > 0), 2)),
                'probability_of_10k_profit': float(round(np.mean(m_arr > 10000), 2)),
                'histogram': self._create_histogram(m_arr),
                'risk_level': self._assess_risk(m_arr)
            }
        except Exception as e:
            logger.error(f"[scenarios] Monte Carlo failed: {e}")
            return {'probability_of_profit': 0.5, 'risk_level': 'medium'}
    
    def _create_histogram(self, data: np.ndarray, n_bins: int = 15) -> List[Dict]:
        counts, bin_edges = np.histogram(data, bins=n_bins)
        res = []
        for i in range(len(counts)):
            res.append({
                'bin_start': float(round(bin_edges[i], 1)),
                'bin_end': float(round(bin_edges[i+1], 1)),
                'count': int(counts[i]),
                'percentage': float(round(counts[i] / len(data) * 100, 1))
            })
        return res
    
    def _assess_risk(self, profits: np.ndarray) -> str:
        prob = np.mean(profits > 0)
        if prob < 0.4: return 'high'
        elif prob < 0.65: return 'medium'
        return 'low'
    
    def _generate_recommendations(self, scenarios: Dict, monte_carlo: Dict) -> List[str]:
        recs = []
        prob = monte_carlo.get('probability_of_profit', 0.5)
        if prob > 0.7:
            recs.append("Strong viability: Over 70% probability of monthly profit under base assumptions.")
        elif prob < 0.4:
            recs.append("High risk: Less than 40% probability of profit. Reduce COGS or refine target audience to lower CAC.")
            
        be = scenarios.get('base', {}).get('breakeven_months')
        if be:
            recs.append(f"Estimated breakeven occurs at month {be} in base operating scenario.")
        return recs

scenario_planner = ScenarioPlanner()
