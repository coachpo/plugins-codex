# Stitch UI/UX for Codex

This Codex plugin provides five UI/UX skills adapted from
`google-labs-code/stitch-skills` for use with a separately configured official
Google Stitch Remote MCP:

- `enhance-prompt` turns product intent into a structured, accessible UI brief.
- `generate-design` generates, edits, reviews, and retrieves Stitch screens.
- `design-md` extracts a reusable semantic design system into `DESIGN.md`.
- `stitch-loop` coordinates bounded multi-page design iterations.
- `react-components` converts selected Stitch screens into maintainable React.

The skills are optimized for GPT-5.6-style execution with lean outcome and
evidence contracts, contextual design choices, exact tool routing, explicit
authority, bounded recovery, and visual validation. Each skill also provides a
minimal Codex UI prompt under `agents/openai.yaml`. The plugin remains
targeted at Codex with GPT-5.6, but it does not select or configure the runtime
model or create a Codex GOAL unless the user explicitly requests that host
behavior.

## Stitch MCP prerequisite

The four MCP-backed skills declare the official Stitch endpoint as a
discoverable `streamable_http` dependency named `stitch`. The plugin does not
bundle credentials or authenticate on your behalf; complete the host's official
Stitch MCP setup so its tools appear as `mcp__stitch__<tool>` in Codex.

1. Follow the [official Stitch MCP setup](https://stitch.withgoogle.com/docs/mcp/setup/)
   for the authentication method supported by your host.
2. Keep API keys, tokens, cookies, and other credentials out of chat and source files.
3. Restart Codex or start a new task after configuring the connection or
   installing or updating the plugin.

If Stitch tools are unavailable or authentication fails, repair the external
MCP connection; reinstalling this skills-only plugin will not configure it.

## Default workflow

1. Clarify the user journey, platform, content, constraints, and acceptance bar.
2. Generate or edit a Stitch screen only when the user requested that external write.
3. Retrieve the final screen with `mcp__stitch__get_screen` and return only the
   screenshot, HTML, and additional artifacts actually exposed by its live result.
4. Review hierarchy, task completion, responsive behavior, accessibility, and states.
5. Never resend an ambiguous timed-out write; verify remote state first. Use
   targeted edits instead of blind regeneration and preserve a non-secret,
   recoverable audit trail in `.stitch/` when executing `stitch-loop` or when
   local artifacts are requested.

This is a derivative plugin, not an officially supported Google product. It is
distributed under Apache-2.0. See `NOTICE`, `THIRD_PARTY_NOTICES.md`, and
`UPSTREAM.md` for source and modification details.
