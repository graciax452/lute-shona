"""
Data tables for Shona morpheme splitting.

Every table here is plain data (no matching logic — see morphology.py
for that). The design priority is that a root is only ever split off
when we're confident it's correct, not maximum split coverage. Grow
these tables from real reading text as gaps show up.

Primary source for noun classes/pronouns as of this revision: a
structured reference document ("3 Noun Classes.pdf") covering all 21
noun classes with concrete example nouns per class, plus a full
personal-pronoun/concord table (basic + past subject concords, object
markers, possessives, demonstratives). This superseded the earlier
"best effort, handful of examples" sourcing for several tables below —
noted per table where it applies.
"""

# Proper nouns / names. Checked first, before anything else, and only
# against the ORIGINAL-cased word (must be capitalized). Shona names are
# often spelled identically to ordinary words (Kuda "to want/love" vs.
# Kuda the name), so there is no way to tell them apart from spelling or
# position alone -- a curated list that always wins for these exact
# strings is the only honest option. This means a genuine sentence-
# initial capitalized use of the ordinary word will also be treated as
# the name if it's in this list; that's an accepted tradeoff (under-
# splitting is the safe failure mode throughout this whole design).
# "Chipo" added as a confirmed class 1a proper-noun example from the
# noun-classes reference. Honorific "Va-" + surname forms (VaGumbo,
# VaNdingoveni, also from that reference) deliberately do NOT need an
# entry here -- they already stay whole for free, since "va-" matches
# the ordinary class 2/2a noun prefix but the surname stem (e.g.
# "Gumbo") is never going to be in NOUN_ROOT_LEXICON (surnames are as
# open-ended as any other proper noun), so the lexicon gate blocks the
# split automatically. Replace/expand PROPER_NOUNS from names actually
# used in your own material.
PROPER_NOUNS = {
    "Kuda",
    "Tendai",
    "Rutendo",
    "Chiedza",
    "Chipo",
    "Kamba",  # "Sekuru Kamba" (Grandpa Tortoise), the character name in
              # a real story tested against this parser -- without this,
              # "Kamba" wrongly split as ka+mba ("small house"); see the
              # WORD_EXCEPTIONS note on lowercase "kamba" for the same
              # collision when it isn't capitalized.
}

# Whole-word bypasses, checked before any splitting is attempted.
# Three kinds of entries live here:
#   - words that would otherwise coincidentally match a pattern and
#     mis-split
#   - confirmed-but-genuinely-ambiguous forms where splitting would mean
#     guessing (e.g. which subject a contracted negative encodes) -- and
#     guessing wrong teaches incorrect grammar, which is worse than
#     showing the whole word.
#   - real verb/noun branch collisions: words where the noun-prefix
#     reading is correct but the verb-slot branch (tried first, see
#     morphology.py) *also* happens to resolve against the verb lexicon,
#     and wins by running first. Both found empirically by dry-running
#     every example from the noun-classes reference against the actual
#     code, not by inspection -- exactly the kind of case the module
#     docstring's "cross-contamination" warning was anticipating in the
#     abstract, now with concrete instances:
#       - "mudzidzisi" ("teacher", cl.1 mu- + whole noun "dzidzisi") --
#         verb-slot wrongly resolves it as mu- (subject) + dzidz-
#         (root, "learn") + -is- (causative) + -i, because "dzidz" is a
#         seeded verb root and the causative-extension strip happens to
#         land on it.
#       - "mukanwa" ("mouth", cl.18 locative mu- + "kanwa") -- verb-slot
#         wrongly resolves it as mu- (subject) + -ka- (past TAM) + nwa
#         (root, "drink"), i.e. "you(pl) drank", because "nw" is a
#         seeded verb root.
#     Both are one-word patches, not a fix to the underlying ambiguity
#     (there isn't a clean general fix -- see DESIGN.md). Expect more of
#     these to surface as the lexicons grow; add them here as found.
#   - true homonyms, where two genuinely different real words share a
#     spelling and there's no morphological signal to pick between them:
#       - "kamba" -- can be ka+mba ("small house", regular diminutive)
#         or the indivisible animal name "tortoise". Confirmed from a
#         real story ("Sekuru Kamba", Grandpa Tortoise) where it means
#         tortoise every time it appears. Left whole rather than
#         defaulting to the "small house" split: the diminutive reading
#         is fully regular and recognizable even shown as one word,
#         while "tortoise" is a specific vocabulary item that needs
#         accurate whole-word tracking -- same undersplit-by-default
#         tradeoff as everywhere else, just applied to a true lexical
#         homonym instead of a branch-ordering collision.
#       - "mudiki"/"vadikisa" -- "diki" ("small") is a common adjective
#         stem that combines with noun-class-agreement prefixes exactly
#         like a noun (mudiki, vadiki, chidiki, ...). It collides with
#         VERB_ROOT_LEXICON's "d" (from kuda) via depth-2 extension
#         stripping: mudiki -> mu+d+ik+i, vadikisa -> va+d+ik+isa, both
#         wrong. This is a more systemic risk than the two collisions
#         above -- any "diki"-derived form is likely affected by the
#         same coincidence, since a 1-letter seeded root like "d" is
#         unusually easy to land on by accident. Only the two forms
#         actually seen in real text are listed; add siblings (vadiki,
#         chidiki, zvidiki, tudiki, kadiki, ...) as they show up rather
#         than guessing the whole family preemptively.
# "ndakuisisa"/"ndakuisisisa" used to live here too (reduplication of
# the "is" root, morpheme boundary unconfirmed) but have since been
# resolved -- see the note on PAST_SUBJECT_PREFIXES below -- and now
# split correctly via the general engine, so they were removed. This
# table is a two-way street: entries get added when a collision is
# found, and removed once the underlying rule is confirmed and the
# collision no longer applies -- don't leave stale exceptions around.
WORD_EXCEPTIONS = {
    "mudzidzisi",
    "mukanwa",
    "kamba",
    "mudiki",
    "vadikisa",
}

