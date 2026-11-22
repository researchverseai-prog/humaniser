#!/usr/bin/env python3
"""
Check that a rewrite kept everything that must survive: citations, numbers,
acronyms, quotations, URLs/DOIs, named terms, and load-bearing words
(negations, hedges, modals, scope words). Also reports how much changed and
whether the rewrite drifted into choppy "staccato" prose.

Idea adapted from the fact-preservation contract in OPSHARP/unslop (MIT).

Usage:
  python3 check_preservation.py original.txt revised.txt
Exit code 0 = nothing lost, 1 = something must be fixed before sending.
"""
import difflib, re, sys
from collections import Counter

HARD = {
    "citation": r"\([A-Z][A-Za-z'’\-]+(?: (?:et al\.|and|&) ?[A-Z]?[A-Za-z'’\-]*)?,? \d{4}[a-z]?(?:[;,] [^)]{0,80})?\)|\[\d+(?:[,–-]\s?\d+)*\]|[A-Z][A-Za-z'’\-]+ (?:et al\. )?\(\d{4}[a-z]?\)",
    "number": r"(?<![\w.])\$?\d[\d,]*(?:\.\d+)?\s?(?:%|percent|[KMB]\b|million|billion)?",
    "acronym": r"\b[A-Z]{2,}[a-z]?s?\b",
    "quote": r"[\"“][^\"”]{8,}[\"”]",
    "url/doi": r"https?://\S+|\b10\.\d{4,}/\S+",
    "named term": r"\b(?:[A-Z][a-z]+(?:-[A-Z]?[a-z]+)?)(?: (?:of |and |for )?[A-Z][a-z]+(?:-[A-Z]?[a-z]+)?){1,4}\b",
}
# words whose loss or addition changes the claim (counted, compared)
LOAD_BEARING = {
    "negation": r"\b(?:not|no|never|none|neither|nor|cannot|without)\b|n['’]t\b",
    "hedge": r"\b(?:may|might|could|can|suggests?|suggested|appears?|likely|unlikely|possibly|potentially|preliminary|tentative|partly|partially|arguably)\b",
    "obligation": r"\b(?:must|shall|should|required?|always)\b",
    "scope": r"\b(?:all|every|only|most|some|many|few|several|at least|at most|no more than|mainly|largely|primarily)\b",
    "condition": r"\b(?:if|unless|except|provided that|when)\b",
}
SENT = re.compile(r"(?<!\bal\.)(?<!\be\.g\.)(?<!\bi\.e\.)(?<!\bvs\.)(?<!\bcf\.)(?<=[.!?])[\"')\]]?\s+(?=[\"'(\[]?[A-Z0-9])")
SENT_START_WORDS = {"The", "This", "These", "That", "Those", "It", "In", "A", "An", "For", "To", "But", "And", "So",
                    "However", "First", "Second", "Third", "Finally", "Over", "At", "Such", "Most", "Many", "Some"}

def items(kind, text):
    found = re.findall(HARD[kind], text)
    if kind == "named term":  # drop phrases that are only capitalised because they start a sentence
        found = [f for f in found if f.split()[0] not in SENT_START_WORDS]
    if kind == "citation":  # compare individual references, so reordering inside brackets is fine
        refs = []
        for f in found:
            inner = f.strip("()[]")
            refs += [p.strip() for p in re.split(r";\s*", inner) if p.strip()] if f.startswith("(") else [f.strip()]
        return Counter(refs)
    if kind == "number":
        found = [f.strip().rstrip(",.") for f in found if f.strip().rstrip(",.")]
    return Counter(f.strip() for f in found)

def sentences(text):
    return [s for p in re.split(r"\n\s*\n", text.strip()) for s in SENT.split(p.strip()) if s.strip()]

def staccato(text):
    lens = [len(re.findall(r"[\w'’-]+", s)) for s in sentences(text)]
    if len(lens) < 4: return 0.0, 0
    short = sum(1 for n in lens if n <= 8) / len(lens)
    run = best = 0
    for n in lens:
        run = run + 1 if n <= 6 else 0
        best = max(best, run)
    return short, best

def renamed(val, new):
    ow = set(val.lower().split())
    return any(len(ow & set(nt.lower().split())) >= max(1, len(ow) - 1) for nt in items("named term", new))

def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    orig = open(sys.argv[1], encoding="utf-8").read()
    new = open(sys.argv[2], encoding="utf-8").read()
    problems, notes, total, kept = [], [], 0, 0

    for kind in HARD:
        o, n = items(kind, orig), items(kind, new)
        for val, cnt in o.items():
            total += 1
            if n.get(val, 0) >= 1 or (kind == "named term" and val.lower() in new.lower()):
                kept += 1
            else:
                if kind == "named term" and renamed(val, new): continue  # reported as RENAMED below
                (problems if kind != "named term" else notes).append(f"{kind} missing: {val!r}")
        if kind in ("citation", "number", "url/doi"):
            for val in n:
                if val not in o:
                    problems.append(f"{kind} ADDED (not in original, possible fabrication): {val!r}")

    # a named term that is missing but has a near-match in the revision was probably RENAMED (e.g. by a paraphraser)
    new_terms = set(items("named term", new))
    for val in items("named term", orig):
        if val.lower() in new.lower(): continue
        ow = set(val.lower().split())
        for nt in new_terms:
            nw = set(nt.lower().split())
            if len(ow & nw) >= max(1, len(ow) - 1) and nt.lower() != val.lower():
                problems.append(f"named term RENAMED: {val!r} → {nt!r} (a defined term must keep its exact name)")
                break

    # content words that carried claims in the original and vanished from the revision
    STOP = set("about above after again against among because before being below between both could during either every first further having other their there these those through under until where which while whose would should might shall since also into from with that this than then they them were been have more most such only very each same some what when your".split())
    def content(t): return {w for w in re.findall(r"[a-z][a-z-]{4,}", t.lower()) if w not in STOP}
    co, cn = content(orig), content(new)
    lost = sorted(w for w in co - cn if not any(x.startswith(w[:6]) for x in cn))
    if len(lost) >= 3:
        notes.append(f"{len(lost)} content words from the original are gone; check no claim was dropped: " + ", ".join(lost[:15]) + (" …" if len(lost) > 15 else ""))

    for kind, pat in LOAD_BEARING.items():
        o = len(re.findall(pat, orig, re.I)); n = len(re.findall(pat, new, re.I))
        if o != n:
            msg = f"{kind} words: {o} → {n}. Re-read: was a {kind} dropped, added or changed?"
            (problems if kind in ("negation", "condition") and n < o else notes).append(msg)

    ratio = difflib.SequenceMatcher(None, orig.split(), new.split()).ratio()
    s_o, r_o = staccato(orig); s_n, r_n = staccato(new)

    print("=== PRESERVATION CHECK ===")
    print(f"  constraints preserved: {kept}/{total}")
    print(f"  change from original: {round((1 - ratio) * 100)}% of words")
    print(f"  short sentences (<=8 words): {s_o:.0%} → {s_n:.0%}; longest run of <=6-word sentences: {r_o} → {r_n}")
    if s_n > 0.45 and s_n > s_o + 0.1 or r_n >= 3 > r_o:
        problems.append("rewrite became staccato (too many short sentences in a row); restore some longer sentences")
    if (1 - ratio) > 0.6:
        notes.append("over 60% of the wording changed; confirm the edit was the smallest repair needed")
    for p in problems: print(f"  [FIX]   {p}")
    for p in notes:    print(f"  [CHECK] {p}")
    if not problems and not notes: print("  all clear")
    sys.exit(1 if problems else 0)

if __name__ == "__main__":
    main()
