"""
Sanity checks for lute_shona_parser.morphology.split_word.

Run with: python -m pytest tests/ (or plain `python tests/test_morphology.py`)

These are a real-text regression corpus, not just clean textbook
cases -- several entries here are deliberately expected to stay whole
(contractions, unseeded roots, confirmed-ambiguous exceptions). That's
correct v1 behaviour, not a bug: see morphology.py's docstring for why.
"""

from lute_shona_parser.morphology import split_word


def check(word, expected):
    actual = split_word(word)
    assert actual == expected, f"{word!r}: expected {expected!r}, got {actual!r}"
    assert "".join(actual) == word, f"{word!r}: tokens {actual!r} do not reconstruct the original word"


def test_sample_infinitives():
    check("kufamba", ["ku", "famba"])
    check("kutenda", ["ku", "tenda"])
    check("kugara", ["ku", "gara"])
    check("kumira", ["ku", "mira"])
    check("kuuya", ["ku", "uya"])
    check("kuenda", ["ku", "enda"])
    check("kudya", ["ku", "dya"])
    check("kuda", ["ku", "da"])
    check("kunyora", ["ku", "nyora"])
    check("kuverenga", ["ku", "verenga"])
    check("kuterera", ["ku", "terera"])
    check("kuona", ["ku", "ona"])
    check("kunwa", ["ku", "nwa"])
    check("kudzidza", ["ku", "dzidza"])
    check("kubika", ["ku", "bika"])
    check("kuisa", ["ku", "isa"])


def test_worked_example_vachamubikira():
    check("vachamubikira", ["va", "cha", "mu", "bik", "ira"])


def test_extension_chain_disambiguation():
    # kuisa: root "-is-" is also the causative extension form -- must
    # resolve as a plain root (direct hit wins before any extension
    # attempt), not a fake sub-root + causative marker.
    check("kuisa", ["ku", "isa"])
    check("kuiswa", ["ku", "is", "wa"])
    check("kuisiswa", ["ku", "is", "is", "wa"])


def test_noun_class_prefixes():
    # source: original xlsx seed -- confirm prefix-stripping doesn't
    # over-fire on short roots once they're seeded in the lexicon.
    check("munhu", ["mu", "nhu"])  # cl.1
    check("vanhu", ["va", "nhu"])  # cl.2
    check("chinhu", ["chi", "nhu"])  # cl.7
    check("zvinhu", ["zvi", "nhu"])  # cl.8
    check("banga", ["banga"])  # cl.5, zero/irregular prefix -- whole
    check("mapanga", ["ma", "panga"])  # cl.6
    check("rukuni", ["ru", "kuni"])  # cl.11
    check("kambuyu", ["ka", "mbuyu"])  # cl.12
    check("tumbuyu", ["tu", "mbuyu"])  # cl.13
    check("upfu", ["u", "pfu"])  # cl.14
    check("pamba", ["pa", "mba"])  # cl.16
    check("kumusha", ["ku", "musha"])  # cl.17 locative (not the infinitive -- "musha" isn't a seeded verb root)
    check("mumunda", ["mu", "munda"])  # cl.18 locative attaches to the whole noun "munda", not the bare root "nda"
    check("mumota", ["mu", "mota"])  # cl.18 locative


