"""Lexical retrieval over a curated public VA / CFR / VFW corpus.

Live fetch is optional and restricted to an allowlist. Snapshots in
corpus/snapshots/ are the default so the tool works offline.

This module cites public sources. It does not give legal advice or file claims.
"""

from __future__ import annotations

import json
import math
import re
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = ROOT / "corpus"
MANIFEST_PATH = CORPUS_DIR / "manifest.json"
SNAPSHOT_DIR = CORPUS_DIR / "snapshots"
CACHE_DIR = CORPUS_DIR / ".cache"

ALLOWED_HOSTS = {
    "www.va.gov",
    "va.gov",
    "www.ecfr.gov",
    "ecfr.gov",
    "www.law.cornell.edu",
    "www.knowva.ebenefits.va.gov",
    "knowva.ebenefits.va.gov",
    "www.vfw.org",
    "vfw.org",
    "www.govinfo.gov",
    "govinfo.gov",
    "www.publichealth.va.gov",
    "publichealth.va.gov",
}

USER_AGENT = "vso-agent-retriever/0.1 (+https://github.com/dlhiwig/vso-agent)"

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "to", "for", "in", "on", "at", "by",
    "is", "are", "was", "be", "as", "that", "this", "with", "from", "your",
    "you", "we", "will", "may", "if", "not", "can", "into", "about", "any",
}

TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?", re.I)


class RetrievalError(ValueError):
    pass


@dataclass
class Source:
    id: str
    title: str
    url: str
    publisher: str
    kind: str
    topics: list[str] = field(default_factory=list)
    snapshot: str = ""
    official_url: str = ""


@dataclass
class Chunk:
    source: Source
    text: str
    index: int


@dataclass
class Hit:
    score: float
    source: Source
    text: str
    chunk_index: int


class _HTMLText(HTMLParser):
    skip = {"script", "style", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__()
        self._skip = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.skip:
            self._skip += 1
        if tag in {"p", "div", "li", "h1", "h2", "h3", "h4", "br", "tr", "section"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.skip and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self.parts.append(data)


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text) if t.lower() not in STOPWORDS and len(t) > 1]


def load_manifest(path: Path = MANIFEST_PATH) -> list[Source]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    sources: list[Source] = []
    for item in raw.get("sources") or []:
        sources.append(
            Source(
                id=str(item["id"]),
                title=str(item["title"]),
                url=str(item["url"]),
                publisher=str(item.get("publisher") or ""),
                kind=str(item.get("kind") or "other"),
                topics=[str(t) for t in (item.get("topics") or [])],
                snapshot=str(item.get("snapshot") or ""),
                official_url=str(item.get("official_url") or item["url"]),
            )
        )
    return sources


def _read_snapshot(source: Source) -> str:
    if not source.snapshot:
        return ""
    path = ROOT / source.snapshot
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _chunk_text(text: str, size: int = 900) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    chunks: list[str] = []
    buf = ""
    for para in paras:
        if para.startswith("#") and buf:
            chunks.append(buf.strip())
            buf = para
            continue
        if len(buf) + len(para) + 2 > size and buf:
            chunks.append(buf.strip())
            buf = para
        else:
            buf = f"{buf}\n\n{para}" if buf else para
    if buf:
        chunks.append(buf.strip())
    return chunks or [text.strip()]


def build_index(sources: list[Source] | None = None) -> list[Chunk]:
    sources = sources if sources is not None else load_manifest()
    chunks: list[Chunk] = []
    for source in sources:
        body = _read_snapshot(source)
        if not body:
            continue
        for i, piece in enumerate(_chunk_text(body)):
            chunks.append(Chunk(source=source, text=piece, index=i))
    if not chunks:
        raise RetrievalError("Corpus is empty. Add snapshots under corpus/snapshots/.")
    return chunks


def _idf(chunks: list[Chunk]) -> dict[str, float]:
    df: dict[str, int] = {}
    for chunk in chunks:
        seen = set(tokenize(chunk.text + " " + chunk.source.title + " " + " ".join(chunk.source.topics)))
        for tok in seen:
            df[tok] = df.get(tok, 0) + 1
    n = len(chunks)
    return {tok: math.log((n + 1) / (count + 1)) + 1.0 for tok, count in df.items()}


