# Stitch UI/UX for Codex

This Codex plugin provides five UI/UX skills adapted from
`google-labs-code/stitch-skills` for use with a separately configured official
Google Stitch Remote MCP:

- `enhance-prompt` turns product intent into a structured, accessible UI brief.
- `generate-design` generates, edits, reviews, and retrieves Stitch screens.
- `design-md` extracts a reusable semantic design system into `DESIGN.md`.
- `stitch-loop` coordinates bounded multi-page design iterations.
- `react-components` converts selected Stitch screens into maintainable React.

The skills are optimized for GPT-5.6-style execution with lean outcome
contracts, contextual design choices, bounded tool routing, explicit authority,
and visual validation. The plugin remains model-agnostic and does not select or
configure the Codex model.

## Stitch MCP prerequisite

The plugin does not bundle an MCP server definition or manage authentication.
Configure the official Stitch MCP outside this plugin, and name the connection
`stitch` if you want its tools to appear as `mcp__stitch__<tool>` in Codex.

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
3. Retrieve the final screen with `get_screen` and return its screenshot, HTML,
   and Figma export when available.
4. Review hierarchy, task completion, responsive behavior, accessibility, and states.
5. Use targeted edits instead of blind regeneration; preserve an audit trail in
   `.stitch/` when local artifacts are requested.

This is a derivative plugin, not an officially supported Google product. It is
distributed under Apache-2.0. See `NOTICE`, `THIRD_PARTY_NOTICES.md`, and
`UPSTREAM.md` for source and modification details.
