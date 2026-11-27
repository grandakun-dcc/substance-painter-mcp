import json

from substancepainter_mcp.install import install, uninstall


def test_install_includes_nested_workflows_and_preserves_user_edits(tmp_path, monkeypatch):
    monkeypatch.setenv("PAINTER_MCP_HOME", str(tmp_path / "state"))
    result = install()
    assert result["installed"]
    state = tmp_path / "state"
    schema = state / "modules/substancepainter_mcp/legacy/catalog.json"
    assert len(json.loads(schema.read_text("utf-8"))) == 79
    assert (state / "modules/substancepainter_mcp/licenses/SubstancePainterMCP-MIT.txt").is_file()
    startup = state / "python/startup/substancepainter_startup.py"
    assert "substancepainter_mcp.plugin" in startup.read_text("utf-8")
    window = state / "python/startup/substancepainter_window.py"
    assert "substancepainter_mcp.worker_window" in window.read_text("utf-8")
    startup.write_text("# custom startup\n", "utf-8")
    assert install()["installed"] is False
    assert startup.read_text("utf-8") == "# custom startup\n"
    result = install(replace_edited=True)
    assert result["installed"] and len(result["backups"]) == 1
    startup.write_text("# preserve\n", "utf-8")
    result = uninstall()
    assert str(startup) in result["preserved"]
    assert not schema.exists()
    assert not window.exists()
