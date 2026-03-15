# Claude Code Journaling

A set of prompts and agents for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that process daily journal entries into structured monthly reviews from multiple perspectives.

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

