"""Serve, install, repair or diagnose SubstancePainter-MCP."""

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .client import Client
from .common import Fault, connection_path


def main():
    parser = argparse.ArgumentParser(prog="SubstancePainter-MCP")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("serve", help="Run the MCP stdio server")
    for action in ("install", "repair"):
        setup = commands.add_parser(action, help="Install or repair this fork's Painter plugin")
        setup.add_argument("--painter-python", type=Path)
        setup.add_argument("--replace-edited", action="store_true")
    commands.add_parser("uninstall", help="Remove unchanged managed plugin files")
    doctor = commands.add_parser("doctor", help="Read connection health without printing credentials")
    doctor.add_argument("--connection", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "serve":
            from .server import main as serve
            serve()
            return
        if args.command in ("install", "repair"):
            from .install import install
            result = install(args.painter_python, args.replace_edited)
        elif args.command == "uninstall":
            from .install import uninstall
            result = uninstall()
        else:
            result = {"connected": True, "connection_file": str(args.connection or connection_path()),
                      **Client(args.connection).health()}
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if result.get("installed") is False:
            raise SystemExit(2)
    except (Fault, OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        error = exc.json() if isinstance(exc, Fault) else {"code": "SETUP_ERROR", "message": str(exc)}
        print(json.dumps({"ok": False, "error": error}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
