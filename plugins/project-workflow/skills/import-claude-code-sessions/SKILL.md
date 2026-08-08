---
name: import-claude-code-sessions
description: Import selected Claude Code chats into Codex through the supported native CLI flow and verify the imported target before reporting success. Use when the user asks to import, migrate, or continue Claude Code work identified by project or chat. Do not use for standard Claude Chat data or manual transcript conversion.
---

# Import Claude Code Sessions

## Goal

Bring the user-selected Claude Code chats into Codex through the current official importer while leaving Claude source data and unrelated existing setup unchanged.

Standard Claude Chat data is unsupported. This skill does not convert or directly ingest transcript files.

## Authorization and boundaries

- Listing, inspection, explanation, diagnosis, and planning are read-only.
- A direct request to import, migrate, or continue Claude Code work authorizes the native local import of the selected chats. It does not authorize selecting additional chats, projects, setup items, or duplicate copies in the importer.
- Use an independent local Codex CLI running `/import`. Never write Codex databases or rollout files, modify Claude source data, or substitute a custom staging or conversion path.
- Do not reveal credentials, authentication material, unrelated source details, or message bodies as import evidence. When the user asks to continue the imported work, use its history only as needed for that request. Any sign-in, connection authorization, or post-import setup remains a user action unless separately authorized.

## Success evidence

Success requires both of these checks:

- the native importer completes the selected chat import without a reported failure;
- the imported target exists, opens, and contains the expected conversation history.

Also report these fields when the supported surface exposes them:

- the selected Claude Code chat identity, including title and project when shown;
- the native importer result for the selected items, including imported or failed counts when shown;
- the imported target title or identifier when shown;
- any remaining setup or review status.

An importer completion message alone is insufficient when the target cannot be opened and checked.

## Stop conditions

Stop without claiming success when:

- the requested source or selection is ambiguous;
- the source is not Claude Code or is not offered by the official importer;
- an independent local Codex CLI is unavailable;
- proceeding would import items outside the user's selection or create a duplicate that was not requested;
- the importer reports a failure or the target cannot be opened or verified.

Report a failed attempt or unverifiable target as incomplete. For ambiguity, an unavailable CLI, or required authentication, report that user action is needed. In either case, state the evidence already obtained and the smallest next action. Read [references/troubleshooting.md](references/troubleshooting.md) only after one of these conditions occurs.

## Official workflow

1. When internet access is available, open the current official import documentation: https://learn.chatgpt.com/docs/import.
2. If an exact imported target already exists, return it instead of making another copy unless the user explicitly requests a duplicate.
3. Start an independent local Codex CLI, enter `/import`, choose **Claude Code**, resolve the requested project and chat in the native selector, review the authorized selection, and import. The CLI imports up to 50 chats from the last 30 days; `/import` is unavailable inside a running task, a remote session, or a session connected to a local app-server daemon.
4. Apply the success checks above. If the importer reports setup still required after the chat target is verified, report `imported; setup pending` and stop before authentication or connection changes.
5. If the user asked to continue the imported work, navigate to or continue the verified imported target. Do not create a separate task unless the user explicitly asks for one.

## Output requirements

Lead with one of: imported, already present, incomplete, or user action needed. Then report the selected source, importer result, imported target, verification evidence, any setup still required, and the minimum next action. Include identifiers and counts only when they are actually available. Keep the import report to metadata and omit routine narration.
