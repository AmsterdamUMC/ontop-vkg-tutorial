"""
metadata_renderer.py  v0.6
──────────────────────────
- Drops 'abstract' (MyST renders it automatically at the top)
- Appends a small <script> that moves the block into the page footer via JS
"""

from __future__ import annotations
import re
import yaml
from pathlib import Path
from docutils import nodes
from sphinx.application import Sphinx

# ── badge helpers ─────────────────────────────────────────────────────────────

ORCID_ICON = (
    '<img src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png" '
    'alt="ORCID" style="height:14px;vertical-align:middle;margin-right:3px;">'
)
ROR_ICON = (
    '<img src="https://raw.githubusercontent.com/ror-community/ror-logos/main/'
    'ror-icon-rgb.svg" alt="ROR" '
    'style="height:14px;vertical-align:middle;margin-right:3px;">'
)

def _orcid_link(url: str, label: str) -> str:
    orcid_id = url.rstrip("/").split("/")[-1]
    return (
        f'<a href="https://orcid.org/{orcid_id}" target="_blank" '
        f'class="meta-badge meta-badge--orcid">{ORCID_ICON}{label}</a>'
    )

def _ror_link(url: str, label: str) -> str:
    return (
        f'<a href="{url}" target="_blank" '
        f'class="meta-badge meta-badge--ror">{ROR_ICON}{label}</a>'
    )

def _doi_link(doi: str) -> str:
    doi_clean = re.sub(r"^https?://doi\.org/", "", doi)
    return (
        f'<a href="https://doi.org/{doi_clean}" target="_blank" '
        f'class="meta-badge meta-badge--doi">🔗 DOI: {doi_clean}</a>'
    )

def _license_badge(lic: dict) -> str:
    url  = lic.get("url", "#")
    name = lic.get("short") or lic.get("name", "License")
    return (
        f'<a href="{url}" target="_blank" '
        f'class="meta-badge meta-badge--license">⚖ {name}</a>'
    )

# ── HTML assembly (no abstract — MyST renders that automatically) ─────────────

def _build_metadata_html(meta: dict) -> str:
    parts: list[str] = []

    if doi := meta.get("doi"):
        parts.append(f'<div class="meta-row">{_doi_link(doi)}</div>')

    if date := meta.get("date"):
        parts.append(
            f'<div class="meta-row">'
            f'<span class="meta-label">Published:</span> '
            f'<span class="meta-value">{date}</span>'
            f'</div>'
        )

    if authors := meta.get("authors"):
        author_blocks = []
        for author in authors:
            name = author.get("name", "Unknown")
            name_html = (
                _orcid_link(author["orcid"], name)
                if "orcid" in author
                else f'<span class="meta-author">{name}</span>'
            )
            affils = []
            for aff in author.get("affiliations", []):
                aff_name = aff.get("name", "")
                if ror := aff.get("ror"):
                    affils.append(_ror_link(ror, aff_name))
                elif aff_name:
                    affils.append(f'<span class="meta-affiliation">{aff_name}</span>')
            block = name_html
            if affils:
                block += '<span class="meta-affil-sep">, </span>' + " · ".join(affils)
            author_blocks.append(f'<div class="meta-author-block">{block}</div>')

        parts.append(
            '<div class="meta-row meta-row--authors">'
            '<span class="meta-label">Authors:</span>'
            '<div class="meta-authors">' + "".join(author_blocks) + "</div>"
            "</div>"
        )

    if lic := meta.get("license"):
        parts.append(
            f'<div class="meta-row">'
            f'<span class="meta-label">License:</span> {_license_badge(lic)}'
            f'</div>'
        )

    if kws := meta.get("keywords"):
        kw_html = " ".join(f'<span class="meta-keyword">{k}</span>' for k in kws)
        parts.append(
            f'<div class="meta-row">'
            f'<span class="meta-label">Keywords:</span> {kw_html}'
            f'</div>'
        )

    if not parts:
        return ""

    move_js = """
<script>
(function() {
  var block = document.getElementById('page-metadata-footer');
  if (!block) return;
  var footer = document.querySelector('footer');
  if (footer) {
    footer.parentNode.insertBefore(block, footer);
    block.style.margin = '0';
    block.style.borderTop = 'none';
  }
})();
</script>
"""

    return (
        '<div id="page-metadata-footer" class="page-metadata" '
        'role="region" aria-label="Page metadata">'
        + "".join(parts)
        + "</div>"
        + move_js
    )

# ── front-matter reader ───────────────────────────────────────────────────────

_FM_RE = re.compile(r"^---[ \t]*\n(.*?)\n---[ \t]*\n", re.DOTALL)

def _read_frontmatter(src_dir: Path, docname: str) -> dict:
    for ext in (".md", ".ipynb", ".rst"):
        p = src_dir / (docname + ext)
        if p.exists():
            try:
                text = p.read_text(encoding="utf-8")
                m = _FM_RE.match(text)
                if m:
                    return yaml.safe_load(m.group(1)) or {}
            except Exception:
                pass
    return {}

# ── event handler ─────────────────────────────────────────────────────────────

def _inject_metadata(app: Sphinx, doctree, docname: str) -> None:
    fm = _read_frontmatter(Path(app.env.srcdir), docname)
    if not fm:
        return
    html = _build_metadata_html(fm)
    if not html:
        return
    # Append to end of doctree; JS will move it into the real footer
    doctree.append(nodes.raw("", html, format="html"))

# ── registration ──────────────────────────────────────────────────────────────

def setup(app: Sphinx) -> dict:
    app.connect("doctree-resolved", _inject_metadata)
    return {"version": "0.6.0", "parallel_read_safe": True}