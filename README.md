# VSO Agent

Open-source AI copilot for **Veteran Service Officers** supporting VFW posts and accredited claims work.

The agent drafts, organizes, and checks completeness. **Accredited humans review, correct, and file.** The agent never files a claim and never acts as a VA-accredited representative.

> Not affiliated with, endorsed by, or an official product of the Veterans of Foreign Wars of the United States or the U.S. Department of Veterans Affairs.

## Purpose

Help VSOs at VFW posts:

- Intake a veteran conversation and produce a structured case brief
- Map stated issues to common benefit pathways (compensation, pension, DIC, healthcare enrollment, education, home loan, burial)
- Assemble a review packet: cover sheet, evidence index, condition sheets, draft narrative
- Retrieve public VA / 38 CFR / VFW excerpts with official URLs
- Hand that packet to the accredited VSO for review and official filing

## Packet assembler

Deterministic. No model required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.cli assemble examples/sample-case.json -o examples/packets/sample-packet.md
```

Rendered sample: [examples/packets/sample-packet.md](examples/packets/sample-packet.md)  
How it works: [docs/packet-assembler.md](docs/packet-assembler.md)

## Public-source retrieval

```bash
python -m src.cli retrieve "tinnitus hearing loss artillery MOS"
python -m src.cli assemble examples/sample-case.json --cite
```

Curated snapshots live in `corpus/snapshots/`. Official URLs are recorded even when the readable reprint is LII. Live refresh is allowlisted and optional (`python -m src.cli refresh-corpus`).

See [docs/retrieval.md](docs/retrieval.md) and [examples/retrieval-tinnitus.md](examples/retrieval-tinnitus.md).

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
src/retrieve.py   public-source search
src/cli.py        chat + assemble + retrieve
docs/             operating model, packet, retrieval
corpus/           public VA/CFR/VFW snapshots + manifest
examples/         synthetic case JSON, packet, retrieval sample
```

## Chat copilot (optional)

```bash
cp .env.example .env
python -m src.cli chat "Veteran reports bilateral tinnitus after 12 years as a 13B. Build a VFW VSO brief."
```

Point `VSO_AGENT_MODEL` at a local Ollama model or any OpenAI-compatible endpoint.

## Next

1. OpenClaw / MCP adapter so post VSOs can run this beside existing agent stacks.
2. Post-level playbook: appointment prep, volunteer VSO checklist, handoff to Department Service Officer.
3. Grow the corpus (more M21-1 public articles, 38 CFR musculoskeletal, PACT Act fact sheets).

## License

MIT. See [LICENSE](LICENSE).
