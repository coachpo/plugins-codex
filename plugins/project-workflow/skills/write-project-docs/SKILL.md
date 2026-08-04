---
name: write-project-docs
description: Inspect a codebase and create, maintain, consolidate, standardize, or migrate its fixed Simplified-Chinese project documentation set. Support one Chinese or English canonical filename for each product, architecture, development-rules, and source-size authority. Use for new-project documentation, repository documentation audits, canonical filename alignment, architecture and project-specific development-rule consolidation, shared Coding Agent source-size governance, or repair of the managed documentation block in an existing root AGENTS.md. Preserve useful specialized documentation; perform ADR work only when explicitly requested. Modify project documentation and the narrowly managed root AGENTS.md block only.
---

# Write Project Documentation

Create and maintain a concise, fact-based Simplified-Chinese documentation set. Treat the eight canonical documents, their authority boundaries, and their allowed Chinese or English paths as the global convention for every project that uses the skill; do not add project profiles or project-name branches. Treat the selected development-rules path as the engineering-rules entry point and authority for verified project- and technology-specific implementation rules. Treat the selected source-size-rules path as its physically separate, project-agnostic specialized policy. Treat an existing project-root `AGENTS.md` as an instruction and navigation surface, not as a ninth canonical document.

## Non-negotiable Rules

- Modify project documentation and, only when it already exists as a regular non-symlink file, the managed documentation block in the project-root `AGENTS.md`. Do not create `AGENTS.md`. Do not modify nested `AGENTS.md` files or other instruction files by default.
- Read all applicable instruction files before editing. Treat `AGENTS.md` as instructions and navigation rather than a second authority for product facts, architecture, or development rules. Preserve every instruction outside the managed documentation block except unambiguous canonical-path substitutions in the project-root file.
- Obey higher-priority instructions that prohibit or constrain modification of `AGENTS.md`. When the root file cannot be safely updated, leave it unchanged and report the exact stale or missing navigation.
- Establish project facts from the user's instructions or repository evidence. Do not invent commands, features, architecture, status, owners, plans, environments, users, or data.
- Treat absence of evidence as unknown rather than a negative fact. Missing deployment configuration, persistence code, user records, or compatibility policy does not by itself prove that the project is undeployed, has no external users, has no non-discardable data, or has no compatibility commitments.
- Treat the bundled shared assets as user-approved normative policy, not as facts inferred from the repository. Replace only their declared canonical-path template variables; preserve all other bytes.
- Write explanatory prose in Simplified Chinese. Preserve code identifiers, commands, paths, configuration keys, and official product names in their original form.
- Omit unverifiable fields and sections. Do not add placeholders, “待确认”, open questions, speculation, or missing-information reports.
- Do not inspect, infer, request, or report human maintainers, human owners, approvers, commit-message conventions, release dates or conditions, business KPIs/SLOs, or unrecorded external environments and data unless the user explicitly requests the topic and supplies verifiable evidence. A module or data `owner` means the component that owns a responsibility, write path, or lifecycle; establish it only from verified architecture evidence.
- Do not introduce process or administrative-management documentation merely to make the documentation set appear complete. Unless the user explicitly requests it and supplies verifiable evidence, do not add approval, reporting, meeting, scheduling, personnel-governance, release-governance, commit-management, KPI/SLO, or similar content, documents, sections, placeholders, or open questions.
- Do not create `docs/INDEX.md`, `docs/通用工程规范.md`, or additional documents such as Runbooks, `SECURITY.md`, `LICENSE`, `CHANGELOG.md`, glossaries, test plans, or technical-design documents unless explicitly requested. Preserve existing valuable specialized documents.
- Keep one authoritative source for each fact. Link instead of duplicating bodies or generic rules.

## Canonical Documentation Set

Use these paths and authority boundaries:

