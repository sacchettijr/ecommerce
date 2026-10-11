---
description: Reconcile .claude/ documentation and memory with verified implementation changes
---

Reconcile project documentation/memory with the current implementation:
$ARGUMENTS

Use this after a chunk of real implementation work (not for routine,
single-file edits — that's `context.md`'s job). Steps:

1. Identify what actually changed since `.claude/memory/changelog.md`'s
   last entry — use `git log`/`git diff` and your own recollection of this
   session's work, not assumption.
2. For each change, find the `.claude/context/*.md` file(s) it affects
   and update them to match reality. Re-verify the surrounding content in
   that file while you're there — don't just append without checking the
   rest is still accurate.
3. If a previously-logged issue in `.claude/memory/known_issues.md` was
   fixed, remove it or mark it resolved (with the commit/change that
   fixed it) rather than leaving it to look unresolved.
4. If a new issue was discovered during the work, add it to
   `known_issues.md` with a clear confirmed-vs-hypothesis label.
5. Add a `.claude/memory/changelog.md` entry summarizing what changed and
   why.
6. Update `.claude/memory/current_task.md` to reflect the current
   objective and next steps, replacing stale content rather than
   appending indefinitely.
7. Report what was reconciled and what (if anything) in `.claude/` is
   still out of date and needs a follow-up.
