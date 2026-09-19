# VSO Agent

Open-source AI copilot for **Veteran Service Officers** supporting VFW posts and accredited claims work.

The agent drafts, organizes, and checks completeness. **Accredited humans review, correct, and file.** The agent never files a claim and never acts as a VA-accredited representative.

> Not affiliated with, endorsed by, or an official product of the Veterans of Foreign Wars of the United States or the U.S. Department of Veterans Affairs.

## Purpose

Help VSOs at VFW posts:

- Intake a veteran conversation and produce a structured case brief
- Map stated issues to common benefit pathways (compensation, pension, DIC, healthcare enrollment, education, home loan, burial)
- Assemble a review packet: cover sheet, evidence index, condition sheets, draft narrative
- Hand that packet to the accredited VSO for review and official filing

## Packet assembler

Deterministic. No model required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.cli assemble examples/sample-case.json -o examples/packets/sample-packet.md
```

Input: `examples/sample-case.json`  
Output: cover sheet + numbered evidence index + per-condition sheets + 21-4138-style draft narrative + VSO handoff.

Rendered sample: [examples/packets/sample-packet.md](examples/packets/sample-packet.md)  
How it works: [docs/packet-assembler.md](docs/packet-assembler.md)

The assembler does not fill official VA PDFs and does not submit to VA.gov, VBMS, or QuickSubmit. Every packet is headed `DRAFT — VSO REVIEW REQUIRED`.

## Hard rules

1. The agent does **not** file with VA.gov, VBMS, or any claims system.
2. The agent does **not** guarantee ratings, awards, or timelines.
3. The agent does **not** invent buddy statements, diagnoses, or duty events.
4. Fraudulent or fabricated evidence is refused and flagged.
5. Every draft is labeled `DRAFT — VSO REVIEW REQUIRED`.
6. Official representation remains with a VA-accredited VSO, agent, or attorney.

Find accredited reps: [VA OGC accreditation search](https://www.va.gov/ogc/apps/accreditation/).  
Find VFW National Veterans Service: [vfw.org](https://www.vfw.org/).

## Layout

```
agents/           system prompt
src/packet.py     cover sheet / index / narrative assembler
src/cli.py        chat + assemble commands
docs/             operating model and packet notes
examples/         synthetic case JSON and rendered packet
```

## Chat copilot (optional)

```bash
cp .env.example .env
python -m src.cli chat "Veteran reports bilateral tinnitus after 12 years as a 13B. Build a VFW VSO brief."
```

Point `VSO_AGENT_MODEL` at a local Ollama model or any OpenAI-compatible endpoint.

## Next

1. Retrieval over public VA policy sources (38 CFR excerpts, M21-1 public pages, VA benefit fact sheets).
2. OpenClaw / MCP adapter so post VSOs can run this beside existing agent stacks.
3. Post-level playbook: appointment prep, volunteer VSO checklist, handoff to Department Service Officer.

## License

MIT. See [LICENSE](LICENSE).