def test_noun_classes_from_reference_pdf():
    # source: "3 Noun Classes.pdf" -- every entry here was dry-run
    # against the actual code before being written down (see the
    # WORD_EXCEPTIONS additions this surfaced: mudzidzisi, mukanwa).
    # cl.1 (mu-/mw-) and cl.2/2a/2b (va-/vana-/a-)
    check("mukomana", ["mu", "komana"])  # boy
    check("mukadzi", ["mu", "kadzi"])  # woman -- "kadzi" is a cross-class root, also cl.2/7/8
    check("mwenga", ["mw", "enga"])  # betrothed woman -- mw- allomorph before vowel-initial stem
    check("mweni", ["mw", "eni"])  # visitor/guest
    check("vakadzi", ["va", "kadzi"])  # women
    check("vaeni", ["va", "eni"])  # visitors/guests
    check("varapi", ["va", "rapi"])  # healers
    check("vanatezvara", ["vana", "tezvara"])  # fathers-in-law, cl.2a
    check("vasahwira", ["va", "sahwira"])  # honoured friend, cl.2a
    check("amai", ["a", "mai"])  # mother, cl.2b
    check("ambuya", ["a", "mbuya"])  # grandmother, cl.2b
    # cl.3/4 (mu-/mw- singular, mi-/mw- plural)
    check("musasa", ["mu", "sasa"])  # Musasa tree
    check("mwando", ["mw", "ando"])  # cold
    check("munamato", ["mu", "namato"])  # prayer
    check("minamato", ["mi", "namato"])  # prayers -- same root as munamato, different class
    check("miti", ["mi", "ti"])  # trees
    check("miromo", ["mi", "romo"])  # mouths
    # cl.6 (ma-)
    check("makudo", ["ma", "kudo"])  # baboons
    check("mabhasikoro", ["ma", "bhasikoro"])  # bicycles -- "bhasikoro" is a borrowed noun root
    # cl.7/8 (chi-/zvi-)
    check("chimuti", ["chi", "muti"])  # a stick -- "muti" is cross-class (also cl.12/13)
    check("zvihuta", ["zvi", "huta"])  # quails
    check("zvombo", ["zvombo"])  # weapons -- NOT zvi+ombo: zvi- elides before this
    # vowel-initial stem (zvi-ombo -> zvombo), same unmodeled
    # phonological process as chi-uru -> churu (see DESIGN.md);
    # correctly stays whole rather than force a wrong split.
    # cl.9/10 -- mostly zero/prenasalized surface (not modeled), except
    # the two classes' "i-"/"dzi-" forms, which do show a clean prefix.
    check("imba", ["i", "mba"])  # house, cl.9
    check("dzimba", ["dzi", "mba"])  # houses, cl.10 (plural of imba)
    # cl.11 (ru-/rw-)
    check("rubetsero", ["ru", "betsero"])  # help
    check("rudo", ["ru", "do"])  # love
    check("rwizi", ["rw", "izi"])  # river -- rw- allomorph before vowel-initial stem
    check("rwaivhi", ["rw", "aivhi"])  # chameleon
    # cl.12/13 (ka-/tu-) -- including the diminutive-on-whole-noun
    # pattern (kamunhu/tuvanhu attach to the already-prefixed cl.1/2
    # noun, not the bare root)
    check("kamuti", ["ka", "muti"])  # small tree
    check("kamunhu", ["ka", "munhu"])  # small person
    check("kasikana", ["ka", "sikana"])  # little girl
    check("tuvanhu", ["tu", "vanhu"])  # small people
    check("tukomana", ["tu", "komana"])  # small boys
    # cl.14 (u-/hw-/hu-)
    check("upenyu", ["u", "penyu"])  # life
    check("hupenzi", ["hu", "penzi"])  # craziness -- hu- allomorph, distinct from hw-
    check("utsinye", ["u", "tsinye"])  # cruelness
    # cl.16/17/18 locatives, including the locative-on-whole-noun
    # pattern (pamusoro/kurwizi attach to the already-prefixed noun)
    check("pamusoro", ["pa", "musoro"])  # on top
    check("pachikomo", ["pa", "chikomo"])  # on the hill
    check("panzvimbo", ["pa", "nzvimbo"])  # on the place
    check("kutsime", ["ku", "tsime"])  # at the well
    check("kugwenga", ["ku", "gwenga"])  # in the desert
    check("kurwizi", ["ku", "rwizi"])  # at the river
    check("mudura", ["mu", "dura"])  # in the silo
    check("mupoto", ["mu", "poto"])  # in the pot
    # cl.19 (svi-, Karanga dialect diminutive -- confirmed but low
    # frequency outside that dialect)
    check("svimbudzi", ["svi", "mbudzi"])  # little/pitiful goats
    check("svisikana", ["svi", "sikana"])  # the little girls
    # cl.21 (zi-, augmentative)
    check("zidzoro", ["zi", "dzoro"])  # big head
    check("zibhuku", ["zi", "bhuku"])  # enormous book


def test_verb_noun_branch_collision_exceptions():
    # Real collisions found by dry-running the noun-classes reference:
    # the noun-prefix reading is correct, but verb-slot (tried first)
    # also happens to resolve against the verb lexicon and wins. Both
    # protected via WORD_EXCEPTIONS -- see the comment there for the
    # exact mechanism of each collision.
    check("mudzidzisi", ["mudzidzisi"])  # teacher, cl.1 -- NOT mu+dzidz(causative "is")+i
    check("mukanwa", ["mukanwa"])  # mouth, cl.18 locative -- NOT mu(subject)+ka(past)+nwa(drink)