def search(query: str, k: int = 6, sources: list[Source] | None = None) -> list[Hit]:
    q = query.strip()
    if not q:
        raise RetrievalError("Query is empty")
    q_tokens = tokenize(q)
    if not q_tokens:
        raise RetrievalError("Query has no searchable terms")
    chunks = build_index(sources)
    idf = _idf(chunks)
    hits: list[Hit] = []
    for chunk in chunks:
        hay = tokenize(chunk.text)
        title_toks = set(tokenize(chunk.source.title))
        topic_toks = set(tokenize(" ".join(chunk.source.topics)))
        tf: dict[str, int] = {}
        for tok in hay:
            tf[tok] = tf.get(tok, 0) + 1
        score = 0.0
        for tok in q_tokens:
            score += tf.get(tok, 0) * idf.get(tok, 1.0)
            if tok in title_toks:
                score += 3.0 * idf.get(tok, 1.0)
            if tok in topic_toks:
                score += 2.0 * idf.get(tok, 1.0)
        if score <= 0:
            continue
        hits.append(Hit(score=score, source=chunk.source, text=chunk.text, chunk_index=chunk.index))
    hits.sort(key=lambda h: h.score, reverse=True)
    seen: set[str] = set()
    unique: list[Hit] = []
    for hit in hits:
        if hit.source.id in seen:
            continue
        seen.add(hit.source.id)
        unique.append(hit)
        if len(unique) >= k:
            break
    return unique


def format_hits(hits: list[Hit], query: str) -> str:
    lines = [
        "# Public-source retrieval",
        "",
        f"**Query:** {query}",
        "",
        "Excerpts from a curated public corpus. Verify the live official page before relying on a citation. "
        "Not legal advice. Not a VA or VFW publication.",
        "",
    ]
    if not hits:
        lines.append("No matching excerpts.")
        return "\n".join(lines) + "\n"
    for i, hit in enumerate(hits, start=1):
        cite_url = hit.source.official_url or hit.source.url
        excerpt = hit.text.strip()
        if len(excerpt) > 900:
            excerpt = excerpt[:900].rsplit(" ", 1)[0] + " …"
        lines.extend(
            [
                f"## {i}. {hit.source.title}",
                "",
                f"- **Kind:** {hit.source.kind}",
                f"- **Publisher / reprint:** {hit.source.publisher}",
                f"- **Official URL:** {cite_url}",
                f"- **Score:** {hit.score:.2f}",
                "",
                excerpt,
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def host_allowed(url: str) -> bool:
    host = urlparse(url).hostname or ""
    return host.lower() in ALLOWED_HOSTS


def html_to_text(html: str) -> str:
    parser = _HTMLText()
    parser.feed(html)
    text = re.sub(r"[ \t]+", " ", "".join(parser.parts))
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [ln.strip() for ln in text.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def fetch_url(url: str, timeout: int = 30) -> str:
    if not host_allowed(url):
        raise RetrievalError(f"Host not on allowlist: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read()
    except urllib.error.URLError as exc:
        raise RetrievalError(f"Fetch failed for {url}: {exc}") from exc
    try:
        html = raw.decode("utf-8")
    except UnicodeDecodeError:
        html = raw.decode("latin-1", errors="ignore")
    return html_to_text(html)


def refresh_source(source: Source) -> Path:
    text = fetch_url(source.url)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    dest = CACHE_DIR / f"{source.id}.txt"
    header = (
        f"# {source.title}\n\n"
        f"Source URL: {source.url}\n"
        f"Official URL: {source.official_url or source.url}\n"
        f"Publisher: {source.publisher}\n\n"
    )
    dest.write_text(header + text + "\n", encoding="utf-8")
    return dest


def refresh_all() -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    for source in load_manifest():
        try:
            path = refresh_source(source)
            results.append((source.id, str(path)))
        except RetrievalError as exc:
            results.append((source.id, f"ERROR: {exc}"))
    return results


def hits_to_json(hits: list[Hit], query: str) -> dict[str, Any]:
    return {
        "query": query,
        "hits": [
            {
                "score": round(hit.score, 3),
                "id": hit.source.id,
                "title": hit.source.title,
                "kind": hit.source.kind,
                "publisher": hit.source.publisher,
                "url": hit.source.official_url or hit.source.url,
                "excerpt": hit.text,
            }
            for hit in hits
        ],
    }
