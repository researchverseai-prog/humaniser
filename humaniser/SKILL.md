---
name: humaniser
description: Revise or audit stiff, machine-sounding prose, especially academic writing (literature reviews, abstracts, methods, theses) but also emails and web copy, so it reads like a careful human wrote it. Varies sentence and paragraph rhythm, cuts formulaic transitions and filler, fixes word-choice errors, removes AI tells ("not X but Y" reframes, bloated verbs, post-ChatGPT academic vocabulary), and verifies that every citation, number, hedge and negation survived. Also checks text from other humaniser or paraphrasing tools against its source for renamed terms, dropped claims and hidden characters. Use whenever the user asks to humanise, de-AI or de-slop text, make it less robotic or more natural, flag AI tells, shorten a passage by a percentage, or says "run the humaniser", even if they just paste the next paragraph after earlier humanising turns.
---

# Humaniser

Turn uniform, formulaic prose into writing with natural rhythm, while keeping every claim, citation and technical term the author wrote. The skill pairs deterministic scripts (metrics, safe mechanical edits, flags, a preservation check) with a hand edit, because most of what makes text read as machine-written (flat rhythm, hedges, wrong words) needs judgement the scripts don't have.

## Ground rules (and why)

- **Never add facts, citations, numbers, examples or personal anecdotes.** A humaniser that invents a study or a "when I was at university…" story creates fabricated scholarship. Where specifics or first-person voice would help, ask for them, write around them honestly, or leave a marked placeholder like `[need: screening count]`, and list any placeholders left at the end.
- **Keep meaning exactly.** That covers citations (e.g. "(Scott et al., 2024)"), numbers, defined terms, acronyms, negations, conditions and scope words (*mainly, most, only*). Changing "mainly concentrates" to "concentrates", or "failing to give" to "never gives", changes the claim even when it reads better.
- **Keep load-bearing hedges.** In scientific, legal, medical and security text, words like *may, suggests, preliminary, arguably, must* and *never* carry the claim's certainty. Only habit hedges get cut ("seeks to", "potential remedy", "it could be argued that"). If you're unsure which kind a hedge is, keep it. See `references/style-rules.md` §10.
- **Make the smallest repair.** Edit only sentences with a confirmed problem, and copy every other sentence unchanged. If nothing is wrong, say so and return the text as it is. A script flag alone never justifies an edit: confirm it in context, or record it as protected (a literal, domain-valid, quoted or attributed use).
- **Don't overcorrect into staccato.** Strings of short punchy sentences are their own AI tell. Vary length; don't just shorten.
- **Keep the register.** Academic text should stay academic. The aim is clearer and more varied prose, not casual prose. Pick a mode: **academic** (the default: no contractions, literal technical terms like *data-driven* or *predictive* stay) or **general** (emails, posts, web copy: contractions, I/you, shorter paragraphs). See `references/style-rules.md` §2.
- **Rule priority when rules collide:** accurate > clear > specific > sounds human > style. If a rule makes a sentence worse, break it.
- **This is an editing aid, not a detector-evasion tool.** If the user frames the goal as beating Turnitin/GPTZero, still help with the writing, but don't promise or optimise for detector scores (detectors are unreliable, and chasing a score makes sentences worse), and remind them once that submitting machine-generated work as their own may breach their institution's rules.

## Choose the flow

- **Audit:** "just flag it", "don't change anything", "review this before I submit". Run step 2 with `--analyze-only`, read every sentence yourself, and reply with the audit format below. Don't rewrite.
- **Rewrite:** the default for "humanise this" or a bare pasted paragraph. Follow the full workflow.
- **Compare tool output:** the user pastes a source text *and* another tool's "humanised" or paraphrased version, or asks "is this version OK?" or "what did this tool change?". Follow "Checking another tool's output" below. Those tools swap synonyms without understanding the text, so they often rename defined terms, change the field, drop claims or shift hedges while sounding fluent.

## Checking another tool's output

1. Save the source as `original.txt` and the tool's version as `spun.txt`. Run:
   ```bash
   python3 <skill-dir>/scripts/check_preservation.py original.txt spun.txt
   python3 <skill-dir>/scripts/humanize.py spun.txt --analyze-only
   ```
2. **Meaning damage comes first.**
   - **`named term RENAMED`:** a defined term was changed, e.g. "Algorithmic" → "Artificial Information Infrastructure". Always blocking.
   - **Missing citations or numbers.**
   - **The dropped-content-words list:** read the source sentences those words came from and say which claims vanished.
   - **Changed hedge, scope or negation counts.**
   - **Things no script sees:** read both versions side by side for a changed field or discipline ("Information Systems" → "Communication Systems"), reversed or weakened claims, and new claims the source never made ("particularly important from governance perspectives").
