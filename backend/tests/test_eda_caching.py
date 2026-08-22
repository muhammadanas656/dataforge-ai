import os
import json
import pytest
from src import eda_engine, phase1, cp2, cp3, governance, executor
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_eda_caching_and_force_refresh(monkeypatch):
    def mock_chat(*args, **kwargs):
        return '{"domain": "nutrition", "analyses": [], "steps": []}'

    monkeypatch.setattr("src.llm.tracked_chat", mock_chat)
    monkeypatch.setattr("src.cp2.tracked_chat", mock_chat)
    monkeypatch.setattr("src.cp3.tracked_chat", mock_chat)
    monkeypatch.setattr("src.llm_critic.tracked_chat", mock_chat)
    monkeypatch.setattr("src.ai_planner.tracked_chat", mock_chat)

    prof = phase1.run_phase1('uploads/cereal.csv')
    did = prof['dataset_id']
    cp2.run_cp2(f'reports/profile_{did}.json')
    cp3.run_cp3(f'reports/profile_{did}.json')
    gov = governance.run_governance(f'reports/plan_{did}.json')
    step_ids = [s['id'] for s in gov['steps']]
    executor.run_execution(did, step_ids, gov)

    # 1. First GET request -> generates and caches
    res1 = client.get(f'/api/eda/report/{did}')
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1['analysis_count'] > 0
    assert os.path.exists(f'reports/eda_{did}.json')

    # 2. Second GET request -> instant cache hit
    res2 = client.get(f'/api/eda/report/{did}')
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2['analysis_count'] == data1['analysis_count']

    # 3. POST /api/eda/full/{did}?force=true -> forces cache regeneration
    res3 = client.post(f'/api/eda/full/{did}?force=true')
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3['analysis_count'] == data1['analysis_count']
