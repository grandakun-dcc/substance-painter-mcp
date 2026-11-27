"""Compose both upstreams at the existing application-thread boundary."""

from .adapter import PainterAdapter
from .legacy.client import PainterRemote
from .legacy.operations import PainterOperations
from .legacy.wrappers import build


class UnifiedAdapter(PainterAdapter):
    def __init__(self, state, sp=None):
        super().__init__(state, sp)
        self.remote = PainterRemote(self)
        self.workflows = build(PainterOperations(self.remote))

    def invoke(self, name, args):
        self.assert_thread()
        if name.startswith("workflow."):
            return self.workflows[name.partition(".")[2]](**args)
        if name in ("mesh_maps.plan_export", "mesh_maps.export"):
            from .mesh_export import export_mesh_maps_data, plan_mesh_maps
            if name == "mesh_maps.export":
                return export_mesh_maps_data(**args)
            plan = plan_mesh_maps()
            plan.pop("config", None)
            return plan
        return super().invoke(name, args)

    def close(self):
        self.remote.close()
        super().close()
