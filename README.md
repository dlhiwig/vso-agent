# VSO Agent

Open-source AI copilot for **Veteran Service Officers** supporting VFW posts and accredited claims work.

The agent drafts, organizes, and checks completeness. **Accredited humans review, correct, and file.** The agent never files a claim and never acts as a VA-accredited representative.

> Not affiliated with, endorsed by, or an official product of the Veterans of Foreign Wars of the United States or the U.S. Department of Veterans Affairs.

## Purpose (v0)

Help VSOs at VFW posts:

- Intake a veteran conversation and produce a structured case brief
- Map stated issues to common benefit pathways (compensation, pension, DIC, healthcare enrollment, education, home loan, burial)
- Build an evidence checklist and missing-document list
- Draft interview questions, buddy-statement prompts, and decision-letter summaries
- Hand a clean packet to the accredited VSO for review and official filing

## Hard rules

1. The agent does **not** file with VA.gov, VBMS, or any claims system.
2. The agent does **not** guarantee ratings, awards, or timelines.
3. The agent does **not** invent buddy statements, diagnoses, or duty events.
4. Fraudulent or fabricated evidence is refused and flagged.
5. Every draft is labeled `DRAFT — VSO REVIEW REQUIRED`.
6. Official representation remains with a VA-accredited VSO, agent, or attorney.

Find accredited reps: [VA OGC accreditation search](https://www.va.gov/ogc/apps/accreditation/).
Find VFW National Veterans Service: [vfw.org](https://www.vfw.org/).

## Status

Public scaffold. First slice is a VFW-post VSO copilot, not a veteran-facing claims chatbot.

## Layout

```
agents/          system prompt and tool contracts
src/             reference CLI / local runner
docs/            operating model and legal posture
examples/        sample intake (synthetic, non-PII)
```

## Local run (reference CLI)

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m src.cli "Veteran reports bilateral tinnitus and hearing loss after 12 years as a 13B. Wants a VFW VSO packet."
```

Point `VSO_AGENT_MODEL` at a local Ollama model or any OpenAI-compatible endpoint. Default is local-first.

## Next

1. Wire retrieval over public VA policy sources (38 CFR excerpts, M21-1 public pages, VA benefit fact sheets).
2. Add a packet assembler (cover sheet, evidence index, draft 21-526EZ narrative — still draft-only).
3. Optional OpenClaw / MCP adapter so post VSOs can run this beside existing agent stacks.
4. Post-level playbook: appointment prep, volunteer VSO checklist, handoff to Department Service Officer.

## License

MIT. See [LICENSE](LICENSE).
