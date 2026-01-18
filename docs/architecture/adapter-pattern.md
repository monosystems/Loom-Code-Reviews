# Git Platform Adapter Pattern

**Version:** 0.1.0  
**Status:** Design Phase

---

## Purpose

The adapter pattern allows Loom to support **any git platform** (GitHub, GitLab, Bitbucket, Gitea, etc.) through a unified interface, while handling platform-specific details in separate adapters.

---

## Core Concept

```python
# Abstract interface
class GitAdapter(ABC):
    """Base class for all git platform adapters"""
    
    @abstractmethod
    async def verify_webhook(self, request: Request) -> bool:
        """Verify webhook signature"""
        
    @abstractmethod
    async def parse_webhook(self, payload: dict) -> WebhookEvent:
        """Parse webhook payload into standard event"""
        
    @abstractmethod
    async def fetch_diff(self, repo: str, pr_number: int) -> str:
        """Get PR/MR diff"""
        
    @abstractmethod
    async def fetch_file(self, repo: str, path: str, ref: str) -> str:
        """Fetch file content from repository"""
        
    @abstractmethod
    async def post_comment(self, repo: str, pr_number: int, comment: Comment):
        """Post review comment"""
        
    @abstractmethod
    async def get_pr_info(self, repo: str, pr_number: int) -> PRInfo:
        """Get PR/MR metadata"""
```

---

## Standardized Data Models

### WebhookEvent
```python
@dataclass
class WebhookEvent:
    """Normalized webhook event"""
    platform: str              # "github", "gitlab", etc.
    event_type: str            # "pull_request", "merge_request"
    action: str                # "opened", "synchronize", "reopened"
    repo_full_name: str        # "owner/repo"
    pr_number: int             # PR/MR number
    pr_title: str              # PR/MR title
    pr_author: str             # Author username
    source_branch: str         # Feature branch
    target_branch: str         # Base branch
    head_sha: str              # Latest commit SHA
```

### PRInfo
```python
@dataclass
class PRInfo:
    """PR/MR metadata"""
    number: int
    title: str
    description: str
    author: str
    state: str                 # "open", "closed", "merged"
    source_branch: str
    target_branch: str
    created_at: datetime
    updated_at: datetime
    mergeable: bool
    changed_files: int
    additions: int
    deletions: int
```

### Comment
```python
@dataclass
class Comment:
    """Review comment"""
    body: str                  # Comment text
    path: Optional[str]        # File path (for inline comments)
    line: Optional[int]        # Line number (for inline comments)
    severity: str              # "blocker", "warning", "info"
```

---

## Platform Implementations

### GitHub Adapter

**Webhook Verification:**
```python
import hmac
import hashlib

async def verify_webhook(self, request: Request) -> bool:
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        return False
    
    secret = os.getenv("GITHUB_WEBHOOK_SECRET").encode()
    body = await request.body()
    
    expected = "sha256=" + hmac.new(
        secret, body, hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)
```

**API Endpoints:**
- Base URL: `https://api.github.com`
- Auth: `Authorization: Bearer <token>` or `token <token>`
- Rate Limit: 5000/hour (authenticated)

**Key Endpoints:**
```python
GET  /repos/{owner}/{repo}/pulls/{number}
GET  /repos/{owner}/{repo}/pulls/{number}/files
POST /repos/{owner}/{repo}/pulls/{number}/comments
POST /repos/{owner}/{repo}/issues/{number}/comments
GET  /repos/{owner}/{repo}/contents/{path}?ref={sha}
```

### GitLab Adapter

**Webhook Verification:**
```python
async def verify_webhook(self, request: Request) -> bool:
    token = request.headers.get("X-Gitlab-Token")
    expected = os.getenv("GITLAB_WEBHOOK_SECRET")
    return token == expected
```

**API Endpoints:**
- Base URL: `https://gitlab.com/api/v4` (or self-hosted URL)
- Auth: `PRIVATE-TOKEN: <token>` or `Authorization: Bearer <token>`
- Rate Limit: 2000/minute (authenticated)

