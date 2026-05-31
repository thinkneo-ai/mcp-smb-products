# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Email:** security@thinkneo.ai
2. **Do not** open a public issue for security vulnerabilities
3. Include steps to reproduce, impact assessment, and suggested fix if possible

We will acknowledge receipt within 48 hours and provide a detailed response within 5 business days.

## Security Measures

- All tool inputs are validated and sanitized
- Bearer token authentication on all non-public endpoints
- Rate limiting per IP and per API key
- No secrets or credentials stored in code
- Dependencies pinned and regularly audited
- PII detection runs on all user-facing text inputs
