# SubstancePainter-MCP

合并 PainterMCP 与 SubstancePainterMCP 的新 MCP 项目，版本 **1.0.0**。

一个 stdio MCP 服务提供 8 个顶层工具、45 个原生操作、79 个 `workflow.*` 操作，以及 2 个网格贴图导出操作。外部 Python 环境与 Painter 插件分离；Painter 内只依赖标准库和自带的 PySide6/Adobe API。

## 安装与启动

需要 Python 3.10+、已授权的 Adobe Substance 3D Painter。已在本机 Painter 12.1.5 / 内置 Python 3.13.9、外部 MCP Python 3.11.9 验证，其他版本应以 `painter_describe` 和实际调用结果为准。

安装完成后，将生成的 `mcp.json` 导入支持 stdio 的 MCP 客户端并重新连接。重新部署时按以下步骤执行。

```powershell
.\install.ps1
.\start_painter.ps1 -KeepAlive
```

启动脚本应保留在独立 PowerShell 窗口中。它创建最小化的后台 Painter，不切换现有编辑窗口。无需启用 Adobe 固定端口的 Remote Scripting。

安装目录：`%LOCALAPPDATA%\MCP\SubstancePainter-MCP\.venv`；插件、连接和运行状态：该目录下的 `state`。将生成的 `mcp.json` 导入 TRAE 或其他 MCP 客户端。不同实例使用不同的 `PAINTER_MCP_HOME`、`PAINTER_MCP_CONNECTION` 与插件路径；可复制配置并通过 `start_painter.ps1 -WorkerRoot <独立state路径>` 启动另一个实例，先用相同环境变量执行 `python -m substancepainter_mcp install` 安装该实例插件。

## MCP 调用

8 个顶层工具为 `painter_status`、`painter_describe`、`painter_observe`、`painter_run`、`painter_script`、`painter_session`、`painter_request`、`painter_changes`。

先发现操作：

```json
{"domain": "workflow", "limit": 5}
```

在 `painter_describe` 中读取精确参数、可用 API、修改标记及撤销范围，再调用 `painter_run`：

```json
{
  "steps": [
    {"id": "project", "op": "project.info"},
    {"id": "audit", "op": "workflow.audit_project"},
    {"id": "plan", "op": "mesh_maps.plan_export"}
  ]
}
```

`workflow.*` 保留旧工具名和参数，例如 `workflow.inspect_baking`、`workflow.plan_texture_export`、`workflow.get_project_info`。旧项目中的 `confirm`、文件覆盖、允许目录与 raw Python 开关仍适用，但现在这些检查在 Painter worker 进程中执行：启动 worker 前设置 `SP_MCP_PROJECT_ROOTS`、`SP_MCP_EXPORT_ROOTS` 等环境变量。`workflow.execute_python` 默认关闭；`painter_script` 延续 PainterMCP 的完全权限脚本功能。

原生和 workflow 图层引用不同：原生操作使用 `node:...` 引用，workflow 使用整数 UID。不要直接混传；可读取各自的图层列表获得对应引用。

烘焙模式可能没有 active stack；烘焙后检查 mesh maps 或图层时请显式传 `texture_set`，避免依赖界面当前选择。

一次调用最多 64 步。`execution_available:false` 表示排队或执行中，用同一 `request_id` 查询 `painter_request`；不能把受理当成完成。请求结果保留 15 分钟，重启或过期后要先检查工程状态。`undo:"layerstack"` 仅支持原生图层堆栈操作和只读步骤，提供原生分组撤销，**不会在失败时自动回滚**。workflow 修改、工程切换、烘焙与文件导出不能加入该撤销范围。

## 批量网格贴图导出

```powershell
$pythonExe = "$env:LOCALAPPDATA\MCP\SubstancePainter-MCP\.venv\Scripts\python.exe"
& $pythonExe .\batch_export.py --status
& $pythonExe .\batch_export.py --project 'Y:\...\_SPFile\example.spp' --dry-run
& $pythonExe .\batch_export.py --project 'Y:\...\_SPFile\example.spp' --overwrite
& $pythonExe .\batch_export.py --folder 'D:\GameProject\Character' --recursive --overwrite
```

从纹理集已指定的网格贴图导出 **Normal / AO / Curvature**，文件为真实 8-bit TGA，名称 `<纹理集名>_Normal.tga` 等；UDIM 加 tile 后缀。输出为 SPP 所在目录的上一级下的 `SP_Texture`。保持工程贴图分辨率，只导出已有 mesh maps，缺少的项目会报告并跳过。

批处理核验 worker PID、runtime 和源 SPP SHA-256；不保存源 SPP。拒绝切走批次开始前有未保存修改的工程。批次结束后恢复原工程或原始空状态；批次自行产生的导出设置 dirty 可被丢弃。同名文件默认拒绝覆盖，传 `--overwrite` 才覆盖。

## 维护

```powershell
& $pythonExe -m substancepainter_mcp doctor
& $pythonExe -m substancepainter_mcp repair
& $pythonExe -m substancepainter_mcp uninstall
```

修复和卸载保护用户改动过的托管文件；`repair --replace-edited` 会先备份。安装器只管理此 fork 的文件。此项目不启用上游自动更新，升级需要重新安装本项目并重启 worker/MCP 客户端。

开发验证：

```powershell
& $pythonExe -m pip install '.[dev]'
& $pythonExe -m pytest --basetemp "$env:TEMP\SubstancePainter-MCP-tests"
```

见 `VALIDATION.md`、`evaluations.xml` 和 `THIRD_PARTY_NOTICES.md`。两份上游 MIT 许可证已保留。
