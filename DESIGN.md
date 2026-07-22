# Design notes: why this parser is built the way it is

This document exists for two audiences: future-you tuning `rules.py`
after more reading, and anyone forking this to build a parser for
another Bantu language. It records not just *what* was built but *why*
— the alternatives considered, the mistakes made and caught along the
way, and where the boundary between "Shona-specific" and "probably
generalizes to other Bantu languages" actually sits.

For the quick-start (install, run tests, generate CSS), see
[README.md](README.md). This document is the deep-dive.

## 1. The problem this solves

Lute3 is a reading-based language-learning tool: you read text, click
unknown words, and Lute tracks them as vocabulary at various stages of
"known." That model assumes each clickable token is one word worth
learning.

Shona (and Bantu languages generally) is agglutinative: a single
space-delimited "word" is often several grammatical morphemes fused
together. `vachamubikira` = `va` (they) + `cha` (future) + `mu`
(him/her) + `bik` (cook) + `ira` (applicative "for" + ending vowel) =
"they will cook for him/her." Without splitting, Lute treats the whole
inflected word as one unclickable/untrackable blob, and the learner
ends up manually re-marking the root every single time it appears in a
different inflection. This is the same problem Korean particle
attachment caused before that parser (see below) split them out.

**The goal is not maximal linguistic decomposition.** It's: get the
root tracked correctly every time, and get the small closed set of
grammatical pieces (prefixes, tense markers, etc.) out of the way so
they stop cluttering every word — the same "mark it known once, it
recedes forever" value proposition Lute already gives you for ordinary
vocabulary.

## 2. Source material

- **`Shona_noun_classes.xlsx`** — user-compiled reference table, all
  21 noun classes with prefixes, example nouns, and allomorph notes
  (e.g. `u-` → `hw-` before a vowel-initial stem). This is the source
  for `NOUN_CLASS_PREFIXES` and the initial `NOUN_ROOT_LEXICON` seed
  (`nhu`, `nda`, `panga`, `ngwa`, `kuni`, `mbuyu`, `pfu`, `mba`,
  `musha`, `gomana`, `huku` all trace back to example nouns in this
  table).
- **A verb morphology summary** (pasted into the planning conversation)
  — the slot structure `[Hortative] + [Subject Prefix] + [TAM] +
  [Object Marker] + ROOT + [Extensions] + [Terminal Vowel]`, with the
  worked example `vanhu vachamubikira`. Source for
  `VERB_SUBJECT_PREFIXES`, `TAM_MARKERS`, `OBJECT_MARKERS`,
  `VERB_EXTENSIONS`.
- **`Beginners Shona Level 1.docx`** — mostly greetings/vocabulary, but
  supplied the ~15 sample infinitives that seed `VERB_ROOT_LEXICON`
  (`kufamba`, `kutenda`, `kugara`, `kumira`, `kuuya`, `kuenda`,
  `kudya`, `kuda`, `kunyora`, `kuverenga`, `kuterera`, `kuona`,
  `kunwa`, `kudzidza`).
- **A Fivaz (1966) academic text on Shona morphophonemic structure**
  (`Some aspects of Shona structure-TXT-download.zip`, OCR'd, rough
  quality; also available as `-JP2-download.zip` for the page images)
  — genuine linguistic reference on consonant-mutation/allomorph rules,
  deliberately **not** mined for v1. Flagged as a "come back to this
  when you hit real accuracy gaps" resource, not needed to get a
  working baseline.
