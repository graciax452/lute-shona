"""
Shona morpheme-splitting engine.

Pure functions, no Lute dependency -- exercised directly by
tests/test_morphology.py without needing Lute installed.

Design: lexicon-gated stripping, not blind string-matching. A candidate
noun-class prefix or verb subject/TAM/object/extension affix is only
accepted if what remains after stripping it resolves to a known root in
NOUN_ROOT_LEXICON / VERB_ROOT_LEXICON. This avoids "overstemming" (a
documented failure mode of naive rule-based agglutinative parsing --
see Swahili SALAMA/xsma): a word that merely happens to start with a
prefix-shaped string, like "mvura" ("water") starting with what looks
like it could be stripped, is left whole rather than mangled, because
the remainder never resolves to a real root. The cost is lower split
coverage for anything not yet in the seed lexicons; that's accepted
because a wrong split teaches wrong grammar, which is worse than no
split at all. Grow rules.NOUN_ROOT_LEXICON / VERB_ROOT_LEXICON as real
text surfaces words worth adding.

The verb-slot branch is tried before the noun-prefix branch because
Bantu subject concords and noun class prefixes legitimately share
surface forms (mu-, va-, chi-, ...) -- the branch requiring more
structure to succeed (a validated root *and* a valid terminal vowel)
goes first to reduce cross-contamination between the two guesses.
"""

from typing import List, Optional

from lute_shona_parser.rules import (
    NEGATIVE_HAVE_PREFIX,
    NEGATIVE_HAVE_SUFFIX,
    NOUN_CLASS_PREFIXES,
    NOUN_ROOT_LEXICON,
    OBJECT_MARKERS,
    PAST_SUBJECT_PREFIXES,
    PROPER_NOUNS,
    SATI_SUFFIX,
    TAM_MARKERS,
    TERMINAL_VOWELS,
    VERB_EXTENSIONS,
    VERB_ROOT_LEXICON,
    VERB_SUBJECT_PREFIXES,
    WORD_EXCEPTIONS,
)

_SUBJECT_PREFIXES_BY_LENGTH = sorted(
    set(VERB_SUBJECT_PREFIXES) | set(PAST_SUBJECT_PREFIXES), key=len, reverse=True
)
_NOUN_PREFIXES_BY_LENGTH = sorted(NOUN_CLASS_PREFIXES, key=lambda p: len(p[0]), reverse=True)
_EXTENSIONS_BY_LENGTH = sorted(VERB_EXTENSIONS, key=len, reverse=True)


def split_word(word: str) -> List[str]:
    """
    Split a single space-delimited Shona word into its morphemes.

    Returns a list of substrings of `word` that concatenate back to
    `word` exactly (required by Lute's ParsedToken contract). Falls
    back to `[word]` whenever no branch produces a confident,
    lexicon-backed match.
    """
    if not word:
        return [word]

    if word[0:1].isupper() and word in PROPER_NOUNS:
        return [word]

    lword = word.lower()

    if lword in WORD_EXCEPTIONS:
        return [word]

    negative_have = _try_negative_have(word, lword)
    if negative_have is not None:
        return negative_have

    sati = _try_sati_construction(word, lword)
    if sati is not None:
        return sati

    infinitive = _try_infinitive(word, lword)
    if infinitive is not None:
        return infinitive

    verb = _try_verb_slot(word, lword)
    if verb is not None:
        return verb

    noun = _try_noun(word, lword)
    if noun is not None:
        return noun

    return [word]


def _try_negative_have(word: str, lword: str) -> Optional[List[str]]:
    """
    ha- + subject concord + -na ("does/did not have"), e.g. haina =
    ha + i (cl.9 concord) + na. Both ends are fixed; the middle is
    only accepted on an *exact* match against a known subject concord
    -- not "any letters" -- so this can't fire on an unrelated word
    that merely starts with "ha" and ends with "na" (e.g. "hana",
    heart: middle would be empty and gets rejected below).
    """
    if not lword.startswith(NEGATIVE_HAVE_PREFIX) or not lword.endswith(NEGATIVE_HAVE_SUFFIX):
        return None
    prefix_len = len(NEGATIVE_HAVE_PREFIX)
    suffix_len = len(NEGATIVE_HAVE_SUFFIX)
    middle = lword[prefix_len:-suffix_len]
    if middle and (middle in VERB_SUBJECT_PREFIXES or middle in PAST_SUBJECT_PREFIXES):
        return [
            word[:prefix_len],
            word[prefix_len : prefix_len + len(middle)],
            word[prefix_len + len(middle) :],
        ]
    return None


def _try_sati_construction(word: str, lword: str) -> Optional[List[str]]:
    """
    Subject prefix + -sati ("before [subject] ~s/~ing"), e.g.
    ndisati = ndi + sati. "sati" must be the entire remainder after
    the subject prefix -- nothing else follows it in the word.
    """
    if not lword.endswith(SATI_SUFFIX):
        return None
    prefix_candidate = lword[: -len(SATI_SUFFIX)]
    if prefix_candidate and (
        prefix_candidate in VERB_SUBJECT_PREFIXES or prefix_candidate in PAST_SUBJECT_PREFIXES
    ):
        split_at = len(prefix_candidate)
        return [word[:split_at], word[split_at:]]
    return None


