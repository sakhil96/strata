---
name: snowflake-security-baseline
description: Validate Snowflake account security configuration against the project baseline.
---

# Security baseline

Check the following and report deviations:

1. **Roles**: hierarchy matches AGENTS.md; no extra grants to persona roles.
2. **Network policies**: account-level and service-user policies exist; allowed IPs match committed list.
3. **Row access policies**: attached to every conformed fact table.
4. **Masking policies**: attached to every column tagged with sensitivity >= CONFIDENTIAL.
5. **Resource monitors**: exist with notify and suspend thresholds.
6. **Event table**: configured and receiving logs.
7. **Secrets**: no plaintext credentials in any file; connections use key-pair JWT from `~/.snowflake`.
8. **Service spec**: no host networking; the container authenticates with the SPCS session token, so it holds no secret.
9. **Time Travel**: DATA_RETENTION_TIME_IN_DAYS set to edition maximum on CONFORMED and AUDIT schemas.
