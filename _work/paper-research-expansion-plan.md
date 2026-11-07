# Paper Research Expansion Plan

**Goal:** Extend the existing paper library with publicly accessible high-quality work by Kaiming He and Simiao Lai, analyze their research trajectories, and collect Wuhan University of Technology AI-related CCF-A conference papers.

**Architecture:** Keep separate metadata manifests and PDF folders for each collection. Use the official CCF 2026 seventh edition as the venue-classification source, add all acquired PDFs to the existing page-by-page extraction archive, and link the new searchable collection and route analysis from the current reading entry.

**Execution:** Native execution in the existing workspace, as directed by the user.

## Tasks

1. Reconcile author and group identities, inclusion rules, paper titles, venue status, affiliation-at-publication, and legal public full-text URLs against primary sources.
2. Download each publicly available full text into a collection-specific folder. Verify PDF signature, title/author identity, page count, and SHA-256; record unavailable full texts without bypassing access controls.
3. Add collection manifests, page-by-page text extraction records, searchable HTML catalog(s), and links from the main reading entry. Keep CCF-A conference status distinct from author-level or venue-adjacent quality.
4. Write comparative research-route analyses for Kaiming He and Simiao Lai, and a concise group-level overview for the WUT papers. Check generated relative links and title/manifest coverage.

## Scope rules

- Apply the official CCF 2026 seventh edition, published 2026-03-31 and corrected 2026-04-09. For conference CCF-A claims, require a full/regular main-track paper; label accepted but not yet published separately.
- Include public PDFs from arXiv, official conference libraries, or author/institution repositories. Record paywalled or missing full texts as gaps.
- For WUT, use verified AI-school/lab membership and actual publication-page affiliations; clearly mark scope limits where the public records do not prove institution-wide exhaustiveness.
- No model training, changes to research code, or paid/download-restricted access.

## Review focus

- Same-title versions and workshop versions must not be counted as separate CCF-A full papers.
- Current CCF classification must not be inferred from older profile labels.
- Coauthored work must not be presented as sole-author contribution in route analysis.
- WUT faculty work published before joining WUT must not be described as WUT-affiliated at publication.
- Every local PDF and HTML link must resolve, and the raw-text index must match PDF identity and pages.
