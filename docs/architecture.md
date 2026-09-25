# Architecture

Small local tool. No VA credentials. No submit path.

```
intake JSON  →  src.packet.assemble()  →  Markdown packet
                     ↑
               optional --cite
                     ↑
         src.retrieve.search(corpus/)
```

## Layout

| Path | Role |
| --- | --- |
| `src/cli.py` | argparse: `assemble`, `retrieve`, `chat`, `refresh-corpus` |
| `src/packet.py` | deterministic cover / index / narrative |
| `src/retrieve.py` | lexical search over `corpus/snapshots` |
| `src/paths.py` | repo-root paths |
| `agents/SYSTEM.md` | chat-only persona |
| `corpus/manifest.json` | catalog + official URLs |
| `examples/sample-case.json` | synthetic intake |
| `examples/case.schema.json` | field contract |
| `tests/` | stdlib unittest |

## Rules that shape the code

- Assemble and retrieve have **zero required third-party packages**.
- Chat is optional (`pip install -e '.[chat]'`).
- Real veteran files stay out of git (`packets/` is gitignored).
- Retrieval never leaves the allowlist in `src/retrieve.py`.