3. **Then the style damage.** `[SPUN]` flags paraphraser phrasing ("make use of", "bring about", "the possibility to utilise", "Any possible issue", "As to theory", "provides a contribution to"). The tool usually keeps or adds the AI tells it was meant to remove ("not only… but also", "not merely X, but"), so check `[REFRAME]` too.
4. **Respond:**
   - **A table:** source wording | tool's wording | what changed in meaning.
   - **A verdict:** usually "don't use this version".
   - **A clean revision built from the source,** not from the spun text, following the normal rewrite workflow.
   - **One sentence of advice:** paraphrasing tools trade meaning for surface variation, and invisible characters or spun phrasing are themselves things reviewers and detectors now notice.

## Workflow (rewrite)

1. **Save the original** to `original.txt` in a scratch location, with a blank line between paragraphs.
2. **Run the analyser** for metrics and flags:
   ```bash
   python3 <skill-dir>/scripts/humanize.py original.txt --seed 3 -o script.txt
   ```
   - **Mode:** add `--mode general` for non-academic text.
   - **Report:** it goes to stderr: before/after metrics, the changes made, and a NEEDS YOU list.
   - **Paragraph reshaping:** off by default because it misfires. Do paragraph structure by hand.
   - **Input cleaning:** the script strips invisible characters (zero-width joiners and similar) and adds missing spaces after full stops ("governance.AI"). It reports `[HIDDEN]` and `[SPACING]`. Always tell the user about `[HIDDEN]`: some humaniser tools insert these characters to fool detectors, and detectors now flag them. Strip them from `original.txt` too before step 6, so the comparison is fair.
