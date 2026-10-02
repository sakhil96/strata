---
name: authorship-hygiene
description: Enforce the authorship rules — no machine fingerprints, domain names, sparse comments, no dead code.
---

# Authorship hygiene

## Banned comment content
Never write comments containing: "generated", "AI", "assistant", "here is", "example",
"placeholder", "sample", "TODO", "lorem", "foo", "bar".

Exception: the compiler's single-line header on generated files.

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
