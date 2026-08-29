# Agent memory — mirror for device migration

Claude Code keeps its per-project memory **outside the repo**, at:

```
<home>/.claude/projects/<project-slug>/memory/
```

`git push` does **not** carry that directory. This folder is a committed copy of
those files so they survive a machine change. Snapshot date: **2026-08-30**.

Files (same names as the live memory dir):

| file | what it is |
|---|---|
| `MEMORY.md` | the index loaded into every session — one line per memory |
| `pipeline-architecture-2026-08.md` | validation gate, per-subject config, non-destructive merge, 2026-08-28 OCR hardening, **2026-08-30 Step-7 truncation gate** |
| `bgs-issues.md` | BGS: no hallucinated chapters; ch1 date + আগরতলা fixes; ch13–15 page-range bug; ch3 mid-chapter truncation; partial run |
| `higher-math-partial-run.md` | Higher Math: partial run — do NOT auto-run or ad-hoc fix |
| `accounting-issues.md` | Accounting: known misreads, chapter-map typo, owes body reconciliation |

## Restore on the new device

1. Clone the repo, then run Claude Code once inside it (any prompt) so it creates
   `~/.claude/projects/<slug>/`.
2. Find `<slug>`: it is the repo's absolute path, lowercased, with the drive
   colon removed and every `\` or `/` turned into `-`
   (`F:\vibe-code\nctb-topic-mapping` → `f--vibe-code-nctb-topic-mapping`).
   If the new checkout path differs, the slug differs — just look for the
   `~/.claude/projects/*/` directory that was created in step 1.
3. Copy every `*.md` in this folder into
   `~/.claude/projects/<slug>/memory/` (create `memory/` if absent).
   Keep `MEMORY.md` as the index.
4. Verify: start a new session; the `MEMORY.md` lines should appear in context.

## Keeping this mirror current

This is a snapshot, not a live link. After any session that changes the live
memory, re-copy the files here (or run: from repo root,
`cp ~/.claude/projects/<slug>/memory/*.md docs/agent-memory/`) and commit.