# Past subject concords -- a confirmed, complete paradigm (not one-off
# contractions), sourced directly from the personal-pronoun/concord
# table in the noun-classes reference: 1sg ndi-/nda-, 2sg u-/wa-, 3sg
# a-/a- (unchanged), 1pl ti-/ta-, 2pl mu-/ma-, 3pl va-/va- (unchanged).
# Only the forms that actually differ from the basic subject concord
# are listed here (3sg and 3pl are identical in both tenses, so adding
# them again would be a no-op). Matched the same way as
# VERB_SUBJECT_PREFIXES (see morphology.py) -- this is a real,
# confirmed tense-marking paradigm, not a phonological rule engine and
# not a general shape rule. "nda" (1sg) additionally corroborated by
# Aranovich (2015) on Shona verb morphology: "the simple past form
# nda-tora 'I took' is formed with the prefix nda- '1.SG.PAST' attached
# directly to the root."
# Note: "ma" (2pl past) is the same surface string as the class 6 noun
# prefix ("ma-", e.g. mapanga) -- verified this doesn't cause
# regressions, since the lexicon gate on each side uses disjoint root
# sets (VERB_ROOT_LEXICON vs NOUN_ROOT_LEXICON), so a word like
# "mapanga" correctly fails the verb-slot attempt (no seeded verb root
# "pang") and falls through to the noun branch as before.
# Candidates to verify and add later: handina/hauna/hatina/hamuna (if
# those turn out to be spelled distinctly from the ambiguous "haina")
# and the twa- family. ("havana" doesn't belong on this list -- it's
# not a contracted/past-tense form at all, it's the regular negative-
# have construction (ha- + va concord + -na, "did not") with a
# different subject concord than "haina"'s. Confirmed working already
# via _try_negative_have, from a real story: "Sekuru havana kutsika
# zvakanaka" -- see tests/test_morphology.py's
# test_grandpa_tortoise_story_correct_splits.)
PAST_SUBJECT_PREFIXES = {
    "nda": "1sg past",
    "wa": "2sg past",
    "ta": "1pl past",
    "ma": "2pl past",
}