| Path | Authority |
| --- | --- |
| `README.md` | Project entry point, concise description, verified commands, status summary, and links. |
| `STATUS.md` | Current lifecycle, deployment, user/data, compatibility, and allowed-change facts. |
| `CONTRIBUTING.md` | Project-specific setup and commands plus the rendered shared contribution block. |
| `docs/README.md` | Documentation index and authority map only. |
| `docs/产品说明.md` or `docs/product.md` | Product problem, users, goals, scope, flows, requirements, and acceptance facts. |
| `docs/架构说明.md` or `docs/architecture.md` | Sole architecture authority: current design, module/data owners, boundaries, dependency directions, risks, and concrete architecture or security exceptions. |
| `docs/开发规范.md` or `docs/development-rules.md` | Engineering-rules entry point and authoritative home for verified project- and technology-specific implementation rules; must link to the source-size specialized policy. |
| `docs/源代码规模与职责规则.md` or `docs/source-code-size-and-responsibility-rules.md` | Physically separate, project- and technology-agnostic source-size and responsibility policy subordinate to the development-rules entry point and rendered from the bundled asset. |

Select paths independently for the four bilingual authorities:

- Preserve the one existing Chinese or English path when exactly one variant exists.
- When neither variant exists, create the Chinese path unless the user explicitly requests the English path.
- Never keep both variants for the same authority. Do not use redirects, symlinks, or duplicated bodies to expose both names.
- Keep explanatory prose in Simplified Chinese even when the selected filename is English.

Preserve independently valuable specialized documentation when justified by the project, including API references, data dictionaries, UI/UX guidelines, design systems, test strategies, security designs, research, release documentation, and operations documentation. Do not force empty symmetry between projects and do not create such documents merely to complete a template.

## Workflow

1. Read instruction files in the current directory and applicable parent directories.
2. Inventory existing documentation, managed markers, and every reference to documentation paths in documentation, source code, configuration, CI, tests, and instruction files. Identify generated or externally maintained documentation.
3. Inspect dependency manifests, configuration, primary source code, tests, CI, and available commands to establish current project facts.
4. Classify existing content as canonical-document content, still-valuable specialized documentation, generated or externally maintained documentation, duplicated or outdated content, or unverifiable content.
5. Select one allowed path for each bilingual authority before rewriting. Map every verified, still-valid fact to one authoritative canonical document. Preserve project conventions that do not conflict with the authority boundaries. Consolidate duplicated verified development rules in the selected development-rules path instead of repeating them elsewhere.
6. Create missing canonical files and minimally update existing ones. In the selected development-rules document, keep the required managed source-size-policy link immediately after the title, followed only by verified project- and technology-specific rules. Put concrete architecture or security exceptions only in the selected architecture document and reference them from the development rules without copying their bodies.
7. Render the source-size asset, the managed development-rules link block, and the shared CONTRIBUTING block with the selected canonical paths. Run `scripts/update_development_rules.py` after both the development-rules and source-size documents exist. Do not change any other shared content. The development-rules document remains the engineering-rules entry point; the source-size asset remains the sole file-size and file-responsibility authority.
8. When a regular project-root `AGENTS.md` already exists and applicable instructions allow it, run `scripts/update_agents_navigation.py` to render its managed documentation navigation and content-boundary block and perform only the unambiguous path substitutions defined below. Do not create the file or modify nested instruction files.
9. Run `scripts/validate_project_docs.py` and existing repository documentation checks. Fix all ordinary validation errors. Use `--strict` after explicitly authorized migration cleanup to also fail on legacy-path, nested-instruction, and suspected duplicate-rule warnings.
10. Report files created, updated, and preserved; specialized documents retained; deprecation or cleanup candidates; validation performed; root `AGENTS.md` managed-block changes; and exact non-documentation or nested-instruction locations that still reference old paths.

## Shared Resources

Resolve resource paths relative to this skill directory.

