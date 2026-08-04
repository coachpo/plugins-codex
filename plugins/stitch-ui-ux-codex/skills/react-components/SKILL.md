---
name: react-components
description: Retrieve selected Google Stitch screens and convert or synchronize them into maintainable React components with design-token reuse, real routing, responsive and accessible states, visual fidelity checks, and native project validation. Use for Stitch-to-React implementation or handoff.
---

# Convert Stitch screens to React

> **Adaptation notice:** Rewritten on 2026-07-19 from the Apache-2.0
> `google-labs-code/stitch-skills` version to preserve existing React
> architectures, use project-native validation, and add accessibility gates.
> Updated on 2026-08-03 for GPT-5.6 with leaner tool routing, bounded retrieval
> fallbacks, and intentional visual-detail selection.

Implement the selected design in the user's existing application. Preserve the
repository's architecture and behavior unless the request explicitly changes
them. Do not replace a working app with a fresh Vite scaffold merely because the
source design is HTML.

## Authentication and selection gate

1. Verify a separately configured official Stitch MCP with read-only
   `mcp__stitch__list_projects`.
2. Resolve the exact project and selected screens with
   `mcp__stitch__list_screens`.
3. If “all screens” is ambiguous or includes unrelated experiments, present the
   candidate screen map and narrow it before implementation.
4. If the tools are unavailable or authentication fails, tell the user to
   configure or reauthenticate the external MCP connection and start a new
   task. Never accept credentials in chat or source files.

## Retrieve authoritative design artifacts

Resolve all selected screen IDs first. Retrieve independent screens
concurrently when safe, then synthesize the artifacts before editing code. Keep
dependent calls and writes sequential. If a listing, screen, or artifact result
is empty, partial, or suspiciously narrow, try at most two meaningful fallbacks
such as refreshing the listing or retrieving the exact ID, then report the
missing evidence.

For each selected screen:

1. Call `mcp__stitch__get_screen` using the current live schema.
2. Record resource ID, title, device type, dimensions, and design-system link.
3. Download `htmlCode.downloadUrl` and `screenshot.downloadUrl` when present to
   `.stitch/designs/<route-slug>.*`.
4. Use `scripts/fetch-stitch.sh` only with an exact URL returned by the MCP. Do
   not add auth headers or fetch arbitrary input URLs.
5. Inspect every downloaded screenshot. Use original image detail for large,
   dense, coordinate-sensitive, OCR, or localization checks only when the extra
   precision is material; use normal detail for ordinary fidelity review. HTML
   is implementation evidence, not a substitute for visual review.

If a local artifact already exists, compare its recorded screen ID/update time
with Stitch. Refresh stale artifacts automatically when synchronization is part
of the request; otherwise explain the mismatch before overwriting user files.

## Understand the target codebase

Before editing, inspect the existing framework, routing, styling, components,
tokens, state/data conventions, dependencies, tests, and relevant AGENTS.md.

- Reuse the existing stack and installed dependencies.
- Introduce a dependency only when the design requires it and native/project
  capabilities cannot meet the need.
- Preserve user-authored changes and unrelated behavior.
- Map each Stitch screen to an explicit route or component destination.

## Extract and map the design system

Derive recurring color roles, typography, spacing, radii, elevation, grid, and
breakpoints from all selected HTML/screenshots. Reconcile them with existing
application tokens and `.stitch/DESIGN.md`:

1. reuse an equivalent existing token;
2. add the smallest missing semantic token;
3. document intentional divergence from the screenshot.

Avoid page-local magic values and do not copy generated utility/config blocks
blindly into production.

## Component implementation

- Split by stable product responsibility and repeated UI pattern, not every DOM
  wrapper. Keep page composition readable.
- Put shared components in the project's established component location.
- Keep data, state, and event logic where the existing architecture expects it;
  do not create hooks or mock-data modules solely to satisfy a template.
- Replace placeholder `href="#"` links with real routes or buttons. Ensure the
  primary logo/home affordance and back paths work on every relevant viewport.
- Use semantic elements, accessible names, keyboard interaction, visible focus,
  valid error association, sufficient contrast, non-color cues, touch targets,
  meaningful alt text, and reduced-motion behavior.
- Implement loading, empty, error, validation, success, disabled, and permission
  states that are visible in the design or required by the user journey.
- Treat generated copy and data as fixtures unless the request makes them real.
- Keep secrets, signed artifact URLs, and Stitch credentials out of source.

## Fidelity and responsiveness gate

Compare implementation against the retrieved screenshots at the represented
viewport and at least one adjacent responsive size. Check hierarchy, spacing,
typography, color roles, imagery, overflow, interaction states, and navigation.
Fix material differences; do not chase irrelevant sub-pixel differences.

When browser tooling is available, render the local application and capture a
fresh screenshot. Visual checks are read-only validation and do not require a
separate permission. Do not deploy or publish.

## Validation

Run the most relevant non-destructive checks already available in the target
project: targeted tests, typecheck, lint, and build. Project-native validation
is authoritative. Do not weaken tests or silence legitimate errors to make the
conversion pass.

## Handoff

Report:

- Stitch screen → route/component mapping;
- files and tokens created or changed;
- artifacts retrieved and screenshots actually reviewed;
- validation commands actually run and their results;
- intentional deviations, missing states, or unverified responsive surfaces.

Never claim pixel fidelity, accessibility, or successful compilation without
the corresponding inspection or validation evidence.