def test_true_homonyms_and_short_root_collisions():
    # Found by running a real story ("sekuru kamba - grandpa tortoise")
    # through split_word rather than more synthetic examples -- both
    # protected via WORD_EXCEPTIONS, see the comment there for the full
    # reasoning on each.
    check("Kamba", ["Kamba"])  # character name "Sekuru Kamba" -- via PROPER_NOUNS
    check("kamba", ["kamba"])  # true homonym: tortoise (confirmed 2/2 in
    # real text) vs ka+mba "small house" (regular but not observed) --
    # left whole rather than default to the less-observed reading
    check("mudiki", ["mudiki"])  # "small" -- NOT mu+d(want/love)+ik+i
    check("Vadikisa", ["Vadikisa"])  # "small ones/they tried hard" -- NOT va+d+ik+isa
    check("Kamaba", ["Kamaba"])  # typo in the source text for "Kamba" --
    # correctly just falls through unrecognized, no special handling needed


def test_grandpa_tortoise_story_correct_splits():
    # Positive results from the same real-text run -- confirms the
    # engine generalizes correctly to text it wasn't built against,
    # including one construction (negative-have with the "va" concord)
    # only ever tested before with "i" (Haina).
    check("Ndatenda", ["Nda", "tenda"])  # "I thank/am grateful"
    check("Pachikomo", ["Pa", "chikomo"])  # "on the hill", sentence-initial
    check("anoda", ["a", "no", "da"])  # "he/she/it wants": a + no (present habitual) + da
    check("auya", ["a", "uya"])  # "he/she/it came"
    check("havana", ["ha", "va", "na"])  # "did not" (negative past auxiliary) -- confirms
    # the ha-+concord+na construction generalizes beyond the "i" concord it was built with
    check("kuenda", ["ku", "enda"])  # "to go"
    check("kumba", ["ku", "mba"])  # "home" (locative "to the house")
    check("kumira", ["ku", "mira"])  # "to stand"
    check("vadya", ["va", "dya"])  # "(they/honorific) ate"


def test_unseeded_word_falls_back_whole():
    check("mvura", ["mvura"])


def test_shona_spacy_bulk_import():
    # Second bulk source: shona-spacy's manually-verified JSON lexicon
    # (MIT licensed, see rules.py's bulk-import comments). Includes two
    # real collisions this specific dataset surfaced (both fixed, see
    # rules.py) and one result that looks surprising but is actually a
    # correct compositional parse, not a bug.
    check("mukuwasha", ["mu", "kuwasha"])  # son-in-law
    check("mukoma", ["mu", "koma"])  # elder brother
    check("vabereki", ["va", "bereki"])  # parents -- NOT va+b(steal)+er+eki;
    # fixed by adding the missing root "berek" (bear/give birth), not a
    # WORD_EXCEPTIONS bypass -- see rules.py's VERB_ROOT_LEXICON comment.
    check("kubereka", ["ku", "bereka"])  # to give birth
    check("kuberekwa", ["ku", "berek", "wa"])  # to be born (passive)
    check("murwere", ["murwere"])  # patient/sick person -- NOT mu+rw(fight,
    # dialectal)+er(applicative)+ere; true collision from the Kaikki
    # round's "rw" root, protected via WORD_EXCEPTIONS since the real
    # derivation (from "-rwar-", to be sick) needs an unconfirmed vowel
    # change, not simple concatenation.
    check("varwere", ["varwere"])
    check("mufundisi", ["mu", "fund", "isi"])  # pastor -- mu+fund(learn)+
    # is(causative)+i(agentive): "one who causes others to learn." This
    # IS the real etymology, not a coincidental collision -- deliberately
    # left as a compositional parse, not an exception.
    check("kuchikoro", ["ku", "chikoro"])  # to/at school -- locative on an
    # already-prefixed noun (chi+koro), same pattern as mumunda/kutsime
    check("kamwana", ["ka", "mwana"])  # small child -- diminutive on the
    # already-prefixed cl.1 noun "mwana", same pattern as kamunhu
    check("pfungwa", ["pfungwa"])  # thought/idea -- zero-prefix root,
    # stays whole on its own (correct, nothing to strip)


