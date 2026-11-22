# Humaniser: a Claude skill for academic prose

A Claude skill that revises stiff, machine-sounding writing, especially literature reviews, methods
sections, abstracts and theses, so it reads like a careful person wrote it. It **keeps every citation,
number, hedge and negation intact** and never invents facts.

It is an editing aid, not an AI-detector bypass tool. Detectors are unreliable, and writing to beat one
produces worse sentences.

## What it does

1. **Analyses** the text with `scripts/humanize.py`. The analyser:
   - Reports sentence and paragraph rhythm metrics.
   - Removes stock transitions and filler.
   - Flags AI tells: bloated verbs, "not X but Y" reframes, post-ChatGPT academic vocabulary, false
     agency, generic conclusions, vague attribution, habitual three-item lists and em dashes.
2. **Hand-edits** with Claude, following the rules in `references/style-rules.md`. There is an academic
   mode (the default) and a general mode for emails, posts and web copy.
3. **Verifies** with `scripts/check_preservation.py`, which checks that the rewrite kept every citation,
   number, acronym, quotation, negation, condition and hedge. It also catches citations or numbers that
   were added, and rewrites that turned choppy.
4. **Replies** with the revised text, what changed and why, a preservation summary, and a list of things
   only the author can check.

It also has an **audit mode**: say "just flag the AI tells" and it lists issues and protected spans
without rewriting.

It can also **check another tool's output.** Paste your source and a paraphraser's or humaniser's
version, and it lists the meaning damage those tools typically cause: renamed defined terms, changed
fields, dropped claims, shifted hedges, invisible zero-width characters and spun phrasing. Then it
rewrites from your source instead.

## Install

**Claude.ai.** Download [`humaniser.skill`](humaniser.skill), then go to Settings → Capabilities →
Skills and upload it.

**Claude Code.** Copy the `humaniser/` folder into `~/.claude/skills/`:

```bash
git clone https://github.com/researchverseai-prog/humaniser.git
```

```bash
cp -r humaniser/humaniser ~/.claude/skills/
```

## Use

Paste a paragraph and say "humanise this", "de-AI this" or "run the humaniser". After the first turn,
pasting the next paragraph is enough.

The scripts also run on their own (Python 3, no dependencies):

```bash
python3 humaniser/scripts/humanize.py draft.txt --analyze-only
```

```bash
python3 humaniser/scripts/check_preservation.py original.txt revised.txt
```

## Layout

```
humaniser/
├── SKILL.md                    # skill instructions (workflow, rules, response format)
├── references/style-rules.md   # full ruleset: modes, bans, register guards, final pass
└── scripts/
    ├── humanize.py             # analyser and safe mechanical edits
    └── check_preservation.py   # citation/number/hedge preservation check
humaniser.skill                 # packaged bundle for Claude.ai upload
```

## Credits and licence

MIT, see `LICENSE`. This skill adapts rules from Avik Bal's *Anti-AI Writing Style* and from
OPSHARP/unslop, both MIT-licensed. See `NOTICE.md`.
