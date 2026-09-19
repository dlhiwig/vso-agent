# VFW post playbook

How a post uses VSO Agent without confusing it for accredited representation.

## Roles

| Role | Does | Does not |
| --- | --- | --- |
| Post volunteer / intake | Collects facts, runs assemble/retrieve, prints the draft packet | File with VA, sign 21-22 as the organization unless accredited and authorized |
| Accredited VSO | Reviews packet, corrects issues, obtains 21-22, files | Rely on the agent as a nexus opinion |
| Department Service Officer | Takes complex, denied, or remand cases | Need the draft packet to be perfect |

Find accredited people: [VA OGC search](https://www.va.gov/ogc/apps/accreditation/).

## Appointment prep (day before / walk-in)

1. Confirm the veteran wants VFW assistance. Do not pressure membership as a condition of help.
2. Ask only what the packet needs: service dates/MOS if known, conditions in the veteran's words, what documents they already have.
3. Do not write down a full SSN. File number last-4 only if they already have one.
4. Copy `examples/sample-case.json` to a local case file that never gets committed.
5. Mark each document `have` / `requested` / `missing` / `va-to-obtain`.
6. Mark hypothesized issues as `hypothesized`. Do not list a specific diagnosis the veteran does not have.
7. Run:

```bash
python -m src.cli assemble local-case.json --cite -o packets/ready.md
```

8. Print or save the markdown. Hand it to the accredited VSO with the paper documents.

## Volunteer VSO checklist

- [ ] 21-22 discussed; veteran understands POA
- [ ] Conditions on the cover sheet match what the veteran wants claimed
- [ ] No invented buddy statements
- [ ] DD-214 or other separation document in hand or requested
- [ ] Private records: have them, or 21-4142 ready
- [ ] Packet still says `DRAFT — VSO REVIEW REQUIRED`
- [ ] File-ready flag on the cover is honest (gaps remain if they remain)
- [ ] Accredited officer — not the volunteer and not the software — will file

## Handoff to Department Service Officer

Send the DSO when any of these are true:

- Prior denial or Statement of the Case / Board remand
- Character of discharge is not honorable / needs COD review
- IU, SMC, or 1151
- Contested claim, fiduciary, or suspected fraud
- The post VSO is not accredited for the work in front of them

Include: draft packet, document list, and a one-paragraph ask ("review nexus on hearing loss; knees are hypothesized only").

## What the post must not do

- Charge a fee or a percentage of back pay
- Let the agent "just file it"
- Paste a generated buddy letter over someone else's name
- Store SSNs in the git repo or a shared chat log
