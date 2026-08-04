---
name: init-deep
description: Initialize or refresh a hierarchical AGENTS.md knowledge base for a repository. Use when Codex needs to map a codebase, preserve and improve existing AGENTS.md guidance, decide which complex or distinct subdirectories need scoped instructions, or regenerate the hierarchy with /init-deep, --create-new, or --max-depth.
---

# init-deep

Create a durable, evidence-backed `AGENTS.md` hierarchy: one root file plus only the child files whose subtrees need materially different guidance.

## Inputs and modes

Accept:

```text
/init-deep
/init-deep --create-new
/init-deep --max-depth=N
```

- Default to **update mode**: preserve deliberate existing rules, correct stale claims, and create missing files only where warranted.
- Treat `--create-new` as authorization to replace repository `AGENTS.md` contents after reading them. Do not delete files before replacements are ready.
- Default `--max-depth` to `3`. Apply it to candidate child-file locations, not to evidence gathering when deeper inspection is needed.
- Keep all writes inside the requested repository. Respect narrower user scope and higher-priority instructions.

## Success criteria

Finish only when:

- the repository's purpose, entry points, build and test commands, major boundaries, and project-specific constraints have evidence;
- every existing `AGENTS.md` in scope has been read;
- the root file is accurate and useful without generic engineering advice;
- each child file adds subtree-specific information and does not repeat its parent;
- commands and paths included in generated files have been verified where feasible;
- all written files have been reread and checked for contradictions, redundancy, and stale generated metadata.

## Workflow

Track four phases with the available planning tool when the task is nontrivial: discovery, placement, generation, validation. Keep only one phase in progress. Do not depend on a particular planning-tool name.

### 1. Discover the repository

Start with a fast inventory, then deepen only where it changes the output.

#### Read durable guidance first

1. Locate every `AGENTS.md` and `CLAUDE.md` in scope, excluding generated or dependency directories.
2. Read every existing `AGENTS.md` before editing any of them, including in `--create-new` mode.
3. Record each file's scope, non-obvious rules, commands, and explicit prohibitions.
4. Preserve intentional instructions unless the user requests a change or repository evidence shows they are stale.

#### Build the structural map

Measure enough to identify boundaries and hotspots:

- directories and depth;
- source-file counts and code concentration by directory;
- languages and package/workspace boundaries;
- entry points, manifests, build/CI configuration, tests, and generated/vendor directories;
- unusually large or central modules.

Prefer repository-aware tools over broad text search:

1. Use codebase-memory graph tools first for code discovery. If the repository is not indexed, run the available repository indexer before graph queries.
2. Use `get_architecture` for the overview, `search_graph` for symbols and entry points, `trace_path` for callers/callees, and change/blast-radius tools when available.
3. Use LSP symbols and references as complementary evidence when available.
4. Use fast filesystem search for configuration, literal rules, documentation, and gaps the graph cannot answer.
5. If neither graph nor LSP is available, inspect manifests, entry points, and representative source files; mark symbol centrality as unmeasured rather than guessing.

Exclude `.git`, dependencies, virtual environments, caches, coverage, build outputs, and generated artifacts from scale measurements unless the repository treats them as source.

#### Use parallel exploration selectively

Parallelize independent discovery when subagents are available and the repository is large enough to benefit. Keep dependent work sequential and synthesize findings before writing.

Choose workstreams from actual uncertainty, for example:

- architecture and entry points;
- build, CI, and repository conventions;
- tests and validation paths;
- explicit prohibitions and deprecated patterns;
- monorepo packages or deep, distinct domains;
- complexity and cross-cutting hotspots.

Do not spawn a fixed fleet. Use no subagents for small, obvious repositories; use a few focused workstreams for medium repositories; add package- or language-specific workstreams only for genuinely independent large-repository areas. Never exceed available concurrency, and do not delegate overlapping scans.

Give each explorer a bounded prompt:

```text
Goal: identify [specific evidence] for AGENTS.md.
Scope: [directories or package].
Use: code graph/LSP first for code structure; filesystem search for configs and literals.
Return: verified paths, symbols or commands; project-specific rules; uncertainties.
Do not write files. Omit generic advice.
```

### 2. Decide file placement

Always create or update the root `AGENTS.md`. Add a child only when its subtree has a distinct domain, commands, architecture, risk boundary, or conventions that would otherwise make the root noisy.

