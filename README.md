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

See [docs/retrieval.md](docs/retrieval.md).

## Post playbook

Appointment prep, volunteer checklist, and DSO handoff: [docs/post-playbook.md](docs/post-playbook.md).

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
docs/             operating model, packet, retrieval, post playbook
corpus/           public VA/CFR/VFW snapshots + manifest
examples/         synthetic case JSON, packet, retrieval sample
```

## Chat copilot (optional)

```bash
cp .env.example .env
python -m src.cli chat "Veteran reports bilateral tinnitus after 12 years as a 13B. Build a VFW VSO brief."
```

## Later (not standby)

OpenClaw / MCP is a checklist item only. See [docs/later.md](docs/later.md).

Still useful when you want it: grow the public corpus (more M21-1 articles, musculoskeletal schedule, PACT Act fact sheets).

## License

MIT. See [LICENSE](LICENSE).