# Noun class prefixes (morphology.py sorts these by length at match time,
# so e.g. "vana" is always tried before "va" regardless of table order
# here). Zero/complex-surface classes (1a, 5, 9 [most forms], 10 [most
# forms], 17a) are excluded -- either there's nothing to strip, or (for
# most of class 5/9/10) the "prefix" only ever surfaces as a consonant
# mutation or prenasalization fused into the stem, not a separable
# string (e.g. class 5 /ri-/ + -panga -> banga; class 9 N- + -mombe ->
# mombe) -- not modeled here, see DESIGN.md. The two classes that *do*
# show a clean, separable prefix on some/most nouns -- class 9 "i-"
# (imba) and class 10 "dzi-" (dzimba) -- are included. Allomorphs
# included: mw- for mu- (before vowel-initial stems), hw- and hu- for
# u- (both attested for class 14 -- hw- specifically before vowel-
# initial stems per the source notes, hu- attested in "hupenzi"), rw-
# for ru- (before vowel-initial stems, e.g. rwizi, rwaivhi). Class 19
# (svi-, diminutive, Karanga dialect) included as confirmed but
# genuinely low-frequency outside that dialect.
NOUN_CLASS_PREFIXES = [
    ("vana", "2a"),
    ("mu", "1"),
    ("mw", "1"),
    ("va", "2"),
    ("mi", "4"),
    ("ma", "6"),
    ("chi", "7"),
    ("zvi", "8"),
    ("i", "9"),
    ("dzi", "10"),
    ("ru", "11"),
    ("rw", "11"),
    ("ka", "12"),
    ("tu", "13"),
    ("hw", "14"),
    ("hu", "14"),
    ("u", "14"),
    ("ku", "15"),  # also class 17 locative; infinitive handled separately
    ("pa", "16"),
    ("svi", "19"),
    ("zi", "21"),
    ("a", "2b"),  # amai, ambuya -- kinship terms; verified this doesn't
                  # collide with the identically-spelled 3sg verb subject
                  # concord "a-", since the verb-slot branch (tried
                  # first) fails to resolve on both confirmed examples
                  # and correctly falls through to this noun branch.
]

# Noun roots. The exact-match requirement in _try_noun (the full
# remainder after the prefix must equal a lexicon entry, not just
# start with one) means even short entries like "do" or "ti" carry no
# incremental overstemming risk -- they only ever match when they are
# the *entire* remaining stem.
#
# Two kinds of entries:
#  - bare roots (the normal case)
#  - whole already-prefixed nouns, added as their own entries alongside
#    the bare root, for the confirmed pattern where a *second* prefix
#    (locative pa-/ku-/mu-, or diminutive ka-/tu-) attaches to an
#    already-prefixed noun rather than the bare root -- e.g. mumunda
#    (cl.18 locative + "munda", not the bare root "nda"), pamusoro
#    (pa- + "musoro", not bare "soro"), kamunhu (ka- + "munhu", not
#    bare "nhu"). Marked "(whole noun)" below.
#
# Source: the noun-classes reference document's per-class example
# tables (all comments below cite the specific example word(s) that
# confirm each entry), plus the original xlsx seed carried over from
# the first version of this file.
NOUN_ROOT_LEXICON = {
    # class 1 (mu-/mw-)
    "nhu",      # munhu / vanhu / chinhu / zvinhu
    "komana",   # mukomana, also vakomana (cl.2), tukomana (cl.13)
    "kadzi",    # mukadzi, also vakadzi (cl.2), chikadzi (cl.7), zvikadzi (cl.8)
    "dzidzisi", # mudzidzisi
    "enga",     # mwenga
    "eni",      # mweni, also vaeni (cl.2)
    # class 2/2a/2b (va-/vana-/a-)
    "rapi",     # varapi
    "sahwira",  # vasahwira
    "tete",     # vatete
    "tezvara",  # vanatezvara
    "mai",      # amai
    "mbuya",    # ambuya
    # class 3 (mu-/mw-)
    "sasa",     # musasa
    "soro",     # musoro
    "musoro",   # pamusoro (whole noun -- locative pa- on the already-prefixed noun)
    "ando",     # mwando
    "kaka",     # mukaka
    "namato",   # munamato, also minamato (cl.4)
    # class 4 (mi-/mw-)
    "ti",       # miti
    "sika",     # misika
    "romo",     # miromo
    "riwo",     # miriwo
    # class 5 -- zero/mutated surface, not modeled; roots harvested below
    # only where they're independently confirmed via another class's
    # visible prefix (panga via class 6 mapanga, bhasikoro via class 6
    # mabhasikoro).
    # class 6 (ma-)
    "panga",    # mapanga (cl.6 plural of cl.5 banga)
    "kudo",     # makudo
    "bhasikoro",# mabhasikoro
    "virira",   # mavirira
    "hombekombe", # mahombekombe
    # class 7/8 (chi-/zvi-)
    "ngwa",     # chingwa, zvingwa
    "muti",     # chimuti, also kamuti (cl.12), tumuti (cl.13)
    "huta",     # zvihuta
    "ombo",     # zvombo
    # class 9/10 -- mostly zero/prenasalized surface, not modeled;
    # "mba" (below) is the one clean case with a visible i-/dzi- prefix.
    "mba",      # imba (cl.9, i-), dzimba (cl.10, dzi-), also pamba (cl.16), kamba (cl.12), tumba (cl.13)
    # class 11 (ru-/rw-)
    "kuni",     # rukuni
    "betsero",  # rubetsero
    "do",       # rudo
    "izi",      # rwizi
    "rwizi",    # kurwizi (whole noun -- locative ku- on the already-prefixed noun)
    "aivhi",    # rwaivhi
    # class 12/13 (ka-/tu-)
    "mbuyu",    # kambuyu, tumbuyu
    "munhu",    # kamunhu (whole noun -- diminutive ka- on the already-prefixed cl.1 noun mu+nhu)
    "vanhu",    # tuvanhu (whole noun -- diminutive tu- on the already-prefixed cl.2 noun va+nhu)
    "sikana",   # kasikana, also svisikana (cl.19)
    # class 14 (u-/hw-/hu-)
    "pfu",      # upfu
    "penyu",    # upenyu
    "penzi",    # hupenzi
    "tsinye",   # utsinye
    "tsi",      # utsi
    # class 16/17/18 (pa-/ku-/mu-)
    "chikomo",  # pachikomo (whole noun -- "chikomo" itself is chi- + a stem not independently confirmed as a standalone example, so seeded as one unit)
    "ruware",   # paruware (whole noun, same reasoning as chikomo)
    "nzvimbo",  # panzvimbo ("on the place" -- source table shows "panvimbo", almost certainly an OCR-dropped "z"; using the standard spelling)
    "musha",    # kumusha
    "tsime",    # kutsime
    "gwenga",   # kugwenga
    "chechi",   # kuchechi
    "kanwa",    # mukanwa
    "dura",     # mudura
    "poto",     # mupoto
    "fafitera", # mufafitera
    "nda",      # munda (bare root, class 3)
    "munda",    # mumunda (whole noun -- locative mu- on the already-prefixed noun, class 18)
    "mota",     # mumota
    # class 19 (svi-, Karanga dialect diminutive)
    "mbudzi",   # svimbudzi
    "muto",     # svimuto
    # ("mvura" deliberately NOT seeded, even though the source shows
    # svimvura -- kept unseeded so tests/test_morphology.py has a
    # reliably-unseeded word to demonstrate safe fallback with.)
    # class 21 (zi-)
    "gomana",   # zigomana
    "dzoro",    # zidzoro
    "gora",     # zigora
    "dofo",     # zidofo
    "bhuku",    # zibhuku
    "huku",     # huku (class 9/10, zero-prefix -- kept for completeness, doesn't enable any split on its own)
}

