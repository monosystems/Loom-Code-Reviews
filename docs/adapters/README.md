# Platform Adapters

This directory contains detailed implementation guides for each supported git platform.

---

## Overview

Loom uses the **adapter pattern** to support multiple git platforms through a unified interface. Each platform has its own adapter that handles:
- Webhook signature verification
- API authentication
- Fetching PR diffs
- Fetching file contents
- Posting comments

---

## Supported Platforms

| Platform | Popularity | Complexity | Status |
|----------|-----------|------------|--------|
| [GitHub](github.md) | ⭐⭐⭐⭐⭐ | Medium | Ready |
| [GitLab](gitlab.md) | ⭐⭐⭐⭐ | Medium | Ready |
| [Gitea](gitea.md) | ⭐⭐⭐ | Low | Ready |
| [Bitbucket](bitbucket.md) | ⭐⭐⭐ | Medium | Ready |
| [Azure DevOps](azure-devops.md) | ⭐⭐ | High | Ready |

---

## Quick Comparison

### Authentication

| Platform | Method | Header |
|----------|--------|--------|
| GitHub | Bearer Token | `Authorization: Bearer ghp_...` |
| GitLab | Private Token | `PRIVATE-TOKEN: glpat-...` |
| Bitbucket | Basic Auth | `Authorization: Basic <base64>` |
| Gitea | Token | `Authorization: token <token>` |
| Azure DevOps | Basic Auth (PAT) | `Authorization: Basic <base64(:PAT)>` |

### Webhook Verification

| Platform | Method | Header |
|----------|--------|--------|
| GitHub | HMAC-SHA256 | `X-Hub-Signature-256: sha256=...` |
| GitLab | Token Comparison | `X-Gitlab-Token: ...` |
| Bitbucket | UUID Check | `X-Hook-UUID: {...}` |
| Gitea | HMAC-SHA256 | `X-Gitea-Signature: ...` |
| Azure DevOps | Basic Auth | `Authorization: Basic ...` |

### Rate Limits

| Platform | Limit | Window |
|----------|-------|--------|
| GitHub | 5,000 | per hour |
| GitLab | 2,000 | per minute |
| Bitbucket | 1,000 | per hour |
| Gitea | Unlimited | (self-hosted) |
| Azure DevOps | ~200 | varies (TSTU-based) |

### Inline Comments

| Platform | Supported | Notes |
|----------|-----------|-------|
| GitHub | ✅ Yes | Via review comments API |
| GitLab | ✅ Yes | Via discussions API |
| Bitbucket | ❌ No | API doesn't support (UI only) |
| Gitea | ✅ Yes | Via pull request comments |
| Azure DevOps | ✅ Yes | Via threads with context |

---

## Implementation Priority

**Recommended order for MVP:**

1. **GitHub** - Most popular, well-documented
2. **GitLab** - Popular for self-hosted, good docs
3. **Gitea** - Simple, similar to GitHub
4. **Bitbucket** - Corporate users, limited inline comments
5. **Azure DevOps** - Complex, specific use case

---

## Common Patterns

### Adapter Interface

All adapters implement the same interface:

```python
class GitAdapter(ABC):
    @abstractmethod
    async def verify_webhook(self, request: Request) -> bool:
        """Verify webhook signature/token"""
    
    @abstractmethod
    async def parse_webhook(self, payload: dict) -> WebhookEvent:
        """Parse platform-specific payload to standard event"""
    
    @abstractmethod
    async def fetch_diff(self, repo: str, pr_number: int) -> str:
        """Fetch PR/MR diff"""
    
    @abstractmethod
    async def fetch_file(self, repo: str, path: str, ref: str) -> str:
        """Fetch file content at specific commit"""
    
    @abstractmethod
    async def post_comment(self, repo: str, pr_number: int, comment: Comment):
        """Post review comment"""
    
    @abstractmethod
    async def get_pr_info(self, repo: str, pr_number: int) -> PRInfo:
        """Get PR/MR metadata"""
```

### Standard Event Format

All webhooks are parsed into:

```python
@dataclass
class WebhookEvent:
    platform: str              # "github", "gitlab", etc.
    event_type: str            # "pull_request", "merge_request"
    action: str                # "opened", "synchronize", etc.
    repo_full_name: str        # "owner/repo"
    pr_number: int             # PR/MR number
    pr_title: str              # PR/MR title
    pr_author: str             # Author username
    source_branch: str         # Feature branch
    target_branch: str         # Base branch
    head_sha: str              # Latest commit SHA
```

---

## Environment Variables

Each platform requires specific environment variables:

### GitHub
```bash
GITHUB_API_TOKEN=ghp_...
GITHUB_WEBHOOK_SECRET=your-secret
```

