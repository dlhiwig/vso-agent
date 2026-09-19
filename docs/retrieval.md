# Public-source retrieval

The agent searches a **curated corpus** of public pages:

- 38 CFR excerpts (official eCFR URL recorded; LII used as a readable reprint when eCFR blocks automated fetch)
- VA.gov fact sheets: evidence, eligibility, filing, Fully Developed Claims, PACT Act, intent to file
- Musculoskeletal schedule excerpts (§§ 4.40, 4.59, 4.71a knees/spine)
- M21-1 public KnowVA excerpts (prologue, auditory, lay evidence). Statute and regulation still control.
- VFW National Veterans Service claims-assistance page

It does **not** search VBMS, CAPRI, or any authenticated VA system.

## Run

```bash
python -m src.cli retrieve "tinnitus hearing loss artillery MOS"
python -m src.cli retrieve "PACT Act burn pit sinusitis"
python -m src.cli retrieve "painful motion knee 4.59"
python -m src.cli assemble examples/sample-case.json --cite -o packets/sample.md
```

`--cite` without a query uses the condition names on the case file.

## Refresh

Live fetch is allowlisted (`va.gov`, `ecfr.gov`, `law.cornell.edu`, `knowva.ebenefits.va.gov`, `vfw.org`, `govinfo.gov`, `publichealth.va.gov`).

```bash
python -m src.cli refresh-corpus --source va-pact-act
```

Writes `corpus/.cache/`. Cached live pages are gitignored. Seed snapshots stay in `corpus/snapshots/` so offline search still works.

eCFR often redirects automated clients. Prefer the checked-in snapshot and open `official_url` in a browser to verify.

## Rules

- Retrieval is decision support for an accredited VSO, not a rating.
- Always quote the official URL in any packet appendix.
- 38 U.S.C. / 38 CFR beat M21-1 when they conflict (M21-1 prologue).
- Presumptive lists change. Re-open the live VA page before telling a veteran a condition is presumptive.
- Expand the manifest instead of scraping the open web.
