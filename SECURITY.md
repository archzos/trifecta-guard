# Security Policy

## Supported versions

This repository is pre-1.0. Security fixes target the latest `main` branch.

## Reporting a vulnerability

Please do not file public issues for vulnerabilities.

Report privately to: `security@archzos.com`

Include:
- Affected component(s)
- Reproduction steps / proof of concept
- Impact assessment
- Suggested remediation (if available)

You can expect:
- Initial acknowledgement within 72 hours
- Triage and severity assessment
- Coordinated disclosure after a fix is available

## Scope

In scope:
- Policy bypasses
- Taint tracking inconsistencies
- Unsafe default behavior in adapters/middleware
- Data leakage through telemetry or dashboard endpoints

Out of scope:
- Vulnerabilities only present in forks or modified deployments
- Issues requiring non-default, explicitly insecure configuration