**Key Endpoints:**
```python
GET  /projects/{id}/merge_requests/{mr_iid}
GET  /projects/{id}/merge_requests/{mr_iid}/changes
POST /projects/{id}/merge_requests/{mr_iid}/notes
POST /projects/{id}/merge_requests/{mr_iid}/discussions
GET  /projects/{id}/repository/files/{file_path}?ref={sha}
```

### Bitbucket Adapter

**Webhook Verification:**
```python
async def verify_webhook(self, request: Request) -> bool:
    # Bitbucket uses UUID in header or basic auth
    webhook_uuid = request.headers.get("X-Hook-UUID")
    # Verify against stored webhook UUIDs
    return webhook_uuid in self.registered_webhooks
```

**API Endpoints:**
- Base URL: `https://api.bitbucket.org/2.0`
- Auth: Basic Auth or App Password
- Rate Limit: 1000/hour

**Key Endpoints:**
```python
GET  /repositories/{workspace}/{repo}/pullrequests/{id}
GET  /repositories/{workspace}/{repo}/pullrequests/{id}/diff
POST /repositories/{workspace}/{repo}/pullrequests/{id}/comments
GET  /repositories/{workspace}/{repo}/src/{commit}/{path}
```

### Gitea Adapter

**Webhook Verification:**
```python
import hmac
import hashlib

async def verify_webhook(self, request: Request) -> bool:
    signature = request.headers.get("X-Gitea-Signature")
    if not signature:
        return False
    
    secret = os.getenv("GITEA_WEBHOOK_SECRET").encode()
    body = await request.body()
    
    expected = hmac.new(secret, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)
```

**API Endpoints:**
- Base URL: `https://gitea.instance/api/v1`
- Auth: `Authorization: token <token>`
- Rate Limit: Configurable per instance

**Key Endpoints:**
```python
GET  /repos/{owner}/{repo}/pulls/{index}
GET  /repos/{owner}/{repo}/pulls/{index}.diff
POST /repos/{owner}/{repo}/pulls/{index}/reviews
GET  /repos/{owner}/{repo}/raw/{filepath}?ref={sha}
```

### Azure DevOps Adapter

**Webhook Verification:**
```python
async def verify_webhook(self, request: Request) -> bool:
    # Azure DevOps uses Basic Auth for webhooks
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Basic "):
        return False
    
    # Verify credentials
    # ...implementation
```

**API Endpoints:**
- Base URL: `https://dev.azure.com/{organization}`
- Auth: PAT token in Basic Auth
- Rate Limit: Complex (varies by resource)

**Key Endpoints:**
```python
GET  /{organization}/{project}/_apis/git/pullrequests/{id}
GET  /{organization}/{project}/_apis/git/pullrequests/{id}/iterations/{iteration}/changes
POST /{organization}/{project}/_apis/git/pullrequests/{id}/threads
GET  /{organization}/{project}/_apis/git/repositories/{repo}/items?path={path}&version={sha}
```

---

## Adapter Registration

```python
# adapters/registry.py
from typing import Dict, Type
from .base import GitAdapter
from .github import GitHubAdapter
from .gitlab import GitLabAdapter
from .bitbucket import BitbucketAdapter
from .gitea import GiteaAdapter
from .azure_devops import AzureDevOpsAdapter

ADAPTERS: Dict[str, Type[GitAdapter]] = {
    "github": GitHubAdapter,
    "gitlab": GitLabAdapter,
    "bitbucket": BitbucketAdapter,
    "gitea": GiteaAdapter,
    "azure-devops": AzureDevOpsAdapter,
}

def get_adapter(platform: str) -> GitAdapter:
    """Get adapter instance for platform"""
    adapter_class = ADAPTERS.get(platform)
    if not adapter_class:
        raise ValueError(f"Unsupported platform: {platform}")
    return adapter_class()
```

---

## Webhook Routing

