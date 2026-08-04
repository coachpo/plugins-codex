---
name: design-md
description: Analyze representative Google Stitch screens and synthesize their visual language, tokens, components, responsive behavior, accessibility rules, and design rationale into a reusable DESIGN.md. Use when extracting or refreshing a design system from an existing Stitch project.
---

# Extract a semantic DESIGN.md from Stitch

> **Adaptation notice:** Rewritten on 2026-07-19 from the Apache-2.0
> `google-labs-code/stitch-skills` version for Codex, multi-screen evidence,
> accessibility, responsive rules, and explicit design rationale.
> Updated on 2026-08-03 for GPT-5.6 with leaner evidence routing, bounded
> fallbacks, and intentional image-detail selection.

Build a design system from evidence, not from a single screenshot or generic
style preferences. Use a separately configured official Stitch MCP; when the
connection is named `stitch`, its tools are normally exposed as
`mcp__stitch__<tool>` in Codex.

## Preconditions and security

- Verify the external connection with the read-only
  `mcp__stitch__list_projects` call. If the tools are unavailable or
  authentication fails, tell the user to configure or reauthenticate the
  official Stitch MCP outside this plugin and start a new task. Never ask them
  to paste credentials into chat or source files.
- Require an existing project with at least one completed design screen.
- Do not create or modify a Stitch design system unless the user separately
  requests that external write. This skill extracts and documents.
- Download only URLs returned by `mcp__stitch__get_screen`, without adding credentials.

## Evidence collection

Resolve the project and screen IDs before retrieval. Run independent
`mcp__stitch__get_screen` reads concurrently when safe, then synthesize the
evidence before choosing tokens or rules. If a listing or screen result is
empty, partial, or suspiciously narrow, try at most two meaningful fallbacks
such as refreshing the listing or retrieving the exact ID; do not turn missing
evidence into a factual absence.

1. Resolve the project by explicit resource ID or unambiguous title.
2. Call `mcp__stitch__list_screens` and choose a representative set:
   - primary/high-traffic screen;
   - a content-dense or form screen;
   - a screen containing reusable navigation/components;
   - mobile/desktop counterparts when available.
3. Call `mcp__stitch__list_design_systems` and record any existing system as one source, not
   unquestioned truth.
4. Call `mcp__stitch__get_screen` for every selected screen and retrieve its
   screenshot and HTML when present.
5. Inspect screenshots visually and parse HTML/CSS for repeated values. Use
   original image detail only for dense, coordinate-sensitive, OCR, localization,
   or token-level inspection where the extra precision is material. Separate
   true recurring tokens from one-off page details.

If screens materially disagree, document the inconsistency and propose a
canonical rule; do not silently average conflicting designs.

## Synthesis method

Infer the smallest coherent system that explains the evidence:

- **Principles and rationale:** product qualities, hierarchy, density, trust,
  and why the system makes those choices.
- **Color roles:** semantic names, exact values, light/dark behavior, contrast,
  and allowed usage—not a list of every encountered color.
- **Typography:** families, scale, weights, line heights, readable line length,
  and hierarchy.
- **Layout:** grid, containers, breakpoints, spacing scale, alignment, and
  density rules.
- **Shape/elevation/motion:** radii, borders, shadows, durations, easing, and
  reduced-motion alternatives.
- **Components:** anatomy, variants, sizes, states, and content rules for the
  recurring components actually found.
- **Responsive behavior:** what reflows, hides, collapses, scrolls, or becomes
  another control.
- **Accessibility:** contrast, focus, keyboard order, labels, errors, targets,
  semantics, and non-color cues.
- **Do / don't rules:** constraints that keep future Stitch generations aligned.

## Required DESIGN.md structure

```markdown
# [Product] Design System

## 1. Product context and design principles
## 2. Visual direction and rationale
## 3. Color tokens and usage
## 4. Typography
## 5. Spacing, grid, and responsive layout
## 6. Shape, elevation, and motion
## 7. Component patterns and states
## 8. Content and iconography
## 9. Accessibility requirements
## 10. Stitch generation rules
## 11. Source screens and known inconsistencies
```

Use natural-language visual descriptions followed by exact values where useful.
Include a compact “Stitch generation rules” block that another skill can reuse;
do not paste the entire document into every prompt.

## Output and validation

- Default local path: `.stitch/DESIGN.md` when the user requested an artifact or
  the surrounding implementation needs one; otherwise present the document.
- Record project/screen resource IDs and extraction date, never credentials.
- Re-read the completed file and verify that every token or rule is supported by
  evidence or explicitly labeled as a recommendation.
- Report which screens and files were inspected, unresolved inconsistencies,
  and whether mobile, dark mode, or interaction states were absent from evidence.
