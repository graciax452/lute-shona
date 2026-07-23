# Shona dataset search notes

Working reference for growing `NOUN_ROOT_LEXICON`/`VERB_ROOT_LEXICON`.
Purpose: avoid re-checking sources that already turned out to be
unusable, and know what's still an open lead. Update this file as new
sources are checked — status markers:

- ✅ Used — merged into `rules.py`, see `DESIGN.md` for the extraction writeup.
- ⚠️ Real, not directly usable — exists and is legitimately licensed, but wrong shape (e.g. sentence pairs, not a lexicon) or needs work we haven't done (e.g. a stemmer).
- 🆕 Found, not yet checked — a real lead, but not downloaded/verified yet.
- ❓ Unverified — mentioned somewhere, never actually checked in this project.
- ❌ Rejected — checked and ruled out; the notes column says why, so it doesn't get re-suggested.

| Source | Format / Size | License | Status | Notes |
|---|---|---|---|---|
| **Kaikki.org Shona Wiktionary extract** (`kaikki.org/dictionary/Shona/`) | JSONL, 515 words | CC BY-SA 4.0 | ✅ Used | Clean, class-tagged, verb roots pre-separated from `ku-`. Primary source. Note: the site's main download link is marked "DEPRECATED, will be removed in the near future" but was still live when fetched — re-check if it 404s later, there's a "raw data" alternative linked from the same page. |
| **shona-spacy `shona_lexicon.json`** (`github.com/HappymoreMasoka/shona-spacy`) | JSON, 136 entries | MIT (confirmed via `pyproject.toml`, not via a repo-level LICENSE file — there isn't one) | ✅ Used | Small but hand-verified ("Verified manually" per entry). Independent open-source Shona morphological analyzer, arXiv:2511.16680. |
| **shona-spacy `shona_tokens_with_classes.csv`** (same repo) | CSV, 8MB | MIT (repo-level) | ❌ Rejected | Noisy social-media scrape (English words, typos mixed in), class tags come from an ungated heuristic guesser, not real ground truth. Don't reconsider unless someone cleans/re-verifies it. |
| **OPUS-MT560 English-Shona** (`michsethowusu/english-shona_sentence-pairs_mt560`, HuggingFace) | Parquet, ~100k+ sentence pairs | CC-BY-4.0 | ⚠️ Real, not directly usable | Sentence pairs, not a dictionary. Would need a stemmer to pull roots out — circular, since that's what this project is building. Revisit only if a separate Shona stemmer/lemmatizer turns up. |
| **google/smol** (HuggingFace) | Parquet, Shona is 1 of 221 languages | CC-BY-4.0 | ⚠️ Real, not directly usable | Professional translation pairs, same "needs a stemmer" limitation as OPUS-MT560. |
| **PanLex** (`panlex.org`) | SQLite/CSV/JSON, full multi-GB global dump | **CC BY-NC-SA 4.0** — corrected: a pasted source claimed CC0 ("copy, modify, and distribute"); the license page (`panlex.org/license/`) actually says "shared under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0... Commercial use... permitted only by obtaining written permission." Fine for this noncommercial open-source project, but not CC0. | ⚠️ Real, unassessed | Huge; per-language quality varies a lot for lower-resource languages. Would need the Shona slice pulled out and quality-checked before it's worth using — not a quick win. |
| **Berlin Shona Novel Corpus (BeShoNo)** (`rs.cms.hu-berlin.de/beshono`) | Toolbox-format morpheme-annotated text, ~40% of 3 Shona novels | Not an open license — page gives an academic citation format only, translation files explicitly copyright-restricted; would need to contact the project leads before bulk use | 🆕 Found, not yet checked (license needs direct confirmation) | Genuinely interesting, different in kind from everything else here: real linguists' morpheme-boundary annotations on literary text, not just a wordlist. Could work as a **validation corpus** (checking this project's splits against professional ones) even before it works as a lexicon source. Real academic project (Humboldt University Berlin), not fabricated. |
| **`HappymoreMasoka/Working_with_shona-slang`** (GitHub) | CSV, ~34,000 Shona-English slang/chitchat utterances, tagged intent/sentiment/tone | No LICENSE file or repo-level license found | 🆕 Found, not yet checked | Same author as shona-spacy (a real, previously-verified source), so probably genuine — but this is *conversational slang* (SMS-speak: "Hie swit mom"), not dictionary-shaped, and no license was found to confirm reuse rights. Would need both a license check and heavy filtering before it could feed a root lexicon the way Kaikki did. |
| **Wikidata Lexemes for Shona** (SPARQL query against `query.wikidata.org`, `wd:Q34004`) | JSON/CSV via SPARQL | CC0 | ❌ Real infrastructure, no actual data | A pasted source rated this "High" suitability with a ready-to-run query. The query itself is valid and was run directly against Wikidata: **3 lexeme entries total** for Shona. Not a typo — three. Technically real, practically empty; not worth building a pipeline around. |
| **An Abstract Multilingual WordNet (AMWN)** (Angelov, GWC 2025 — a pasted source miscited this as "ACL 2025") | TSV/JSON, 265 languages total | CC BY 4.0 (per the paper) | ❌ Not independently useful | Read the actual paper (`aclanthology.org/2025.gwc-1.3`): it's **built directly on top of PanLex** ("The main source for both the old languages and the new ones is PanLex"), with per-language entries marked validated/unchecked/**guessed** — guessed entries are automated best-guesses, not confirmed translations. A pasted source's specific "~22,900 Shona lemmas" figure could not be confirmed anywhere in the paper's text (may be fabricated, same pattern as `masakhane/maharasa` earlier). Even if real, this is PanLex-derived with extra automated uncertainty layered on — going to PanLex directly is strictly better. |
| **CBOLD (Comparative Bantu Online Dictionary)** (UC Berkeley / CNRS) | SIL Toolbox `.txt` (`\lx`/`\ps`/`\ge`/`\nc` tags) | Academic, unconfirmed | ❌ Dead link | Both stated URLs checked directly: the CNRS mirror (`cbold.ish-lyon.cnrs.fr`) doesn't resolve (DNS failure) and the Berkeley page redirects to that same dead CNRS host. Same category as the ALLEX/Duramazwi 1990s-2000s academic archive pages found dead earlier — a real historical project with no live access point today. |
| **ASJP Shona wordlist** (`asjp.clld.org/languages/SHONA`) | wordlist, ~50 items | academic/open | ❌ Too small | Smaller than what's already merged from Kaikki alone. Not worth the integration effort. |
| **Common Voice Shona** (Mozilla) | speech audio | CC0 | ❌ Wrong data type | Speech, not text/lexicon. Only relevant for a future pronunciation/audio feature. |
| **Africa Commons "Shona Language Lexical Data"** (ties to Hannan's dictionary) | unknown | unknown | ❓ Unverified | Page returned HTTP 403 to an automated fetch — couldn't see contents, format, or license. Worth a manual look in a real browser. |
| **VaShona.com "Project Lexicon Hub"** (claimed 100k+ words) | web dictionary | proprietary | ❌ Rejected | Site explicitly says "All rights reserved, do not distribute." No bulk export despite the claim. |
| **Hannan's *Standard Shona Dictionary*** (archive.org) | scanned PDF/DjVu | copyrighted scan | ❌ Not tabular | Real, authoritative, but only page images — same OCR/extraction problem as isiXhosa's Oosthuysen grammar, at a much bigger scale. Possible future project, not a quick source. |
| **ALLEX/Duramazwi official dictionaries** (ALRI) | — | — | ❌ No access point | No public digital release found — dead institutional pages (University of Oslo project pages 404/503), ALRI's own page lists them as completed works with no download/purchase info. |
| **`asideofcode/duramazwi`** (GitHub) | — | — | ❌ Misattributed | Claimed to be "the real ALLEX dictionary backend" in a pasted source list — actually an unrelated small hobby app (188 commits, 2 stars), no stated data provenance. |
| **`masakhane/maharasa`** (claimed HuggingFace dataset) | — | — | ❌ Doesn't exist | Checked via HF API — 404. Fabricated in a pasted source list; don't chase this name again. |
| **`saillab/alpaca_shona_taco`** (HuggingFace) | Parquet | unstated | ❌ Wrong tool | Translated Alpaca/TaCo instruction-tuning data (LLM prompts), not vocabulary or natural text. |

| **Lexibank / CLDF** (`clld/lexibank` on GitHub, MPI-EVA) | CSV (CLDF standard: `forms.csv`, `parameters.csv`) | CC BY 4.0 | ❓ Not checked for Shona specifically | Real, legitimate infrastructure (used across many real Lexibank datasets), but not verified whether any Lexibank dataset actually includes Shona, or at what scale — most comparative-Bantu Lexibank datasets are Swadesh-list-sized (~100-200 items) for any given language, not the "1,000+ core vocabulary" a pasted source claimed generically. Worth a specific existence check, not worth assuming. |
| **RefLex Database** (CNRS/LLACAN) | Web database export / TSV | Academic, unconfirmed | ❓ Not checked | Real Africanist lexicon database. Claimed to include Ndau/Cindau (a Shona-cluster variant) extracts. Not yet verified for actual Shona (not just a related variant) coverage, format, or license. |

## Biggest open leads

1. **BeShoNo** — the most genuinely novel find this round: professionally
   morpheme-annotated real literature, useful as a *validation* corpus
   even before (or instead of) a lexicon source. Needs a license
   confirmation email to the project leads before bulk use.
2. **PanLex** — real, CC BY-NC-SA 4.0 (not CC0 — corrected above), still
   the most promising *lexicon-shaped* bulk lead, just needs someone to
   pull the Shona slice and check quality.
3. A manual look at the **Africa Commons** page in a real browser,
   since the automated fetch got blocked (still unverified).

## A note on this round's research quality

Two rounds of pasted "new leads" both needed real correction, worth
flagging as a pattern: PanLex's license was mis-stated as CC0 (it's
CC BY-NC-SA — still usable here, but a materially different claim),
Wikidata's Shona lexeme count was described as a "High" fit while
actually being 3 entries, AMWN's specific lemma count couldn't be
confirmed in the source paper and the paper turned out to be
PanLex-derived rather than independent, and CBOLD's stated URLs are
dead. None of this means the underlying research effort was worthless
— BeShoNo and the shona-slang repo are both genuine, useful-shaped
finds that weren't in any earlier list — but every specific claim
(license, size, "fit" rating) needs the same direct verification
before acting on it, every time, regardless of how confident or
detailed the write-up sounds.