# Closed set of word-initial verbal markers -- basic (present-tense-
# neutral) subject concords, sourced from the personal-pronoun table in
# the noun-classes reference (1sg ndi-, 2sg u-, 3sg a-, 1pl ti-, 2pl
# mu-, 3pl va-) plus noun-class concords for classes without a distinct
# person (confirmed alongside each class's entry in that same
# document). Some entries (e.g. "chi") do double duty as both a
# noun-class subject concord and a consecutive/narrative "then" mood
# marker in real usage -- same surface form, different grammatical
# function, but the split output is identical either way, so only the
# label differs, not the matching behaviour.
VERB_SUBJECT_PREFIXES = {
    "ndi": "1sg",
    "u": "2sg",
    "a": "3sg (cl.1)",
    "i": "cl.9 concord",
    "ti": "1pl",
    "mu": "2pl / cl.1,3,18 concord",
    "va": "3pl (cl.2) concord",
    "chi": "cl.7 concord / consecutive 'then'",
    "zvi": "cl.8 concord",
    "ri": "cl.5 concord",
    "dzi": "cl.10 concord",
    "ru": "cl.11 concord",
    "pa": "cl.16 concord",
}

# Negative existential "ha- + subject concord + -na" ("does/did not
# have"), e.g. haina = ha + i (cl.9 concord) + na. Both ends are fixed,
# closed-class pieces, and the middle is only accepted if it's an exact
# match against VERB_SUBJECT_PREFIXES/PAST_SUBJECT_PREFIXES -- unlike
# a bare "starts with ha, ends with na" shape rule, this can't fire on
# an unrelated word like "hana" (heart), since its middle would be
# empty and gets rejected (see morphology.py's _try_negative_have).
NEGATIVE_HAVE_PREFIX = "ha"
NEGATIVE_HAVE_SUFFIX = "na"

