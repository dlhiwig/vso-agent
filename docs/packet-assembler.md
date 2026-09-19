# Packet assembler

Turns a structured case JSON file into a VSO review packet:

1. Cover sheet
2. Evidence index + forms checklist
3. Condition sheets
4. Draft narrative (21-4138 starting language)
5. Handoff notes for the accredited VSO

The assembler does **not** fill official VA PDFs and does **not** submit anything.

## Case file

See `examples/sample-case.json`.

Required shape:

```json
{
  "claim_action": "Original compensation claim",
  "veteran": { "name": "...", "branch": "..." },
  "conditions": [{ "name": "...", "claim_type": "original" }],
  "evidence": [{ "title": "DD-214", "status": "missing", "supports": ["all"] }]
}
```

`claim_type`: `original` | `increase` | `new-condition` | `secondary` | `supplemental` | `hltlr` | `other`

Evidence `status`: `have` | `requested` | `missing` | `va-to-obtain` | `not-applicable`

Do not put a Social Security number in the case file. Use `va_file_hint` only if the VSO already has a file number.

## Run

```bash
python -m src.cli assemble examples/sample-case.json -o examples/packets/sample-packet.md
```

Deterministic. No model required.

## What the VSO still does

- Confirms every condition name that will appear on 21-526EZ
- Obtains 21-22 POA
- Decides Fully Developed Claim vs standard process
- Writes or accepts statements; never files invented buddy letters
- Files in VBMS / VA.gov
