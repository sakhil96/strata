---
description: Deploy to an environment through the release gate
---

Use the release-and-rollback skill. Ask for the environment if not given. Run `make release ENV=<env>`; for prod, `scripts/release_gate.py` must pass first. Never run against prod without explicit confirmation in this session.
