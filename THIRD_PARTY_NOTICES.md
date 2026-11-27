# Third-party notices

SubstancePainter-MCP 1.0.0 is a maintained fork combining:

- [parodyband/painter-mcp](https://github.com/parodyband/painter-mcp), version 1.1.0, revision `b7ef175de3a369b5ff01b2a639d9109e43d24d15`. Main-thread bridge, operation catalog, engine, request broker, transport, state, client and adapted tests. MIT license: `licenses/PainterMCP-MIT.txt`.
- [elliezu/SubstancePainterMCP](https://github.com/elliezu/SubstancePainterMCP), version 1.0.0, revision `e382927cc1a3ea7d4bd6e48d28403d339a4613df`. Vendored workflow implementation, generated wrappers and schemas. MIT license: `licenses/SubstancePainterMCP-MIT.txt`.

Adaptations: renamed package, local workflow transport instead of fixed-port HTTP, isolated callback globals, combined catalog, dedicated mesh-map exporter, independent installer and worker launcher. Workflow baking no longer rejects non-UDIM texture sets for having an empty tile list. Upstream update/download/activation code is omitted to keep upstream releases from replacing the fork.

Adobe Substance 3D Painter and its Python/JavaScript APIs are supplied by the user's installed Adobe software and are not redistributed.
