#!/usr/bin/env python3
"""
Style humanizer: rewrites the mechanical patterns typical of machine-generated
prose (uniform paragraphs, flat sentence rhythm, stock transitions) and flags
the places that need a human (citations, first-person voice, awkward lines).

It never invents facts, citations, or personal anecdotes.

Usage:
  python humanize.py input.txt -o output.txt          # rewrite + report
  python humanize.py input.txt --analyze-only         # metrics + flags only
  cat draft.txt | python humanize.py - --seed 7
"""
import argparse, random, re, statistics, sys

# ---------------------------------------------------------------- text utils
SENT_RE = re.compile(r'(?<=[.!?])["\')\]]?\s+(?=["\'(\[]?[A-Z0-9])')

def split_paragraphs(text):
    return [p.strip() for p in re.split(r'\n\s*\n', text.strip()) if p.strip()]

def split_sentences(par):
    return [s.strip() for s in SENT_RE.split(par) if s.strip()]

def words(s):
    return re.findall(r"[A-Za-z0-9'’-]+", s)

def cap(s):
    return s[:1].upper() + s[1:] if s else s

def decap(s):
    w = s.split(' ', 1)[0]
    # keep "I", acronyms, and likely proper nouns (capitalized not at sentence start is unknowable; be conservative)
    if w in ('I',) or w.isupper() or w.startswith("I'"):
        return s
    return s[:1].lower() + s[1:]

def cv(xs):
    if len(xs) < 2: return 0.0
    m = statistics.mean(xs)
    return statistics.pstdev(xs) / m if m else 0.0

# ------------------------------------------------- Method 3: stock transitions
# (pattern at sentence start, list of replacements; "" means delete the connector)
OPENERS = [
    (r"In conclusion,\s*", [""]),
    (r"To conclude,\s*", [""]),
    (r"In summary,\s*", [""]),
    (r"Overall,\s*", ["", "All told, "]),
    (r"Moreover,\s*", ["", "And "]),
    (r"Furthermore,\s*", ["", "Beyond that, "]),
    (r"Additionally,\s*", ["", "Also, "]),
    (r"In addition,\s*", ["", "Also, "]),
    (r"Consequently,\s*", ["So ", "As a result, "]),
    (r"Therefore,\s*", ["So ", ""]),
    (r"Thus,\s*", ["So ", ""]),
    (r"Nevertheless,\s*", ["Still, "]),
    (r"Nonetheless,\s*", ["Still, ", "Even so, "]),
    (r"However,\s*", ["But ", "However, ", "Then again, "]),
    (r"Firstly,\s*", ["First, "]),
    (r"Secondly,\s*", ["Second, "]),
    (r"Lastly,\s*", ["Finally, ", ""]),
    (r"Ultimately,\s*", ["", "In the end, "]),
    (r"Notably,\s*", [""]),
    (r"Importantly,\s*", [""]),
    (r"Initially,\s*", ["At first, "]),
    (r"Subsequently,\s*", ["Later, ", "After that, "]),
    (r"Thereafter,?\s*", ["After that, ", "Then "]),
    (r"Hence,\s*", ["So "]),
    (r"That (?:being )?said,\s*", [""]),
    (r"With that in mind,\s*", [""]),
    (r"Moving forward,\s*", [""]),
    (r"At the end of the day,\s*", [""]),
    (r"In other words,\s*", [""]),
    (r"To put this in perspective,\s*", [""]),
]
FILLER = [  # anywhere in a sentence: delete and let the note speak for itself
    r"it is (?:important|worth|crucial|essential) to (?:note|mention|remember|highlight|recognize) that\s*",
    r"it(?:'s| is) worth noting that\s*",
    r"it should be noted that\s*",
    r"needless to say,?\s*",
    r"it goes without saying that\s*",
    r"it is also worth mentioning that\s*",
    r",? in the (?:overall|grand|wider) scheme of things",
    r"in today's (?:fast-paced|modern|digital|ever-changing) (?:world|society|landscape),?\s*",
    r"in the realm of\s*",
    r"when it comes to\s*",
]
WORD_SWAPS = {
    r"\butilize[sd]?\b": lambda m: {"utilize": "use", "utilizes": "uses", "utilized": "used"}[m.group(0).lower()],
    r"\butilization\b": "use",
    r"\bleverage\b": "use",
    r"\bdelve into\b": "dig into",
    r"\bdelves into\b": "digs into",
    r"\ba plethora of\b": "plenty of",
    r"\ba myriad of\b": "many",
    r"\bmyriad\b": "many",
    r"\bin order to\b": "to",
    r"\bdue to the fact that\b": "because",
    r"\bat this point in time\b": "now",
    r"\bfacilitate\b": "help",
    r"\bseamless(?:ly)?\b": lambda m: "smooth" + ("ly" if m.group(0).lower().endswith("ly") else ""),
    r"\brobust\b": "solid",
    r"\btapestry\b": "mix",
    r"\bunderscores\b": "shows",
    r"\bnavigat(?:e|ing) the complexities of\b": "dealing with",
}

