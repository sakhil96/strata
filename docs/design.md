# Design specification

## Tokens

See `web/styles/tokens.css` for the full set. Key decisions:

- Single accent: --ore #E36F2E. Used for active persona, current answer, focus ring.
- Neutral palette: ground, stratum, stratum-2, hairline, bone, ash.
- Status colours reserved: --good, --warn, --critical. Never used decoratively.

## Type scale (px)

11 (micro-labels, uppercase, 0.14em tracking) · 13 · 15 · 18 · 24 · 36 · 56 · 88 · 128

- Fraunces: display, large numerals. Optical size on, tight tracking.
- Instrument Sans: interface text.
- JetBrains Mono: labels, hashes, SQL, timestamps. tabular-nums feature.

## Layout

- 12-column grid, 1440px max, 24px gutters.
- Asymmetric: 7/5 and 8/4. Never centred stacks.
- Section numerals 01, 02, 03 in Fraunces 300.
- 8px spacing grid. 2px radii on inputs, 0 on surfaces. 1px hairline borders. No shadows.

## Bans

Purple/blue gradients · glassmorphism · glowing/animated borders · emoji/sparkle/rocket/brain/robot
icons · centred hero with three equal cards · chat bubbles with avatars · "Powered by AI" badge ·
default library styling · stock photos/video · lorem ipsum · rainbow colours · drop shadows ·
pill buttons · dark-mode toggle as hero feature.

## Components

PersonaDial · Ledger · Builder · Convergence · Strata · Index · Lineage · Chart ·
AuditStream · StatusBar. Each in `web/components/` with a fixture at /styleguide.

## Motion

- Entrances: 160-240ms ease-out, 40ms stagger.
- Hover: colour or underline weight, never scale.
- Large numerals count up once (600ms).
- prefers-reduced-motion: all motion disabled.

## QA checklist

Run before merging any change under `web/`. Items marked (auto) fail CI.

- [ ] (auto) `npm run lint`: authorship lint and Prettier
- [ ] (auto) Playwright at 390, 1024 and 1440: no console errors, no CSP violations, axe clean (WCAG 2.1 AA)
- [ ] (auto) Security headers on every page
- [ ] Colours come from `styles/tokens.css` only; ore is the single accent
- [ ] Numerals in Fraunces, labels and hashes in JetBrains Mono with tabular figures
- [ ] Asymmetric 7/5 or 8/4 layout; no centred stacks of equal cards
- [ ] No shadows, gradients, glass, glow, pill buttons or icon decoration from the bans list
- [ ] Hover changes colour or underline only; motion respects reduced motion
- [ ] Loading, empty, fallback and error states shown for every resource
- [ ] Screenshots refreshed with `make screenshots` when a page changes
