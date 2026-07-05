---
name: branch-completion
description: "Use when finishing a branch or PR after verification and review, including merge, PR publication, keep, discard, cleanup, local sync, and reporting merge or PR URLs with current git state."
metadata:
  short-description: Finish branch and PR lifecycle
---

## Purpose

Use this skill to close the lifecycle of a branch or PR after implementation,
verification, and review.

It makes the end state explicit: merged, published for review, kept, discarded,
or cleaned up later.

## Preconditions

- Inspect current git state before acting.
- Keep unrelated local changes out of commits, pushes, merges, and cleanup.
- Confirm required verification and review state from the repository's source
  of truth.
- Use non-destructive cleanup by default. Delete local or remote branches only
  when the user or workflow explicitly allows it.

## Decision Paths

### Publish PR

Use when the branch is implemented and verified but still needs review.

- Check branch name, base branch, staged files, untracked files, and remote.
- Commit only in-scope changes.
- Push the branch.
- Open or update the PR.
- Report the raw PR URL.

### Merge PR

Use when review and required checks allow merge.

- Verify approval or explicit merge authorization.
- Verify required checks are passing or intentionally non-required.
- Merge using the repository-preferred method.
- Sync local main with the remote default branch.
- Report the raw PR URL and merge commit or squash SHA.

### Keep Branch

Use when a branch should remain open for more work.

- Record why it remains open.
- Record next steps and blockers.
- Leave local and remote branches intact.

### Discard Branch

Use only with explicit authorization or a workflow rule that clearly permits
discarding the branch.

- Record the branch, commits, and unmerged changes before discarding.
- Preserve or report unrelated worktree changes.
- Avoid destructive git commands unless the user explicitly requested them.

### Cleanup

Use after merge or abandonment when cleanup is allowed.

- Sync the default branch first.
- Remove only branches known to be completed and safe to delete.
- Leave unknown, dirty, or unrelated branches untouched.

## Completion Record

```markdown
Decision: merge | publish-pr | keep | discard | cleanup-only

Git state:
- current branch:
- base/head:
- dirty or untracked files:

Evidence:
- verification:
- review/approval:
- CI/checks:

Actions:
- <commit/push/PR/merge/sync/cleanup performed>

Result:
- PR URL:
- merge SHA:
- local sync state:
- cleanup deferred:
```

## Output expectation

- Fill the Completion Record above with a decision of exactly one of: `merge`, `publish-pr`, `keep`, `discard`, `cleanup-only`.
- Record current branch, base/head, and dirty/untracked file state.
- Record verification, review/approval, and CI/checks evidence.
- List the actions actually performed (commit/push/PR/merge/sync/cleanup).
- Report the raw PR URL and, when merging, the merge or squash SHA.