def fix_transitions(sent, rng, stats):
    for pat, reps in OPENERS:
        m = re.match(pat, sent)
        if m:
            rep = rng.choice(reps)
            rest = sent[m.end():]
            sent = cap(rep + (decap(rest) if rep else rest)) if rep else cap(rest)
            stats['transitions'] += 1
            break
    for pat in FILLER:
        new = re.sub(pat, "", sent, flags=re.I)
        if new != sent:
            stats['filler'] += 1
            sent = cap(new.strip())
    for pat, rep in WORD_SWAPS.items():
        def _r(m, rep=rep):
            out = rep(m) if callable(rep) else rep
            return cap(out) if m.group(0)[0].isupper() else out
        new = re.sub(pat, _r, sent, flags=re.I)
        if new != sent:
            stats['word_swaps'] += 1
            sent = new
    return sent

# --------------------------------------------- Method 2: sentence-length variance
SPLIT_POINTS = [", but ", ", and ", "; ", ", which means ", ", so ", ", while ", ", although "]
SPLIT_LEAD = {", but ": "But ", ", and ": "And ", "; ": "", ", which means ": "That means ",
              ", so ": "So ", ", while ": "Meanwhile, ", ", although ": "Still, "}

def split_long(sent, max_words):
    n = len(words(sent))
    if n <= max_words: return [sent]
    best = None
    for sp in SPLIT_POINTS:
        for m in re.finditer(re.escape(sp), sent):
            left = len(words(sent[:m.start()]))
            if left < 6 or n - left < 6: continue
            # don't split a list ("A, B, and C"): another comma within the 5 words before
            if sp == ", and " and "," in sent[:m.start()]: continue
            score = abs(left - n / 2)
            if best is None or score < best[0]:
                best = (score, m.start(), sp)
    if not best: return [sent]
    _, i, sp = best
    a = sent[:i].rstrip() + "."
    b = SPLIT_LEAD[sp] + (decap(sent[i + len(sp):]) if SPLIT_LEAD[sp] else cap(sent[i + len(sp):]))
    return [a, cap(b)]

def merge_short(a, b):
    a_core = a.rstrip(".")
    if a.endswith(("?", "!")) or b.startswith(("But ", "And ", "So ")): return None
    return f"{a_core}, and {decap(b)}"

def vary_rhythm(sents, rng, stats, max_words=30, short=9):
    # pass 1: break overly long sentences (roughly every long one; the rhythm comes from mix)
    out = []
    for s in sents:
        parts = split_long(s, max_words)
        if len(parts) > 1: stats['splits'] += 1
        out.extend(parts)
    # pass 2: occasionally fuse two short neighbours so not everything is short
    res, i = [], 0
    while i < len(out):
        if (i + 1 < len(out) and len(words(out[i])) <= short and len(words(out[i+1])) <= short
                and rng.random() < 0.5):
            m = merge_short(out[i], out[i+1])
            if m:
                res.append(m); stats['merges'] += 1; i += 2; continue
        res.append(out[i]); i += 1
    return res

