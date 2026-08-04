---
name: stitch-loop
description: Coordinate a bounded, human-reviewable multi-page Google Stitch design loop with shared requirements, design-system consistency, artifact retrieval, visual QA, and progress state. Use for flows or sites that require several related screens rather than one autonomous endless iteration.
---

# Run a bounded multi-page Stitch loop

> **Adaptation notice:** Rewritten on 2026-07-19 from the Apache-2.0
> `google-labs-code/stitch-skills` version to replace an open-ended autonomous
> baton with scoped, recoverable, human-reviewable Codex iterations.
> Updated on 2026-08-03 for GPT-5.6 with sparse progress updates and explicit
> sequencing for dependent design work.

Turn a product brief into a coherent set of screens while keeping decisions,
IDs, artifacts, and quality evidence recoverable. “Loop” means deliberate
iteration toward an agreed completion bar, not inventing pages forever.

## Scope and authority

A request to design a named flow/site authorizes generation and targeted edits
for the screens in that scope. Before creating anything, state the proposed
screen list and critical user journey. Ask only if a missing choice materially
changes scope. Expanding to a new journey, audience, or platform needs user
direction.

Use a separately configured official Stitch MCP. Verify it with
`mcp__stitch__list_projects`; if the tools are unavailable or authentication
fails, ask the user to configure or reauthenticate that external connection and
start a new task. Never ask them to paste credentials into chat, and never fall
back to cookies, website automation, or private APIs.

## Durable state

Use this structure when local artifacts are part of the request:

```text
.stitch/
  SITE.md             # outcome, audience, journey, sitemap, acceptance bar
  DESIGN.md           # shared semantic system
  metadata.json       # non-secret project and screen resource IDs
  next-prompt.md      # next approved screen/refinement only
  designs/            # retrieved HTML/screenshots/Figma exports
```

Do not overwrite an existing `.stitch/` plan without reconciling completed
screens and user changes. Metadata must never contain tokens or API keys.

## Planning gate

Before generation, define in `SITE.md` or the response:

- user-visible outcome and primary journey;
- ordered screen inventory and navigation relationships;
- shared content/brand constraints;
- target surfaces and responsive strategy;
- per-screen acceptance criteria and global consistency criteria;
- what “done” means for design, retrieval, and implementation handoff.

Obtain or extract `.stitch/DESIGN.md` with the plugin's `design-md` workflow. If
there is not enough existing evidence, create a provisional design direction in
the first enhanced prompt and stabilize it after the first accepted screen.

## Per-screen iteration

Before tool calls, give one brief update with the proposed screen sequence and
immediate next step. Update only when a major phase begins, evidence changes the
plan, or a material wait occurs. Keep screens in journey order because each
accepted result may refine the shared system. Parallelize only independent
read-only artifact retrieval after IDs are resolved; keep writes and dependent
decisions sequential.

For each approved screen, in journey order:

1. **Read state:** skip completed screens unless refresh was requested.
2. **Enhance prompt:** use `enhance-prompt`, shared system rules, and the exact
   role of this screen in the journey.
3. **Generate:** use `generate-design` with the existing project and correct
   device type. Do not create one project per page.
4. **Retrieve:** call `mcp__stitch__get_screen`; save screenshot and HTML under stable slugs.
5. **Review:** inspect the screenshot against task, hierarchy, content, states,
   responsive behavior, accessibility, and cross-screen consistency.
6. **Refine:** use a targeted `mcp__stitch__edit_screens` prompt for high-impact gaps. Check
   whether a timed-out write already completed before retrying.
7. **Record:** update metadata, sitemap, decisions, and artifact paths.

Default to at most three refinement rounds per screen. If the same blocking
issue persists, report the evidence instead of looping indefinitely.

## Cross-screen quality gate

Before declaring the flow complete, verify:

- navigation and back/escape paths form a complete journey;
- labels, components, tokens, and interaction patterns stay consistent;
- loading, empty, error, permission, success, and destructive-confirmation
  states exist where the product needs them;
- responsive adaptations preserve priority and task completion;
- keyboard focus, semantics, contrast, touch targets, and reduced motion are
  addressed;
- every final screen has a retrievable screenshot and HTML when Stitch exposes
  them, and no stale artifact is reported as current.

Run relevant local, non-destructive checks without asking when implementation is
in scope. Starting a deployment, publishing, or adding screens outside the plan
still requires separate authority.

## Baton behavior

`next-prompt.md` may hold the next unfinished approved item. Update it only when
work remains. When the agreed screen list is complete, mark the loop complete
instead of inventing another page.

## Final handoff

Return the Stitch project ID, screen-to-route map, completion status, local and
remote artifacts, review/iteration summary, and remaining gaps. Distinguish
designs that were generated from designs that were merely planned.
