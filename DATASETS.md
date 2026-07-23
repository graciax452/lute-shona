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
| **PanLex** (`panlex.org`) | SQLite/CSV/JSON, full multi-GB global dump | CC0 | ⚠️ Real, unassessed | Huge; per-language quality varies a lot for lower-resource languages. Would need the Shona slice pulled out and quality-checked before it's worth using — not a quick win. |
| **ASJP Shona wordlist** (`asjp.clld.org/languages/SHONA`) | wordlist, ~50 items | academic/open | ❌ Too small | Smaller than what's already merged from Kaikki alone. Not worth the integration effort. |
| **Common Voice Shona** (Mozilla) | speech audio | CC0 | ❌ Wrong data type | Speech, not text/lexicon. Only relevant for a future pronunciation/audio feature. |
| **Africa Commons "Shona Language Lexical Data"** (ties to Hannan's dictionary) | unknown | unknown | ❓ Unverified | Page returned HTTP 403 to an automated fetch — couldn't see contents, format, or license. Worth a manual look in a real browser. |
| **VaShona.com "Project Lexicon Hub"** (claimed 100k+ words) | web dictionary | proprietary | ❌ Rejected | Site explicitly says "All rights reserved, do not distribute." No bulk export despite the claim. |
| **Hannan's *Standard Shona Dictionary*** (archive.org) | scanned PDF/DjVu | copyrighted scan | ❌ Not tabular | Real, authoritative, but only page images — same OCR/extraction problem as isiXhosa's Oosthuysen grammar, at a much bigger scale. Possible future project, not a quick source. |
| **ALLEX/Duramazwi official dictionaries** (ALRI) | — | — | ❌ No access point | No public digital release found — dead institutional pages (University of Oslo project pages 404/503), ALRI's own page lists them as completed works with no download/purchase info. |
| **`asideofcode/duramazwi`** (GitHub) | — | — | ❌ Misattributed | Claimed to be "the real ALLEX dictionary backend" in a pasted source list — actually an unrelated small hobby app (188 commits, 2 stars), no stated data provenance. |
| **`masakhane/maharasa`** (claimed HuggingFace dataset) | — | — | ❌ Doesn't exist | Checked via HF API — 404. Fabricated in a pasted source list; don't chase this name again. |
| **`saillab/alpaca_shona_taco`** (HuggingFace) | Parquet | unstated | ❌ Wrong tool | Translated Alpaca/TaCo instruction-tuning data (LLM prompts), not vocabulary or natural text. |

## Biggest open lead

**PanLex** (real, CC0, just needs someone to pull the Shona slice and
check quality) or a manual look at the **Africa Commons** page in a
real browser, since the automated fetch got blocked.
