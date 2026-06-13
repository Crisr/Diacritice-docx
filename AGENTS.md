# Agent Instructions

<!-- xls-files -->
## XLS Files — Read-Only, Never Modify

**CRITICAL: Never modify, restore, delete, or replace any `.xls` files in `data/input/` (PretITFRR.xls, Achizitie.xls).** Read-only access only. If you see them changed in git status, DO NOT run `git restore` or any operation that alters them without explicit user approval. Always ask first. These files are user-managed and must not be touched.
<!-- /xls-files -->

<!-- lean-ctx -->
## lean-ctx

Prefer lean-ctx MCP tools over native equivalents for token savings.
Full rules: @LEAN-CTX.md

**IMPORTANT: Windows paths** — This system runs Windows 11 (PowerShell 5.1). All paths passed to lean-ctx tools must use Windows conventions (e.g., `C:\Users\...`), NOT Linux-style paths (e.g., `/c/Users/...`). Use backslashes and Windows drive letters for all file/directory arguments.

**CRITICAL: Never use the `bash` tool to invoke `lean-ctx.cmd`.** The `bash` tool executes PowerShell (5.1), which cannot interpret the `/c/Users/...` path format (that's Git Bash/MSYS syntax). Attempting this will always fail with "not recognized as the name of a cmdlet". Always use the `lean-ctx_ctx_shell` MCP tool instead, which handles path resolution correctly.
<!-- /lean-ctx -->

<!-- pushtogit -->
## pushtogit

**Load the `pushtogit` skill before committing and pushing to git.** This skill enforces a pre-push checklist: session compaction, dependency audit/sync, README/TDD.md updates. Reference: @skills/pushtogit/SKILL.md

1. **Session compaction** — `lean-ctx_ctx_session action=save`
2. **Dependency audit/sync** — Check all imports in `server/src/` are declared in root or server `package.json`; run `pnpm test`
3. **README update** — Add new features, verify installation instructions, update data files table
4. **TDD.md update** — Update `tdd/TDD.md` to reflect the latest changes
5. **Commit and push to git** — `git add`, `git commit`, `git push`
<!-- /pushtogit -->