# ---------------------------------------------- Method 1: paragraph-length pattern
def vary_paragraphs(pars, rng, stats):
    """pars: list[list[sentence]]. Split long uniform paragraphs; promote a punchy line."""
    lens = [len(p) for p in pars]
    uniform = len(pars) >= 3 and cv(lens) < 0.35
    out, promoted = [], 0
    for p in pars:
        if uniform and len(p) >= 5 and rng.random() < 0.6:
            cut = rng.choice(range(2, len(p) - 1))
            out += [p[:cut], p[cut:]]; stats['para_splits'] += 1
            continue
        # pull a short closing line out as its own one-line paragraph (emphasis)
        if (len(p) >= 4 and len(words(p[-1])) <= 12 and promoted < max(1, len(pars) // 4)
                and not re.match(r"(This|That|It|These|Those|They|Then|After that|Later|So|And|But)\b", p[-1])
                and "etc" not in p[-1] and rng.random() < 0.5):
            out += [p[:-1], [p[-1]]]; promoted += 1; stats['one_liners'] += 1
            continue
        out.append(p)
    return out

# --------------------------------------- Methods 4–6: flags for the human pass
VAGUE = [r"\bmany (?:studies|researchers|experts|people|students|scholars)\b",
         r"\b(?:some|several|various) (?:researchers|experts|studies|scholars|critics)?\s*(?:argue|suggest|believe|claim|show)\b",
         r"\bstudies (?:have )?show(?:n)?\b", r"\bresearch (?:has )?(?:shows?|suggests?|indicates?)\b",
         r"\bit is (?:widely|generally|commonly) (?:believed|accepted|known)\b",
         r"\bexperts (?:agree|say|believe)\b"]
REWORD = [  # flagged, not auto-edited: deleting these breaks the sentence
    (r"\bplays? an? (?:crucial|vital|pivotal|significant|key|important) role\b", "stock phrase: say what it actually does"),
    (r"\bseeks? to\b", "hedge: say what the study does"),
    (r"\bsuch as\b[^.]*\betc\.?", "'such as' + 'etc.' is redundant: drop 'etc.'"),
    (r"\benlists?\b", "'enlist' means recruit: 'lists' or 'identifies'?"),
    (r"\b(?:a )?(?:wide|broad) (?:range|variety|array) of\b", "vague quantifier"),
    (r"\bpotential (?:remedy|solution)\b", "hedge"),
]
REWORD += [
    (r"\b(?:serves?|stands?|acts?|functions?) as\b", "bloated verb: use 'is'"),
    (r"\b(?:boasts?|marks? a|represents? a)\b", "bloated verb: use 'is'/'has'"),
    (r"\b(?:aims?|helps?) to\b", "bloated verb: say what it does"),
    (r",\s*(?:highlighting|underscoring|reflecting|paving the way for|opening the door to|contributing to|setting the stage for)\b",
     "fake-depth participle: give the point its own sentence or cut it"),
    (r"\b(?:a )?(?:key turning point|pivotal moment|major shift|significant evolution|broader implications)\b", "puffery: state the fact"),
    (r"\bfrom [\w\s-]{2,30} to [\w\s-]{2,30}\b(?=[,.])", "possible false range: keep only if the middle matters"),
    (r"\b(?:think of it as|imagine|picture this|it is (?:kind of )?like|works like|the (?:backbone|engine|fuel|fabric|heartbeat|DNA|glue|north star|cornerstone) of|a (?:bridge|lens|roadmap|mirror) (?:between|for|of))\b",
     "analogy setup: write literally unless the analogy truly clarifies"),
    (r"\b(?:in this (?:section|article|paper), (?:I|we) will|let me walk you through|here is a comprehensive overview|this article will cover)\b",
     "meta commentary: say the thing (a one-line roadmap is fine in an academic intro)"),
    (r"\b(?:as of my last update|based on available information|while specific details are limited)\b", "AI disclaimer: delete"),
]
REWORD += [  # adapted from OPSHARP/unslop taboo-phrases (MIT)
    (r"\b(?:the )?(?:numbers|data|results|figures) (?:speak|speaks) for themselves\b|\btells? a (?:clear |compelling )?story\b|\bpaints? a (?:clear |vivid )?picture\b",
     "false agency: state the finding"),
    (r"\b(?:the future looks bright|only time will tell|remains to be seen|one thing is certain|what remains clear is|exciting times lie ahead|poised for (?:growth|success))\b",
     "generic conclusion: end on the actual finding or implication"),
    (r"\bcontinues? to (?:evolve|shape|grow|transform)\b", "vague ongoing-ness: say what changes"),
    (r"\b(?:here['’]s what (?:is interesting|caught my eye|stood out)|worth (?:exploring|a look|checking out|paying attention to))\b",
     "reader-steering: state the point"),
    (r"^(?:While|Although) [^,]{3,80}(?:is promising|has made strides|has limitations|shows promise)\b", "false concession: name the actual tradeoff"),
    (r"\b(?:nobody (?:talks|is talking) about|the insight everyone['’]s missing|what nobody tells you)\b", "novelty bait"),
    (r"\((?:and )?(?:perhaps more importantly|increasingly|arguably|or,? more precisely)[^)]*\)", "parenthetical hedge: own sentence or cut"),
    (r"\b(?:to answer your question|you['’]re asking about|let me think step by step|breaking this down)\b", "chat artifact: delete"),
]
# Academic excess vocabulary: words whose frequency jumped in PubMed abstracts after ChatGPT
# (Berens & Kobak, Science Advances 2024, via unslop). Soft: legitimate, flag when clustered.
ACADEMIC_EXCESS = [r"\belucidat\w*", r"\bdelineat\w*", r"\bunderpin\w*", r"\bunveil\w*", r"\binvaluable\b", r"\bnoteworthy\b",
    r"\bholds? (?:great |significant )?promise\b", r"\bnew avenues\b", r"\bsheds? (?:new )?light\b", r"\bwarrants? further (?:investigation|research|study)\b",
    r"\bin recent years\b", r"\bwith the advent of\b", r"\btaken together\b", r"\bgarner(?:ed|s)? (?:significant|considerable|increasing) attention\b",
    r"\ba (?:deeper|more nuanced|comprehensive) understanding\b", r"\bever-(?:evolving|changing|growing)\b", r"\ba growing body of\b",
    r"\bhas been (?:widely )?(?:described|regarded) as\b", r"\bis widely regarded as\b", r"\bobservers have noted\b", r"\bin the realm of\b",
    r"\bcomprehensive(?:ly)?\b", r"\bmultifaceted\b", r"\bnuanced\b", r"\bnotably\b"]
NEG_PARALLEL = [  # reject-X-then-assert-Y reframes
    r"\bnot (?:just|only|solely|simply|merely|purely)\b[^.]{1,120}?\b(?:but|instead|rather)\b",
    r"\b(?:is|are|was|were) not (?:a |an |the )?[^.,;]{1,60}[,;] (?:instead|rather)\b",
    r"\b(?:is|are|was|were)n['’]?t (?:just |only |simply )?(?:about )?[^.]{1,60}[.;] (?:it|this|they)(?:['’]s|['’]re| is| are)\b",
    r"\bthe (?:real |actual )?(?:question|problem|issue|answer|goal|point) is not\b",
    r"\bit (?:was|is) never about\b",
    r"^(?:Most people think|Many assume|At first glance|On the surface|Conventional wisdom says|The common assumption is|While [^,]{1,60} may seem|Although [^,]{1,60} appears)\b",
    r"\bless [\w-]+, more [\w-]+\b",
]
TECH_OK = {  # literal technical terms in research writing; only flagged in --mode general
    "data-driven", "predictive", "transparent", "integrated", "dynamic", "scalable", "robust", "optimize",
    "adaptive", "proprietary", "accelerate", "align", "intuitive", "immersive", "disruptive", "highlight", "emphasize", "enhance",
}
VOCAB = ("delve realm harness unlock tapestry paradigm cutting-edge revolutionize intricate intricacies showcasing crucial pivotal "
         "surpass meticulously vibrant unparalleled underscore underscores leverage synergy innovative game-changer testament commendable "
         "meticulous highlight emphasize boast groundbreaking align foster showcase enhance holistic garner accentuate pioneering "
         "trailblazing unleash versatile transformative redefine seamless optimize scalable robust breakthrough empower streamline "
         "frictionless elevate adaptive effortless data-driven insightful proactive mission-critical visionary disruptive reimagine "
         "unprecedented intuitive leading-edge synergize democratize accelerate state-of-the-art dynamic immersive predictive transparent "
         "proprietary integrated plug-and-play turnkey future-proof paradigm-shifting supercharge enduring interplay valuable captivate").split()
TRIAD = re.compile(r"\b[\w-]+(?: [\w-]+){0,2}, [\w-]+(?: [\w-]+){0,2},? and [\w-]+")
FIRST_PERSON = re.compile(r"\b(?:I|I'm|I've|my|me|we|our)\b")
NOMINAL = re.compile(r"\b\w+(?:tion|ment|ness|ity|ance|ence)s?\b", re.I)

def flags(pars, mode="academic"):
    found = []
    fp = 0
    for pi, p in enumerate(pars, 1):
        for s in p:
            fp += len(FIRST_PERSON.findall(s))
            for v in VAGUE:
                m = re.search(v, s, re.I)
                if m:
                    found.append(("SPECIFICS", pi, f'"{m.group(0)}" → name the actual study/person, or cut it: {s[:90]}…'))
                    break
            for pat, why in REWORD:
                m = re.search(pat, s, re.I)
                if m:
                    found.append(("REWORD", pi, f'"{m.group(0)}" ({why}): {s[:90]}…'))
            for pat in NEG_PARALLEL:
                m = re.search(pat, s, re.I)
                if m:
                    found.append(("REFRAME", pi, f'"{m.group(0)[:50]}" rejects X to assert Y: delete the rejected half, state Y directly: {s[:80]}…'))
                    break
            if re.search(r"—|(?<!\d)–|–(?!\d)| -- ", s):  # en dash between digits (12–15) is a correct range
                found.append(("DASH", pi, f"em/en dash: use a comma, colon, period or parentheses: {s[:80]}…"))
        for a_, b_ in zip(p, p[1:]):  # reframe split across two sentences
            if (re.search(r"\b(?:is|are|was|were) not\b|n['’]t\b|^(?:Most|Many) (?:people|teams|assume)", a_)
                    and re.match(r"(?:It|This|That|They|The real|The actual)\b(?: is| are|['’]s|['’]re)?(?: (?:really|actually|about))?", b_)
                    and re.search(r"\b(?:really|actually|about|real)\b", b_ + " " + a_)):
                found.append(("REFRAME", pi, f"two-sentence reframe: delete the rejected half, state the claim directly: {a_[:50]}… {b_[:40]}…"))
        ptxt = " ".join(p)
        vocab = sorted({w for w in VOCAB if re.search(r"\b" + re.escape(w) + r"\w{0,3}\b", ptxt, re.I)
                        and not (mode == "academic" and w in TECH_OK)})
        if vocab:
            found.append(("VOCAB", pi, "AI-favoured words, keep only if literally exact: " + ", ".join(vocab)))
        acad = sorted({m.group(0).lower() for pat in ACADEMIC_EXCESS for m in re.finditer(pat, ptxt, re.I)})
        if len(acad) >= 2 or (acad and mode == "general"):
            found.append(("ACADEMIC-VOCAB", pi, "post-ChatGPT excess words clustered here (fine alone, tell-tale together): " + ", ".join(acad)))
        if len(TRIAD.findall(ptxt)) >= (3 if mode == "academic" else 2):
            found.append(("RULE-OF-3", pi, f"{len(TRIAD.findall(ptxt))} three-item lists: use the real number of items, not 3 by habit"))
        for s in p:
            n = len(words(s))
            if n > 35 or (n > 15 and len(NOMINAL.findall(s)) / n > 0.18):
                found.append(("READ-ALOUD", pi, f"{n} words, noun-heavy — rewrite as you'd say it: {s[:90]}…"))
    return found, fp

# ------------------------------------------------------------------- metrics
TRANS_ALL = re.compile(r"\b(?:moreover|furthermore|additionally|in addition|in conclusion|consequently|"
                       r"nevertheless|it is important to note|it is worth noting|in summary|notably)\b", re.I)

def metrics(text):
    pars = split_paragraphs(text)
    sents = [s for p in pars for s in split_sentences(p)]
    sl = [len(words(s)) for s in sents]
    pl = [len(split_sentences(p)) for p in pars]
    nw = sum(sl) or 1
    return {
        "words": nw, "paragraphs": len(pars), "sentences": len(sents),
        "sent_len_mean": round(statistics.mean(sl), 1) if sl else 0,
        "sent_len_sd": round(statistics.pstdev(sl), 1) if len(sl) > 1 else 0,
        "sent_len_cv (rhythm)": round(cv(sl), 2),
        "para_len_cv": round(cv(pl), 2),
        "short_sents(<=8w)": sum(1 for x in sl if x <= 8),
        "long_sents(>=30w)": sum(1 for x in sl if x >= 30),
        "max_run_<=6w (staccato)": max((len(r) for r in re.findall(r"S+", "".join("S" if x <= 6 else "L" for x in sl))), default=0),
        "stock_transitions/1k": round(len(TRANS_ALL.findall(text)) * 1000 / nw, 1),
    }

# -------------------------------------------------------------------- driver
def humanize(text, seed=None, max_words=30, reshape=False):
    rng = random.Random(seed)
    stats = dict.fromkeys(['transitions', 'filler', 'word_swaps', 'splits', 'merges',
                           'para_splits', 'one_liners'], 0)
    pars = []
    for p in split_paragraphs(text):
        sents = [fix_transitions(s, rng, stats) for s in split_sentences(p)]
        sents = [s for s in sents if words(s)]
        pars.append(vary_rhythm(sents, rng, stats, max_words=max_words))
    if reshape:
        pars = vary_paragraphs(pars, rng, stats)
    return "\n\n".join(" ".join(p) for p in pars if p), stats, pars

def report(before, after, stats, fl, fp, out=sys.stderr):
    p = lambda *a: print(*a, file=out)
    p("\n=== METRICS (before → after) ===")
    for k in before:
        p(f"  {k:24s} {before[k]!s:>7} → {after[k]!s:<7}")
    p("  (higher rhythm/para CV = more varied; human prose usually ≳0.5 sentence CV)")
    p("\n=== CHANGES ===")
    for k, v in stats.items(): p(f"  {k:12s} {v}")
    p("\n=== NEEDS YOU (tool won't invent these) ===")
    p(f"  [VOICE] first-person markers: {fp}" +
      ("  → if the format allows, add one real 'when I first…' moment." if fp == 0 else ""))
    for tag, pi, msg in fl: p(f"  [{tag}] ¶{pi}: {msg}")
    if not fl: p("  nothing flagged")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="file path or - for stdin")
    ap.add_argument("-o", "--output")
    ap.add_argument("--seed", type=int, default=None, help="for reproducible output")
    ap.add_argument("--max-words", type=int, default=30, help="split sentences longer than this")
    ap.add_argument("--analyze-only", action="store_true")
    ap.add_argument("--reshape-paragraphs", action="store_true",
                    help="also split/promote paragraphs automatically (off by default: it often misfires; do it by hand)")
    ap.add_argument("--mode", choices=["academic", "general"], default="academic",
                    help="academic keeps literal technical terms (data-driven, predictive, …) out of VOCAB flags")
    a = ap.parse_args()
    text = sys.stdin.read() if a.input == "-" else open(a.input, encoding="utf-8").read()
    before = metrics(text)
    if a.analyze_only:
        fl, fp = flags([split_sentences(p) for p in split_paragraphs(text)], a.mode)
        report(before, before, {}, fl, fp); return
    new, stats, pars = humanize(text, a.seed, a.max_words, a.reshape_paragraphs)
    fl, fp = flags(pars, a.mode)
    if a.output: open(a.output, "w", encoding="utf-8").write(new + "\n")
    else: print(new)
    report(before, metrics(new), stats, fl, fp)

if __name__ == "__main__":
    main()
