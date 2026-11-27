import builtins
import concurrent.futures
import inspect
from types import SimpleNamespace

import pytest

from substancepainter_mcp.catalog import OPS
from substancepainter_mcp.common import Fault, validate
from substancepainter_mcp.legacy.client import PainterRemote
from substancepainter_mcp.legacy.operations import PainterOperations
from substancepainter_mcp.legacy.wrappers import build
from substancepainter_mcp.adapter import PainterAdapter
from substancepainter_mcp.broker import Broker


def bridge():
    adapter = PainterAdapter.__new__(PainterAdapter)
    adapter.thread_id = __import__("threading").get_ident()
    adapter.sp = SimpleNamespace()
    return PainterRemote(adapter)


def test_all_workflow_schemas_and_wrappers_agree():
    workflows = build(PainterOperations(bridge()))
    assert len(workflows) == 79
    for name, function in workflows.items():
        spec = OPS["workflow." + name]
        signature = inspect.signature(function)
        assert set(signature.parameters) == set(spec["inputSchema"]["properties"])
        assert set(spec["inputSchema"].get("required", [])) == {
            key for key, param in signature.parameters.items() if param.default is inspect.Parameter.empty}
        assert spec["undo"] == "none"
        with pytest.raises(Fault):
            validate({"unrecognized": True}, spec["inputSchema"])


def test_local_bridge_json_isolation_preserves_quotes_unicode_and_types():
    remote = bridge()
    params = {"text": "中文\\path'\";\n", "nested": {"items": [False, None, 1]}}
    value = remote.execute_python_json(
        "params['nested']['items'].append(2)\nresult = params", params)
    assert value["success"] is True
    assert value["data"]["text"] == params["text"]
    assert params["nested"]["items"] == [False, None, 1]
    assert value["data"]["nested"]["items"] == [False, None, 1, 2]
    assert remote.execute_python("1 + 2") == 3


def test_bridge_refuses_background_threads_before_running_code():
    remote = bridge()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        with pytest.raises(Fault) as failure:
            pool.submit(remote.execute_python_json, "result = 'wrong'").result()
    assert failure.value.code == "WRONG_THREAD"


def test_nested_workflow_mapping_value_types_are_validated():
    spec = OPS["workflow.set_fill_channels"]["inputSchema"]
    validate({"uid": 1, "values": {"BaseColor": [1.0, 0.0, 0.0], "Roughness": 0.5}}, spec)
    with pytest.raises(Fault):
        validate({"uid": 1, "values": {"Roughness": "invalid"}}, spec)


def test_upstream_raw_python_permission_remains_opt_in(monkeypatch):
    monkeypatch.delenv("SP_MCP_ALLOW_EXECUTE_PYTHON", raising=False)
    tool = build(PainterOperations(bridge()))["execute_python"]
    with pytest.raises(PermissionError):
        tool("result = 1")
    monkeypatch.setenv("SP_MCP_ALLOW_EXECUTE_PYTHON", "1")
    assert tool("result = 1") == {"success": True, "data": 1}


def test_shutdown_disconnects_owned_callbacks_without_touching_other_plugins():
    remote = bridge()
    removed = []
    remote.adapter.sp.event = SimpleNamespace(
        DISPATCHER=SimpleNamespace(disconnect=lambda event, callback: removed.append((event, callback))),
        ProjectEditionEntered="created")
    remote.execute_python_json(
        "import builtins\n"
        "callback = lambda e: None\n"
        "builtins._painter_unified_workflow_bake_refs = [('bake', callback)]\n"
        "builtins._painter_unified_workflow_project_creation_callback = callback\n"
        "builtins._painter_unified_workflow_bake_state = {'status':'running'}")
    state = builtins._painter_unified_workflow_bake_state
    unrelated = object()
    builtins._sp_mcp_bake_refs = unrelated
    try:
        remote.close()
        remote.close()
        assert len(removed) == 2
        assert state["status"] == "unknown"
        assert builtins._sp_mcp_bake_refs is unrelated
        assert not hasattr(builtins, "_painter_unified_workflow_bake_refs")
    finally:
        del builtins._sp_mcp_bake_refs


def test_workflow_busy_job_controls_are_recognized():
    for op in ("workflow.get_bake_job", "workflow.cancel_bake",
               "workflow.get_project_creation_job", "workflow.get_mesh_reload_job",
               "workflow.get_shelf_refresh_job"):
        assert op in OPS
        assert Broker._control({"tool": "painter_run", "args": {"steps": [{"op": op}]}})
    assert not Broker._control({"tool": "painter_run", "args": {"steps": [
        {"op": "workflow.get_bake_job"}, {"op": "workflow.create_fill_layer"}]}})


@pytest.mark.parametrize("udim,tiles,ready", [
    (False, [], True), (True, [], False),
    (True, [SimpleNamespace(u=0, v=0)], True)])
def test_bake_preflight_requires_tiles_only_for_udim(monkeypatch, udim, tiles, ready):
    import sys
    from types import ModuleType

    usage = SimpleNamespace(name="Normal")
    common = {}
    for key, value in {"HipolyMesh": "", "CageMesh": "", "LowAsHigh": True,
                       "CageMode": 0, "OutputSize": [7, 7]}.items():
        common[key] = SimpleNamespace(value=lambda value=value: value,
                                      enum_values=lambda: {"Distance": 0})
    target = SimpleNamespace(name="Test", has_uv_tiles=lambda: udim,
                             get_mesh_map_resource=lambda usage: None)
    settings = SimpleNamespace(
        common=lambda: common, is_textureset_enabled=lambda: True,
        get_enabled_bakers=lambda: [usage], get_enabled_uv_tiles=lambda: tiles)
    package = ModuleType("substance_painter")
    package.__path__ = []
    modules = {
        "baking": SimpleNamespace(BakingParameters=SimpleNamespace(
            from_texture_set=lambda target: settings)),
        "project": SimpleNamespace(is_open=lambda: True, is_busy=lambda: False),
        "textureset": SimpleNamespace(all_texture_sets=lambda: [target],
            MeshMapUsage=SimpleNamespace(__members__={"Normal": usage})),
    }
    monkeypatch.setitem(sys.modules, "substance_painter", package)
    for name, module in modules.items():
        setattr(package, name, module)
        monkeypatch.setitem(sys.modules, "substance_painter." + name, module)
    qt = ModuleType("PySide6")
    qt.QtCore = SimpleNamespace()
    monkeypatch.setitem(sys.modules, "PySide6", qt)
    result = PainterOperations(bridge()).preflight_bake(["Test"])
    assert result["ready"] is ready
    assert any(e["code"] == "no_enabled_uv_tiles" for e in result["errors"]) is not ready