- Use `scripts/canonical_paths.py` to resolve the selected Chinese or English path for each bilingual authority and to render declared `{{...}}` path variables in shared assets. Reject a project that contains both variants for one authority.
- Render `assets/源代码规模与职责规则.md` to the selected source-size-rules path without editing, reformatting, or adding project-specific content. Preserve UTF-8, LF line endings, and one trailing newline.
- Render `assets/开发规范-规模规则区块.md` into the selected development-rules document immediately after its `# 开发规范` title. Replace the complete block bounded by `<!-- write-project-docs:development-source-size:start -->` and `<!-- write-project-docs:development-source-size:end -->` when it already exists; otherwise insert the rendered block once. Run `python3 <skill-dir>/scripts/update_development_rules.py <project-root>` instead of hand-editing this block.
- Render `assets/CONTRIBUTING-通用区块.md` into `CONTRIBUTING.md`. Replace the complete block bounded by `<!-- write-project-docs:shared-contributing:start -->` and `<!-- write-project-docs:shared-contributing:end -->` when it already exists; otherwise insert the rendered asset once in an appropriate location.
- When the project-root `AGENTS.md` exists and is safely editable, render `assets/AGENTS-文档导航区块.md` with the selected paths. This managed block contains both canonical documentation navigation and the boundary against introducing unrequested process or administrative-management content. Replace the complete block bounded by `<!-- write-project-docs:document-navigation:start -->` and `<!-- write-project-docs:document-navigation:end -->` when it already exists; otherwise insert the rendered asset once in an appropriate documentation-navigation location.
- After confirming that applicable instructions permit the narrow root-file edit, run `python3 <skill-dir>/scripts/update_agents_navigation.py <project-root>`. The script skips an absent file, rejects symlinks and malformed managed markers, preserves unrelated text, and never creates `AGENTS.md`.
- Put project-specific source-size, architecture, and security exceptions in the selected architecture document. Each exception must include its exact scope, rationale, compensating controls, verification, and expiry or objectively testable exit condition. Do not customize a shared asset or create an ADR unless explicitly requested.
- Do not repeat the `240`/`300`/`500`/`50` thresholds in `CONTRIBUTING.md` or the selected development-rules document; link to the selected source-size document.
- Run `python3 <skill-dir>/scripts/validate_project_docs.py <project-root>`. Ordinary validation fails on missing canonical files, an absent or drifted development-rules source-size link, invalid shared assets, missing/drifted/duplicated managed blocks, broken local links, and other integrity violations. It reports legacy canonical paths, nested `AGENTS.md` references, and suspected repeated size rules as non-failing migration warnings.
- Use `--strict` after explicitly authorized cleanup. Strict mode performs the same integrity checks and additionally turns every migration warning into failure; it does not use weaker byte or marker checks than ordinary mode.

## Existing Root AGENTS.md Managed Block

Apply this section only to `AGENTS.md` located directly at the project root.

- If the root `AGENTS.md` does not exist, do not create it and do not report its absence as a documentation gap.
- If it is a symlink, generated file, externally maintained file, or protected by applicable instructions, leave it unchanged and report why the managed block was not updated.
- Use `scripts/update_agents_navigation.py` to replace an existing managed block or append the asset once when the block is absent. Do not hand-rewrite surrounding instructions.
- Outside the managed block, replace only `docs/INDEX.md` and an unselected bilingual counterpart with the project's selected canonical path. Preserve every selected path and all surrounding wording, conditions, priorities, and scope.
- Do not copy product, status, architecture, contribution, or development-rule bodies into `AGENTS.md`. The managed block points to authoritative documents and states the documentation-content boundary; it does not become a competing authority for project facts.
- Inspect nested `AGENTS.md` files for stale paths and broken links, but report them without modification unless the user separately requests nested-instruction work.

## Consolidation and Migration

Use these standard mappings:

- `docs/INDEX.md` → `docs/README.md`
- An unselected Chinese or English canonical counterpart → the selected path for the same authority.
- Verified project- or technology-specific implementations, limits, commands, and development rules → the selected development-rules path.
- Project-agnostic size and responsibility rules embedded elsewhere → the selected source-size-rules path.
- Project-specific rules found in an old size guide → the selected development-rules path or the `结构性例外` section of the selected architecture path.

Apply these migration rules:

