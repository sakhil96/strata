# Security Policy

## Supported versions

Only the latest release on the `main` branch receives security updates.

## Reporting a vulnerability

Email security findings to the repository maintainers. Do not open a public issue for
security vulnerabilities. We acknowledge reports within 48 hours and aim to release a
fix within 7 days for critical issues.

Include:
- A description of the vulnerability and its impact.
- Steps to reproduce.
- Any suggested remediation.

## Scope

- The Snowflake account configuration (roles, policies, network rules).
- The API and its input validation.
- The container image and its dependencies.
- The front-end security headers and CSP.
- Secret management and key rotation.

## Out of scope

- Snowflake platform vulnerabilities (report to Snowflake directly).
- Denial of service against the Snowflake account (covered by resource monitors).

## Disclosure

We follow coordinated disclosure. We will credit reporters in CHANGELOG.md unless they
prefer anonymity.
