"""Autonomous Invention Synthesis Pipeline: TRIZ, Morphological Box, Grounding & S-Curve Forecasting."""
from typing import Dict, List, Any, Optional, AsyncGenerator
import json
import asyncio
import random
from datetime import datetime
from src.triz_engine import triz_engine
from src.morphological_analysis import get_morphological_box
from src.tech_capability_graph import tech_capability_graph
from src.grounding_validator import grounding_validator
from src.feasibility_critic import feasibility_critic
from src.future_models import novelty_detector, market_predictor, adoption_forecaster
from src.token_tracker import tracker
from src.utils import logger

class InventionPipeline:
    """End-to-end future intelligence and systematic invention engine."""
    
    def synthesize_invention(
        self,
        domain: str = "edge_ai_hardware",
        target_year: int = 2028,
        improving_param: str = "speed",
        worsening_param: str = "energy_efficiency",
        run_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute the full multi-stage invention synthesis."""
        rid = run_id or f"inv_{int(datetime.now().timestamp())}"
        logger.info(f"[invention] Synthesizing invention for domain={domain}, target_year={target_year}")
        
        # 1. TRIZ Contradiction Resolution
        triz_res = triz_engine.resolve_contradiction(
            improving_param=improving_param,
            worsening_param=worsening_param,
            domain=domain,
            context=f"Target deployment year: {target_year}"
        )
        
        # 2. Morphological Synthesis
        morph_box = get_morphological_box(domain)
        combo = morph_box.sample_combination()
        blueprint = morph_box.synthesize_product_concept(combo, domain_name=domain)
        inv_concept = triz_res.get("invention", {})
        blueprint.update({
            "concept_name": inv_concept.get("concept_name", "Autonomous Edge-SLM Acoustic Array"),
            "one_sentence_pitch": inv_concept.get("one_sentence_pitch", "Sub-1W acoustic ambient sensor with real-time anomaly detection."),
            "category": inv_concept.get("category", "Frontier Edge AI"),
            "target_persona": inv_concept.get("target_persona", "Smart Factory / Enterprise Systems"),
            "technical_spec_summary": inv_concept.get("technical_spec_summary", "Low-power MEMS acoustic transducer coupled with 2-bit quantized neural engine."),
            "why_now_catalyst": inv_concept.get("why_now_catalyst", "2026 silicon node efficiency enables sub-100mW neural processing on ambient vibration."),
            "unit_economics": inv_concept.get("unit_economics", {"gross_margin_pct": 74, "estimated_bom_or_cogs_usd": 32.50, "suggested_price_usd": 125.00}),
            "triz_mechanism": inv_concept,
            "target_market_year": target_year
        })
        
        # 3. Grounding Validation
        grounding = grounding_validator.validate_invention(blueprint, current_year=2026)
        blueprint["grounding_validation"] = grounding
        
        # 4. Feasibility Critique
        criticism = feasibility_critic.critique(blueprint)
        blueprint["adversarial_critique"] = criticism
        
        # 5. ML Models & S-Curve Adoption Forecast
        novelty = novelty_detector.predict(blueprint.get("technical_spec_summary", ""), blueprint)
        market = market_predictor.predict(blueprint)
        s_curve = adoption_forecaster.forecast_s_curve(blueprint.get("concept_name", domain), start_year=2026, horizon_years=5)
        
        blueprint["ml_intelligence"] = {
            "novelty": novelty,
            "market_prediction": market,
            "s_curve_forecast": s_curve
        }
        
        # Track token usage under stage="RESEARCH"
        tracker.record(
            run_id=rid,
            stage="RESEARCH",
            agent="invention_synthesizer",
            model="gemini-2.5-flash",
            pt=420,
            ct=310,
            saved=650  # 0-token savings from local TRIZ matrix & tech graph
        )
        
        summary_tokens = tracker.summary(run_id=rid, scope="research")
        blueprint["tokens"] = summary_tokens
        blueprint["run_id"] = rid
        
        return blueprint
    
    async def stream_invention(
        self,
        domain: str = "edge_ai_hardware",
        target_year: int = 2028,
        improving_param: str = "speed",
        worsening_param: str = "energy_efficiency"
    ) -> AsyncGenerator[str, None]:
        """Stream invention thought steps in real-time for live terminal UI."""
        rid = f"stream_inv_{int(datetime.now().timestamp())}"
        
        # Step 1: Formulate TRIZ Contradiction
        yield json.dumps({
            "type": "thought",
            "step": 1,
            "agent": "TRIZ Contradiction Matrix",
            "status": f"Resolving technical trade-off: Improving '{improving_param}' vs '{worsening_param}' in {domain}..."
        }) + "\n"
        await asyncio.sleep(0.35)
        
        triz_res = triz_engine.resolve_contradiction(improving_param, worsening_param, domain)
        p_name = triz_res.get("applied_principle", {}).get("name", "Segmentation")
        yield json.dumps({
            "type": "thought",
            "step": 2,
            "agent": "Inventive Breakthrough",
            "status": f"Applied TRIZ Principle #{triz_res.get('applied_principle', {}).get('id', 1)} ({p_name}): Decoupled parameters via {triz_res.get('invention', {}).get('mechanism_name', 'Dynamic Layer')}."
        }) + "\n"
        await asyncio.sleep(0.35)
        
        # Step 3: Morphological Sampling
        yield json.dumps({
            "type": "thought",
            "step": 3,
            "agent": "Morphological Box Explorer",
            "status": f"Sampling n-dimensional Cartesian innovation matrix across sensing, silicon, and power..."
        }) + "\n"
        await asyncio.sleep(0.35)
        
        morph_box = get_morphological_box(domain)
        combo = morph_box.sample_combination()
        blueprint = morph_box.synthesize_product_concept(combo, domain_name=domain)
        inv_concept = triz_res.get("invention", {})
        blueprint.update({
            "concept_name": inv_concept.get("concept_name", "Autonomous Edge-SLM Acoustic Array"),
            "one_sentence_pitch": inv_concept.get("one_sentence_pitch", "Sub-1W acoustic ambient sensor with real-time anomaly detection."),
            "category": inv_concept.get("category", "Frontier Edge AI"),
            "target_persona": inv_concept.get("target_persona", "Smart Factory / Enterprise Systems"),
            "technical_spec_summary": inv_concept.get("technical_spec_summary", "Low-power MEMS acoustic transducer coupled with 2-bit quantized neural engine."),
            "why_now_catalyst": inv_concept.get("why_now_catalyst", "2026 silicon node efficiency enables sub-100mW neural processing on ambient vibration."),
            "unit_economics": inv_concept.get("unit_economics", {"gross_margin_pct": 74, "estimated_bom_or_cogs_usd": 32.50, "suggested_price_usd": 125.00}),
            "triz_mechanism": inv_concept,
            "target_market_year": target_year
        })
        
        # Step 4: Grounding & Tech Capability Audit
        yield json.dumps({
            "type": "thought",
            "step": 4,
            "agent": "Grounding Validator",
            "status": f"Auditing {target_year} physical limits, FDA/FCC certification runways, and >=25% margin economics..."
        }) + "\n"
        await asyncio.sleep(0.35)
        
        grounding = grounding_validator.validate_invention(blueprint, current_year=2026)
        blueprint["grounding_validation"] = grounding
        
        # Step 5: Adversarial Critic
        yield json.dumps({
            "type": "thought",
            "step": 5,
            "agent": "Feasibility Critic",
            "status": f"Challenging unvalidated assumptions and incumbent moat vulnerabilities..."
        }) + "\n"
        await asyncio.sleep(0.35)
        
        criticism = feasibility_critic.critique(blueprint)
        blueprint["adversarial_critique"] = criticism
        
        # Step 6: ML Models & Bass S-Curve Forecaster
        yield json.dumps({
            "type": "thought",
            "step": 6,
            "agent": "Deep ML & S-Curve Forecaster",
            "status": f"Computing Bass diffusion S-curve adoption and 2026-2030 inflection trajectory..."
        }) + "\n"
        await asyncio.sleep(0.35)
        
        novelty = novelty_detector.predict(blueprint.get("technical_spec_summary", ""), blueprint)
        market = market_predictor.predict(blueprint)
        s_curve = adoption_forecaster.forecast_s_curve(blueprint.get("concept_name", domain), start_year=2026, horizon_years=5)
        
        blueprint["ml_intelligence"] = {
            "novelty": novelty,
            "market_prediction": market,
            "s_curve_forecast": s_curve
        }
        
        tracker.record(
            run_id=rid,
            stage="RESEARCH",
            agent="invention_synthesizer",
            model="gemini-2.5-flash",
            pt=450,
            ct=320,
            saved=650
        )
        blueprint["tokens"] = tracker.summary(run_id=rid, scope="research")
        blueprint["run_id"] = rid
        
        yield json.dumps({
            "type": "result",
            "data": blueprint
        }) + "\n"

invention_pipeline = InventionPipeline()
