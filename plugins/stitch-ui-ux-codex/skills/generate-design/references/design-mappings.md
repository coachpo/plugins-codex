# Contextual Design Decisions

Use this reference to turn vague language into decision criteria. It is not a
keyword substitution table. Preserve explicit user values and existing
design-system rules; do not add features or decoration only to make a prompt
sound more professional.

## Clarify intent before naming a pattern

| Input signal | Evidence or decision criteria | Possible precise phrasing |
|:---|:---|:---|
| "menu at the top" | Navigation depth, frequency, available width, and whether access must persist while scrolling | "Top navigation for the primary routes"; add "sticky" only when persistent access is required |
| "big photo" | Whether imagery communicates product value, supplies context, or is decorative | "Prominent product image with a protected focal point"; do not assume a hero or video |
| "list of things" | Whether users scan, compare fields, browse visually, or take row-level actions | Choose a semantic list, table, or card collection based on the task |
| "button" | Action priority, consequence, state, and surrounding alternatives | Name it primary, secondary, destructive, or icon-only only when hierarchy supports that role |
| "form" | Required fields, validation timing, recovery, privacy, and completion flow | "Labeled form with relevant validation and recovery states" |
| "sidebar" | Information architecture, viewport, and whether navigation or supporting content owns the space | "Side navigation" or "supporting panel"; collapse it only when responsive evidence requires it |
| "popup" | Whether the action blocks progress, needs context, or can remain inline | Choose a dialog, drawer, popover, or inline disclosure from task and focus requirements |

The phrasing column contains examples, not automatic outputs. If the evidence
does not select a pattern, state the assumption or ask only when the choice
materially changes the user journey.

## Translate a vibe into product qualities

Interpret broad terms such as "modern", "professional", "playful", "luxury",
or "technical" through the product context:

1. Identify the intended qualities: trust, energy, calm, density, precision,
   warmth, editorial emphasis, or another user-relevant property.
2. Reuse existing typography, color, shape, imagery, and motion tokens.
3. Change only the dimensions needed to express those qualities.
4. Avoid bundled defaults such as gradients, glassmorphism, neon, serif
   headings, rounded cards, or animation unless the user or design system
   supports them.

## Geometry and elevation

Describe shape and depth semantically first: sharp, slightly softened, rounded,
pill-shaped, flat, bordered, raised, or inset. Use exact radii and shadow tokens
only when supplied by the design system or extracted from evidence. Do not
invent framework utility values or shadows solely from an adjective.
