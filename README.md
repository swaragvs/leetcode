# LeetCode Solutions

Automatically synchronized archive of my LeetCode submissions.

This repository is kept up to date by a small, self-written GitHub Actions
workflow (see `.github/workflows/`) that checks for new **accepted**
submissions and commits them here. No third-party sync action is used —
every line of automation in this repo is auditable.

## Progress

<!-- STATS_START -->
| Difficulty | Solved |
|------------|--------|
| Easy       | 4      |
| Medium     | 1      |
| Hard       | 0      |
| **Total**  | **5** |
<!-- STATS_END -->

*(This table updates automatically after each sync.)*

```
solutions/
├── 0001-two-sum/
│   └── solution.py
├── 0020-valid-parentheses/
│   └── solution.py
└── ...
```

Each folder is named `<problem-number>-<slug>` and contains the accepted
solution exactly as submitted, plus a short metadata note (runtime,
language, submission date).

## How this works

1. A scheduled GitHub Action runs daily (and can be triggered manually).
2. It reads my recent accepted submissions.
3. It diffs them against what's already archived.
4. New solutions are added and committed with `GITHUB\_TOKEN` — no personal
access token required.

See the project plan in `docs/` (added in a later phase) for the full
security rationale.