def test_kaikki_bulk_import_new_short_roots():
    # Spot-checks for the shortest new roots added by the Kaikki.org
    # bulk import (see rules.py's bulk-import comments) -- same "watch
    # for collisions" category as the pre-existing 1-letter "d". None
    # of these regressed anything in the rest of this file when checked.
    check("kupa", ["ku", "pa"])  # to give -- new root "p"
    check("kuba", ["ku", "ba"])  # to steal -- new root "b"
    check("kufa", ["ku", "fa"])  # to die -- new root "f"
    check("kumwa", ["ku", "mwa"])  # to drink, Karanga/Manyika dialect form
    # of the already-seeded "nw" (kunwa) -- new root "mw", same surface
    # string as the mw- class 1/3 noun-prefix allomorph (mwenga/mwando
    # etc., see test_noun_classes_from_reference_pdf), but no collision
    # is possible: the noun allomorph is only ever tried by the noun
    # branch, which requires no subject-prefix match, while "mw" the
    # verb root is only ever reached after a real subject prefix is
    # stripped off first -- the two paths can't fire on the same word.
    check("kurwa", ["ku", "rwa"])  # to fight -- new root "rw"
    check("mumwe", ["mu", "mwe"])  # someone/other/one -- resolves via the
    # new verb root "mw" + subjunctive/imperative -e, but the token
    # boundary (mu | mwe) is the same one real Shona morphology gives
    # for the indefinite stem "-mwe" ("other"), so this isn't a wrong
    # split even though it's not the mechanism a fluent speaker would
    # name -- see rules.py for the full note.
    check("vababa", ["va", "baba"])  # fathers -- "baba" (father) is a new
    # class 1a zero-prefix root; confirms it combines correctly with the
    # existing va- class 2 prefix rather than only working standalone.


def test_negative_have_construction():
    # ha- + subject concord + -na ("does/did not have")
    check("Haina", ["Ha", "i", "na"])  # ha + cl.9 concord "i" + na
    check("hana", ["hana"])  # heart -- must NOT false-trigger: middle would be empty, rejected


def test_past_subject_prefixes():
    # A confirmed, complete past-tense subject concord paradigm
    # (source: the personal-pronoun/concord table in the noun-classes
    # reference), not one-off contractions -- 1sg nda-, 2sg wa-, 1pl
    # ta-, 2pl ma- (3sg/3pl past are identical to their basic forms,
    # so no separate entries needed for those). "ma" (2pl past) is the
    # same surface string as the cl.6 noun prefix "ma-" -- verified
    # this doesn't regress cl.6 noun splitting (test_noun_classes_from_reference_pdf's
    # makudo/mabhasikoro etc.), since the lexicon gate on each side uses
    # disjoint root sets.
    check("Ndaisa", ["Nda", "isa"])  # 1sg past, also see test_reduplicated_causative
    check("wafamba", ["wa", "famba"])  # 2sg past: "you walked"
    check("tafamba", ["ta", "famba"])  # 1pl past: "we walked"
    check("mafamba", ["ma", "famba"])  # 2pl past: "you(pl) walked"


def test_sati_construction():
    # subject prefix + -sati ("before [subject] ~s/~ing") -- confirmed
    # productive by the user across usati/tisati/musati/chisati, not
    # just the one ndisati example, so this is a real closed
    # construction (dedicated rule), not a whole-word exception.
    check("ndisati", ["ndi", "sati"])
    check("usati", ["u", "sati"])
    check("tisati", ["ti", "sati"])
    check("musati", ["mu", "sati"])
    check("chisati", ["chi", "sati"])