3. **Check the script's output before trusting it.** Its edits are rule-based and can misfire, for example lowercasing a name after a removed opener, or a swapped connector ("And…") that reads flat. When it barely changes anything, which is common with academic text, say so plainly.
4. **Hand edit**, starting from the original (not the script output, if the script's changes were poor).
   - **Read every sentence yourself.** Phrase lists are incomplete, so recognise padding by what it does.
   - **Resolve each flag:** mark it *confirmed* and fix it, or *protected* and say why.
   - **Full ruleset:** for anything beyond a paragraph or two, or for REFRAME, VOCAB and analogy flags, read `references/style-rules.md`.
5. **Run the final pass** in `references/style-rules.md` §9 silently.
6. **Verify preservation.** Save the revision to `revised.txt` and run:
   ```bash
   python3 <skill-dir>/scripts/check_preservation.py original.txt revised.txt
   ```
   - **`[FIX]` lines are blocking:** a missing or altered citation, number or acronym, an added citation or number, a dropped negation or condition, or a rewrite that became staccato. Fix the revision and rerun.
   - **`[CHECK]` lines** (hedge, scope or obligation counts changed, a named term missing, large rewrite): re-read the sentence and confirm the meaning is the same. Mention any real change under "Check these yourself".
7. **Respond** in this shape:
   - One line on what the script did (or didn't do) and any misfire.
   - The revised text as a blockquote.
   - **What changed and why:** short bullets naming the original wording → new wording.
   - **Preserved:** one line from the check, e.g. "Citations, numbers and acronyms 5/5; one negation added on purpose (see below)."
   - **Check these yourself:** facts only the author knows (acronym first use, referents like "This" across paragraphs, journal style for serial commas and first person, real numbers or citations they could add, placeholders left).

If the user sends the same text again, give a structurally different alternative (e.g. problem-first instead of study-first) and say when each version suits (abstract vs. methods section).

## Audit format

```markdown
## Issues found
- "<smallest defective span>": <category>. <why it reads as machine-written or unclear> → <suggested fix>

## Protected (flagged but fine here)
- "<span>": <why it stays: literal, domain term, load-bearing hedge, attributed, genre-natural>

## Overall
<1–2 lines: the biggest pattern, e.g. "uniform 20-word sentences; four habit hedges">
```

## Methods, in order of impact

1. **Break the paragraph-length pattern.** Avoid runs of paragraphs that are all 4–6 sentences. Split a paragraph that does two jobs (for example, problem plus contribution). Use a short paragraph for emphasis, but only for a strong line, never for a weak trailing one. Vary where the topic sentence sits.
2. **Vary sentence length.** Machine prose sits at 15–25 words per sentence. Cut 40-word noun piles into two or three sentences, add a short declarative line ("The theory is fragmented too."), and merge choppy pairs. Aim for rhythm, not chaos. A sentence-length CV (spread of sentence lengths relative to the average) of about 0.5 or more is typical of human prose.
3. **Replace formulaic transitions.** Moreover, Furthermore, Additionally, In conclusion, Initially/Subsequently/Thereafter, "it is important to note that". Delete them, or replace with a concrete link to the previous point ("used to be… Over time…").
4. **First-person voice, only where the format allows.** Many journals accept "we propose". Suggest it; don't force it.
5. **Concrete specifics.** Flag "many studies show", "some experts argue" or "a growing body of" and ask for the real source. Never supply one.
6. **Remove AI tells.**
   - **Bloated verbs:** serves as, plays a role in, aims to, seeks to → is, has, shows.
   - **Banned vocabulary:** delve, crucial, pivotal, harness, leverage, underscore…
   - **Post-ChatGPT academic vocabulary when clustered:** elucidate, underpin, shed light, holds promise, a more nuanced understanding, in recent years, garnered attention, warrants further investigation.
   - **"Not X but Y" reframes, even across sentences:** delete the rejected half and state the claim directly. Contrast with a *named* prior approach or a factual correction is fine.
   - **Fake-depth participles and false agency:** ", highlighting…", "the data tells a story".
   - **Generic closers and false concessions:** "only time will tell", "continues to evolve", "While X is promising, Y remains a challenge".
   - **Habitual rule-of-three lists and unearned analogies:** "the backbone of", "a bridge between". Field terms like "data ecosystem" stay.
   - **Dashes:** no em dashes in the revised text.
7. **Read-aloud pass.** Rewrite noun-heavy lines ("enriches the body of research by providing…") as a person would say them. Fix misused words (enlist ≠ list), redundancy ("such as… etc."), habit hedges ("seeks to", "potential remedy") and broken agreement ("This can… they…").
8. **Structural check.** Reread the whole passage. Logical order (gap before remedy), clear referents, consistent style, and no recap ending that only repeats earlier facts.

## Script reference

Both scripts are pure Python 3 with no dependencies.

`scripts/humanize.py`: analyse and make safe mechanical edits.

| Flag | Meaning |
|---|---|
| `-o FILE` | write revised text (otherwise stdout) |
| `--analyze-only` | metrics + flags, no rewrite |
| `--seed N` | reproducible choices |
| `--max-words N` | split sentences longer than N (default 30) |
| `--mode academic\|general` | academic (default) exempts literal technical terms from VOCAB and is gentler on rule-of-three |
| `--reshape-paragraphs` | also split/promote paragraphs automatically (off by default) |

Report tags:
- `[SPECIFICS]` vague attribution
- `[REWORD]` stock phrase, bloated verb, hedge, puffery, false agency, generic closer, false concession, analogy setup, fake-depth participle, chat artifact or misused word
- `[REFRAME]` "not X but Y" negative parallelism, within or across sentences
- `[VOCAB]` AI-favoured words in the paragraph
- `[ACADEMIC-VOCAB]` cluster of post-ChatGPT excess words (soft: fine alone)
- `[RULE-OF-3]` habitual three-item lists
- `[DASH]` em/en dash
- `[READ-ALOUD]` long or noun-heavy sentence
- `[VOICE]` no first-person markers
- `[SPUN]` two or more paraphraser-tool phrases in a paragraph: the text was probably run through a synonym spinner, so check its meaning against the source
- `[HIDDEN]` / `[SPACING]` invisible characters removed, or missing spaces after full stops added

`check_preservation.py` adds:
- `named term RENAMED` (blocking): a capitalised term reappears with a word changed.
- A list of dropped content words, which points to claims that may have vanished.

Flags are prompts for judgement, not verdicts: "not only X but also Y" can be a legitimate scope statement in a methods section.

`scripts/check_preservation.py original.txt revised.txt` compares the two versions.
- **What it checks:** citations, numbers, acronyms, quotations, URLs/DOIs and named terms; counts of negation, hedge, obligation, scope and condition words; the share of wording changed; and staccato drift.
- **Exit codes:** 1 if anything blocking is found, 0 otherwise.

Known limits: `humanize.py` won't split lists ("A, B, and C"), can't fix word-choice errors on its own, and moves sentence-length variance only a little. `check_preservation.py` compares counts and strings, not meaning: a rephrased condition can pass while changing sense, so step 6 still needs a re-read.

Credits (both MIT License):
- The AI-tell rules are adapted from Avik Bal's *Anti-AI Writing Style* skill.
- The preservation contract, register guards and extended phrase catalogue are adapted from OPSHARP/unslop. Its academic vocabulary comes from Berens & Kobak, *Science Advances* (2024).