Use this additive evidence score as a decision aid, not a quota:

| Evidence | Points |
| --- | ---: |
| More than 20 relevant files | 3 |
| More than 5 relevant subdirectories | 2 |
| More than 70% source-code files | 2 |
| Own manifest or tool configuration | 1 |
| Clear module/package boundary | 2 |
| More than 30 meaningful symbols | 2 |
| More than 10 public exports | 2 |
| More than 20 inbound references or equivalent centrality | 3 |

Apply these rules:

- Score `16+`: create a child unless the parent already covers it cleanly.
- Score `8–15`: create only for a genuinely distinct domain or local workflow.
- Score below `8`: keep guidance in the nearest parent.
- Do not create child files merely to mirror the directory tree.
- Prefer the shallowest file that scopes an instruction correctly.
- Keep candidates within `--max-depth`.

Record the decision before writing:

```text
AGENTS_LOCATIONS =
- . — root
- packages/api — score 14; distinct service commands and API constraints

SKIPPED =
- src/utils — score 7; parent guidance is sufficient
```

### 3. Generate or update files

Write the root first so child files can be deduplicated against it. Then write independent child files in parallel when safe.

Edit existing files in place. Create only missing files. In `--create-new` mode, replace each file only after its new content is ready; do not perform a broad pre-emptive deletion.

#### Root content

Include only sections supported by repository evidence:

````markdown
# PROJECT KNOWLEDGE BASE

## OVERVIEW
<!-- Purpose and core stack in 1–3 sentences. -->

## STRUCTURE
<!-- Only non-obvious directories and boundaries. -->

## WHERE TO LOOK
| Task | Location | Notes |
| --- | --- | --- |

## CODE MAP
| Symbol or area | Type | Location | Role |
| --- | --- | --- | --- |

## CONVENTIONS
<!-- Repository-specific deviations and durable rules. -->

## ANTI-PATTERNS
<!-- Explicitly forbidden or demonstrably harmful patterns in this repo. -->

## COMMANDS
```bash
# Verified development, test, lint, and build commands only.
```

## NOTES
<!-- Non-obvious operational or architectural gotchas. -->
````

Omit empty sections. Do not add timestamps, branches, or commit hashes that become stale immediately. Prefer roughly 40–120 lines, but never pad or remove necessary evidence to hit a line count.

#### Child content

Keep each child scoped to its directory. Prefer roughly 20–60 lines and include only useful local sections:

- one-line overview;
- local structure when navigation is non-obvious;
- task-to-location table;
- conventions that differ from or refine the parent;
- local anti-patterns, commands, or validation rules.

Do not repeat root commands, repository-wide conventions, or obvious filenames. Assume the parent applies.

### 4. Validate the hierarchy

Reread every written file and verify:

1. **Accuracy:** paths, symbols, and commands exist; factual claims are grounded.
2. **Scope:** each instruction lives at the shallowest correct level.
3. **Deduplication:** child content does not restate parent content.
4. **Actionability:** guidance answers where to look, what differs, what to run, or what to avoid.
5. **Durability:** remove generic advice, transient status, inventories likely to churn, and speculative claims.
6. **Consistency:** resolve contradictions across the hierarchy and with higher-priority instructions.
7. **Size:** trim repetition and low-value detail; do not enforce line targets mechanically.

Run the cheapest relevant verification for commands included in the files, such as help/list modes, targeted tests, or configuration parsing. Do not run destructive, external, or costly commands merely to verify documentation. If a claim cannot be verified, omit it or label the uncertainty in the final report rather than encoding it as fact.

## Final report

Lead with completion and evidence:

```text
=== init-deep complete ===
Mode: update | create-new

Created:
- ./AGENTS.md
- packages/api/AGENTS.md

Updated:
- apps/web/AGENTS.md

Analyzed: N relevant files across N directories
Validation: [checks run and results]
Skipped candidates: [path and brief reason]
Unverified: [only material gaps, or none]
```

Report created and updated files separately. Include a compact hierarchy when more than one file exists.

## Guardrails

- Never invent architecture, conventions, commands, or prohibitions from framework norms alone.
- Never replace repository-specific instructions with generic best practices.
- Never create an `AGENTS.md` for every directory.
- Never treat parallelism or agent count as a success criterion.
- Never let a numeric score override evidence about scope and distinctness.
- Never claim validation that was not run.