def test_reduplicated_causative():
    # ndakuisisa/ndakuisisisa used to be whole-word exceptions (exact
    # morpheme boundary unconfirmed). Now resolved: nda (sourced 1sg
    # hodiernal past, Aranovich 2015) + object marker + repeated
    # causative "is", via the same extension-loop already exercised by
    # kuisiswa -- no new mechanism, just removing the now-unneeded
    # exception and letting the existing engine run. ndakuisisisa sits
    # exactly at the depth-2 extension cap (root + two causative
    # strips); see test_extension_depth_cap_fails_closed for the next
    # step past this boundary.
    #
    # Object-marker readings confirmed directly by the user with
    # parallel glosses: "I made you/her-him/it put it".
    check("ndakuisisa", ["nda", "ku", "is", "isa"])  # ku = 2sg object ("you")
    check("ndamuisisa", ["nda", "mu", "is", "isa"])  # mu = cl.1 object ("her/him")
    check("ndachiisisa", ["nda", "chi", "is", "isa"])  # chi = cl.7 object ("it")
    check("ndakuisisisa", ["nda", "ku", "is", "is", "isa"])


def test_verb_slot_optional_combinations():
    # Full stack (subject + TAM + object + root + extension) is covered
    # by test_worked_example_vachamubikira. These cover the other
    # combinations of which optional slots are present, to exercise the
    # {TAM present/absent} x {object marker present/absent} search in
    # _try_verb_slot directly rather than only ever testing all-present
    # or all-absent.
    check("vafamba", ["va", "famba"])  # subject only
    check("vachafamba", ["va", "cha", "famba"])  # subject + TAM, no object
    check("vamubikira", ["va", "mu", "bik", "ira"])  # subject + object, no TAM


def test_extension_depth_cap_fails_closed():
    # Root "is" + three stacked "is"/causative-shaped extensions would
    # need a depth-3 strip to resolve -- one more than the depth-2 cap
    # supports. Must fall back to the whole word rather than accept a
    # three-strip guess with no lexicon anchor at that depth. This is a
    # synthetic (not necessarily real Shona) string, constructed only
    # to pin down the cap's fail-closed behaviour as a regression test.
    check("kuisisisisa", ["kuisisisisa"])


def test_case_preservation():
    # Matching is case-insensitive, but returned tokens must be exact
    # slices of the original-cased input (required by Lute's
    # ParsedToken contract -- see DESIGN.md section 5). Sentence-
    # initial capitals and all-caps input must round-trip correctly.
    check("Kufamba", ["Ku", "famba"])  # sentence-initial capital, not a listed name
    check("KUFAMBA", ["KU", "FAMBA"])
    check("Vachamubikira", ["Va", "cha", "mu", "bik", "ira"])


def test_name_vs_verb_case_sensitivity():
    # "Kuda" (capitalized, in PROPER_NOUNS) is the name; "kuda"
    # (lowercase, mid-sentence) is the ordinary verb "to want/love".
    # Only the exact capitalized form is protected.
    check("Kuda", ["Kuda"])
    check("kuda", ["ku", "da"])


def test_empty_and_minimal_input():
    check("", [""])
    check("a", ["a"])  # too short for any branch to fire -- whole word
    check("i", ["i"])  # matches the cl.9 subject concord alone, but nothing follows to resolve


def test_stress_sentence():
    # Kuda isa bhutsu mumota. Ndaisa bhutsu mumota. Haina kuisa mumota.
    # Isa ndisati ndakuisisa. Unoda kuisiswa here? Chiisa ka!
    check("Kuda", ["Kuda"])  # name (PROPER_NOUNS), not the verb "to want/love"
    check("isa", ["isa"])  # bare imperative, no prefix to strip
    check("bhutsu", ["bhutsu"])  # borrowed noun, not in any table
    check("mumota", ["mu", "mota"])
    check("Ndaisa", ["Nda", "isa"])
    check("Haina", ["Ha", "i", "na"])
    check("kuisa", ["ku", "isa"])
    check("ndisati", ["ndi", "sati"])  # confirmed productive subject+sati construction
    check("ndakuisisa", ["nda", "ku", "is", "isa"])  # reduplicated causative, see test_reduplicated_causative
    check("Unoda", ["U", "no", "da"])
    check("kuisiswa", ["ku", "is", "is", "wa"])
    check("here", ["here"])
    check("Chiisa", ["Chi", "isa"])  # consecutive "then" marker, not class-7 concord
    check("ka", ["ka"])  # stripping would leave an empty remainder -- blocked by the lexicon gate


if __name__ == "__main__":
    import sys
    import traceback

    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError:
            failures += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    if failures:
        print(f"\n{failures}/{len(tests)} test functions failed")
        sys.exit(1)
    print(f"\nAll {len(tests)} test functions passed")
