"""One-click export of the mesh maps assigned in Texture Set Settings."""

from pathlib import Path
import re

import substance_painter.export as sp_export
import substance_painter.project as sp_project
import substance_painter.textureset as sp_textureset


_MAPS = (
    ("Normal", sp_textureset.MeshMapUsage.Normal, "normal_base", "RGB"),
    ("AO", sp_textureset.MeshMapUsage.AO, "ambient_occlusion", "L"),
    ("Curvature", sp_textureset.MeshMapUsage.Curvature, "curvature", "L"),
)


def _filename_part(value):
    return re.sub(r'[<>:"/\\|?*$\x00-\x1f]', "_", value).strip(" .") or "Unnamed"


def build_export_config():
    """Read the current project and prepare an export without changing it."""
    if not sp_project.is_open():
        raise RuntimeError("请先打开一个 Substance 3D Painter 工程。")
    if sp_project.is_busy():
        raise RuntimeError("Painter 正在处理任务，请完成烘焙或其他操作后再导出。")
    project_file = sp_project.file_path()
    if not project_file:
        raise RuntimeError("请先保存当前工程为 .spp 文件，以确定导出目录。")

    project_path = Path(project_file)
    output_dir = project_path.parent.parent / "SP_Texture"
    config = {
        "exportPath": output_dir.as_posix(),
        "exportShaderParams": False,
        "exportPresets": [],
        "exportList": [],
        "exportParameters": [{
            "parameters": {
                "fileFormat": "tga",
                "bitDepth": "8",
                "dithering": False,
                "paddingAlgorithm": "passthrough",
                "dilationDistance": 0,
            }
        }],
    }
    missing = []
    names = set()
    for index, texture_set in enumerate(sp_textureset.all_texture_sets()):
        texture_name = texture_set.name
        prefix = _filename_part(texture_name)
        tile_suffix = "_$udim" if texture_set.has_uv_tiles() else ""
        maps = []
        for label, usage, source, channels in _MAPS:
            if texture_set.get_mesh_map_resource(usage) is None:
                missing.append("{}：{}".format(texture_name, label))
                continue
            filename = "{}_{}{}".format(prefix, label, tile_suffix)
            if filename.casefold() in names:
                raise RuntimeError(
                    "纹理集名称生成了重复文件名：{}。请调整纹理集名称后重试。"
                    .format(filename))
            names.add(filename.casefold())
            maps.append({
                "fileName": filename,
                "channels": [{
                    "destChannel": channel,
                    "srcChannel": channel,
                    "srcMapType": "meshMap",
                    "srcMapName": source,
                } for channel in channels],
            })
        if not maps:
            continue
        preset_name = "mesh_maps_{}".format(index)
        config["exportPresets"].append({"name": preset_name, "maps": maps})
        root_path = texture_name
        if texture_set.is_layered_material():
            stacks = texture_set.all_stacks()
            if not stacks:
                raise RuntimeError("纹理集 {} 没有可导出的图层堆栈。".format(texture_name))
            root_path += "/" + stacks[0].name()
        config["exportList"].append({
            "rootPath": root_path,
            "exportPreset": preset_name,
        })
    if not config["exportList"]:
        raise RuntimeError(
            "纹理集中没有可导出的 Normal、AO 或 Curvature 网格贴图。\n"
            "请先在“纹理集设置 → 网格贴图”中烘焙或指定这些贴图。")
    return config, missing


def plan_mesh_maps():
    """Return a read-only plan usable by the Painter MCP execute_python tool."""
    config, missing = build_export_config()
    listed = sp_export.list_project_textures(config)
    paths = [Path(path) for group in listed.values() for path in group]
    if not paths:
        raise RuntimeError("Painter 没有生成可导出的贴图列表。")
    if len({str(path).casefold() for path in paths}) != len(paths):
        raise RuntimeError("导出文件名重复，请检查纹理集名称或 UV Tile 编号。")
    output_dir = Path(config["exportPath"])
    if any(path.parent != output_dir for path in paths):
        raise RuntimeError("Painter 生成的文件路径超出了 SP_Texture 目录。")
    return {
        "project": sp_project.file_path(),
        "output_directory": str(output_dir),
        "files": [str(path) for path in paths],
        "conflicts": [str(path) for path in paths if path.exists()],
        "missing": missing,
        "config": config,
    }

def export_mesh_maps_data(overwrite=False):
    """Export assigned mesh maps and return JSON-compatible data without dialogs."""
    plan = plan_mesh_maps()
    if plan["conflicts"] and not overwrite:
        raise FileExistsError("已有 {} 张同名贴图；覆盖导出时请指定 overwrite=True。"
                             .format(len(plan["conflicts"])))
    Path(plan["output_directory"]).mkdir(parents=True, exist_ok=True)
    result = sp_export.export_project_textures(plan["config"])
    written = {Path(path) for group in result.textures.values() for path in group}
    expected = {Path(path) for path in plan["files"]}
    invalid = [path.name for path in written
               if not path.is_file() or path.stat().st_size == 0]
    if invalid or (result.status != sp_export.ExportStatus.Cancelled and written != expected):
        raise RuntimeError("导出未完整写入所有贴图。\n{}".format(result.message))
    return {
        "project": plan["project"],
        "output_directory": plan["output_directory"],
        "status": result.status.name,
        "message": result.message,
        "files": sorted(str(path) for path in written),
        "missing": plan["missing"],
    }
