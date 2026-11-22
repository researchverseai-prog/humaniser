# Third-party notices

This skill adapts material from two MIT-licensed projects. Both are used under the MIT License,
whose text is in `LICENSE`.

- **Anti-AI Writing Style** by Avik Bal, https://github.com/avikbal-dm/anti-ai-writing-claude-skill
  (MIT, Copyright 2026 Avik Bal). Adapted: the AI-tell ruleset (banned vocabulary and phrase shapes,
  negative-parallelism ban, analogy control, final pass) in `humaniser/references/style-rules.md` §1–9
  and the matching detectors in `humaniser/scripts/humanize.py`.
- **unslop** by Clayton Kim / OPSHARP, https://github.com/OPSHARP/unslop (MIT). Adapted: the
  smallest-repair contract, register guards and fact-preservation rules (`style-rules.md` §10–11,
  `scripts/check_preservation.py`), and parts of its phrase catalogue, including the academic excess
  vocabulary from Berens & Kobak, "Delving into ChatGPT usage in academic writing", *Science Advances* (2024).

No code was copied verbatim from either project. The scripts here are independent implementations.
