# lute-shona

A Shona language parser plugin for [Lute3](https://github.com/LuteOrg/lute-v3), splitting agglutinative noun/verb morphology into separately trackable tokens.

## What this solves

Shona is space-delimited, so Lute's stock "Space Delimited" parser already gets word boundaries right. The problem is that a single space-delimited Shona word is often several grammatical morphemes glued together — e.g. `vachamubikira` = `va` (they) + `cha` (future) + `mu` (him/her) + `bik` (cook) + `ira` (for + ending vowel). Without splitting, the whole inflected word is one unclickable blob and you end up manually re-marking the root every time — the same pain point Korean particles caused before that parser was fixed.

This plugin peels known noun-class prefixes and verb subject/tense/object/extension affixes off each already-space-split word, using hand-built lookup tables — no external tokenizer or dependency, since Shona doesn't need one for word boundaries.

## Design: lexicon-gated stripping

A candidate affix is only stripped if what's left over matches a known root in a small seed lexicon (`rules.py`'s `NOUN_ROOT_LEXICON` / `VERB_ROOT_LEXICON`). This avoids **overstemming** — blindly stripping any string that looks like a prefix, even when it isn't grammatically that prefix, is a documented failure mode in rule-based agglutinative parsing (the same trap Swahili's SALAMA/xsma parsers are built to avoid).

The practical effect: **most words outside the seed lexicons won't split in v1.** That's intentional, not a bug — a wrong split teaches wrong grammar, which is worse than showing the whole word. Grow the lexicons in `rules.py` as real reading text surfaces words worth adding.

A handful of other small, tightly-gated tables handle known hard cases that don't fit the regular noun/verb pattern, all in `rules.py`:
- `PROPER_NOUNS` — names (checked first; Shona names are often spelled identically to ordinary words, e.g. "Kuda" the name vs. "kuda" "to want")
- `WORD_EXCEPTIONS` — whole-word bypasses for forms that are genuinely unresolved (e.g. `ndakuisisa`, a confirmed reduplication whose exact morpheme boundary isn't)
- `PAST_SUBJECT_PREFIXES` — the confirmed past-tense subject concord paradigm (`nda`/`wa`/`ta`/`ma` for 1sg/2sg/1pl/2pl; 3sg/3pl are unchanged from the basic concord), sourced from a full pronoun/concord reference table, not a phonological rule engine
- negative existential `ha- + concord + -na` (e.g. `haina`) and the productive `[subject] + sati` "before ~ing" construction (e.g. `ndisati`) — each its own small rule, not routed through the general verb pipeline
- extension-stacking (up to 2 deep) for causative+passive-style verb constructions

**For the full reasoning behind every one of these — including the alternatives considered, what was tried and reverted, and guidance for forking to another Bantu language — see [DESIGN.md](DESIGN.md).**

## Install

```powershell
pip install -e .
```

into whichever venv runs your Lute3 instance. Restart Lute; "Shona" should appear in `Enabled parsers:` at startup and in the language dropdown. Create a Shona language in Lute's Settings with parser type `lute_shona` (there's no bundled `language_defs/shona` template, so this is a manual "add new language" like any community language).

## Optional: highlight grammar tokens

```powershell
python scripts/generate_css.py > shona_grammar.css
```

Paste the output into Lute's Settings → Custom Styles to bold/color grammar tokens (prefixes, TAM markers, extensions) before you've marked them "known" — uses Lute's existing per-span `data-text` attribute, no core patch.

## Tests

```powershell
python tests/test_morphology.py
python tests/test_generate_css.py
```

(or `python -m pytest tests/` if you have pytest installed — both test files support either).

`tests/test_morphology.py` includes a real-text stress sentence, not just clean textbook cases — several expected outputs are deliberately whole-word (contractions, unseeded roots) to document today's known coverage gaps, plus edge cases (empty/minimal input, case preservation, the extension-depth cap failing closed on a synthetic overreach). See [DESIGN.md](DESIGN.md) for why each one is there.
