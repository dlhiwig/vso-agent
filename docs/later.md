# Later / not now

Items that belong on a checklist, not in the running stack.

## OpenClaw / MCP adapter

Not required for v0. Posts can run the CLI as-is:

```bash
python -m src.cli assemble path/to/case.json --cite
python -m src.cli retrieve "question"
```

If a post later wants this beside an existing agent runtime, the adapter would only wrap those two commands. It must not file claims, hold VA credentials, or talk to VBMS.

Status: **parked**. Do not build on standby.

## Other parked items

- Cloud multi-tenant hosting of veteran packets
- Auto-fill of official VA PDFs
- Any submit / QuickSubmit integration
