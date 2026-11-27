"""Batch mesh-map export through the isolated SubstancePainter-MCP worker."""

import argparse
import asyncio
import hashlib
import json
import time
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def call_tool(session, name, arguments=None):
    deadline = time.monotonic() + 600
    while True:
        response = await session.call_tool(name, arguments or {})
        texts = [part.text for part in response.content if part.type == "text"]
        if response.isError:
            raise RuntimeError("\n".join(texts))
        envelope = response.structuredContent or json.loads("\n".join(texts))
        if not envelope.get("ok"):
            raise RuntimeError(str(envelope))
        data = envelope["data"]
        if data.get("execution_available") is not False:
            return data
        receipt = data["request"]
        request_id = receipt["request_id"]
        if receipt["state"] not in ("queued", "running"):
            raise RuntimeError("请求结果不可用：{}".format(request_id))
        if time.monotonic() >= deadline:
            raise TimeoutError("请求仍在运行，勿重复导出；请查询请求 {}".format(request_id))
        await asyncio.sleep(0.25)
        name, arguments = "painter_request", {"request_id": request_id}


async def script(session, source, arguments=None):
    data = await call_tool(session, "painter_script", {
        "source": source, "arguments": arguments or {}, "language": "python"})
    return data["result"]


async def project_info(session):
    return await script(session, """
import os
import substance_painter.project as project
result = {
    "pid": os.getpid(),
    "open": project.is_open(),
    "path": project.file_path() if project.is_open() else None,
    "busy": project.is_busy(),
    "dirty": project.needs_saving() if project.is_open() else False,
}
""")


async def switch_project(session, path, expected_pid, discard=False):
    return await script(session, """
import os
from pathlib import Path
import substance_painter.project as project
if os.getpid() != arguments["pid"]:
    raise RuntimeError("Worker PID changed.")
if project.is_busy():
    raise RuntimeError("Worker is busy.")
previous_path = project.file_path() if project.is_open() else None
if project.is_open():
    if project.needs_saving() and not arguments["discard"]:
        raise RuntimeError("Worker has unsaved changes; save or close it first.")
    project.close()
try:
    project.open(arguments["path"])
except Exception:
    if project.is_open():
        project.close()
    if previous_path:
        project.open(previous_path)
    raise
result = {"open": project.is_open(), "path": project.file_path()}
""", {"pid": expected_pid, "path": str(path), "discard": discard})


async def close_owned_project(session, expected_pid):
    return await script(session, """
import os
import substance_painter.project as project
if os.getpid() != arguments["pid"] or project.is_busy():
    raise RuntimeError("Worker changed or is busy.")
if project.is_open():
    project.close()
result = {"open": project.is_open()}
""", {"pid": expected_pid})


async def run(args):
    config = json.loads((Path(__file__).parent / "mcp.json").read_text(encoding="utf-8-sig"))
    server = config["mcpServers"]["SubstancePainter-MCP"]
    connection_path = Path(server["env"]["PAINTER_MCP_CONNECTION"])
    connection = json.loads(connection_path.read_text(encoding="utf-8"))
    parameters = StdioServerParameters(
        command=server["command"], args=server["args"], env=server["env"])
    async with stdio_client(parameters) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            status = await call_tool(session, "painter_status")
            if status["runtime_id"] != connection["runtime_id"]:
                raise RuntimeError("Worker runtime changed; retry after checking its project.")
            original = await project_info(session)
            if original["pid"] != connection["pid"]:
                raise RuntimeError("Worker PID does not match its connection file.")
            if getattr(args, "expected_pid", None) and original["pid"] != args.expected_pid:
                raise RuntimeError("Connection is not the requested worker PID.")
            if args.status:
                tools = await session.list_tools()
                return {"connected": True, "pid": original["pid"],
                        "project": original, "painter_version": status["capabilities"]["painter_version"],
                        "tools": [tool.name for tool in tools.tools]}
            original_path = original.get("path")
            projects = [Path(path).resolve() for path in args.project]
            if args.folder:
                folder = Path(args.folder).resolve()
                if not folder.is_dir():
                    raise ValueError("工程目录不存在：{}".format(folder))
                projects.extend(sorted(folder.rglob("*.spp") if args.recursive
                                       else folder.glob("*.spp")))
                if not projects:
                    raise ValueError("目录中没有 .spp 工程。")
            projects = list(dict.fromkeys(projects))
            for path in projects:
                if path.suffix.lower() != ".spp" or not path.is_file():
                    raise ValueError("工程路径无效：{}".format(path))
            results = []
            switched = False
            current_path = original_path
            try:
                for path in projects or [None]:
                    if path is not None and (
                            not current_path or path != Path(current_path)):
                        opened = await switch_project(
                            session, path, original["pid"], discard=switched)
                        if not opened.get("open") or Path(opened.get("path") or "") != path:
                            raise RuntimeError("无法核验当前工程：{}".format(path))
                        current_path = opened["path"]
                        switched = True
                    source = Path(current_path) if current_path else None
                    before_hash = fingerprint(source) if source else None
                    result = await call_tool(session, "painter_run", {"steps": [{
                        "id": "export",
                        "op": "mesh_maps.plan_export" if args.dry_run else "mesh_maps.export",
                        "args": {} if args.dry_run else {"overwrite": args.overwrite},
                    }]})
                    report = result["steps"][0]["result"]
                    after_hash = fingerprint(source) if source else None
                    if before_hash != after_hash:
                        raise RuntimeError("Source SPP changed during export: {}".format(source))
                    report["source_sha256"] = before_hash
                    report["source_unchanged"] = before_hash == after_hash
                    results.append(report)
                    if report.get("status") == "Cancelled":
                        break
            finally:
                if switched:
                    if original_path:
                        await switch_project(
                            session, original_path, original["pid"], discard=True)
                    elif not original_path:
                        await close_owned_project(session, original["pid"])
            return {"pid": original["pid"], "projects": results}


def error_message(exc):
    nested = getattr(exc, "exceptions", None)
    if nested:
        return "\n".join(error_message(item) for item in nested)
    return str(exc)


def fingerprint(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", action="store_true", help="Only check the live MCP connection.")
    parser.add_argument("--project", action="append", default=[], help="An .spp path; repeat for a batch.")
    parser.add_argument("--folder", help="Find .spp projects in this directory.")
    parser.add_argument("--recursive", action="store_true", help="Include subdirectories.")
    parser.add_argument("--dry-run", action="store_true", help="List output files without exporting.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing texture files.")
    parser.add_argument("--expected-pid", type=int, help="Require this exact dedicated worker PID.")
    args = parser.parse_args()
    try:
        result = asyncio.run(run(args))
    except Exception as exc:
        parser.exit(1, "{}\n".format(error_message(exc)))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