def _try_infinitive(word: str, lword: str) -> Optional[List[str]]:
    "ku- + verb root (class 15 infinitive), disambiguated from the identically-spelled class 15/17 noun prefix by requiring a root-lexicon hit."
    if not lword.startswith("ku"):
        return None
    stem_tokens = _resolve_stem(word[2:])
    if stem_tokens is None:
        return None
    return [word[:2]] + stem_tokens


def _try_verb_slot(word: str, lword: str) -> Optional[List[str]]:
    "subject prefix + optional TAM + optional object marker + resolved stem."
    for subj in _SUBJECT_PREFIXES_BY_LENGTH:
        if not lword.startswith(subj):
            continue
        subj_label = word[: len(subj)]
        after_subj = word[len(subj) :]
        lafter_subj = after_subj.lower()

        tam_matches = [t for t in TAM_MARKERS if lafter_subj.startswith(t)]
        for tam in sorted(tam_matches, key=len, reverse=True) + [None]:
            after_tam = after_subj[len(tam) :] if tam else after_subj
            lafter_tam = after_tam.lower()

            obj_matches = [o for o in OBJECT_MARKERS if lafter_tam.startswith(o)]
            for obj in sorted(obj_matches, key=len, reverse=True) + [None]:
                after_obj = after_tam[len(obj) :] if obj else after_tam
                stem_tokens = _resolve_stem(after_obj)
                if stem_tokens is None:
                    continue
                tokens = [subj_label]
                if tam:
                    tokens.append(after_subj[: len(tam)])
                if obj:
                    tokens.append(after_tam[: len(obj)])
                tokens.extend(stem_tokens)
                return tokens
    return None


def _try_noun(word: str, lword: str) -> Optional[List[str]]:
    "longest-matching noun class prefix, gated on the remaining stem being a known root."
    for prefix, _class_id in _NOUN_PREFIXES_BY_LENGTH:
        if not lword.startswith(prefix):
            continue
        stem = word[len(prefix) :]
        if stem and stem.lower() in NOUN_ROOT_LEXICON:
            return [word[: len(prefix)], stem]
    return None


def _resolve_stem(remainder: str) -> Optional[List[str]]:
    """
    Resolve a verb stem (root + optional extensions + terminal vowel),
    working from both ends toward the middle: the terminal vowel and
    any extensions are peeled from the right during analysis (needed
    to correctly locate the root boundary), and the root lexicon is
    the anchor in the middle that confirms the whole chain of guesses
    was actually correct. The terminal vowel itself is never emitted
    as its own token, though -- it's merged back onto whichever
    morpheme ends up last (the extension if one was found, otherwise
    the root) before returning, e.g. vachamubikira resolves to
    ["bik", "ira"], not ["bik", "ir", "a"] (see TERMINAL_VOWELS in
    rules.py for why: a lone Latin letter is low-value, noisy, and
    easy to mis-click as its own token).

    Tries direct root match first, then one stripped extension, then
    two (capped -- covers common causative+passive-style stacking,
    e.g. kuisiswa = ku+is+is+wa, without unbounded search). Stops at
    the *first* level that produces a lexicon hit -- the shallowest,
    least-stripped match always wins, even if a deeper strip would
    also technically resolve. This is what keeps a word like "isa"
    (root "-is-", also the causative extension form) as one root
    instead of being fake-decomposed just because the string allows
    it -- kuisa must resolve at the direct-hit check below before the
    extension-stripping loops ever run.

    Extensions are stripped from the end of the word inward (closest
    to the terminal vowel first), which happens to match the Bantu
    CARP ordering constraint (extensions attach Causative before
    Applicative before Reciprocal before Passive), so this order isn't
    arbitrary.
    """
    if len(remainder) < 2:
        return None
    lremainder = remainder.lower()
    if lremainder[-1] not in TERMINAL_VOWELS:
        return None

    tv = remainder[-1]
    body = lremainder[:-1]
    orig_body = remainder[:-1]

    if body in VERB_ROOT_LEXICON:
        return [orig_body + tv]

    for ext in _EXTENSIONS_BY_LENGTH:
        if not body.endswith(ext):
            continue
        root = body[: -len(ext)]
        if root and root in VERB_ROOT_LEXICON:
            orig_root = orig_body[: len(root)]
            orig_ext = orig_body[len(root) :]
            return [orig_root, orig_ext + tv]

    for ext1 in _EXTENSIONS_BY_LENGTH:
        if not body.endswith(ext1):
            continue
        mid = body[: -len(ext1)]
        for ext2 in _EXTENSIONS_BY_LENGTH:
            if not mid.endswith(ext2):
                continue
            root = mid[: -len(ext2)]
            if root and root in VERB_ROOT_LEXICON:
                orig_root = orig_body[: len(root)]
                orig_ext2 = orig_body[len(root) : len(root) + len(ext2)]
                orig_ext1 = orig_body[len(root) + len(ext2) :]
                return [orig_root, orig_ext2, orig_ext1 + tv]

    return None
