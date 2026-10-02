---
name: strata-design-system
description: Enforce the STRATA design tokens, typography, layout rules, component specifications and hard bans.
---

# STRATA design system

## Tokens (styles/tokens.css)
- --ground: #0B0D10
- --stratum: #121519
- --stratum-2: #181C22
- --hairline: #232830
- --bone: #E9E4DA (primary text)
- --ash: #9AA0A6 (secondary text)
- --ore: #E36F2E (single accent)
- --good: #6FCF97
- --warn: #F2C94C
- --critical: #EB5757
- --paper: #F4F1EA (light mode / print)
- --ink: #121212 (light mode / print)

## Typography
- Fraunces: display, large numerals. Weights 300, 600. Optical size on, tight tracking.
- Instrument Sans: interface text.
- JetBrains Mono: labels, hashes, SQL, timestamps. tabular-nums.
- Scale: 11, 13, 15, 18, 24, 36, 56, 88, 128 px.

## Layout
- 12-column grid, max 1440 px, 24 px gutters.
- Asymmetric: 7/5 and 8/4. Never centred stacks.
- Section numerals 01, 02, 03 in Fraunces 300.
- 8 px spacing grid. 2 px radii on inputs, 0 on surfaces. 1 px hairline borders. No shadows.

## Motion
- Entrances: 160-240 ms ease-out, 40 ms stagger.
- Hover: colour or underline weight change, never scale.
- Large numerals count up once (600 ms).
- Respect prefers-reduced-motion.

## Hard bans
Purple/blue gradients, glassmorphism, glowing/animated borders, emoji/sparkle/rocket/brain/robot
icons, centred hero with three equal cards, chat bubbles with avatars, "Powered by AI" badge,
default library styling, stock photos/video, lorem ipsum, rainbow colours, drop shadows,
pill buttons everywhere, dark-mode toggle as hero feature.
