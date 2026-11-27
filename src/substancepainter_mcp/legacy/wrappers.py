"""Upstream tool wrappers, adapted to an injected operations object."""
from __future__ import annotations
import os
from typing import Any

def build(operations):

    def painter_status() -> dict[str, Any]:
        """Check the connection and report Painter, Python API, and project status."""
        return operations.status()

    def get_project_info() -> dict[str, Any]:
        """Return the current project path and texture-set names."""
        return operations.project_info()

    def plan_project_creation(mesh_file_path: str, output_path: str, mesh_map_file_paths: list[str] | None=None, template_file_path: str | None=None, settings: dict[str, Any] | None=None, overwrite: bool=False, replace_current: bool=False, backup_current_path: str | None=None, backup_mode: str='Incremental', overwrite_backup: bool=False) -> dict[str, Any]:
        """Validate a new project, typed import settings, context switch, and backup."""
        return operations.plan_project_creation(mesh_file_path, output_path, mesh_map_file_paths, template_file_path, settings, overwrite, replace_current, backup_current_path, backup_mode, overwrite_backup)

    def create_project(mesh_file_path: str, output_path: str, mesh_map_file_paths: list[str] | None=None, template_file_path: str | None=None, settings: dict[str, Any] | None=None, overwrite: bool=False, replace_current: bool=False, backup_current_path: str | None=None, backup_mode: str='Incremental', overwrite_backup: bool=False, confirm: bool=False) -> dict[str, Any]:
        """Back up an optional current project, create a typed project, and verify its file."""
        return operations.create_project(mesh_file_path, output_path, mesh_map_file_paths, template_file_path, settings, overwrite, replace_current, backup_current_path, backup_mode, overwrite_backup, confirm)

    def get_project_creation_job(job_id: str | None=None) -> dict[str, Any]:
        """Read terminal state and file verification for an asynchronous project creation."""
        return operations.get_project_creation_job(job_id)

    def save_project(mode: str='Incremental', confirm: bool=False) -> dict[str, Any]:
        """Overwrite and verify the current saved project after explicit confirmation."""
        return operations.save_project(mode, confirm)

    def open_project(project_path: str, confirm: bool=False, backup_current_path: str | None=None, backup_mode: str='Incremental', overwrite_backup: bool=False) -> dict[str, Any]:
        """Open an approved .spp, requiring a backup when the current project is dirty."""
        return operations.open_project(project_path, confirm, backup_current_path, backup_mode, overwrite_backup)

    def get_capabilities() -> dict[str, Any]:
        """Report runtime-supported channels, blend modes, and version-sensitive features."""
        return operations.capabilities()

    def audit_project() -> dict[str, Any]:
        """Audit texture sets, channels, layer hygiene, and outdated resources."""
        return operations.audit_project()

    def inspect_baking(texture_set: str | None=None) -> dict[str, Any]:
        """Inspect enabled bakers, UV tiles, and mesh-map assignments without starting a bake."""
        return operations.inspect_baking(texture_set)

    def inspect_baking_parameters(texture_set: str, baker: str | None=None) -> dict[str, Any]:
        """Inspect editable common parameters and one baker's typed property metadata."""
        return operations.inspect_baking_parameters(texture_set, baker)

    def configure_baking(texture_set: str, enabled: bool | None=None, enabled_bakers: list[str] | None=None, enabled_uv_tiles: list[int] | None=None, curvature_method: str | None=None, common_values: dict[str, Any] | None=None, baker_values: dict[str, dict[str, Any]] | None=None, confirm: bool=False) -> dict[str, Any]:
        """Transactionally configure Texture Set, UV tile, common, and per-baker settings."""
        return operations.configure_baking(texture_set, enabled, enabled_bakers, enabled_uv_tiles, curvature_method, common_values, baker_values, confirm)

    def set_baking_mesh_inputs(texture_set: str, high_poly_files: list[str] | None=None, cage_file: str | None=None, low_as_high: bool | None=None, cage_mode: str | None=None, confirm: bool=False) -> dict[str, Any]:
        """Assign sandboxed high-poly/cage meshes and related common baker settings."""
        return operations.set_baking_mesh_inputs(texture_set, high_poly_files, cage_file, low_as_high, cage_mode, confirm)

    def set_baking_resource_input(texture_set: str, parameter: str, resource_url: str | None=None, baker: str | None=None, clear: bool=False, confirm: bool=False) -> dict[str, Any]:
        """Set or clear a Resource-typed common/per-baker input transactionally."""
        return operations.set_baking_resource_input(texture_set, parameter, resource_url, baker, clear, confirm)

    def capture_baking_preset(texture_set: str, bakers: list[str] | None=None) -> dict[str, Any]:
        """Capture a portable JSON baking preset without filesystem-backed properties."""
        return operations.capture_baking_preset(texture_set, bakers)

    def apply_baking_preset(texture_set: str, preset: dict[str, Any], confirm: bool=False) -> dict[str, Any]:
        """Apply a captured baking preset transactionally after explicit confirmation."""
        return operations.apply_baking_preset(texture_set, preset, confirm)

    def preflight_bake(texture_sets: list[str] | None=None) -> dict[str, Any]:
        """Validate selected Texture Sets, mesh inputs, UV tiles, and expected mesh maps."""
        return operations.preflight_bake(texture_sets)

    def start_batch_bake(texture_sets: list[str], confirm: bool=False, backup_path: str | None=None, backup_mode: str='Incremental', overwrite_backup: bool=False) -> dict[str, Any]:
        """Preflight and start a cancellable multi-Texture-Set bake with result manifests."""
        return operations.start_batch_bake(texture_sets, confirm, backup_path, backup_mode, overwrite_backup)

    def start_bake(texture_set: str, confirm: bool=False, backup_path: str | None=None, backup_mode: str='Incremental', overwrite_backup: bool=False) -> dict[str, Any]:
        """Start an asynchronous mesh-map bake after explicit confirmation."""
        return operations.start_bake(texture_set, confirm, backup_path, backup_mode, overwrite_backup)

    def get_bake_job(job_id: str | None=None) -> dict[str, Any]:
        """Return progress and terminal status for the latest or selected bake job."""
        return operations.get_bake_job(job_id)

    def cancel_bake(job_id: str) -> dict[str, Any]:
        """Request cooperative cancellation of a running bake job."""
        return operations.cancel_bake(job_id)

    def plan_mesh_reload(mesh_file_path: str, backup_path: str | None=None, backup_mode: str='Incremental', overwrite_backup: bool=False, preserve_strokes: bool=True, import_cameras: bool=True, auto_unwrap_settings: dict[str, Any] | None=None, mesh_settings: dict[str, Any] | None=None) -> dict[str, Any]:
        """Validate a mesh reload and preview texture-set and backup impact."""
        return operations.plan_mesh_reload(mesh_file_path, backup_path, backup_mode, overwrite_backup, preserve_strokes, import_cameras, auto_unwrap_settings, mesh_settings)

    def start_mesh_reload(mesh_file_path: str, confirm: bool=False, backup_path: str | None=None, backup_mode: str='Incremental', overwrite_backup: bool=False, preserve_strokes: bool=True, import_cameras: bool=True, auto_unwrap_settings: dict[str, Any] | None=None, mesh_settings: dict[str, Any] | None=None) -> dict[str, Any]:
        """Back up and asynchronously reload a mesh after explicit confirmation."""
        return operations.start_mesh_reload(mesh_file_path, confirm, backup_path, backup_mode, overwrite_backup, preserve_strokes, import_cameras, auto_unwrap_settings, mesh_settings)

    def get_mesh_reload_job(job_id: str | None=None) -> dict[str, Any]:
        """Return status and texture-set changes for the latest mesh reload job."""
        return operations.get_mesh_reload_job(job_id)

    def list_layers(texture_set: str | None=None, recursive: bool=True) -> dict[str, Any]:
        """List layers with stable UIDs, types, visibility, and optional group children."""
        return operations.list_layers(texture_set=texture_set, recursive=recursive)

    def find_layers(query: str='', node_type: str | None=None, visible: bool | None=None, texture_set: str | None=None) -> dict[str, Any]:
        """Search layers by partial name, exact node type, and visibility."""
        return operations.find_layers(query, node_type, visible, texture_set)

    def snapshot_layer_tree(texture_set: str | None=None) -> dict[str, Any]:
        """Capture a detailed layer/effect snapshot with a deterministic SHA-256 digest."""
        return operations.snapshot_layer_tree(texture_set)

    def diff_layer_snapshots(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
        """Compare two layer snapshots by UID and report added, removed, and changed nodes."""
        return operations.diff_layer_snapshots(before, after)

    def get_geometry_mask(uid: int) -> dict[str, Any]:
        """Inspect a layer's Mesh/UVTile geometry mask and available elements."""
        return operations.get_geometry_mask(uid)

    def set_geometry_mask(uid: int, mask_type: str, elements: list[str | int], inclusion_list: bool=True) -> dict[str, Any]:
        """Set a geometry mask using mesh names or standard UDIM numbers."""
        return operations.set_geometry_mask(uid, mask_type, elements, inclusion_list)

    def create_fill_layer(name: str, texture_set: str | None=None, base_color: list[float] | None=None) -> dict[str, Any]:
        """Create a top-level Fill Layer, optionally setting sRGB base color [r,g,b]."""
        return operations.create_fill_layer(name, texture_set, base_color)

    def create_group(name: str, texture_set: str | None=None) -> dict[str, Any]:
        """Create a top-level layer group."""
        return operations.create_group(name, texture_set)

    def create_paint_layer(name: str, texture_set: str | None=None) -> dict[str, Any]:
        """Create a top-level Paint Layer."""
        return operations.create_paint_layer(name, texture_set)

    def plan_layer_recipe(recipe: list[dict[str, Any]], texture_set: str | None=None, backup_path: str | None=None, backup_mode: str='Incremental', overwrite_backup: bool=False) -> dict[str, Any]:
        """Validate a recipe, resolve channels, and preview backup/mutation scope without editing."""
        return operations.plan_layer_recipe(recipe, texture_set, backup_path, backup_mode, overwrite_backup)

    def create_layer_recipe(recipe: list[dict[str, Any]], texture_set: str | None=None, backup_path: str | None=None, backup_mode: str='Incremental', overwrite_backup: bool=False) -> dict[str, Any]:
        """Create a nested recipe atomically, optionally saving an approved .spp backup first."""
        return operations.create_layer_recipe(recipe, texture_set, backup_path, backup_mode, overwrite_backup)

    def insert_smart_material(resource_url: str, texture_set: str | None=None, parent_uid: int | None=None, name: str | None=None) -> dict[str, Any]:
        """Insert a Smart Material resource at stack top or inside a group."""
        return operations.insert_smart_material(resource_url, texture_set, parent_uid, name)

    def apply_smart_mask(uid: int, resource_url: str) -> dict[str, Any]:
        """Apply a Smart Mask resource to a layer using transactional mask insertion."""
        return operations.apply_smart_mask(uid, resource_url)

    def set_fill_base_color(uid: int, color: list[float]) -> dict[str, Any]:
        """Set a Fill Layer's base color using its UID and sRGB [r,g,b] values."""
        return operations.set_fill_base_color(uid, color)

    def get_fill_projection(uid: int) -> dict[str, Any]:
        """Inspect a Fill layer's projection mode and common UV transformation."""
        return operations.get_fill_projection(uid)

    def get_fill_sources(uid: int) -> dict[str, Any]:
        """Inspect a Fill layer's material or per-channel color/resource sources."""
        return operations.get_fill_sources(uid)

    def get_procedural_inputs(uid: int, channel: str | None=None) -> dict[str, Any]:
        """Inspect image inputs on Fill, Fill Effect, Generator, or Filter sources."""
        return operations.get_procedural_inputs(uid, channel)

    def set_procedural_input(uid: int, input_name: str, resource_url: str | None=None, channel: str | None=None, reset: bool=False) -> dict[str, Any]:
        """Connect a resource to a procedural image input or reset it to its default."""
        return operations.set_procedural_input(uid, input_name, resource_url, channel, reset)

    def get_fill_parameters(uid: int, channel: str | None=None) -> dict[str, Any]:
        """Inspect procedural parameters, metadata, and presets for a Fill source."""
        return operations.get_fill_parameters(uid, channel)

    def set_fill_parameters(uid: int, values: dict[str, Any], channel: str | None=None) -> dict[str, Any]:
        """Transactionally update typed procedural parameters on a Fill source."""
        return operations.set_fill_parameters(uid, values, channel)

    def apply_fill_preset(uid: int, preset: str, channel: str | None=None) -> dict[str, Any]:
        """Apply a named preset exposed by a procedural Fill source."""
        return operations.apply_fill_preset(uid, preset, channel)

    def list_anchor_points(texture_set: str | None=None) -> dict[str, Any]:
        """List Anchor Point effects with owner and Texture Set context."""
        return operations.list_anchor_points(texture_set)

    def set_fill_anchor_source(uid: int, anchor_uid: int, channel: str | None=None, material_mode: bool=False) -> dict[str, Any]:
        """Connect an Anchor Point to one Fill channel or the complete material source."""
        return operations.set_fill_anchor_source(uid, anchor_uid, channel, material_mode)

    def set_fill_resource(uid: int, resource_url: str, channel: str | None=None, material_mode: bool=False) -> dict[str, Any]:
        """Assign a Painter resource to one Fill channel or to the whole material."""
        return operations.set_fill_resource(uid, resource_url, channel, material_mode)

    def set_fill_projection(uid: int, mode: str, scale: list[float] | None=None, rotation: float | None=None, offset: list[float] | None=None) -> dict[str, Any]:
        """Set Fill, UV, or Triplanar projection with transactional transform updates."""
        return operations.set_fill_projection(uid, mode, scale, rotation, offset)

    def set_fill_projection_advanced(uid: int, mode: str, settings: dict[str, Any]) -> dict[str, Any]:
        """Configure UV, triplanar, planar, spherical, or cylindrical projection details."""
        return operations.set_fill_projection_advanced(uid, mode, settings)

    def set_fill_channels(uid: int, values: dict[str, float | list[float]]) -> dict[str, Any]:
        """Set and enable multiple uniform Fill channels, such as Roughness or Metallic."""
        return operations.set_fill_channels(uid, values)

    def set_active_channels(uid: int, channels: list[str]) -> dict[str, Any]:
        """Replace a Fill or Paint layer's active channel set by UID."""
        return operations.set_active_channels(uid, channels)

    def set_layer_mask(uid: int, enabled: bool, background: str='Black') -> dict[str, Any]:
        """Add/update or remove a layer mask; backgrounds are reported by get_capabilities."""
        return operations.set_layer_mask(uid, enabled, background)

    def insert_mask_effect(uid: int, effect_type: str, resource_url: str | None=None, name: str | None=None) -> dict[str, Any]:
        """Insert Fill, Paint, Generator, Filter, Levels, Anchor, or Smart Mask content."""
        return operations.insert_mask_effect(uid, effect_type, resource_url, name)

    def rename_layer(uid: int, name: str) -> dict[str, Any]:
        """Rename a layer or group by UID."""
        return operations.rename_layer(uid, name)

    def set_layer_properties(uid: int, visible: bool | None=None, opacity: float | None=None, blending_mode: str | None=None, channel: str | None=None) -> dict[str, Any]:
        """Set visibility, opacity, or blend mode; channel defaults to BaseColor."""
        return operations.set_layer_properties(uid, visible, opacity, blending_mode, channel)

    def select_layers(uids: list[int]) -> dict[str, Any]:
        """Select one or more layers in Painter by UID."""
        return operations.select_layers(uids)

    def list_export_presets() -> dict[str, Any]:
        """List built-in and shelf export presets without exporting files."""
        return operations.list_export_presets()

    def inspect_export_preset(preset: str, texture_set: str | None=None) -> dict[str, Any]:
        """Resolve an export preset and preview its map names without writing files."""
        return operations.inspect_export_preset(preset, texture_set)

    def list_export_profiles() -> dict[str, Any]:
        """List curated engine export profiles and whether their Painter presets are available."""
        return operations.list_export_profiles()

    def plan_texture_export(output_directory: str, preset: str, texture_sets: list[str] | None=None, size_log2: int | None=None, file_format: str | None=None, bit_depth: str | None=None) -> dict[str, Any]:
        """Validate an export and list exact output files without writing them."""
        return operations.plan_texture_export(output_directory, preset, texture_sets, size_log2, file_format, bit_depth)

    def export_textures(output_directory: str, preset: str, texture_sets: list[str] | None=None, size_log2: int | None=None, file_format: str | None=None, bit_depth: str | None=None, overwrite: bool=False) -> dict[str, Any]:
        """Export textures inside SP_MCP_EXPORT_ROOTS and verify every output file."""
        return operations.export_textures(output_directory, preset, texture_sets, size_log2, file_format, bit_depth, overwrite)

    def plan_profile_export(output_directory: str, profile: str, texture_sets: list[str] | None=None, size_log2: int | None=None) -> dict[str, Any]:
        """Preview an engine-profile texture export without writing files."""
        return operations.plan_profile_export(output_directory, profile, texture_sets, size_log2)

    def export_with_profile(output_directory: str, profile: str, texture_sets: list[str] | None=None, size_log2: int | None=None, overwrite: bool=False) -> dict[str, Any]:
        """Run a curated export profile inside SP_MCP_EXPORT_ROOTS and verify outputs."""
        return operations.export_with_profile(output_directory, profile, texture_sets, size_log2, overwrite)

    def import_project_resource(file_path: str, usage: str, name: str | None=None, group: str | None=None, confirm: bool=False) -> dict[str, Any]:
        """Import and verify a sandboxed resource inside the open Painter project."""
        return operations.import_project_resource(file_path, usage, name, group, confirm)

    def list_shelves() -> dict[str, Any]:
        """List Painter shelves with paths, write capability, and crawling state."""
        return operations.list_shelves()

    def import_shelf_resource(file_path: str, usage: str, shelf_name: str | None=None, name: str | None=None, group: str | None=None, confirm: bool=False) -> dict[str, Any]:
        """Import and verify a safe resource in an editable shelf or the user shelf."""
        return operations.import_shelf_resource(file_path, usage, shelf_name, name, group, confirm)

    def start_shelf_refresh(shelf_name: str, confirm: bool=False) -> dict[str, Any]:
        """Start event-observed discovery for one Painter shelf after confirmation."""
        return operations.start_shelf_refresh(shelf_name, confirm)

    def get_shelf_refresh_job(job_id: str | None=None) -> dict[str, Any]:
        """Read persistent state for the latest or selected shelf refresh job."""
        return operations.get_shelf_refresh_job(job_id)

    def import_session_resource(file_path: str, usage: str, name: str | None=None, group: str | None=None, confirm: bool=False) -> dict[str, Any]:
        """Import and verify a sandboxed resource for the current Painter session."""
        return operations.import_session_resource(file_path, usage, name, group, confirm)

    def list_project_resources() -> dict[str, Any]:
        """List resources referenced by the open project."""
        return operations.list_project_resources()

    def search_resources(query: str, limit: int=50, resource_type: str | None=None, usage: str | None=None) -> dict[str, Any]:
        """Search Painter resources and return identifiers, type, category, and usages."""
        return operations.search_resources(query, limit, resource_type, usage)

    def find_outdated_resources() -> dict[str, Any]:
        """Plan project-resource replacements without modifying the project."""
        return operations.find_outdated_resources()

    def replace_outdated_resources(confirm: bool=False) -> dict[str, Any]:
        """Atomically replace all outdated resources after explicit confirm=true."""
        return operations.replace_outdated_resources(confirm)

    def save_project_copy(output_path: str, mode: str='Incremental', overwrite: bool=False) -> dict[str, Any]:
        """Save a verified .spp copy inside SP_MCP_PROJECT_ROOTS without relocating the project."""
        return operations.save_project_copy(output_path, mode, overwrite)

    def export_smart_material(uid: int, name: str, output_directory: str, overwrite: bool=False) -> dict[str, Any]:
        """Export a group as a verified Smart Material inside SP_MCP_EXPORT_ROOTS."""
        return operations.export_smart_material(uid, name, output_directory, overwrite)

    def export_smart_mask(uid: int, name: str, output_directory: str, overwrite: bool=False) -> dict[str, Any]:
        """Export a layer mask as a verified Smart Mask inside SP_MCP_EXPORT_ROOTS."""
        return operations.export_smart_mask(uid, name, output_directory, overwrite)

    def delete_layer(uid: int) -> dict[str, Any]:
        """Delete a layer or group by UID. This modifies the open project."""
        return operations.delete_layer(uid)

    def execute_python(code: str) -> dict[str, Any]:
        """Execute raw Painter Python only when SP_MCP_ALLOW_EXECUTE_PYTHON=1."""
        if os.getenv('SP_MCP_ALLOW_EXECUTE_PYTHON') != '1':
            raise PermissionError('Raw Python execution is disabled. Set SP_MCP_ALLOW_EXECUTE_PYTHON=1 in the MCP server environment to opt in.')
        return operations.remote.execute_python_json(code)
    return {'painter_status': painter_status, 'get_project_info': get_project_info, 'plan_project_creation': plan_project_creation, 'create_project': create_project, 'get_project_creation_job': get_project_creation_job, 'save_project': save_project, 'open_project': open_project, 'get_capabilities': get_capabilities, 'audit_project': audit_project, 'inspect_baking': inspect_baking, 'inspect_baking_parameters': inspect_baking_parameters, 'configure_baking': configure_baking, 'set_baking_mesh_inputs': set_baking_mesh_inputs, 'set_baking_resource_input': set_baking_resource_input, 'capture_baking_preset': capture_baking_preset, 'apply_baking_preset': apply_baking_preset, 'preflight_bake': preflight_bake, 'start_batch_bake': start_batch_bake, 'start_bake': start_bake, 'get_bake_job': get_bake_job, 'cancel_bake': cancel_bake, 'plan_mesh_reload': plan_mesh_reload, 'start_mesh_reload': start_mesh_reload, 'get_mesh_reload_job': get_mesh_reload_job, 'list_layers': list_layers, 'find_layers': find_layers, 'snapshot_layer_tree': snapshot_layer_tree, 'diff_layer_snapshots': diff_layer_snapshots, 'get_geometry_mask': get_geometry_mask, 'set_geometry_mask': set_geometry_mask, 'create_fill_layer': create_fill_layer, 'create_group': create_group, 'create_paint_layer': create_paint_layer, 'plan_layer_recipe': plan_layer_recipe, 'create_layer_recipe': create_layer_recipe, 'insert_smart_material': insert_smart_material, 'apply_smart_mask': apply_smart_mask, 'set_fill_base_color': set_fill_base_color, 'get_fill_projection': get_fill_projection, 'get_fill_sources': get_fill_sources, 'get_procedural_inputs': get_procedural_inputs, 'set_procedural_input': set_procedural_input, 'get_fill_parameters': get_fill_parameters, 'set_fill_parameters': set_fill_parameters, 'apply_fill_preset': apply_fill_preset, 'list_anchor_points': list_anchor_points, 'set_fill_anchor_source': set_fill_anchor_source, 'set_fill_resource': set_fill_resource, 'set_fill_projection': set_fill_projection, 'set_fill_projection_advanced': set_fill_projection_advanced, 'set_fill_channels': set_fill_channels, 'set_active_channels': set_active_channels, 'set_layer_mask': set_layer_mask, 'insert_mask_effect': insert_mask_effect, 'rename_layer': rename_layer, 'set_layer_properties': set_layer_properties, 'select_layers': select_layers, 'list_export_presets': list_export_presets, 'inspect_export_preset': inspect_export_preset, 'list_export_profiles': list_export_profiles, 'plan_texture_export': plan_texture_export, 'export_textures': export_textures, 'plan_profile_export': plan_profile_export, 'export_with_profile': export_with_profile, 'import_project_resource': import_project_resource, 'list_shelves': list_shelves, 'import_shelf_resource': import_shelf_resource, 'start_shelf_refresh': start_shelf_refresh, 'get_shelf_refresh_job': get_shelf_refresh_job, 'import_session_resource': import_session_resource, 'list_project_resources': list_project_resources, 'search_resources': search_resources, 'find_outdated_resources': find_outdated_resources, 'replace_outdated_resources': replace_outdated_resources, 'save_project_copy': save_project_copy, 'export_smart_material': export_smart_material, 'export_smart_mask': export_smart_mask, 'delete_layer': delete_layer, 'execute_python': execute_python}