### GitLab
```bash
GITLAB_API_TOKEN=glpat-...
GITLAB_WEBHOOK_SECRET=your-secret
GITLAB_BASE_URL=https://gitlab.com/api/v4  # Optional for self-hosted
```

### Bitbucket
```bash
BITBUCKET_USERNAME=your-username
BITBUCKET_APP_PASSWORD=your-app-password
BITBUCKET_WEBHOOK_UUIDS=uuid1,uuid2,uuid3
```

### Gitea
```bash
GITEA_API_TOKEN=your-token
GITEA_WEBHOOK_SECRET=your-secret
GITEA_BASE_URL=https://gitea.company.com/api/v1
```

### Azure DevOps
```bash
AZURE_DEVOPS_PAT=your-pat
AZURE_DEVOPS_WEBHOOK_SECRET=your-secret
AZURE_DEVOPS_ORGANIZATION=your-org
```

---

## Testing Strategy

### Unit Tests

Mock webhook payloads and API responses:

```python
@pytest.mark.parametrize("platform", ["github", "gitlab", "bitbucket", "gitea", "azure-devops"])
def test_webhook_parsing(platform):
    payload = load_fixture(f"{platform}_pr_opened.json")
    adapter = get_adapter(platform)
    event = adapter.parse_webhook(payload)
    
    assert event.platform == platform
    assert event.pr_number > 0
```

### Integration Tests

Test against real APIs (requires tokens):

```python
@pytest.mark.integration
async def test_github_adapter():
    adapter = GitHubAdapter()
    pr_info = await adapter.get_pr_info("owner/repo", 1)
    assert pr_info["number"] == 1
```

### Sample Payloads

Sample webhook payloads for testing are in `/tests/fixtures/`:
- `github_pr_opened.json`
- `gitlab_mr_opened.json`
- `bitbucket_pr_created.json`
- `gitea_pr_opened.json`
- `azure_pr_created.json`

---

## Error Handling

### Common Errors

**All Platforms:**
- 401 Unauthorized - Invalid credentials
- 404 Not Found - Repository or PR doesn't exist
- 429 Rate Limited - Too many requests
- 500 Server Error - Platform issue

**Retry Strategy:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def api_call_with_retry():
    # API call
```

---

## Adding a New Platform

To add support for a new git platform:

1. **Create adapter documentation**
   - `docs/adapters/platform-name.md`
   - Document API, webhooks, authentication

2. **Implement adapter class**
   - `src/adapters/platform_name.py`
   - Implement all abstract methods

3. **Register adapter**
   - `src/adapters/registry.py`
   - Add to ADAPTERS dict

4. **Add webhook endpoint**
   - `src/api/webhooks.py`
   - `POST /webhooks/platform-name`

5. **Add tests**
   - Sample webhook payload
   - Unit tests for parsing
   - Integration tests (optional)

6. **Update documentation**
   - Platform-specific setup guide
   - Environment variables
   - Known limitations

---

## Platform-Specific Notes

### GitHub
- **Pros:** Best documentation, most features
- **Cons:** Rate limits can be restrictive
- **Tip:** Use conditional requests to save rate limit

### GitLab
- **Pros:** Great for self-hosted, flexible
- **Cons:** Discussions API more complex than comments
- **Tip:** URL-encode file paths

### Bitbucket
- **Pros:** Good corporate adoption
- **Cons:** No inline comments via API
- **Tip:** Include file/line in comment body

### Gitea
- **Pros:** Very simple, GitHub-compatible
- **Cons:** Fewer features than GitHub/GitLab
- **Tip:** Nearly identical to GitHub adapter

### Azure DevOps
- **Pros:** Enterprise features
- **Cons:** Most complex API, no simple diff endpoint
- **Tip:** Implement last, after others are stable

---

## References

- [Adapter Pattern Design](../architecture/adapter-pattern.md)
- [Webhook API](../api/webhooks.md)
- [Data Flow](../architecture/data-flow.md)

---

## Support Matrix

| Feature | GitHub | GitLab | Bitbucket | Gitea | Azure DevOps |
|---------|--------|--------|-----------|-------|--------------|
| Webhooks | ✅ | ✅ | ✅ | ✅ | ✅ |
| PR Diff | ✅ | ✅ | ✅ | ✅ | ⚠️ Complex |
| File Fetch | ✅ | ✅ | ✅ | ✅ | ✅ |
| Summary Comments | ✅ | ✅ | ✅ | ✅ | ✅ |
| Inline Comments | ✅ | ✅ | ❌ | ✅ | ✅ |
| Self-Hosted | ❌ | ✅ | ⚠️ Server | ✅ | ✅ |
| Rate Limits | Strict | Moderate | Moderate | None | Complex |
