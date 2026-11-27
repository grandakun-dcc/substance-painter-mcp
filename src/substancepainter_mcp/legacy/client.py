"""Local replacement for the upstream HTTP remote; called only on Painter's thread."""

import builtins
import json
from types import SimpleNamespace


class PainterScriptError(RuntimeError):
    """Compatibility error type used by the vendored workflows."""


class PainterRemote:
    def __init__(self, adapter):
        self.adapter = adapter
        self.config = SimpleNamespace(host="127.0.0.1", port=None)
        self.owned = {}

    def check_connection(self):
        self.adapter.assert_thread()
        return self.adapter.sp.application.version()

    def execute_python(self, code):
        self.adapter.assert_thread()
        return eval(compile(code, "<painter-unified-workflow>", "eval"), {})

    def execute_js(self, code):
        self.adapter.assert_thread()
        return self.adapter.sp.js.evaluate(code)

    def execute_python_json(self, code, params=None):
        self.adapter.assert_thread()
        namespace = {"params": json.loads(json.dumps(params or {}, ensure_ascii=False))}
        prefix = "_painter_unified_workflow_"
        before = {name: getattr(builtins, name) for name in dir(builtins)
                  if name.startswith(prefix)}
        try:
            exec(compile(code, "<painter-unified-workflow>", "exec"), namespace, namespace)
            return json.loads(json.dumps(
                {"success": True, "data": namespace.get("result")},
                ensure_ascii=False, default=str))
        finally:
            for name in dir(builtins):
                if name.startswith(prefix) and getattr(builtins, name) is not before.get(name):
                    self.owned[name] = getattr(builtins, name)

    def close(self):
        self.adapter.assert_thread()
        # Disconnect only callbacks installed by this bridge, never other plugins.
        for name, value in self.owned.items():
            if getattr(builtins, name, None) is not value:
                continue
            refs = value if name.endswith("_refs") else []
            if name.endswith("_project_creation_callback"):
                event = getattr(self.adapter.sp.event, "ProjectEditionEntered", None)
                refs = [(event, value)] if event else []
            for event, callback in refs:
                try:
                    self.adapter.sp.event.DISPATCHER.disconnect(event, callback)
                except (RuntimeError, TypeError, ValueError):
                    pass
            if name.endswith("_state") and isinstance(value, dict) and value.get("status") == "running":
                value.update(status="unknown", error="SubstancePainter-MCP plugin stopped")
            delattr(builtins, name)
        self.owned.clear()
