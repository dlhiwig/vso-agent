# Operating model

## Who this is for

Primary user: a VA-accredited VSO or a VFW post volunteer preparing work for an accredited officer.

Not the primary user: a veteran filing alone. Point those veterans to a VFW or county VSO.

## Why VFW first

VFW National Veterans Service already runs a nationwide accredited network. Post-level officers and volunteers need a fast way to:

- prepare the veteran before the official appointment
- keep evidence organized
- reduce time-per-claim without removing human accreditation

## Chain of custody

```
Veteran conversation
        ↓
VSO Agent draft packet
        ↓
Accredited VSO review / correction
        ↓
Official filing (VBMS / VA.gov / paper) by the accredited human only
```

The model never receives filing credentials and never calls a submit API.

## Data handling

- Prefer local models (Ollama) when packets contain veteran details.
- Do not commit real intake files. `examples/` is synthetic only.
- Strip SSNs and account numbers before any cloud model call.

## Legal posture

This software is a drafting aid. It is not legal advice, not VA accreditation, and not a VFW official tool.
Unaccredited paid claims shops are a known risk; this project does not charge veterans a percentage of benefits and does not contact VA on a veteran's behalf.