- **Direct confirmation from the user** during the build, for anything
  not resolvable from the documents above: the name/verb ambiguity of
  `Kuda`, the `chi-` consecutive "then" reading (not class-7 concord)
  in `Chiisa`, the `ha- + concord + na` negative-existential
  construction, the productive `[subject] + sati` "before ~ing"
  construction (confirmed across `usati`/`tisati`/`musati`/`chisati`,
  not just one example), and the object-marker readings of
  `ndakuisisa`/`ndamuisisa`/`ndachiisisa` ("I made you/her-him/it put
  it").
- **A separate stress-test document** (`test_cases.md`, supplied after
  the initial build) cross-checked every rule against a real sentence
  and flagged several gaps (see §7 and §9).
- **`3 Noun Classes.pdf`** — a structured reference document covering
  all 21 noun classes with multiple concrete example nouns per class,
  plus a full personal-pronoun/concord table (basic subject concord,
  **past** subject concord, object marker concord, possessive
  prefix/stem, demonstratives). This substantially upgraded several
  tables from "best effort, handful of examples" to properly sourced:
  it's where `PAST_SUBJECT_PREFIXES`' `wa`/`ta`/`ma` came from (§7), the
  bulk of the current `NOUN_ROOT_LEXICON`, and the additional noun-class
  prefixes `i-` (cl.9), `dzi-` (cl.10), `svi-` (cl.19), `hu-` (cl.14
  allomorph), `rw-` (cl.11 allomorph). Dry-running every example from
  this document against the actual code (rather than trusting the
  extraction by inspection) is also what surfaced the `mudzidzisi`/
  `mukanwa` verb-slot collisions in §7 and the `zvombo`-style
  vowel-elision cases in §9 — see those sections for what that means.
- **A larger personal Shona-language library** the user has at
  `E:\speakshona\shona textbooks and ebooks\` and
  `E:\speakshona\shona research and papers\` (Hazel Carter's course,
  Fortune's grammar volumes, an "Analytical Grammar of Shona," the FSI
  Basic Course, and more, beyond the Fivaz text already noted above) —
  flagged as available for future deeper mining, not processed for this
  revision. Treat the same way as Fivaz: a resource to come back to
  when you hit a real accuracy gap the currently-sourced tables can't
  resolve, not something to front-load.
- **A real story, `sekuru kamba - grandpa tortoise shona.txt`** (from
  the same library folder) — the first actual connected Shona text run
  through the parser, rather than synthetic stress sentences. Of 123
  unique words, 110 correctly stayed whole and 13 split; 9 of those 13
  were correct without any changes, including one construction
  generalizing correctly to a case it hadn't been tested with before
  (`havana`, see the negative-have entry in §7). The other 4 surfaced
  the true-homonym and short-root-collision cases documented in §7's
  `WORD_EXCEPTIONS` entry (`kamba`, `mudiki`, `Vadikisa`) and one
  addition to `PROPER_NOUNS` (`Kamba`, the story's title character).
  This is the validation method to keep using going forward — run real
  text, don't just extend from reference grammar tables in the
  abstract; see §9 for what fraction of a real, unfamiliar text this
  parser can be expected to handle today.

## 3. Why lexicon-gated stripping, not blind string-matching

The tempting naive design: "if a word starts with a known prefix
string, strip it." This is **overstemming** — a documented failure
mode in rule-based agglutinative parsing. A word that merely happens
to start with a prefix-shaped string gets wrongly amputated into a
fake prefix + garbage remainder, even when it isn't grammatically that
prefix at all.

The fix used everywhere in this codebase: **a candidate affix is only
stripped if what's left over resolves to a known root** in
`NOUN_ROOT_LEXICON` / `VERB_ROOT_LEXICON`. `mvura` ("water") starts
with letters that could coincidentally look strippable, but nothing
downstream of any candidate strip resolves to a seeded root, so it's
left whole. This is deliberate and load-bearing, not a shortcut: the
real precedent is Swahili's **SALAMA/xsma** morphological analyzers
(same Bantu family, rule-based, lexicon+rules architecture, not
statistical), and the same lexicon-anchoring principle shows up in
Turkish/Finnish two-level (Koskenniemi) morphology as the standard
answer to the same class of problem.

**Consequence, stated explicitly because it's easy to mistake for a
bug**: most nouns outside the small seed lexicon will not split in v1.
Nouns are an open lexical class — there's no way to enumerate them all
up front — so the safe default is "leave it whole" rather than guess.
Coverage grows only as real reading text surfaces words worth adding
to `rules.py`. **A wrong split teaches wrong grammar, which is worse
than showing an unsplit word.** This priority — root correctness over
split coverage — is the single most load-bearing decision in the
codebase and should not be relaxed casually.

### The "stop at the shallowest match" corollary

Within `_resolve_stem` (`morphology.py`), once a direct root-lexicon
hit is found, the function returns immediately — it does **not** keep
searching for a deeper match, even if one would also technically
resolve. This is what keeps `kuisa` (root `-is-`, "put") as one root
instead of being fake-decomposed into a bogus sub-root + the
identically-spelled causative extension `-is-`, just because the
string allows that reading. Confirmed live with the
`kuisa`/`kuiswa`/`kuisiswa` progression (§6).

## 4. Why `ShonaParser` subclasses `SpaceDelimitedParser`

Two live design options were considered:

1. Mirror the Korean plugin's shape: implement `AbstractParser`
   directly, with `get_parsed_tokens` doing everything from scratch.
2. Subclass `lute.parse.space_delimited_parser.SpaceDelimitedParser`
   and override just the one method that turns a matched word into a
   token.

Option 2 was chosen. Shona doesn't need a tokenizer at all — it's
already space-delimited, exactly like English — so the entire
word-boundary/punctuation/paragraph/sentence-end handling in
`SpaceDelimitedParser` is already correct and battle-tested; rebuilding
it from scratch (as Korean's MeCab-based parser necessarily does, since
Korean genuinely lacks word boundaries) would just be duplicated, more
fragile code. There's also a direct precedent already living in Lute
core: `TurkishParser(SpaceDelimitedParser)` does exactly this
pattern — subclass, override a couple of things, done.

`ShonaParser.parse_para()` mirrors `SpaceDelimitedParser.parse_para()`
almost line for line (copied because `parse_para` has no smaller
extension hook to override), with the one change: instead of appending
a single `ParsedToken(word, True, False)` per matched word, it calls
`split_word()` and appends one `ParsedToken` per returned morpheme.

**If you're forking this for another Bantu language and that language
is also space-delimited** (true for essentially all of them — Bantu
languages use spaces between words; the difficulty is *within* each
word, not between them), reuse this same pattern. There is no reason
to write a from-scratch tokenizer for a space-delimited language.

## 5. Token model

Every emitted token gets `is_word=True` — Lute's own learning-status
colouring (new/learning/known) does all the "this is unfamiliar, now
it's not" visual work for free, the same mechanism already used for
Korean particles. There is **no custom "root vs. grammar" colour
axis** in the core design — `ParsedToken` has no field for it, and
Lute's rendering pipeline has no concept of morphological role
anywhere (verified directly against `lute/read/render/text_item.py`
and the reading-pane template — see §8 for the one optional exception).

Three kinds of token, one hard rule:

1. **Root** — always its own token, gated by lexicon match, protected
   above everything else. This is the actual vocabulary being learned;
   every other design choice bends around keeping this correct.
2. **Grammatical affixes** (noun class prefix, subject prefix, TAM
   marker, object marker, verb extension, and the closed constructions
   in §7) — each its own token. Closed sets, learn once, done.
3. **Terminal vowel (`-a`/`-e`/`-i`)** — **never** its own token. This
   was explicitly revisited mid-build (a parallel conversation
   proposed splitting it out, `bik | ir | a`, three tokens) and then
   explicitly reverted back to fusion (`bik`, `ira`, two tokens) after
   direct clarification. The reasoning that won: a single Latin letter
   carries almost no standalone learning value and is easy to
   mis-click as its own token — unlike, say, a Hangul syllable block,
   which is visually chunky enough to be a reasonable click target on
   its own. The vowel is *analyzed* (stripped, checked) to correctly
   locate the root/extension boundary, but *merged back* onto whichever
   morpheme ends up last before the token list is returned. **If you
   are re-deriving this for another language, don't re-litigate this
   without a concrete reason — it was already gone back and forth on
   once.**

### Case handling (a correctness requirement, not a style choice)

All matching (prefixes, TAM, object markers, extensions, lexicon
lookups) happens against a **lowercased copy** of the word, but every
returned token is a **slice of the original-cased input**. This isn't
optional: `ParsedToken`s must concatenate back to the exact original
text (Lute's contract — see `lute/parse/base.py`), so a sentence-initial
capital like `Kuda` must come back as `Ku`+`da`, not `ku`+`da`. Every
function in `morphology.py` threads both `word` (original case) and
`lword` (lowercased, matching-only) through for this reason.

## 6. The stem resolver, in detail

`_resolve_stem()` in `morphology.py` is the core of verb handling. It
peels from both ends toward the middle:

- From the left (handled by the caller, `_try_verb_slot` /
  `_try_infinitive`): subject prefix (required), then optional TAM,
  then optional object marker.
- From the right (handled inside `_resolve_stem`): terminal vowel
  (required — reject if the remainder doesn't end in `a`/`e`/`i`),
  then zero, one, or two extensions.
- **The root lexicon is the anchor that confirms the whole chain of
  guesses was actually correct** — not any individual slot match on
  its own. Optional-slot combinations (TAM present/absent × object
  marker present/absent) are tried and the stem resolver run on each
  candidate remainder; the first combination that lands on a lexicon
  hit wins.
- Extensions are capped at depth 2 (covers causative+passive-style
  stacking, e.g. `kuisiswa` = `ku`+`is`+`is`+`wa`) rather than
  unbounded, both to keep the search cheap (each table is tiny — a
  handful of subject prefixes, ~3 TAM markers, ~6 object markers, ~9
  extensions, 3 terminal vowels — so total combinations per word are a
  few dozen at most) and because unbounded stripping would eventually
  start finding coincidental matches with no linguistic basis. A
  synthetic depth-3 case is tested explicitly to confirm the cap fails
  closed (falls back to the whole word) rather than accepting a
  three-strip guess.
- Extensions strip innermost-first (closest to the terminal vowel),
  which happens to match the Bantu **CARP** ordering constraint
  (extensions attach Causative → Applicative → Reciprocal → Passive),
  so the strip order isn't arbitrary — it's the mirror image of
  attachment order.

**Live validation case for all of the above**, worked through directly
in conversation: `kuisa` / `kuiswa` / `kuisiswa`. The root `-is-`
("put") is *also* the exact string of the causative extension. Direct-
root-match-first is what keeps `kuisa` → `ku`+`isa` (one root, no
guessed extension) instead of a fake decomposition; extension-stripped
matching is what correctly resolves `kuiswa` → `ku`+`is`+`wa` (passive)
and `kuisiswa` → `ku`+`is`+`is`+`wa` (causative+passive, depth-2).

### The `ku-` ambiguity

`ku-` is simultaneously the class-15 infinitive marker, the class-17
locative noun prefix, and (per `OBJECT_MARKERS`) the 2sg object
marker. `_try_infinitive` is checked before the general noun/verb
branches specifically so this can be resolved by evidence (does the
remainder match a known verb root?) rather than by guessing; `kufamba`
resolves as an infinitive, `kumusha` ("to the homestead") correctly
does *not*, because `musha` isn't in `VERB_ROOT_LEXICON` — it falls
through to the noun branch instead, where `musha` *is* in
`NOUN_ROOT_LEXICON`.

## 7. The closed grammatical constructions (beyond the regular verb slot)

Several real Shona constructions don't fit the regular
subject+TAM+object+root+extension+vowel template at all. Each was
added as its own small, tightly-gated rule rather than forced through
the general engine or left to an open-ended shape match — the recurring
pattern is **"split the part you're confident about, via an exact
match against a closed set; don't force the rest through machinery
built for something else."**

- **`PROPER_NOUNS`** (names) — checked first, before literally
  everything else. Shona names are frequently spelled identically to
  ordinary words (`Kuda` the name vs. `kuda` "to want/love" — confirmed
  live via the stress-test sentence `Kuda isa bhutsu mumota`, "Kuda,
  put the shoes in the car," a vocative address, not the verb).
  Matched case-sensitively against the *original-cased* word (must be
  capitalized) — there's no positional or contextual signal that
  reliably distinguishes a name from a capitalized ordinary word
  (sentence-initial capitalization is required by orthography
  regardless of word class, so it carries no information on its own).
  Accepted tradeoff: a genuine sentence-initial capitalized use of the
  ordinary word will also be swallowed by this list if it's in
  `PROPER_NOUNS` — consistent with under-splitting as the safe failure
  mode everywhere else in this design. Seeded with a handful of
  placeholder names; **replace/expand from names actually used in your
  own material**, not a generic name list.

- **`WORD_EXCEPTIONS`** — whole-word bypass for forms that are
  genuinely unresolved, *or* for real verb/noun branch collisions where
  the noun reading is correct but verb-slot (tried first) also happens
  to resolve and wins. It briefly held `ndakuisisa` / `ndakuisisisa`
  (reduplication of the `is` root) while their exact morpheme boundary
  was unconfirmed and `nda` had just become a recognized prefix —
  without the explicit exception at that point, the general engine
  would have produced a confident-*looking* but linguistically
  unverified split. Both were later removed once the breakdown was
  confirmed (see the reduplicated-causative note under
  `PAST_SUBJECT_PREFIXES`). It now holds two different entries, found
  empirically by dry-running the noun-classes reference document
  against the actual code rather than trusting the extraction by
  inspection: `mudzidzisi` ("teacher") — verb-slot wrongly resolves it
  as `mu` (subject) + `dzidz` (root "learn") + `is` (causative) + `i`,
  because "dzidz" is a seeded verb root and the causative strip happens
  to land on it, when the correct reading is simply cl.1 `mu` + the
  whole noun "dzidzisi"; and `mukanwa` ("mouth") — verb-slot wrongly
  resolves it as `mu` (subject) + `ka` (past TAM) + `nwa` (root
  "drink"), i.e. "you(pl) drank," when the correct reading is cl.18
  locative `mu` + "kanwa". **The lesson from this table, illustrated
  twice now by two unrelated episodes:** adding a new general-purpose
  prefix/suffix rule, or even just growing a root lexicon, can have
  side effects on *other*, unrelated words that happen to share a
  substring — always re-check the full test corpus (or at minimum
  dry-run new examples against the actual code, not just by inspection)
  after a change — and *removing* an exception once its underlying rule
  is confirmed is just as real a step as adding one; don't leave stale
  exceptions around once the reason for them is gone.

  Two more entries were added after actually testing the parser against
  a real story (`sekuru kamba - grandpa tortoise`, see §2), and they're
  a genuinely different category from the two above — not a
  branch-ordering collision, but two other failure modes worth telling
  apart:

  - **A true lexical homonym**: `kamba` can be `ka`+`mba` ("small
    house", a fully regular diminutive) or the indivisible animal name
    "tortoise" — two different real words, same spelling, no
    morphological signal distinguishes them. In the actual story it's
    tortoise both times it appears lowercase. Left whole rather than
    defaulting to the diminutive reading: the diminutive is regular
    enough to still be recognizable even shown as one word, while
    "tortoise" needs accurate whole-word vocabulary tracking. (The
    capitalized form, `Kamba`, is additionally in `PROPER_NOUNS` since
    it's used as part of the character name "Sekuru Kamba" throughout
    the story — belt-and-suspenders with the lowercase
    `WORD_EXCEPTIONS` entry, not strictly required by it, but records
    the narrative-name usage explicitly.)
  - **A short-root collision, more systemic than `mudzidzisi`/
    `mukanwa`**: `mudiki` ("small") and `Vadikisa` ("small ones"/"they
    tried hard") both wrongly resolve through `VERB_ROOT_LEXICON`'s `d`
    (from `kuda`) — `mudiki` strips the stative `-ik-` from `dik` and
    lands on `d`; `Vadikisa` strips both `-is-` and `-ik-` and lands on
    the same `d`. "diki" is a genuine, productive adjective stem that
    takes noun-class-agreement prefixes exactly like a noun (`mudiki`,
    `vadiki`, `chidiki`, `zvidiki`, `tudiki`, `kadiki` are all
    plausible), and a 1-letter seeded root like `d` is unusually easy
    to land on by coincidence during extension-stripping — so this
    specific collision is more likely to recur across that whole
    family than the `mudzidzisi`/`mukanwa` collisions were to recur
    elsewhere. Only the two forms actually observed are listed; the
    rest of the family should be added the same way, as they show up in
    real text, not guessed at preemptively.

- **`PAST_SUBJECT_PREFIXES`** — a confirmed, complete past-tense
  subject concord paradigm, not one-off contractions: 1sg `nda`, 2sg
  `wa`, 1pl `ta`, 2pl `ma` (3sg/3pl past are identical to their basic
  concords, so they don't need separate entries), matched exactly like
  `VERB_SUBJECT_PREFIXES`. Originally just `nda` (added as a "known
  contracted form" under the name `CONTRACTED_PREFIX_FORMS`) — the
  noun-classes reference document's personal-pronoun/concord table
  later confirmed this is actually a full, regular paradigm rather than
  a one-off, which is why the table was renamed and the other three
  forms added at the same time. `nda` is additionally corroborated by
  Aranovich (2015) on Shona verb morphology: "the simple past form
  nda-tora 'I took' is formed with the prefix nda- '1.SG.PAST' attached
  directly to the root." `nda` is also what unlocked `ndakuisisa`
  (`nda` + `ku` [object marker] + reduplicated causative `is`, resolved
  via the same extension-loop already exercised by `kuisiswa` — see
  `test_reduplicated_causative` in `tests/test_morphology.py`) and
  `ndakuisisisa` (one more causative strip, landing exactly on the
  depth-2 extension cap). The object-marker reading was confirmed
  directly by the user with three parallel examples and glosses:
  `ndakuisisa` "I made you put it" (`ku` = 2sg object), `ndamuisisa` "I
  made her/him put it" (`mu` = cl.1 object), `ndachiisisa` "I made it
  put it" (`chi` = cl.7 object) — the last of which also surfaced a
  real gap (`chi` wasn't yet registered in `OBJECT_MARKERS`, only as a
  subject concord/noun prefix; added). Note: `ma` (2pl past) is the
  same surface string as the class 6 noun prefix `ma-` (e.g.
  `mapanga`) — verified this doesn't cause regressions, since the
  lexicon gate on each side checks against disjoint root sets
  (`VERB_ROOT_LEXICON` vs. `NOUN_ROOT_LEXICON`), so `mapanga` still
  correctly fails the verb-slot attempt (no seeded verb root "pang")
  and falls through to the noun branch as before. This table is
  explicitly **not** a phonological rule engine and **not** a general
  vowel-coalescence shape rule — only literal, individually-confirmed
  forms go here. (An earlier draft nearly implemented `haina` as a
  generic "starts with `ha`, ends with `na`" *shape* rule for exactly
  this reason before being corrected — see the negative-have entry
  below for why the actual implementation is safe and that one
  wouldn't have been.)

- **Negative existential** `ha- + subject concord + -na` ("does/did
  not have"), e.g. `haina` = `ha` + `i` (class 9 concord "it") + `na`.
  Implemented as `NEGATIVE_HAVE_PREFIX`/`NEGATIVE_HAVE_SUFFIX` +
  `_try_negative_have()`. This construction went through a real design
  correction worth recording: the first instinct was a whole-word
  exception (leave `haina` unsplit, since which of
  `handina`/`hauna`/`hatina` it might collapse was initially thought
  ambiguous). The user then confirmed directly that `haina` is not a
  collapse of anything — it's `ha`+`i`+`na` on its own terms, class 9
  concord, known with confidence. The construction is safe to implement
  generally (not just for this one word) *because* both ends are fixed
  and the middle must be an **exact** match against the closed
  subject-concord set — not "any characters." This is what protects an
  unrelated word like `hana` ("heart") from false-triggering: its
  middle slice would be empty, which is explicitly rejected. Later
  confirmed to generalize correctly to a *different* concord than the
  one it was built with: running a real story ("sekuru kamba - grandpa
  tortoise") through the parser turned up `havana` ("Sekuru havana
  kutsika zvakanaka" — "Grandpa didn't step properly"), which resolves
  as `ha` + `va` + `na` with no code changes needed — the construction
  was general from the start, this just hadn't been exercised with a
  concord other than `i` before.

- **`[subject prefix] + sati`** ("before [subject] ~s/~ing"), e.g.
  `ndisati` = `ndi` + `sati`. Also revisited mid-build: first pass
  described it as analyzable but implemented it as a whole-word
  exception (contradiction, caught and fixed). The resolving question
  was **productivity**: does `-sati-` combine regularly with other
  subject prefixes, or is `ndisati` a one-off fixed idiom? The user
  confirmed `usati`/`tisati`/`musati`/`chisati` are all real, regular
  forms — so this is a genuine closed grammatical construction (like a
  TAM marker), not a lexical idiom, and deserves its own rule rather
  than a growing whole-word list. Implemented as `_try_sati_construction()`,
  checked before the general verb-slot engine (rather than relying on
  the general engine to fail safely on it) since `sati` is not a root
  and should never be treated like one even by accident.

**The general lesson from this section**, worth restating for a
forking language: when something doesn't fit the regular verb-slot
template, don't force it through that pipeline and don't reflexively
default to "leave it whole" either. Ask specifically: *is the pattern
productive (generalizes across the whole closed set it should), and
are both boundaries of the pattern fixed/closed-class?* If yes to both,
it deserves its own small, tightly-gated rule. If either answer is no
— or genuinely unconfirmed — it stays a whole-word exception rather
than a guessed rule.

## 8. Optional: visually distinguishing grammar tokens

Lute has no built-in concept of "grammatical role" for a token (checked
directly in the installed Lute source, not assumed) — but every
rendered reading-pane span carries a `data-text="<token>"` attribute
(`lute/templates/read/textitem.html`), and Lute already exposes a
**Custom Styles** setting (raw CSS, injected on every page via
`/theme/custom_styles`). Since our grammar tokens are a small,
enumerable, closed set, plain CSS attribute selectors can target them
by exact surface form — no Lute patch required.

`scripts/generate_css.py` reads `rules.py` and prints a ready-to-paste
CSS block (e.g. `span[data-text="mu" i] { font-weight: 600; }`) for
every closed-class form. This is a presentation nicety, deliberately
kept out of the parser package itself.

## 9. Known limitations, deliberately left unresolved in v1

**Calibration from the one real connected text tested so far** (§2's
`sekuru kamba` story): of 123 unique words, 110 (89%) correctly stayed
whole and 13 split, of which 9 were correct out of the box. That's the
realistic expectation right now for unfamiliar real text — most words
stay whole (safe, not wrong, just not yet split), a small fraction
split correctly, and an even smaller fraction need a one-word exception
added after being caught. Expect this ratio to shift toward more
correct splits as `NOUN_ROOT_LEXICON`/`VERB_ROOT_LEXICON` grow from
more real text, not from more reference-grammar mining in the abstract.

- **Most nouns outside the seed lexicon won't split.** Intentional —
  see §3. The seed grew substantially once the noun-classes reference
  document was mined (§2), but it's still a finite, curated list, not
  comprehensive. Grow `NOUN_ROOT_LEXICON` from real text.
- **True lexical homonyms aren't and can't be disambiguated.** `kamba`
  ("small house" via `ka`+`mba`, vs. the indivisible animal name
  "tortoise") is the confirmed example — see §7's `WORD_EXCEPTIONS`
  entry. No morphological signal distinguishes these; this is a
  fundamentally different problem from the branch-ordering collisions
  above it in the same table, and there's no fix beyond "pick the safer
  default and leave it whole" (English has the same issue with words
  like "bank" — no parser fixes this without semantic/contextual
  modeling, out of scope here).
- **Short seeded roots (1-2 letters) are more collision-prone than
  longer ones.** `d` (from `kuda`) is the confirmed case — see the
  `mudiki`/`Vadikisa` entry in §7. Worth being more cautious than usual
  when seeding a new very short root: check whether it could plausibly
  be the tail end of some other common stem after extension-stripping,
  not just whether it's correct in isolation.
- **Vowel-elision at a prefix/stem boundary is unhandled.** Two
  confirmed cases from the noun-classes reference: `chi-` + `uru`
  ("anthill") surfaces as `churu`, not `chiuru`; `zvi-` + `ombo`
  ("weapons") surfaces as `zvombo`, not `zviombo`. Both are a real
  vowel-initial-stem elision process (parallel to the already-handled
  `mu-`→`mw-`/`u-`→`hw-` allomorphs, but here the vowel drops entirely
  rather than the consonant changing), and neither word literally
  contains its class prefix as a substring, so the current
  concatenation-only model can't strip them — they correctly fall back
  to whole-word rather than mis-split, but don't split either. Only one
  or two examples are confirmed so far, not enough to be confident it's
  a fully general "chi-/zvi- + vowel-initial stem" rule (vs. these two
  being lexically specific) — needs more examples before turning into
  an actual rule, same discipline as everywhere else in this document.
- **Handful of confirmed verb/noun branch collisions require one-word
  patches.** `mudzidzisi` and `mukanwa` — see the `WORD_EXCEPTIONS`
  entry in §7 for the mechanism. Expect more of these as the lexicons
  grow; the fix each time is a targeted `WORD_EXCEPTIONS` addition, not
  a structural change (there isn't a clean general fix — see §7's
  closing note on this).
- **Contracted/fused forms beyond the confirmed `PAST_SUBJECT_PREFIXES`
  paradigm are unhandled.** Candidates mentioned but not yet confirmed:
  `handina`/`hauna`/`hatina`/`havana`/`hamuna` (if distinctly spelled
  from forms already covered by the negative-have construction) and the
  `twa-` family.
- **General root reduplication is still unhandled** (repeating the
  *whole root* for intensive/repeated meaning is a distinct Bantu
  mechanism from extension-stacking and isn't modeled). `ndakuisisa`/
  `ndakuisisisa` turned out *not* to need this, though — once traced
  through, they resolve as `nda` + `ku` + a causative extension applied
  twice/thrice, which is just the existing depth-capped
  extension-stripping loop (`test_reduplicated_causative`), not true
  root reduplication. A genuine reduplicated-root case (if one shows up
  in real text) would still fall back safely, since nothing in the
  tables would match it.
- **`chi-` is genuinely ambiguous** between a class-7 subject concord
  and a consecutive/narrative "then" mood marker (confirmed both
  readings exist on the same surface form). The split output is
  identical either way, so this only affects the grammatical label in
  comments, not behavior — but a hypothetical future feature that
  wanted to *display* the grammatical function (not just the split)
  would need actual disambiguation logic that doesn't exist here.
- **No object-concord-on-imperative reading.** `Chiisa` as "then put it
  in" (chi = consecutive marker) vs. a hypothetical "put it (cl.7) in!"
  (chi = object concord on a bare imperative) are both plausible; the
  current slot model has no way to represent the second reading and
  will always produce the first.

## 10. Forking for another Bantu language (e.g. isiXhosa)

This was discussed explicitly before Shona was built: **don't design a
shared `BantuParser` abstraction before a second concrete
implementation exists to compare against.** Guessing which parts
generalize risks building the wrong abstraction and redoing it anyway.
The practical structure already supports a cheap fork without that
abstraction:

1. Copy the package (`lute_shona_parser/` → `lute_xhosa_parser/`, etc.),
   rename the entry point in `pyproject.toml`.
2. **Replace `rules.py` entirely.** It's 100% language-specific data —
   noun class prefixes, verb affix tables, root lexicon seeds, closed
   constructions. Nothing in it should be assumed to transfer.
3. **Start with `morphology.py` and `parser.py` unchanged**, and see
   how far the *engine* (not the data) actually gets you. The
   `SpaceDelimitedParser` subclassing pattern (§4) and the general
   "peel prefixes, peel suffixes, root lexicon as the anchor" strategy
   (§3, §6) are reasonable bets that they'll generalize across Bantu
   languages, since the underlying noun-class/verb-slot morphology is
   structurally similar across the family. But treat that as a
   hypothesis, not a guarantee — isiXhosa's specific affix inventory,
   click consonants, and phonological rules (e.g. its own vowel
   coalescence and palatalization patterns) are not Shona's, and there
   will likely be constructions (like §7's negative-have and `sati`
   patterns) that are Shona-specific idioms with no isiXhosa
   equivalent, and vice versa.
4. **Only after a second language is actually working**, compare the
   two `morphology.py` files. If they turn out identical or near-
   identical, *that's* the point to extract a genuine shared
   `BantuParser` base class with per-language `rules.py` data —
   informed by two real data points instead of a guess.
5. Expect to need the same category of judgment calls this build hit
   repeatedly: does a given irregular form belong in a whole-word
   exception list, or is it a productive closed construction that
   deserves its own small rule? The deciding question is always the
   same (§7's closing paragraph): is it productive, and are its
   boundaries closed-class? When genuinely unsure, default to the
   whole-word exception — under-splitting is always the safe failure
   mode in this design, for any Bantu language.

## 11. A note on process

Several decisions in this document were made, then revisited, then
corrected — the terminal-vowel-as-separate-token reversal (§5), the
`haina` and `ndisati` reclassifications from "leave whole" to "small
dedicated rule" (§7), `ndakuisisa`/`ndakuisisisa` going from
"whole-word exception" to "resolved by existing machinery" once `nda`
was properly sourced, and `nda` itself being upgraded from a one-off
"contracted form" to the confirmed `PAST_SUBJECT_PREFIXES` paradigm
once a fuller pronoun/concord reference document was found (§7). This
wasn't churn: each correction came from getting more specific, more
confirmed information (a native/fluent speaker's direct confirmation,
an academic citation, or a concrete counter-example) than was available
when the earlier version was written. The lesson for future
maintenance: when a design decision here turns out to conflict with
newly confirmed information, **prefer fixing the decision over
preserving consistency with earlier work** — but always check for and
fix side effects on other rules that were built assuming the old
decision. Two concrete instances of this in the actual history: the
`ndakuisisa` exception was *added* specifically because `nda` becoming
a real prefix had a side effect that needed containing at the time, and
was later *removed* once the reduplicated-causative reading was
confirmed and the side effect was no longer a risk — both the adding
and the removing were the correct move at their respective points, not
a contradiction.
