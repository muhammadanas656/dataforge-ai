import pytest
from src.triz_engine import triz_engine
from src.morphological_analysis import get_morphological_box

def test_triz_parameters_and_contradiction():
    params = triz_engine.get_parameters()
    assert "speed" in params
    assert "energy_efficiency" in params
    
    contra = triz_engine.identify_contradiction("speed", "energy_efficiency")
    assert len(contra["principles"]) > 0
    assert contra["improving"] == "speed"
    assert contra["worsening"] == "energy_efficiency"

def test_morphological_box():
    box = get_morphological_box("edge_ai_hardware")
    assert box.total_combinations() > 10
    
    combo = box.sample_combination()
    assert "sensing_modality" in combo
    assert "compute_architecture" in combo
    
    novelty = box.evaluate_novelty(combo)
    assert 0.0 <= novelty <= 1.0
