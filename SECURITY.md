# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 3.3.x   | :white_check_mark: |
| 3.2.x   | :warning: Contains a known arbitrary file read (fixed in 3.3.0) — upgrade immediately |
| < 3.2.0 | :x:                |

## Deployment Security Model

CineMatrix is a **local-first desktop studio**. It ships with no authentication layer and is designed to be reached only over the loopback interface.

- **Never bind CineMatrix to a non-loopback interface or expose it to the internet.** `POST /system/shutdown` will terminate the process for any caller that can reach it, and all project data is readable without credentials.
- CORS is restricted to `localhost` / `127.0.0.1` origins.
- Set `STORYBOARD_SECRET_KEY` explicitly. Without it, provider API keys are encrypted using a fixed development secret, and an encryption failure currently falls back to plaintext storage. Fail-closed encryption is scheduled for v3.4.0.
- Uploads are capped at 20 MB but are not yet extension-filtered, and archive formats are not yet decompression-bounded. Only ingest scripts you trust.

Current known limitations are tracked in [docs/STATUS.md](docs/STATUS.md) and remediation is scheduled in [docs/ROADMAP.md](docs/ROADMAP.md).

## Reporting a Vulnerability

We take the security of CineMatrix seriously. If you discover a security vulnerability, please do NOT create a public issue.

Instead, please report security issues responsibly:
1. Open a **Private Security Advisory** directly on GitHub under the repository's [Security Advisories tab](https://github.com/kirklasalle/CineMatrix/security/advisories/new).
2. Include a detailed description of the vulnerability, affected components, and steps to reproduce.

### Our Commitment
- We will acknowledge receipt of your vulnerability report within 48 hours.
- We will provide a regular status update until the vulnerability is resolved and patched in a new release.