- Inventory references before changing canonical paths.
- Absorb all unique, verified, still-valid information before identifying an older document as obsolete.
- Leave generated or externally maintained documentation unchanged and record its update mechanism when verifiable.
- Leave unverifiable documents unchanged. Do not propagate their uncertain content; discuss it only when the user explicitly asks for a documentation audit.
- Fix documentation links affected by current edits. In an existing editable project-root `AGENTS.md`, update the managed documentation block and exact standard-mapping references. Report exact source, configuration, CI, test, other instruction-file, and nested `AGENTS.md` references to old paths without editing those files by default.
- Do not delete, move, archive, or reorganize existing documents without explicit cleanup authorization. List fully absorbed old paths and the evidence for deprecation.
- Do not use redirects, symlinks, duplicated shared clauses, parallel managed blocks, or simultaneous Chinese and English variants as a long-term migration state.

## File Requirements

### `README.md`

Include the project name and one-sentence description, current-status summary with a prominent `STATUS.md` link, verified installation/start/test/check/build commands, and links to the documentation index, product, architecture, and contribution documents. Do not copy other document bodies.

### `STATUS.md`

Record only verifiable lifecycle stage, deployment state, external-user state, non-discardable-data state, stability and compatibility commitments, allowed and prohibited changes, last review date when verifiable, and conditions requiring another status review.

Do not derive “undeployed”, “no external users”, or “no non-discardable data” solely from missing repository artifacts. Omit those fields unless direct project evidence or the user's instructions establish them.

When the project is demonstrably local-only, undeployed, has no external users, and has no non-discardable data, state that backward compatibility is not guaranteed for APIs, configuration, or database schemas; breaking refactors and local-data resets are allowed; compatibility layers for old versions must not be created; and applicable quality checks must still pass.

### `CONTRIBUTING.md`

Include verified development-environment and dependency setup, local start/test/check/build commands, project-specific code style and review rules, and the rendered shared block from `assets/CONTRIBUTING-通用区块.md`. Link to architecture, development rules, and source-size rules instead of duplicating them.

### `docs/README.md`

Use this file as a routing page. List the selected path for each canonical document with its authority, including that the selected development-rules document is the engineering-rules entry point and the selected source-size document is its separate specialized policy, then list verified specialized and generated/external documents with concise purposes. Do not turn the index into another source of product, status, architecture, or development facts.

### `docs/产品说明.md` or `docs/product.md`

Include the problem, target users, goals, explicit non-goals, functional scope, core user flows and requirements, acceptance criteria, and known constraints or assumptions when verifiable.

### `docs/架构说明.md` or `docs/architecture.md`

Describe the current design rather than an idealized blueprint: system boundaries and external dependencies, key modules and their responsibility/data/lifecycle owners, allowed dependency directions, data models and flows, module interfaces, technology stack, security boundaries, local execution model, quality attributes, risks and limitations, relevant existing ADR links, and verified source-size, architecture, or security exceptions. For every concrete exception, record its exact scope, rationale, compensating controls, verification, and expiry or objectively testable exit condition.

Do not place generic coding policy here. Use this document to prevent implementations from crossing established module boundaries or adding responsibilities to the wrong component.

### `docs/开发规范.md` or `docs/development-rules.md`

Start with exactly one `# 开发规范` title, followed immediately by the rendered managed block from `assets/开发规范-规模规则区块.md`. After that block, include only verified project- and technology-specific rules. A title plus the managed block is valid when no project-specific rules are verifiable; a title-only file is invalid.

Include rules such as source layout and placement, naming and language/framework conventions, concrete limits, error mappings, security mechanisms, data and concurrency implementations, testing strategy, named quality gates, and project-specific review requirements. Refer to the selected architecture document for owners, boundaries, dependency directions, and concrete exceptions. Use the managed block as the normative link to the selected source-size document.

Do not repeat architecture descriptions, generic implementation-choice priorities, the shared Definition of Done, concrete exception bodies, or shared size thresholds.

### `docs/源代码规模与职责规则.md` or `docs/source-code-size-and-responsibility-rules.md`

Use the rendered bundled asset as the entire document. Replace only declared canonical-path variables. Do not add project names, technologies, exceptions, commands, or local thresholds.

## ADR Exception

Create, rewrite, move, or organize ADRs only when the user explicitly requests ADR work. Preserve existing ADRs and link relevant records from the selected architecture document. Each new ADR must record status, date, context, alternatives, decision, and consequences. Do not report unrecorded decisions unless the user requests an ADR audit.
