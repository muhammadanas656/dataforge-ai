import pandas as pd
from src.plugins import get_registry
from src import plugin_sandbox

def test_registry_discovers_sample():
    assert "discount_depth" in [a.name for a in get_registry().analyses]

def test_sandbox_rejects_eval():
    assert not plugin_sandbox.smoke_test("x=eval('1+1')")["ok"]

def test_sandbox_passes_safe():
    code = open("plugins/analysis_discount_depth.py", encoding="utf-8").read()
    assert plugin_sandbox.smoke_test(code, sample_df=pd.DataFrame({"discount": [10, 50, 60]}))["ok"]