```python
# api/webhooks.py
from fastapi import APIRouter, Request, HTTPException
from adapters.registry import get_adapter

router = APIRouter()

@router.post("/webhooks/{platform}")
async def handle_webhook(platform: str, request: Request):
    """Handle incoming webhook from any platform"""
    
    # Get appropriate adapter
    adapter = get_adapter(platform)
    
    # Verify webhook signature
    if not await adapter.verify_webhook(request):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse webhook payload
    payload = await request.json()
    event = await adapter.parse_webhook(payload)
    
    # Create review job
    from tasks.review import create_review_job
    job_id = await create_review_job(event, adapter)
    
    return {"success": True, "job_id": job_id}
```

---

## Adding New Platforms

To add support for a new git platform:

1. **Create adapter class:**
```python
# adapters/new_platform.py
from .base import GitAdapter

class NewPlatformAdapter(GitAdapter):
    async def verify_webhook(self, request: Request) -> bool:
        # Implement signature verification
        pass
    
    # Implement all abstract methods
    # ...
```

2. **Register adapter:**
```python
# adapters/registry.py
from .new_platform import NewPlatformAdapter

ADAPTERS = {
    # ...
    "new-platform": NewPlatformAdapter,
}
```

3. **Add webhook endpoint:**
```python
POST /webhooks/new-platform
```

4. **Document platform-specific details:**
```markdown
docs/adapters/new-platform.md
```

---

## Error Handling

All adapter methods should raise specific exceptions:

```python
class AdapterError(Exception):
    """Base adapter exception"""

class WebhookVerificationError(AdapterError):
    """Webhook signature verification failed"""

class APIError(AdapterError):
    """API request failed"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(message)

class RateLimitError(APIError):
    """API rate limit exceeded"""
```

---

## Testing Strategy

Each adapter must include:

1. **Unit tests** - Mock API responses
2. **Integration tests** - Real API calls (test account)
3. **Webhook tests** - Sample webhook payloads

```python
# tests/adapters/test_github.py
import pytest
from adapters.github import GitHubAdapter

@pytest.fixture
def github_adapter():
    return GitHubAdapter()

async def test_verify_webhook(github_adapter):
    # Test with valid signature
    # Test with invalid signature
    pass

async def test_parse_webhook(github_adapter):
    # Test with sample payload
    pass
```

---

## Performance Considerations

### Caching
- Cache PR info for 5 minutes
- Cache file contents by SHA (immutable)
- Don't cache diff (changes on synchronize)

### Rate Limiting
- Implement exponential backoff
- Respect platform rate limits
- Use conditional requests (If-None-Match)

### Parallel Requests
- Fetch multiple files in parallel
- Use async/await for all API calls

---

## Security

### Secrets Management
```python
# Environment variables for each platform
GITHUB_WEBHOOK_SECRET
GITHUB_API_TOKEN
GITLAB_WEBHOOK_SECRET
GITLAB_API_TOKEN
BITBUCKET_WEBHOOK_SECRET
BITBUCKET_API_TOKEN
# etc.
```

### Token Permissions

**GitHub:**
- `repo` - Repository access
- `pull_request` - PR/Comments

**GitLab:**
- `api` - Full API access
- Or `read_repository` + `write_repository`

**Bitbucket:**
- Repository read
- Pull request write

---

## Future Enhancements

- [ ] GraphQL support (GitHub, GitLab)
- [ ] Webhook retry mechanism
- [ ] Multi-account support per platform
- [ ] Custom headers for self-hosted instances
- [ ] Proxy support for corporate networks

---

## References

- [GitHub Webhooks](https://docs.github.com/webhooks)
- [GitLab Webhooks](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html)
- [Bitbucket Webhooks](https://support.atlassian.com/bitbucket-cloud/docs/manage-webhooks/)
- [Gitea Webhooks](https://docs.gitea.io/en-us/webhooks/)
- [Azure DevOps Service Hooks](https://learn.microsoft.com/en-us/azure/devops/service-hooks/)
