"""Assemble a VSO review packet from a structured case file.

Output is draft-only. It is not a VA form and is not filed by this tool.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

DRAFT_BANNER = "DRAFT — VSO REVIEW REQUIRED"
DISCLAIMER = (
    "This packet is a drafting aid for an accredited Veteran Service Officer. "
    "It is not a VA form, not a medical opinion, and not a filing. "
    "An accredited human must review, correct, and file. "
    "Not affiliated with VFW or VA."
)

VALID_EVIDENCE_STATUS = {
    "have",
    "requested",
    "missing",
    "va-to-obtain",
    "not-applicable",
}

VALID_CLAIM_TYPES = {
    "original",
    "increase",
    "new-condition",
    "secondary",
    "supplemental",
    "hltlr",
    "other",
}

CORE_FORMS = [
    ("21-22", "Appointment of Veterans Service Organization (POA)"),
    ("21-526EZ", "Application for Disability Compensation and Related Compensation Benefits"),
    ("21-4138", "Statement in Support of Claim (or equivalent personal statement)"),
    ("21-4142 / 21-4142a", "Authorization to Disclose Information / private records"),
    ("21-10210", "Lay/Witness Statement (buddy statement), if used"),
]


class PacketError(ValueError):
    pass


@dataclass
class Veteran:
    name: str = "UNKNOWN"
    preferred_name: str = ""
    branch: str = "UNKNOWN"
    component: str = "UNKNOWN"
    mos: str = "UNKNOWN"
    service_start: str = "UNKNOWN"
    service_end: str = "UNKNOWN"
    character_of_discharge: str = "UNKNOWN"
    current_combined_rating: str = "UNKNOWN"
    va_file_hint: str = "UNKNOWN"  # never store a full SSN
    contact: str = "UNKNOWN"
    post: str = "UNKNOWN"

    @property
    def display_name(self) -> str:
        return self.preferred_name or self.name


@dataclass
class Condition:
    name: str
    claim_type: str = "original"
    status: str = "veteran-reported"  # veteran-reported | diagnosed | hypothesized
    onset: str = "UNKNOWN"
    in_service_event: str = "UNKNOWN"
    current_impact: str = "UNKNOWN"
    secondary_to: str = ""
    notes: str = ""


@dataclass
class EvidenceItem:
    title: str
    status: str = "missing"
    supports: list[str] = field(default_factory=list)
    date: str = ""
    pages: str = ""
    source: str = ""
    notes: str = ""


@dataclass
class Case:
    veteran: Veteran
    conditions: list[Condition]
    evidence: list[EvidenceItem]
    claim_action: str = "original compensation claim"
    intake_source: str = ""
    extra_notes: str = ""
    prepared_for: str = "Accredited VFW VSO"
    prepared_by: str = "VSO Agent (draft)"
    prepared_on: str = ""

    def __post_init__(self) -> None:
        if not self.prepared_on:
            self.prepared_on = date.today().isoformat()


def _require(mapping: dict[str, Any], key: str, default: Any = None) -> Any:
    if key in mapping:
        return mapping[key]
    if default is not None:
        return default
    raise PacketError(f"Missing required field: {key}")


def load_case(path: Path) -> Case:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return case_from_dict(raw)


def case_from_dict(raw: dict[str, Any]) -> Case:
    vraw = _require(raw, "veteran", {})
    veteran = Veteran(
        name=str(vraw.get("name") or "UNKNOWN"),
        preferred_name=str(vraw.get("preferred_name") or ""),
        branch=str(vraw.get("branch") or "UNKNOWN"),
        component=str(vraw.get("component") or "UNKNOWN"),
        mos=str(vraw.get("mos") or "UNKNOWN"),
        service_start=str(vraw.get("service_start") or "UNKNOWN"),
        service_end=str(vraw.get("service_end") or "UNKNOWN"),
        character_of_discharge=str(vraw.get("character_of_discharge") or "UNKNOWN"),
        current_combined_rating=str(vraw.get("current_combined_rating") or "UNKNOWN"),
        va_file_hint=str(vraw.get("va_file_hint") or "UNKNOWN"),
        contact=str(vraw.get("contact") or "UNKNOWN"),
        post=str(vraw.get("post") or "UNKNOWN"),
    )
    conditions: list[Condition] = []
    for item in raw.get("conditions") or []:
        claim_type = str(item.get("claim_type") or "original").lower()
        if claim_type not in VALID_CLAIM_TYPES:
            raise PacketError(f"Invalid claim_type: {claim_type}")
        name = str(item.get("name") or "").strip()
        if not name:
            raise PacketError("Each condition needs a name")
        conditions.append(
            Condition(
                name=name,
                claim_type=claim_type,
                status=str(item.get("status") or "veteran-reported"),
                onset=str(item.get("onset") or "UNKNOWN"),
                in_service_event=str(item.get("in_service_event") or "UNKNOWN"),
                current_impact=str(item.get("current_impact") or "UNKNOWN"),
                secondary_to=str(item.get("secondary_to") or ""),
                notes=str(item.get("notes") or ""),
            )
        )
    evidence: list[EvidenceItem] = []
    for item in raw.get("evidence") or []:
        status = str(item.get("status") or "missing").lower()
        if status not in VALID_EVIDENCE_STATUS:
            raise PacketError(f"Invalid evidence status: {status}")
        title = str(item.get("title") or "").strip()
        if not title:
            raise PacketError("Each evidence item needs a title")
        supports = item.get("supports") or []
        if isinstance(supports, str):
            supports = [supports]
        evidence.append(
            EvidenceItem(
                title=title,
                status=status,
                supports=[str(s) for s in supports],
                date=str(item.get("date") or ""),
                pages=str(item.get("pages") or ""),
                source=str(item.get("source") or ""),
                notes=str(item.get("notes") or ""),
            )
        )
    if not conditions:
        raise PacketError("Case must include at least one condition")
    return Case(
        veteran=veteran,
        conditions=conditions,
        evidence=evidence,
        claim_action=str(raw.get("claim_action") or "original compensation claim"),
        intake_source=str(raw.get("intake_source") or ""),
        extra_notes=str(raw.get("extra_notes") or ""),
        prepared_for=str(raw.get("prepared_for") or "Accredited VFW VSO"),
        prepared_by=str(raw.get("prepared_by") or "VSO Agent (draft)"),
        prepared_on=str(raw.get("prepared_on") or ""),
    )


def readiness(case: Case) -> dict[str, Any]:
    counts = {key: 0 for key in VALID_EVIDENCE_STATUS}
    for item in case.evidence:
        counts[item.status] += 1
    total = len(case.evidence)
    have = counts["have"]
    blocking = counts["missing"] + counts["requested"]
    score = 0 if total == 0 else round(100 * have / total)
    if any(c.status == "hypothesized" for c in case.conditions):
        note = "One or more issues are hypothesized — confirm wording with the veteran before listing on 21-526EZ."
    else:
        note = ""
    return {
        "score": score,
        "total": total,
        "have": have,
        "blocking": blocking,
        "counts": counts,
        "note": note,
        "file_ready": blocking == 0 and total > 0 and not any(
            c.status == "hypothesized" for c in case.conditions
        ),
    }


def _md_cell(value: str) -> str:
    return (value or "").replace("|", "\\|").replace("\n", " ")


def render_cover(case: Case) -> str:
    v = case.veteran
    ready = readiness(case)
    issues = ", ".join(c.name for c in case.conditions) or "UNKNOWN"
    file_line = (
        "READY FOR ACCREDITED VSO FILING REVIEW"
        if ready["file_ready"]
        else "NOT FILE-READY — gaps remain"
    )
    lines = [
        f"# {DRAFT_BANNER}",
        "",
        "## Cover sheet",
        "",
        f"- **Prepared for:** {case.prepared_for}",
        f"- **Prepared by:** {case.prepared_by}",
        f"- **Date:** {case.prepared_on}",
        f"- **VFW post / office:** {v.post}",
        f"- **Packet status:** {file_line}",
        f"- **Evidence completeness:** {ready['score']}% on file ({ready['have']}/{ready['total']}; {ready['blocking']} blocking)",
        "",
        "### Veteran (minimum identifiers — no SSN in this file)",
        "",
        f"- **Name:** {v.name}",
        f"- **Branch / component:** {v.branch} / {v.component}",
        f"- **MOS:** {v.mos}",
        f"- **Service:** {v.service_start} – {v.service_end}",
        f"- **Character of discharge:** {v.character_of_discharge}",
        f"- **Current combined rating:** {v.current_combined_rating}",
        f"- **VA file hint:** {v.va_file_hint}",
        f"- **Contact:** {v.contact}",
        "",
        "### Requested action",
        "",
        f"- {case.claim_action}",
        f"- **Issues listed:** {issues}",
        "",
        "> " + DISCLAIMER,
    ]
    if case.intake_source:
        lines.extend(["", f"- **Intake source:** {case.intake_source}"])
    if ready["note"]:
        lines.extend(["", f"> {ready['note']}"])
    return "\n".join(lines) + "\n"


def render_evidence_index(case: Case) -> str:
    lines = [
        "## Evidence index",
        "",
        "Numbered list for the packet. Status values: `have` | `requested` | `missing` | `va-to-obtain` | `not-applicable`.",
        "",
        "| # | Document | Status | Date | Pages | Supports | Source / notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not case.evidence:
        lines.append("| — | *No evidence catalogued yet* | missing |  |  |  | Add items before VSO appointment |")
    else:
        for i, item in enumerate(case.evidence, start=1):
            supports = ", ".join(item.supports) if item.supports else "—"
            note = " — ".join(p for p in (item.source, item.notes) if p)
            lines.append(
                "| {num} | {title} | `{status}` | {date} | {pages} | {supports} | {note} |".format(
                    num=i,
                    title=_md_cell(item.title),
                    status=item.status,
                    date=_md_cell(item.date),
                    pages=_md_cell(item.pages),
                    supports=_md_cell(supports),
                    note=_md_cell(note),
                )
            )
    lines.extend(["", "### Forms checklist (VSO completes / confirms)", ""])
    for form, label in CORE_FORMS:
        lines.append(f"- [ ] **VA Form {form}** — {label}")
    lines.append("- [ ] DD-214 Member-4 or other separation document")
    lines.append("- [ ] Service treatment records (or VA request)")
    return "\n".join(lines) + "\n"


def render_condition_sheets(case: Case) -> str:
    lines = ["## Condition sheets", ""]
    for cond in case.conditions:
        related = [
            item
            for item in case.evidence
            if not item.supports or cond.name.lower() in {s.lower() for s in item.supports} or "all" in {s.lower() for s in item.supports}
        ]
        lines.extend(
            [
                f"### {cond.name}",
                "",
                f"- **Claim type:** {cond.claim_type}",
                f"- **Fact status:** {cond.status} *(veteran-reported vs diagnosed vs hypothesized)*",
                f"- **Onset / first noticed:** {cond.onset}",
                f"- **In-service event / exposure (as stated):** {cond.in_service_event}",
                f"- **Current functional impact (as stated):** {cond.current_impact}",
            ]
        )
        if cond.secondary_to:
            lines.append(f"- **Claimed as secondary to:** {cond.secondary_to}")
        if cond.notes:
            lines.append(f"- **Notes:** {cond.notes}")
        lines.extend(["", "Evidence mapped to this issue:", ""])
        if not related:
            lines.append("- *None mapped — add evidence or mark gaps.*")
        else:
            for item in related:
                lines.append(f"- `{item.status}` {item.title}")
        lines.append("")
        lines.append(
            "Nexus / link: **not asserted by this agent.** VSO determines whether medical evidence, presumption, or a nexus opinion is required."
        )
        lines.append("")
    return "\n".join(lines)


def _unknown(value: str) -> bool:
    return not value or value.strip().upper() in {"UNKNOWN", "N/A", "NA", ""}


def render_narrative(case: Case) -> str:
    v = case.veteran
    who = v.display_name
    lines = [
        "## Draft narrative",
        "",
        "Use as a starting point for VA Form 21-4138 / personal statement language. ",
        "Write only from facts in the case file. Brackets mark gaps the veteran or VSO must fill.",
        "",
        f"### Statement of {who} (draft)",
        "",
        f"I am {v.name}, a veteran of the {v.branch}",
    ]
    service = []
    if not _unknown(v.component):
        service.append(v.component)
    if not _unknown(v.mos):
        service.append(f"MOS {v.mos}")
    dates = []
    if not _unknown(v.service_start):
        dates.append(v.service_start)
    if not _unknown(v.service_end):
        dates.append(v.service_end)
    svc = ""
    if service:
        svc += f" ({', '.join(service)})"
    if dates:
        svc += f", {dates[0]}" + (f" to {dates[1]}" if len(dates) == 2 else "")
    lines[7] = f"I am {v.name}, a veteran of the {v.branch}{svc}."
    if not _unknown(v.character_of_discharge):
        lines.append(f"My character of discharge is {v.character_of_discharge}.")
    if not _unknown(v.current_combined_rating) and v.current_combined_rating not in {"0", "none", "None"}:
        lines.append(f"My current combined VA disability rating is {v.current_combined_rating}.")
    else:
        lines.append("I have not previously been awarded VA disability compensation, or my current rating is unknown to this draft.")
    lines.append("")
    lines.append(f"I am requesting assistance from a VFW accredited representative with the following action: {case.claim_action}.")
    lines.append("")
    lines.append("The issues I want reviewed are:")
    lines.append("")
    for cond in case.conditions:
        lines.append(f"**{cond.name}** ({cond.claim_type}; {cond.status})")
        onset = cond.onset if not _unknown(cond.onset) else "[date first noticed — UNKNOWN]"
        event = (
            cond.in_service_event
            if not _unknown(cond.in_service_event)
            else "[in-service event or exposure — UNKNOWN]"
        )
        impact = (
            cond.current_impact
            if not _unknown(cond.current_impact)
            else "[how this affects work and daily life — UNKNOWN]"
        )
        lines.append(f"Onset: {onset}. In service: {event}. Now: {impact}.")
        if cond.secondary_to:
            lines.append(f"I believe this may be related to {cond.secondary_to}. That relationship is for medical and VSO review, not a conclusion of this draft.")
        lines.append("")
    have = [e for e in case.evidence if e.status == "have"]
    gaps = [e for e in case.evidence if e.status in {"missing", "requested"}]
    if have:
        lines.append("Documents I can provide now include:")
        for item in have:
            lines.append(f"- {item.title}" + (f" ({item.date})" if item.date else ""))
        lines.append("")
    if gaps:
        lines.append("Documents still needed before filing:")
        for item in gaps:
            lines.append(f"- {item.title} [{item.status}]")
        lines.append("")
    lines.append(
        "I am not asking anyone to invent facts, diagnoses, or witness statements. "
        "I want an accredited VSO to review this draft, correct it, and decide what to file."
    )
    lines.append("")
    lines.append("*[Signature / date reserved for the veteran after VSO review]*")
    return "\n".join(lines) + "\n"


def render_handoff(case: Case) -> str:
    ready = readiness(case)
    lines = [
        "## Handoff to accredited VSO",
        "",
        "Do not file from this packet as-is unless every fact below is verified.",
        "",
        "### Verify before 21-526EZ",
        "",
    ]
    for cond in case.conditions:
        flag = "CONFIRM WORDING" if cond.status != "diagnosed" else "listed as diagnosed in case file — still verify records"
        lines.append(f"- {cond.name}: {flag}")
    lines.extend(
        [
            "",
            "### Blocking items",
            "",
        ]
    )
    blocking = [e for e in case.evidence if e.status in {"missing", "requested"}]
    if blocking:
        for item in blocking:
            lines.append(f"- {item.title} (`{item.status}`)")
    else:
        lines.append("- None catalogued as missing or requested.")
    lines.extend(
        [
            "",
            "### Filing posture",
            "",
            f"- Completeness score: **{ready['score']}%**",
            f"- File-ready flag: **{'yes' if ready['file_ready'] else 'no'}**",
            "- Agent must not submit to VA.gov, VBMS, or QuickSubmit.",
            "- Recommended next human step: appointment with accredited VFW / Department Service Officer.",
        ]
    )
    if case.extra_notes:
        lines.extend(["", "### Case notes", "", case.extra_notes])
    return "\n".join(lines) + "\n"


def assemble(case: Case) -> str:
    parts = [
        render_cover(case),
        render_evidence_index(case),
        render_condition_sheets(case),
        render_narrative(case),
        render_handoff(case),
    ]
    return "\n".join(parts).rstrip() + "\n"


def write_packet(case: Case, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(assemble(case), encoding="utf-8")
    return dest
