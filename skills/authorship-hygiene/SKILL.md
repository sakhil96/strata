---
name: authorship-hygiene
description: Enforce the authorship rules — no machine fingerprints, domain names, sparse comments, no dead code.
---

# Authorship hygiene

## Banned comment content
Never write comments containing: "generated", "AI", "assistant", "here is", "example",
"placeholder", "sample", "TODO", "lorem", "foo", "bar".

Compiled files carry no header; `scripts/authorship_lint.py` skips the compiled output directories.
Run `python scripts/authorship_lint.py` before every commit.

## Naming
Use domain names: ledger, persona, basis, grain, stratum, lane, receipt, shipment,
carrier, tariff, snapshot, crosswalk. Never: data, result, item, temp, handleClick,
MyComponent, utils2.

## Dead code
No unused imports, commented-out blocks, console.log, print(), empty catch blocks
or unused variables.

## Config files
Write package.json, next.config.ts, tailwind.config.ts and pyproject.toml by hand.
Never commit scaffold output.
