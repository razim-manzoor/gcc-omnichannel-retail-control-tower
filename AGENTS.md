# Agent Memory & Second Brain Protocol

This project uses an Obsidian-backed external memory layer located at `.brain/` (linked to `R:\Second Brain\projects\omnichannel-retail-control-tower\`).
All agents must adhere to the master operating conventions in `R:\Second Brain\agent-rules.md`.

### Before Starting Any Task
1. Read `.brain/state.md` to identify the active objective, current driver, and blockers (< 500 tokens).
2. Respect the 2-Tier Context Law: DO NOT scan the entire `.brain/` folder. Only read files linked under `Active References`.
3. Check code state with `git status`.

### When Pausing, Hitting Token/Rate Limits, or Finishing
1. Update `.brain/state.md` with checked-off items and new immediate actions.
2. If pausing or handing off to another agent, generate a handoff note in `.brain/handoffs/YYYY-MM-DD_<task_slug>.md`.
3. Set `current_driver: "None"` in `state.md`.

### Architecture & Client Handover Rules
- **Architectural Decisions:** Decisions in `.brain/adr/` are permanent. Do not change architectural patterns without explicit user consent.
- **Client Handover Sanitization:** Before transferring this repository to a client or pushing to client remotes:
  1. Unlink `.brain/` junction.
  2. Remove `AGENTS.md` and `.agents/` unless the client explicitly requested AI agent enablement.
  3. Ensure all scratch scripts (`scratch_*.py`), credential PDFs, and test artifacts are deleted or gitignored.



# System Rule: Voidtools Everything Search Engine (Mandatory)

On this Windows workstation, the **Voidtools Everything MFT Search Engine** (`es.exe`) is permanently installed, active in the background, and bridged into PATH.

### Mandatory Directive
- **STRICTLY PROHIBITED**: NEVER execute recursive directory crawls such as `Get-ChildItem -Recurse`, `Get-ChildItem -Path ... -Recurse`, `dir /s`, or `findstr /s` across deep directory structures (e.g. `node_modules`, `AppData`, Python venvs, drive roots). These commands cause 30–90 second timeouts, lock the console, and waste context window tokens.
- **MANDATORY**: ALWAYS use `es <pattern>` (or `es-find <pattern>`) for all file, directory, and extension discovery. `es` queries the NTFS Master File Table (MFT) and returns results in sub-15 milliseconds.

### Quick Reference & CLI Syntax
- Find files by name/wildcard: `es myfile.ts` or `es -n 10 *.config.json`
- Scope search to a folder: `es path:"C:\myproject" *.tsx`
- Search by extension: `es ext:parquet` or `es ext:ps1`
- Folders only: `es /ad <folder_name>`
- Files only: `es /a-d <file_name>`
- Case-sensitive search: `es -i <exact_case>`
- Regex search: `es -r "^test_.*\.py$"`
- Export to text file: `es *.log -export-txt "$env:TEMP\results.txt"`
