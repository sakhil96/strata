---
name: release-and-rollback
description: Manage semantic view versioning, deployment to TEST and PROD, and rollback procedures.
---

# Release and rollback

## Deploy flow

1. Compile all targets with `--env test`.
2. Deploy semantic views as `_V{n+1}` to SCM_TEST.
3. Run evaluation suites 1-7 against SCM_TEST.
4. If all pass: deploy to SCM_PROD with the same version suffix.
5. Swap grants from `_V{n}` to `_V{n+1}` on all persona views.
6. Keep `_V{n}` for rollback.

## Rollback

1. Swap grants back from `_V{n+1}` to `_V{n}`.
2. Verify answers match pre-deployment state.
3. Investigate and fix before re-attempting deploy.

## Emergency

If the service is down: `make spcs-rollback` reverts to the previous image tag.
If data is corrupted: restore from Time Travel clone per `docs/runbooks/restore.md`.
