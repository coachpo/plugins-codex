---
name: enhance-prompt
description: Turn vague product or UI ideas into a structured, accessible, responsive Google Stitch prompt. Use before generating a new screen, editing an existing screen, or requesting variants when user intent, hierarchy, content, states, or constraints need clarification.
---

# Enhance a Stitch UI/UX prompt

> **Adaptation notice:** Rewritten on 2026-07-19 from the Apache-2.0
> `google-labs-code/stitch-skills` version for Codex, external MCP operation,
> and explicit UI/UX quality criteria.
> Updated on 2026-08-03 to use lean, outcome-first GPT-5.6 prompt contracts,
> contextual design decisions, and non-conflicting output rules.

Produce a design brief that Stitch can act on without inventing business
requirements. Match the user's language. Keep facts supplied by the user
separate from reasonable design assumptions. Preserve explicit user values;
when a choice is implicit, give decision criteria instead of applying a fixed
keyword-to-component or keyword-to-style mapping.

## Boundaries

- This skill refines a prompt; it does not create or edit a Stitch project.
- Never request, reveal, copy, or persist API keys, tokens, cookies, or browser
  credentials. Authentication belongs to the separately configured MCP
  connection layer.
- Ask a question only when a missing decision materially changes platform,
  user flow, scope, risk, or brand. Otherwise state the assumption and proceed.
- Do not add dark patterns, fake urgency, inaccessible interactions, or generic
  filler copy that changes the product promise.
- Do not add features, components, animation, or decorative UI merely because
  they are common for the requested screen type or appear in a vocabulary list.
- Use assumptions only for presentation choices and neutral placeholder content.
  Do not use them to add business capabilities, entities, permissions,
  workflows, bulk operations, or destructive actions. Omit unrequested
  capabilities; ask only when one materially determines the requested screen.
- Consult the current official prompting guide when freshness matters:
  https://stitch.withgoogle.com/docs/learn/prompting/

## Input audit

Establish only the context that changes the result:

1. **Outcome and audience** — the primary job and critical path.
2. **Surface** — target viewport and required responsive surfaces.
3. **Structure and content** — hierarchy, navigation, user-provided labels,
   neutral placeholders, density, and tone.
4. **Behavior** — relevant interaction states, responsive rules, and accessibility.
5. **System constraints** — brand, DESIGN.md, existing components, framework,
   localization, compliance, and observable acceptance criteria.

If a local `.stitch/DESIGN.md` or `DESIGN.md` exists, read it. If the target
Stitch project already has a design-system asset, reference that system and do
not duplicate literal colors or fonts in a generation prompt. If neither
exists, include a restrained visual direction and clearly label inferred tokens
as assumptions.

## Choose a prompt mode

### New screen

Describe purpose, complete page hierarchy, content, responsive rules, states,
and acceptance criteria. Prefer concrete component names over aesthetic slang.

### Targeted edit

Name the exact screen region, requested change, behavior, and invariants. End
with “preserve all unrelated content, structure, and design-system rules.”

### Variants

Hold product content and user flow constant. State the dimensions allowed to
vary—layout, density, imagery, hierarchy, or color treatment—and how variants
will be compared.

## Output contract

Always return `### Stitch prompt`. Add `### Assumptions` before it only when
non-trivial assumptions are required. Do not emit empty headings.

### Assumptions

List at most five non-trivial assumptions and distinguish them from user facts.

### Stitch prompt

Use this shape as a compact contract. Omit any internal section that would not
change the generated design:

```markdown
[One sentence: user, task, and desired outcome]

**PLATFORM AND VIEWPORT**
- [surface, first viewport, and responsive targets]

**EXPERIENCE PRINCIPLES**
- [2–4 concrete principles tied to the product]

**PAGE STRUCTURE**
1. **[Region]:** [content, hierarchy, components, and action]
2. **[Region]:** [...]

**INTERACTIONS AND STATES**
- [critical interaction, loading/empty/error/success behavior]

**RESPONSIVE BEHAVIOR**
- [breakpoint behavior without prescribing brittle pixel layouts]

**ACCESSIBILITY**
- [semantic, keyboard, focus, contrast, labels, motion, touch]

**CONTENT**
- [preserve user-provided content; identify neutral placeholders without adding product claims]

**DESIGN SYSTEM**
- [reference the linked system, or include only user-provided/inferred direction]

**ACCEPTANCE CRITERIA**
- [observable outcomes used to review the generated screen]
```

Keep the prompt dense and actionable. Do not turn every request into a landing
page, glassmorphism, gradients, card grids, or excessive rounded containers.
Consult `references/KEYWORDS.md` only when exact vocabulary helps express
already-established intent. Treat its terms as candidates, not defaults, and
do not keyword-stuff the prompt.

## Handoff

When another plugin skill requested the refinement, return the prompt directly
to that skill. When the user only asked for prompt help, stop after presenting
the polished prompt unless they also asked to generate the design.
