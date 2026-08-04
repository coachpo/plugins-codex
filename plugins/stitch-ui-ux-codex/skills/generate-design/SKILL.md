---
name: generate-design
description: Create, edit, review, and retrieve Google Stitch UI screens through an available official Remote MCP connection. Use for new text-to-UI designs, targeted screen edits, design variants, screenshot/HTML retrieval, and iterative UI/UX refinement.
---

# Generate and refine a Stitch design

> **Adaptation notice:** Rewritten on 2026-07-19 from the Apache-2.0
> `google-labs-code/stitch-skills` version for Codex tool provenance,
> external MCP discovery, bounded writes, visual review,
> and artifact retrieval.
> Updated on 2026-08-03 for GPT-5.6 with leaner instructions, explicit tool
> routing, bounded fallbacks, and intentional image-detail selection.

Use a separately configured official Stitch Remote MCP. When the connection is
named `stitch`, its tools normally appear as `mcp__stitch__<tool>` in Codex.
Use callable tools from that connection; do not reverse engineer the Stitch
website or private APIs.

## Authentication preflight

Confirm that the Stitch tools are available, then start with the read-only
`mcp__stitch__list_projects` tool.

- If the tools are unavailable, tell the user to configure the official Stitch
  MCP outside this plugin and start a new task, then retry once.
- If the call reports an authentication error, ask the user to repair or
  reauthenticate the external MCP connection using the official setup flow.
- Never ask the user to paste an API key into chat, a file, or a command that
  could be logged. Do not switch authentication methods automatically.
- Never reuse browser cookies or inspect browser storage.

## Authority and side effects

`mcp__stitch__create_project`, `mcp__stitch__generate_screen_from_text`,
`mcp__stitch__edit_screens`, and `mcp__stitch__generate_variants` write to the
user's Stitch account. A request to create,
edit, or iterate a design authorizes the corresponding scoped operation. Do not
create unrelated projects, screens, or variants. Read-only listing, retrieval,
and artifact inspection do not need a second confirmation.

Generation calls can take minutes and may finish after a connection error. Do
not immediately retry. Re-list screens or retrieve the target project first to
check whether the operation succeeded.

## Workflow

Before the first tool call, give one brief update stating the immediate goal.
Update again only at a major phase change, when evidence changes the plan, or
during a material wait; do not narrate routine calls.

Resolve required discovery, retrieval, and validation before a dependent write.
Run independent read-only calls concurrently after resource IDs are resolved;
keep calls sequential when one result determines the next action, and keep
side-effecting calls sequential. If a read is empty, partial, or suspiciously
narrow, try at most two meaningful fallbacks such as refreshing the listing or
retrieving the exact resource ID, then report the missing evidence.

### 1. Normalize the brief

Apply the plugin's `enhance-prompt` workflow. Preserve the user's product facts,
content, platform, and constraints. Define observable acceptance criteria.

### 2. Resolve project and design system

1. Use `mcp__stitch__list_projects` and match by explicit ID/title before creating anything.
2. If the user requested a new design and no suitable project exists, create
   one with a clear title derived from the request.
3. Use `mcp__stitch__list_design_systems` for the selected project.
4. When a system exists, pass the applicable design-system resource according
   to the live tool schema and keep literal theme tokens out of the generation
   prompt. When none exists, use the brief's restrained visual direction.

If multiple plausible existing projects could be modified, stop and ask which
one. Never guess an edit target.

### 3. Choose the operation

#### New screen

Call `mcp__stitch__generate_screen_from_text` with the selected project, enhanced prompt,
device type, and design-system reference supported by the current schema.

#### Targeted edit

Use `mcp__stitch__list_screens`/`mcp__stitch__get_screen` to resolve exact
screen IDs. Call `mcp__stitch__edit_screens`
with a focused prompt containing location, change, intended behavior, and
invariants. Prefer one coherent edit over a long unrelated bundle.

#### Variants

Call `mcp__stitch__generate_variants` only for an existing screen. Keep user flow and core
content stable, request 2–4 variants by default, and state the comparison axis.
Use broader creative range only when the user asks to reimagine the design.

Follow each tool's live JSON schema rather than copying stale example argument
names. Surface useful text and suggestions returned in `outputComponents`.

### 4. Retrieve the authoritative result

After any successful write:

1. Resolve every generated screen ID from the result or `mcp__stitch__list_screens`.
2. Call `mcp__stitch__get_screen` for each selected final screen, concurrently
   when the reads are independent.
3. Capture the resource name, title, device type, dimensions, prompt, and these
   files when present:
   - `screenshot.downloadUrl`
   - `htmlCode.downloadUrl`
   - `figmaExport.downloadUrl`
4. Return the download links promptly because signed URLs can expire.
5. When the user asked to “取回”, export, implement, or save the result, download
   exact URLs returned by `mcp__stitch__get_screen` to
   `.stitch/designs/<screen-slug>.*`.
   Do not attach credentials or download arbitrary user-supplied URLs.

Use a predictable local layout:

```text
.stitch/
  metadata.json
  designs/
    <screen>.png
    <screen>.html
    <screen>.fig
```

Persist only IDs and non-secret metadata. Never persist API credentials.

### 5. UI/UX quality gate

Inspect the downloaded screenshot with the available image viewer. Choose image
detail intentionally: use original detail for large, dense, coordinate-sensitive,
OCR, or localization checks when the precision justifies extra cost and latency;
use normal detail for ordinary hierarchy, color, and layout review. Evaluate:

- primary task completion and information hierarchy;
- real content fit, density, readability, and visual consistency;
- responsive behavior at the requested surfaces;
- keyboard/focus semantics, contrast, labels, touch targets, and motion;
- loading, empty, error, validation, success, and disabled states that matter;
- implementation feasibility and consistency with the design system.

Tie findings to the acceptance criteria. If a high-impact issue is fixable
within the request, make a targeted edit, retrieve the new screen, and review
again. Default to at most three deliberate refinement rounds; stop earlier when
the bar is met. Do not regenerate blindly for cosmetic variation.

## Final handoff

Report:

- project and final screen resource IDs;
- what was generated or changed;
- preview or local screenshot path;
- HTML, screenshot, and Figma artifacts actually available;
- quality checks performed and any remaining risks;
- suggestions from Stitch that materially affect the design.

Never claim that a file was exported or a screen was reviewed unless it was
actually retrieved and inspected.

For contextual design decisions, consult `references/design-mappings.md`. For
vocabulary only, consult `../enhance-prompt/references/KEYWORDS.md`. Treat both
as optional references rather than keyword maps; the live MCP schema remains
authoritative for tool arguments and outputs.
