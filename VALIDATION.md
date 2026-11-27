# 验收记录

验收日期：2026-11-20。新项目版本：SubstancePainter-MCP 1.0.0。

更名核验：项目目录、Python 包、CLI、MCP 服务名称、TRAE 项和安装路径已同步更新。原后台为空工程时正常关闭，并以新名称重启；新服务完成初始化、8 个工具与 126 个操作发现，以及原生/workflow 混合调用检查。

## 环境与隔离

- Adobe Substance 3D Painter **12.1.5**，内置 Python **3.13.9**，Python API **0.3.5**。
- 独立 MCP 环境 Python **3.11.9**，官方 MCP SDK **1.30.0**。
- 验收前段确认编辑进程 **42760** 与 worker **55368** 同时运行；所有本次应用操作都发送给 worker，没有向编辑进程发送保存、关闭或工程切换命令。末次进程检查时 42760 已不在列表，退出原因未确定。
- worker 通过独立插件路径、动态 loopback 端口、Bearer token 与 runtime ID 区分实例；未使用 Adobe 固定端口 Remote Scripting。
- 实际检查 worker 窗口为最小化；工程开关、烘焙后仍保持最小化。
- 批处理和临时工程验证结束后，worker 恢复为空工程、非 busy、无未保存工程。
- 已安装构建出的 wheel；TRAE `SubstancePainter-MCP` 项已切换至新环境，其他 MCP 配置保持原值。客户端重新连接后使用新服务。

## 功能与协议

- 官方 MCP stdio 初始化、工具发现、正常调用、无 Painter 情况错误响应、参数错误后继续连接均通过。
- 顶层工具 **8**；原生操作 **45**；合并 workflow 操作 **79**；专用 mesh-map 导出操作 **2**；总数 **126**。
- BB 工程同时通过两边的工程信息、图层列表、烘焙参数、预设与审计读取。
- 一次 `painter_run` 完成 workflow 创建填充层、引用前一步整数 UID 重命名，并由原生图层列表确认改名结果。
- 临时 OBJ/SPP 中完成 group + fill 配方，生成 **2** 个节点。
- 对配方内 `insert_fill` 注入一次失败后，新增 group 被清理；前后 `snapshot_layer_tree.sha256` 完全一致。注入函数在 `finally` 中恢复。
- 临时工程完成原生异步烘焙、workflow 批量烘焙、workflow 单纹理集烘焙；三次均查询到最终 **Success/success**，并确认 Normal、AO、Curvature 资源存在。
- 修复 workflow 对非 UDIM 纹理集空 tile 列表的误判；保留 UDIM 工程必须启用 tile 的检查。

## 测试与只读评估

**81 / 81** 回归测试通过，包含主线程限制、JSON/参数传递、未知参数拒绝、嵌套映射类型、权限开关、事件清理、请求恢复、队列、输出限额、原生撤销范围、协议与托管文件保护。

`evaluations.xml` 的 **10 / 10** 问题已通过实际只读 MCP 操作求解，合计 **49** 次操作调用。答案及次数保存在 `evaluations_verification.json`。这是工具调用和答案核验，未运行外部模型评分。

## 实际 TGA 导出

源工程：

`<项目根>\Character\M01\Scarf\BB\_SPFile\M01_BB_QuteRed01_Scarf.spp`

源 SPP 导出前后 SHA-256 均为：

`5cce77f411620237803a980014463c987a4c111ec6d8b9d9c079224c9b603097`

导出状态 **Success**，没有缺失的目标 mesh map，文件位于：

`<项目根>\Character\M01\Scarf\BB\SP_Texture`

| 文件 | 解码格式 | 像素尺寸 | 文件字节数 | 像素标准差 |
|---|---|---|---:|---|
| M01_BB_QuteRed01_Scarf_01a_Normal.tga | TGA / RGB | 2048×2048 | 12,582,956 | R 28.12 / G 33.66 / B 27.18 |
| M01_BB_QuteRed01_Scarf_01a_AO.tga | TGA / indexed 8-bit | 2048×2048 | 4,195,116 | 22.32 |
| M01_BB_QuteRed01_Scarf_01a_Curvature.tga | TGA / indexed 8-bit | 2048×2048 | 4,195,116 | 21.22 |

使用 Pillow 完整解码，确认均有非恒定像素内容。导出只写 TGA，不保存源 SPP。

## 边界

126 个操作全部通过 schema 检查，79 个 workflow schema 与包装函数的参数和默认值一致；实际 Painter 验证覆盖上面列出的功能，并非每个操作都逐一执行。其他 Painter 版本、UDIM 批量导出、稀有导入格式仍应在实际环境确认。

分组原生撤销不是失败自动回滚；请求结果恢复不跨 runtime 重启。烘焙模式可能没有 active stack，后续读取请显式指定 `texture_set`。旧 workflow 的确认、文件目录与 raw Python 权限检查在 worker 进程中执行。

源码和安装包保留两份上游 MIT 许可证及来源说明。临时 OBJ/SPP、验证脚本、测试缓存和中间日志在交付后清理。