# Subject prefix + -sati ("before [subject] ~s/~ing"), e.g. ndisati =
# ndi + sati, musati = mu + sati, chisati = chi + sati. Confirmed
# productive by the user (usati/tisati/musati/chisati all real, regular
# forms, not just the one example) -- a closed grammatical
# construction, not a normal verb: no TAM, no object marker, no root,
# no extension, no terminal vowel, and "sati" is the entire remainder
# (nothing else follows it in the word). Matched separately from the
# general verb-slot engine rather than relying on it to fail safely,
# since "sati" isn't a root and shouldn't ever be treated like one.
SATI_SUFFIX = "sati"

# TAM (tense/aspect/mood) markers, infixed between subject prefix and
# object marker/root. Scoped to exactly what was confirmed -- easy to
# extend (e.g. aka, ari) once more forms are confirmed from real text.
# (Past tense is handled separately, via PAST_SUBJECT_PREFIXES replacing
# the basic subject concord entirely, not as a TAM infix -- that's how
# the source material models it, as a distinct concord paradigm.)
TAM_MARKERS = {
    "no": "present habitual/progressive",
    "cha": "future",
    "ka": "past/narrative",
}

# Object markers, infixed immediately before the root. Confirmed via
# the personal-pronoun table (1sg -ndi-, 2sg -ku-, 3sg -mu-, 1pl -ti-,
# 3pl -va-) plus "chi" (cl.7), confirmed directly by the user via
# ndakuisisa ("I made you put it"), ndamuisisa ("I made her/him put
# it"), ndachiisisa ("I made it put it", cl.7) -- same surface forms as
# the subject-prefix/noun-prefix tables, different grammatical slot,
# completely normal syncretism in Bantu concord systems.
OBJECT_MARKERS = {
    "ndi": "me",
    "ku": "you (sg)",
    "mu": "him/her (cl.1)",
    "chi": "it (cl.7)",
    "ti": "us",
    "va": "them (cl.2)",
    "zvi": "reflexive",
}

# Derivational verb extensions, attach between root and terminal vowel.
# Stripped from the end of the word inward -- passive/reciprocal/
# applicative-shaped suffixes sit closer to the terminal vowel than
# causative, which matches the Bantu CARP ordering constraint (extensions
# attach Causative -> Applicative -> Reciprocal -> Passive), so stripping
# innermost-first isn't arbitrary.
VERB_EXTENSIONS = {
    "ir": "applicative",
    "er": "applicative",
    "is": "causative",
    "es": "causative",
    "w": "passive",
    "iw": "passive",
    "an": "reciprocal",
    "ik": "stative",
    "ek": "stative",
}

# Seed verb roots. "bik" (cook) and "is" (put) are included beyond the
# original 14 infinitives specifically because they're needed by the
# worked/stress-test examples used to validate this design -- "is" is
# also identical to the causative extension form, making it the key
# disambiguation test case (see morphology.py docstring). "pfek"
# (kupfeka, "the way one dresses") added from the class 15 infinitive
# examples in the noun-classes reference.
VERB_ROOT_LEXICON = {
    "famb",   # kufamba - walk
    "tend",   # kutenda - thank
    "gar",    # kugara - sit
    "mir",    # kumira - stand
    "uy",     # kuuya - come
    "end",    # kuenda - go
    "dy",     # kudya - eat
    "d",      # kuda - want/love
    "nyor",   # kunyora - write
    "vereng", # kuverenga - read
    "terer",  # kuterera - listen
    "on",     # kuona - see
    "nw",     # kunwa - drink
    "dzidz",  # kudzidza - learn
    "bik",    # kubika - cook
    "is",     # kuisa - put
    "pfek",   # kupfeka - the way one dresses
}

# Never emitted as their own token. Stripped from the right during
# analysis (needed to correctly locate the root/extension boundary --
# see morphology.py's stem resolver), then merged back onto whichever
# morpheme is last (the extension if one was found, otherwise the
# root) before the final token list is returned. A single Latin letter
# carries almost no standalone information and would be visually
# noisy/easy to mis-click as its own token.
TERMINAL_VOWELS = {"a", "e", "i"}
