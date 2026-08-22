import os
import pytest
from src.workspace import (
    set_workspace, get_workspace, workspace_path, workspace_root,
    reset_workspace, list_workspaces, DEFAULT_WORKSPACE
)
from src.knowledge_graph import KnowledgeGraph
from src.storage import storage


def test_default_workspace():
    reset_workspace()
    assert get_workspace() == DEFAULT_WORKSPACE


def test_set_and_reset():
    set_workspace("acme")
    assert get_workspace() == "acme"
    reset_workspace()
    assert get_workspace() == DEFAULT_WORKSPACE


def test_invalid_workspace_rejected():
    with pytest.raises(ValueError):
        set_workspace("../etc")
    with pytest.raises(ValueError):
        set_workspace("bad workspace!")
    with pytest.raises(ValueError):
        set_workspace("a" * 100)


def test_workspace_path_isolation():
    set_workspace("team_a")
    assert workspace_root().endswith(os.path.join("data", "team_a"))
    assert workspace_path("canonical/foo.csv").endswith(
        os.path.join("data", "team_a", "canonical", "foo.csv")
    )
    reset_workspace()


def test_path_traversal_rejected():
    set_workspace("team_b")
    with pytest.raises(ValueError):
        workspace_path("../../etc/passwd")
    reset_workspace()


def test_knowledge_graph_per_workspace(tmp_path):
    set_workspace("ws_alpha")
    kg_a = KnowledgeGraph()
    kg_a.add_column_semantic("price", "currency", "ecommerce")
    reset_workspace()

    set_workspace("ws_beta")
    kg_b = KnowledgeGraph()
    assert kg_b.get_column_semantic("price") is None
    reset_workspace()


def test_storage_writes_to_workspace(tmp_path, monkeypatch):
    set_workspace("ws_store_test")
    src = tmp_path / "src.csv"
    src.write_text("a,b\n1,2\n")
    storage.write_file(str(src), "canonical/test.csv")
    expected = workspace_path("canonical/test.csv")
    assert os.path.exists(expected)
    reset_workspace()


def test_list_workspaces():
    set_workspace("ws_list_test")
    from src.workspace import ensure_workspace_dir
    ensure_workspace_dir()
    reset_workspace()
    ws = list_workspaces()
    assert "ws_list_test" in ws
    assert DEFAULT_WORKSPACE in ws
