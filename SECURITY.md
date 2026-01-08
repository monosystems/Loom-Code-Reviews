# Security Policy

## Supported Versions

We release patches for security vulnerabilities. The following versions are
currently supported:

| Version | Supported |
|---------|-----------|
| Latest  | ✅ Yes    |
| 1.x     | ✅ Yes    |
| 0.x     | ❌ No     |

## Reporting a Vulnerability

We take the security of Loom Code Reviews seriously. If you believe you have
found a security vulnerability, please report it to us responsibly.

### Do NOT

* Create a public GitHub issue
* Post about it in Discord/forums
* Share it with anyone else

### Do

1. **Email us**: Send a detailed report to security@loom-reviews.dev
2. **Include**:
   * Description of the vulnerability
   * Steps to reproduce
   * Affected components
   * Potential impact
   * Your name/contact (optional)

3. **Wait** for our acknowledgment (within 24 hours)

We will:
* Confirm receipt of your report
* Investigate and provide a fix
* Credit you (if you want) in the release notes
* Keep you informed throughout the process

## Security Best Practices

### For Self-Hosted Users

1. **Keep Updated**: Always run the latest version
2. **Secure Secrets**: Use environment variables for API keys, don't commit them
3. **Network Isolation**: Restrict access to Loom's web interface
4. **HTTPS**: Always use HTTPS in production
5. **Webhook Verification**: Enable webhook secret validation
6. **Rate Limiting**: Configure appropriate rate limits

### Environment Variables Security

```bash
# Never commit these to version control
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
BETTER_AUTH_SECRET=your-32-char-secret
GITHUB_CLIENT_SECRET=...
```

### Docker Security

```bash
# Run with non-root user
docker run -u 1000:1000 ghcr.io/loom-reviews/loom:latest

# Read-only filesystem
docker run --read-only ghcr.io/loom-reviews/loom:latest

# Drop capabilities
docker run --cap-drop=ALL ghcr.io/loom-reviews/loom:latest
```

## Dependencies

We use automated tools to scan dependencies:

* **Dependabot** - GitHub's dependency scanning
* **Snyk** - Additional vulnerability scanning
* **CodeQL** - Static analysis

Critical vulnerabilities are patched within 24 hours of disclosure.

## Architecture Security

### Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  GitHub/    │────▶│    Loom     │────▶│   LLM API   │
│  GitLab     │     │   Server    │     │ (external)  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   SQLite/   │
                    │  Postgres   │
                    └─────────────┘
```

### Key Security Measures

1. **No Code Storage**: Loom never stores code permanently
2. **Ephemeral Review**: Code is processed in memory during review
3. **Configurable Caching**: Configs cached with TTL
4. **API Key Protection**: Keys encrypted at rest (for dashboard config)
5. **Webhook Verification**: HMAC signatures validated

## Compliance

For enterprise compliance questions, contact security@loom-reviews.dev:

* SOC 2 - In progress
* GDPR - Compliant (data stays on your infrastructure)
* HIPAA - Contact for BAA
