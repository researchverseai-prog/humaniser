# Style rules (full ruleset)

Adapted from *Anti-AI Writing Style* by Avik Bal (MIT License,
https://github.com/avikbal-dm/anti-ai-writing-claude-skill). This version adds an academic mode and
drops the SEO, brand and draft-from-scratch sections, which don't apply to editing. Sections 7 (additions),
10 and 11 adapt the core contract, register guards and phrase catalogue of OPSHARP/unslop (MIT License,
https://github.com/OPSHARP/unslop).

Read this for any edit longer than a paragraph or two, or when the script reports REFRAME, VOCAB or
analogy flags and you need the reasoning.

## Contents
1. Rule priority
2. Modes: academic vs general
3. Ask before you invent
4. Word-level bans
5. Negative parallelism and reframes
6. Analogy and metaphor control
7. Other machine patterns
8. Anti-overfitting
9. Final pass
10. Register guards (what must survive)
11. Smallest-repair contract

---

## 1. Rule priority

When rules collide: **accurate > clear > specific > sounds human > style.** If a rule makes a sentence
worse, break it. Keep the exact word when it is the exact word.

## 2. Modes

Pick the mode from the text. The script defaults to `--mode academic`.

| | Academic (papers, theses, reviews, reports) | General (posts, emails, web copy, LinkedIn) |
|---|---|---|
| Paragraphs | Vary them, typically 2–6 sentences; one-line paragraphs are rare and only for a strong claim | 1–2 sentences by default, 3–4 sometimes |
| Contractions | Avoid | Use naturally |
| First person | Suggest "we/I" only if the venue allows | Use I/you freely |
| Technical terms | *data-driven, predictive, transparent, integrated, robust, scalable, dynamic, optimise, enhance, highlight, align* are fine when used literally | Treat as VOCAB flags |
| Roadmap sentences | One line ("Section 2 reviews…") is normal in an introduction | Cut all meta commentary |
| Hedging | Hedge real uncertainty precisely ("the evidence is mixed"), not by habit ("seeks to", "potential remedy") | "I think" and "probably" are fine |
| Numbers | Follow the style guide (often words for one to nine) | Digits |
| Citations | Keep every one exactly as written | Use sources only when they add value |

Both modes: no em dashes in the revised text; use commas, colons, periods or parentheses.

## 3. Ask before you invent

Never invent statistics, study results, quotes, named examples, personal experience, dates, prices or
outcomes. When a passage needs one, you can:
1. **Ask** ("What was the screening count in your PRISMA flow?").
2. **Write around it** honestly.
3. **Leave a marked placeholder**, `[need: real figure]`, and tell the user to fill it.

If the user shares samples of their own writing, match those over these defaults.

## 4. Word-level bans

**Banned phrase shapes.** These are bloated verbs that dodge *is/has*: serves as, stands as, acts as,
functions as, marks a, represents a, boasts, features a, offers a, plays a role in, helps to, aims to,
seeks to. Use the plain verb: is, has, uses, gives, shows, causes, changes, removes, adds.
- "The report serves as a guide." → "The report is a guide."
- "Credit plays a crucial role in the economy." → "An economy runs on credit."

**Dead openings and phrases:** In today's…, It is important to note that…, It is worth noting…, In
order to, Let's dive in / explore / unpack, At the end of the day, Moving forward, To put this in
perspective, What makes this particularly interesting is, In other words, It goes without saying,
Most people don't realise, In this article I will.

**Dead transitions:** Furthermore, Additionally, Moreover, That said, That being said, With that in
mind, It is also worth mentioning, On top of that. Use a real link to the previous point, or nothing.

**Banned vocabulary** (the script flags these as VOCAB): delve, realm, harness, unlock, tapestry,
paradigm, cutting-edge, revolutionise, intricate, showcase, crucial, pivotal, surpass, meticulous,
vibrant, unparalleled, underscore, leverage, synergy, innovative, game-changer, testament, groundbreaking,
foster, holistic, garner, pioneering, unleash, versatile, transformative, redefine, seamless,
breakthrough, empower, streamline, elevate, effortless, insightful, proactive, visionary, reimagine,
unprecedented, democratise, state-of-the-art, supercharge, enduring, interplay, valuable, captivate.
In academic mode the literal technical terms in section 2 are exempt.

**Engagement bait and hype:** Let that sink in, Read that again, Full stop, This changes everything,
10x, future-proof, supercharge. Cut them.

## 5. Negative parallelism and reframes

A sentence or pair of sentences fails if it **dismisses X and then asserts Y**, even without the word
"not". The script flags it as REFRAME.

Obvious: "This isn't X. It's Y.", "Not X. Y.", "Not only X, but also Y.", "It is not just about X, it
is about Y.", "The problem is not X. It is Y.", "It was never about X.", "Less X, more Y."

Sneaky openers that set up a pivot: While X may seem…, Although X appears…, At first glance…, On the
surface…, Most people think…, Many assume…, Conventional wisdom says…

Across sentences: "Most teams think they have a hiring problem. They have a standards problem." →
"The team's standards are unclear."

**Fix:** delete the rejected half, then state the claim directly.
- "They are not solely related to technical flaws, but can be manifestations of how institutions are
  structured." → "These problems also reflect how systems, data and institutions are structured."

**Allowed contrast:** correcting a specific fact, scope, legal or technical distinction. Examples:
"Tuesday, not Thursday." "A civil deadline, not a criminal one." In academic writing, contrasting
your framework with a *named* prior approach is a real distinction and is allowed: "Unlike Altman's
(1968) Z-score, the model uses transaction data." A vague strawman is not allowed.

Rhetorical questions that reject and replace ("Is this a productivity problem? No.") are banned too,
and so are reframe headings ("Not a tool. A system.", "The real problem", "Beyond X", "From X to Y").

## 6. Analogy and metaphor control

Default: no analogies. Use one only if all five hold: the subject is abstract or technical, the
analogy makes it easier to understand, it is shorter than the literal version, it won't mislead,
and it sounds normal read aloud. At most 1 per 800–1,500 words, never stacked.

Banned setups: think of it as, imagine, picture, it is like, works like, acts like, functions as,
serves as, a bridge between, a lens for, a roadmap for, the engine / fuel / backbone / foundation /
fabric / heartbeat / DNA / glue of.

Banned metaphor families unless the subject is literal: journeys, battlefields, ecosystems, engines,
maps and compasses, icebergs, bridges, north stars, flywheels, scaffolding, plumbing, gardens, chess,
sports, puzzles. *Academic note:* established field terms such as "data ecosystem", "digital
infrastructure" or "information asymmetry" are technical vocabulary, not decoration. Keep them.

Metaphor verbs for abstract work (woven, layered, baked in, fuelled, sparked, anchored, unpacked,
distilled, surfaced, amplified, bridged…): use literal verbs instead (added, removed, joined, caused,
showed, explained, reduced, clarified, compared).

## 7. Other machine patterns

- **Puffery:** a key turning point, a pivotal moment, broader implications, setting the stage for.
  State the fact and let the reader judge its weight.
- **Rule of three:** don't make every list three items. Use the true number.
- **False ranges:** "from ancient traditions to modern innovation". Delete it if the range has no meaningful middle.
- **Elegant variation:** don't rename the subject to avoid repetition ("Sarah… the seasoned operator").
  In academic text, keep one term for one concept throughout.
- **Fake-depth participles:** ", highlighting its importance", ", reflecting broader trends",
  ", paving the way for". If the point matters, give it its own sentence with a specific claim.
- **Meta commentary and AI disclaimers:** "Let me walk you through", "As of my last update". Delete.
- **Metronome rhythm:** same-length sentences and same-size paragraphs. Vary both.
- **Staccato overcorrection:** three or more very short sentences in a row, or a whole passage of
  fragments, is the opposite tell. Restore some longer sentences.
- **False agency:** "the data tells a story", "the results speak for themselves", "paints a clear
  picture". State the finding: "Default rates fell from 6% to 4%."
- **Generic conclusions:** the future looks bright, only time will tell, remains to be seen, one thing
  is certain, continues to evolve or shape, poised for growth. End on the actual finding or implication.
- **False concession:** "While X is promising, Y remains a challenge." Name the actual tradeoff.
- **Parenthetical hedging:** "(and perhaps more importantly, …)", "(arguably …)". Give it its own sentence or cut it.
- **Reader steering and novelty bait:** "Here's what's interesting", "worth exploring", "a problem nobody talks about".
- **Chat artifacts:** "To answer your question", "Let me think step by step", "Breaking this down".
- **Numbered-list inflation:** "Three key takeaways" when the count is chosen for format, not meaning.
- **Recap coda:** a final paragraph that restates earlier facts as a lesson. Cut it, except in abstracts
  and executive summaries, where restating the main point is the genre.
- **Post-ChatGPT academic vocabulary** (Berens & Kobak, *Science Advances* 2024, excess-word study of
  14M PubMed abstracts): elucidate, delineate, underpin, unveil, invaluable, noteworthy, holds (great)
  promise, new avenues, shed (new) light, warrants further investigation, in recent years, with the
  advent of, taken together, garnered significant attention, a deeper / more nuanced understanding,
  ever-evolving, a growing body of, comprehensive, multifaceted, notably. Each is legitimate alone. Three
  in one paragraph reads as generated. Keep the one that is exact and replace the rest with plain words or
  a specific claim ("holds great promise" → what it improved, by how much, with a citation).
- **Vague attribution:** "has been described as", "is widely regarded as", "observers have noted",
  "a growing body of". These are fine with a named source. Otherwise ask for one.

## 8. Anti-overfitting

The longest list here is of things to avoid. Reading it as a demand for clipped prose creates its own
tell. Don't make every sentence punchy or every paragraph one line, don't add slang, and don't drop an
exact word for a worse synonym. Write normally, then remove what sounds machine-made, and stop when it
sounds like the author. Test: does this sound like the author, or like an AI imitating them?

Don't write to beat an AI detector. Detectors are unreliable, and chasing a score produces worse sentences.

## 9. Final pass (run silently before sending)

1. Cut throat-clearing first sentences.
2. Replace vague claims with specific ones, or mark `[need: …]`.
3. Remove inflated importance.
4. Check for repeated sentence shapes and same-size paragraphs.
5. Replace bloated verbs.
6. Find reframes, including ones across sentences, and delete the rejected half.
7. Remove unearned analogies and metaphor verbs.
8. Cut an ending that only repeats the point.
9. Confirm every fact, number, name and citation came from the user. List any placeholders left.
10. No em dashes in the revised text.
11. Preserve every citation, number and acronym (run `scripts/check_preservation.py`).

---

## 10. Register guards (what must survive)

Before editing, note the wording that carries legal, scientific or safety weight, and protect it exactly.
These spans are constraints, not style problems.

- **Scientific uncertainty:** may cause, can increase, suggests, preliminary, observational, "does not
  establish causation", confidence limits, sample or cohort limits.
- **Legal scope and negation:** shall, must, may, unless, except, not, arguably, section references, limits.
- **Safety and security absolutes:** never, always, must, all input, no secrets, when they state a rule.
- **Scope and quantity:** most, some, only, mainly, at least, no more than, percentages, ranges, dates, named parties.
- **Conditions and negations:** "if A then B" must not become "A and B"; "does not support" must not
  become "partially supports".
- **Comparisons and causal claims:** "3x faster" keeps the 3x; "A caused B" must not weaken to "A influenced B".
- **Approximations:** "about 50%" stays approximate; don't sharpen it to "50%".
- **Lists:** every item survives. Reordering is fine.

**Habit hedges vs load-bearing hedges.** "This study seeks to examine" is a habit hedge: the study does
examine, so write "examines". "These results suggest a causal link" is load-bearing: the evidence only
suggests, so "suggest" stays. If you can't tell, keep it and mention it under "Check these yourself".

## 11. Smallest-repair contract

- **Confirm before editing.** A flag from a script, or a word on a list here, never justifies an edit by
  itself. Confirm the problem in context, such as filler whose deletion loses no meaning, or an inflated
  word with a plain equivalent. Otherwise record it as protected: literal, domain-valid, quoted,
  attributed, accurately caveated or genre-natural.
- **Repair only confirmed sentences**, with the smallest change. Copy every other sentence unchanged. If
  nothing is confirmed, return the text unchanged and say so. A no-op beats an uncertain edit.
- **Add nothing:** no claims, advice, personality, anecdote, certainty or conclusion.
- **Delete empty framing** without substituting new filler.
- **Read every sentence yourself before looking at the script output**, including headings and the last
  line. Phrase lists are incomplete, so recognise padding by what it does.
- **Punctuation, vocabulary or rhythm alone proves neither a defect nor machine authorship.**
- **Re-read the revision** for negations, conditions, scope, certainty and who-does-what, then stop.
  Don't keep polishing matters of taste.
