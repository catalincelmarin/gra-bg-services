# Kimera Common – Agent Navigation Guide

Welcome! This repository ships module-level documentation under `docs/` that mirrors the Python package layout in `src/`. Use this guide to quickly locate the information you need when extending or integrating Kimera components.

## How to Use These Docs
- Treat every import path as `kimera.<module>` as shown below; the Markdown file lives at `docs/<module>.md` (dots become `/`).
- Start with package overviews (`__init__.md` files) to understand responsibilities, then read the module files for class/method details.
- When adding features, update the matching Markdown so future agents can follow the change.

## Directory Map
The table below lists every documentation file and the Python module it describes. Relative paths are from `docs/`.

| Module / Package | Doc Path |
| --- | --- |
| *(root package marker)* | `__init__.md` |
| `kimera` | `kimera/__init__.md` |
| `kimera.Bootstrap` | `kimera/Bootstrap.md` |
| `kimera.auth` | `kimera/auth/__init__.md` |
| `kimera.auth.CanonicalAuthRepo` | `kimera/auth/CanonicalAuthRepo.md` |
| `kimera.comm` | `kimera/comm/__init__.md` |
| `kimera.comm.BaseAuth` | `kimera/comm/BaseAuth.md` |
| `kimera.comm.FastApiWrapper` | `kimera/comm/FastApiWrapper.md` |
| `kimera.comm.Intercom` | `kimera/comm/Intercom.md` |
| `kimera.comm.JWTAuth` | `kimera/comm/JWTAuth.md` |
| `kimera.comm.PubSub` | `kimera/comm/PubSub.md` |
| `kimera.db` | `kimera/db/__init__.md` |
| `kimera.db.Database` | `kimera/db/Database.md` |
| `kimera.db.DBFactory` | `kimera/db/DBFactory.md` |
| `kimera.db.MongoDoc` | `kimera/db/MongoDoc.md` |
| `kimera.db.BaseRepo` | `kimera/db/BaseRepo.md` |
| `kimera.db.ResourceRepo` | `kimera/db/ResourceRepo.md` |
| `kimera.db.AutoWireRepo` | `kimera/db/AutoWireRepo.md` |
| `kimera.dev` | `kimera/dev/__init__.md` |
| `kimera.dev.GitManager` | `kimera/dev/GitManager.md` |
| `kimera.dev.Loggers` | `kimera/dev/Loggers.md` |
| `kimera.dxs` | `kimera/dxs/__init__.md` |
| `kimera.dxs.BaseDXS` | `kimera/dxs/BaseDXS.md` |
| `kimera.dxs.CommonDXS` | `kimera/dxs/CommonDXS.md` |
| `kimera.dxs.ResourceDXS` | `kimera/dxs/ResourceDXS.md` |
| `kimera.helpers` | `kimera/helpers/__init__.md` |
| `kimera.helpers.Helpers` | `kimera/helpers/Helpers.md` |
| `kimera.helpers.Hook` | `kimera/helpers/Hook.md` |
| `kimera.helpers.Auth` | `kimera/helpers/Auth.md` |
| `kimera.helpers.TextExtractors` | `kimera/helpers/TextExtractors.md` |
| `kimera.helpers.DataMapper` | `kimera/helpers/DataMapper.md` |
| `kimera.mcp` | `kimera/mcp/__init__.md` |
| `kimera.mcp.BaseMCP` | `kimera/mcp/BaseMCP.md` |
| `kimera.mcp.CommonMCP` | `kimera/mcp/CommonMCP.md` |
| `kimera.mcp.MCPHelpers` | `kimera/mcp/MCPHelpers.md` |
| `kimera.mcp.types` | `kimera/mcp/types.md` |
| `kimera.process` | `kimera/process/__init__.md` |
| `kimera.process.Spawner` | `kimera/process/Spawner.md` |
| `kimera.process.ThreadKraken` | `kimera/process/ThreadKraken.md` |
| `kimera.process.TaskManager` | `kimera/process/TaskManager.md` |
| `kimera.smBots` | `kimera/smBots/__init__.md` |
| `kimera.smBots.HotDisc` | `kimera/smBots/HotDisc.md` |
| `kimera.store` | `kimera/store/__init__.md` |
| `kimera.store.Store` | `kimera/store/Store.md` |
| `kimera.store.StoreFactory` | `kimera/store/StoreFactory.md` |
| `kimera.store.BaseRepo` | `kimera/store/BaseRepo.md` |
| `kimera.store.BaseDocument` | `kimera/store/BaseDocument.md` |
| `kimera.store.AutoRepo` | `kimera/store/AutoRepo.md` |
| `kimera.store.AutoWireRepo` | `kimera/store/AutoWireRepo.md` |
| `kimera.store.ResourceRepo` | `kimera/store/ResourceRepo.md` |
| `kimera.store.VectorStore` | `kimera/store/VectorStore.md` |
| `kimera.store.FileStore` | `kimera/store/FileStore.md` |
| `kimera.store.MemStore` | `kimera/store/MemStore.md` |
| `kimera.store.ElasticStore` | `kimera/store/ElasticStore.md` |
| `kimera.store.DummyStore` | `kimera/store/DummyStore.md` |
| `kimera.helpers` *(root)* | `kimera/helpers/__init__.md` |
| `kimera.dev` *(root)* | `kimera/dev/__init__.md` |
| `kimera.dxs` *(root)* | `kimera/dxs/__init__.md` |
| `kimera.process` *(root)* | `kimera/process/__init__.md` |
| `kimera.smBots` *(root)* | `kimera/smBots/__init__.md` |

> Need another module? Mirror the structure: create the Python file in `src/kimera/...`, then add the corresponding Markdown under `docs/kimera/...`.

## Tips for Agents
- **Finding usage**: grep the codebase for the import path (e.g., `rg "from kimera.comm.FastApiWrapper"`). Once you understand behaviour, record your changes in the matching doc.
- **Extending services**: Read `kimera/Bootstrap.md` to understand the boot sequence before wiring new stores or routes.
- **Adding APIs**: Update the relevant YAML and read `kimera/comm/FastApiWrapper.md` to see how routes are loaded and authenticated.
- **Background work**: Consult the process docs when dealing with Celery (`kimera/process/TaskManager.md`) or threaded workers (`kimera/process/ThreadKraken.md`).

Happy hacking!
