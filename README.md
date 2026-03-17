# Claude Code Journaling

A set of prompts and agents for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that process daily journal entries into structured monthly reviews from multiple perspectives.

## Privacy

Your journal entries are processed by Claude via the Anthropic API. Here is an honest breakdown of what that means:

**What Anthropic does with your data**

- **Training**: Anthropic's API does not use your data to train its models by default. This is covered by their [API usage policy](https://www.anthropic.com/legal/aup). The consumer product (Claude.ai) has different terms — this system uses the API.
- **Persistent storage**: API calls may be logged temporarily for safety and abuse detection purposes. Zero Data Retention (ZDR) — which disables server-side logging entirely — exists but is only available to Anthropic enterprise customers. It is not available to standard API users.

**What data is sent to the API**

Every time you run `/monthly-review`, the following is transmitted to Anthropic's servers:
- Full text of your daily journal entries for that month
- Context files: `core-profile.md`, `relationships.md`, `focus-personal.md`, and `current.md`

**Optional: Name anonymization**

This repo includes `anonymize.py`, a script that replaces names in your journal files with abstract labels (`Person-A`, `Person-B`, etc.) before processing. This reduces identity attribution risk if data is ever exposed.

**Important limits of anonymization:**
- It only protects the names you explicitly list — there is no automatic detection
- It does **not** protect the content of your entries (events, medical details, situations, etc.)
- Sensitive content transmits regardless of whether names are replaced

See [`names.txt.example`](names.txt.example) and the [anonymize.py usage section](#using-anonymizepy) below for setup instructions.

**For maximum privacy**

If you require that no journal data leaves your device under any circumstances, this system in its current form is not suitable. Local LLM alternatives (e.g., Ollama) exist but are out of scope for this project and involve significant quality tradeoffs.

---

## How It Works

Each month, your daily journal entries are analyzed through 6 different perspectives in parallel, then synthesized into a single comprehensive monthly report.

### Perspectives

| File | Role |
|------|------|
| `therapist.md` | Clinical psychologist — emotional patterns, coping mechanisms, cognitive distortions |
| `coach.md` | Performance coach — goals, productivity, obstacles, accountability |
| `relationships.md` | Relational therapist — connection, attachment patterns, social energy |
| `strengths.md` | Objective observer — evidence-based positives, growth, unacknowledged wins |
| `values-meaning.md` | Philosophical counselor — authenticity, purpose, flow states, values alignment |
| `chronicle.md` | Life chronicler — factual record of events, people, activities |

### Agents

- **`monthly-processor`** — Reads all journal entries for a given month and generates an analysis from a single perspective
- **`monthly-synthesis`** — Combines all 6 perspective analyses into a themed final report

### Commands

- **`/monthly-review`** — Orchestrates the full pipeline: launches 6 perspective agents in parallel, then synthesizes
- **`/interview`** — Asks questions to build up your personal context files
- **`/update-current`** — Updates a "current state" file from recent journal entries

## Using anonymize.py

`anonymize.py` is an optional pre-processing step that replaces names in your journal files before running `/monthly-review`. Original files are never modified.

**Setup**

```bash
# 1. Copy the example and add your own names
cp names.txt.example names.txt

# 2. Edit names.txt — one mapping per line
# Format: RealName → Label
# Example:
#   Michael → Person-A
#   Sarah → Person-B
#   Dr. Chen → Doctor-X
```

**Run**

```bash
python anonymize.py --month 2026-03
# Anonymized copies are written to journals-anonymized/
```

Then temporarily update the journal path in `.claude/agents/monthly-processor.md`. Find this line:

```
`06 Agenda/Journal/YYYY-MM-*.md`
```

And change it to:

```
`journals-anonymized/YYYY-MM-*.md`
```

Run `/monthly-review` as normal, then revert the path change when done.

**Notes**

- `names.txt` and `journals-anonymized/` are git-ignored — they stay on your machine
- Longer names are replaced before shorter ones to avoid partial-match issues (e.g., "Anna" won't corrupt "Annabelle" if "Annabelle" is listed first)
- Re-running the script on the same input always produces the same output

