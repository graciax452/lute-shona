"""
Automated collision detector for lute_shona_parser's lexicons.

Ported from lute-xhosa's scripts/check_collisions.py -- see that
file's docstring for the full rationale. Scans for words where the
verb-slot branch (subject + optional TAM + optional object + a
VERB_ROOT_LEXICON root + terminal vowel) produces a surface string
that exactly matches a noun-slot surface string (a NOUN_CLASS_PREFIXES
prefix + a NOUN_ROOT_LEXICON root). Since _try_verb_slot always runs
before _try_noun in morphology.py, any such match is a real collision
risk -- checked here against split_word() directly, since Shona's
split_word() now prefers the noun reading when it has fewer tokens
(and the longer first-token match on ties), so most of these resolve
correctly on their own; this script reports what's left.

Run with: python scripts/check_collisions.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lute_shona_parser.rules import (
    NOUN_CLASS_PREFIXES,
    NOUN_ROOT_LEXICON,
    OBJECT_MARKERS,
    PAST_SUBJECT_PREFIXES,
    TAM_MARKERS,
    TERMINAL_VOWELS,
    VERB_ROOT_LEXICON,
    VERB_SUBJECT_PREFIXES,
    WORD_EXCEPTIONS,
)
from lute_shona_parser.morphology import split_word


def build_noun_surface_index():
    """word -> list of (prefix, root) pairs that produce it."""
    index = {}
    for prefix, _cls in NOUN_CLASS_PREFIXES:
        for root in NOUN_ROOT_LEXICON:
            word = prefix + root
            index.setdefault(word, []).append((prefix, root))
    return index


def find_collisions():
    noun_index = build_noun_surface_index()
    subjects = sorted(set(VERB_SUBJECT_PREFIXES) | set(PAST_SUBJECT_PREFIXES))
    tams = [None] + sorted(TAM_MARKERS)
    objs = [None] + sorted(OBJECT_MARKERS)

    collisions = []
    for subj in subjects:
        for tam in tams:
            for obj in objs:
                prefix_part = subj + (tam or "") + (obj or "")
                for root in VERB_ROOT_LEXICON:
                    for tv in TERMINAL_VOWELS:
                        word = prefix_part + root + tv
                        if word in WORD_EXCEPTIONS:
                            continue
                        if word in noun_index:
                            collisions.append(
                                {
                                    "word": word,
                                    "verb_analysis": (subj, tam, obj, root, tv),
                                    "noun_analyses": noun_index[word],
                                }
                            )
    return collisions


def main():
    collisions = find_collisions()
    seen = {}
    for c in collisions:
        seen.setdefault(c["word"], c)
    collisions = sorted(seen.values(), key=lambda c: c["word"])

    print(f"Scanned {len(VERB_SUBJECT_PREFIXES) + len(PAST_SUBJECT_PREFIXES)} subjects x "
          f"{len(TAM_MARKERS) + 1} TAM options x {len(OBJECT_MARKERS) + 1} object options x "
          f"{len(VERB_ROOT_LEXICON)} verb roots x {len(TERMINAL_VOWELS)} terminal vowels.")
    print(f"{len(collisions)} words have BOTH a valid verb-slot reading and a valid "
          f"noun reading (WORD_EXCEPTIONS entries already excluded).\n")

    resolved_correctly = []
    still_verb = []
    for c in collisions:
        actual = split_word(c["word"])
        subj, tam, obj, root, tv = c["verb_analysis"]
        verb_tokens = [subj]
        if tam:
            verb_tokens.append(tam)
        if obj:
            verb_tokens.append(obj)
        verb_tokens.append(root + tv)
        if actual == verb_tokens:
            still_verb.append((c, actual))
        else:
            resolved_correctly.append(c)

    print(f"Already resolved correctly by the branch-preference fix: {len(resolved_correctly)}")
    print(f"Still resolving to the verb reading (token-count tie, both branches produce "
          f"2 tokens): {len(still_verb)}\n")

    harmless_ties = []
    real_ties = []
    for c, actual in still_verb:
        noun_token_sets = [[p, r] for p, r in c["noun_analyses"]]
        if actual in noun_token_sets:
            harmless_ties.append((c, actual))
        else:
            real_ties.append((c, actual))

    print(f"  Of which harmless (verb boundary == some valid noun boundary): {len(harmless_ties)}")
    print(f"  Of which genuinely conflicting boundaries (real, unresolved): {len(real_ties)}\n")

    print("--- Genuinely conflicting ties (sample, first 40) ---")
    for c, actual in real_ties[:40]:
        subj, tam, obj, root, tv = c["verb_analysis"]
        verb_str = f"{subj}+" + (f"{tam}+" if tam else "") + (f"{obj}+" if obj else "") + f"{root}+{tv}"
        noun_str = " / ".join(f"{p}+{r}" for p, r in c["noun_analyses"])
        print(f"{c['word']!r}: verb [{verb_str}] -> actual {actual}, noun would be [{noun_str}]")

    return len(real_ties)


if __name__ == "__main__":
    n = main()
    sys.exit(1 if n else 0)
