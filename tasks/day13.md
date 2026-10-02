# Day 13: Release path

- Dockerfile with digest-pinned bases, CI with SBOM and image scan
- SPCS spec, smoke checks, release gate, rollback

Done when: `make reproducible` passes and `make smoke ENV=test` passes against SCM_TEST.
