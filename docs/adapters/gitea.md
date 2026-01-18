# Gitea Adapter

**Version:** 0.1.0  
**Status:** Design Phase  
**Last Updated:** 2026-01-18

---

## Overview

The Gitea adapter handles interactions with Gitea (self-hosted Git service) API and webhooks.

**Supported:**
- Pull request events
- PR diff fetching
- File content retrieval
- Comment posting
- HMAC-SHA256 signature verification

---

## API Details

### Base URL

Self-hosted Gitea instance:
```
https://gitea.yourcompany.com/api/v1
```

### Authentication

**Access Token:**
```http
Authorization: token <gitea-token>
```

**Required Permissions:**
- Repository: Read
- Pull requests: Read & Write

### Rate Limits

Configurable per instance (typically unlimited for self-hosted).

---

## Webhook Format

### Headers
```http
X-Gitea-Event: pull_request
X-Gitea-Signature: abc123def456...
Content-Type: application/json
```

### Payload (Pull Request Opened)
```json
{
  "action": "opened",
  "number": 42,
  "pull_request": {
    "id": 123,
    "number": 42,
    "title": "Add authentication",
    "body": "This PR adds...",
    "state": "open",
    "user": {
      "login": "developer",
      "email": "dev@example.com"
    },
    "head": {
      "ref": "feature/auth",
      "sha": "abc123def456789012345678901234567890abcd"
    },
    "base": {
      "ref": "main",
      "sha": "789012ghi345jkl678901234567890mnop123"
    },
    "created_at": "2026-01-18T14:30:00Z",
    "updated_at": "2026-01-18T14:30:00Z"
  },
  "repository": {
    "id": 456,
    "name": "repo",
    "full_name": "owner/repo",
    "owner": {
      "login": "owner"
    },
    "html_url": "https://gitea.yourcompany.com/owner/repo"
  },
  "sender": {
    "login": "developer"
  }
}
```

---

## Signature Verification

Gitea uses HMAC-SHA256 (similar to GitHub, but without `sha256=` prefix):

```python
import hmac
import hashlib

async def verify_gitea_webhook(request: Request) -> bool:
    signature = request.headers.get("X-Gitea-Signature")
    if not signature:
        return False
    
    secret = os.getenv("GITEA_WEBHOOK_SECRET").encode()
    body = await request.body()
    
    expected = hmac.new(secret, body, hashlib.sha256).hexdigest()
    
    return hmac.compare_digest(signature, expected)
```

**Note:** Unlike GitHub, Gitea doesn't prefix the signature with `sha256=`.

---

## API Endpoints

### 1. Get Pull Request
```python
async def get_pr_info(
    owner: str, 
    repo: str, 
    index: int,
    base_url: str
) -> dict:
    url = f"{base_url}/repos/{owner}/{repo}/pulls/{index}"
```

### 2. Get Pull Request Diff
```python
async def fetch_diff(
    owner: str,
    repo: str, 
    index: int,
    base_url: str
) -> str:
    url = f"{base_url}/repos/{owner}/{repo}/pulls/{index}.diff"
    # Returns unified diff
```

### 3. Get File Contents
```python
async def fetch_file(
    owner: str,
    repo: str,
    filepath: str,
    ref: str,
    base_url: str
) -> str:
    url = f"{base_url}/repos/{owner}/{repo}/raw/{filepath}?ref={ref}"
```

### 4. Post Review Comment
```python
async def post_review(
    owner: str,
    repo: str,
    index: int,
    body: str,
    base_url: str
) -> dict:
    url = f"{base_url}/repos/{owner}/{repo}/pulls/{index}/reviews"
    
    json_data = {
        "body": body,
        "event": "COMMENT"
    }
```

### 5. Post Inline Comment
```python
async def post_inline_comment(
    owner: str,
    repo: str,
    index: int,
    commit_id: str,
    path: str,
    line: int,
    body: str,
    base_url: str
) -> dict:
    # Similar to GitHub API
    url = f"{base_url}/repos/{owner}/{repo}/pulls/{index}/comments"
    
    json_data = {
        "body": body,
        "path": path,
        "position": line  # Or use diff_line
    }
```

---

## Adapter Implementation

```python
class GiteaAdapter:
    def __init__(self, base_url: str):
        self.token = os.getenv("GITEA_API_TOKEN")
        self.webhook_secret = os.getenv("GITEA_WEBHOOK_SECRET")
        self.base_url = base_url  # e.g., https://gitea.company.com/api/v1
    
    async def verify_webhook(self, request: Request) -> bool:
        signature = request.headers.get("X-Gitea-Signature")
        if not signature:
            return False
        
        body = await request.body()
        expected = hmac.new(
            self.webhook_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected)
    
    async def parse_webhook(self, payload: dict) -> WebhookEvent:
        pr = payload["pull_request"]
        repo = payload["repository"]
        
        return WebhookEvent(
            platform="gitea",
            event_type="pull_request",
            action=payload["action"],
            repo_full_name=repo["full_name"],
            pr_number=pr["number"],
            pr_title=pr["title"],
            pr_author=pr["user"]["login"],
            source_branch=pr["head"]["ref"],
            target_branch=pr["base"]["ref"],
            head_sha=pr["head"]["sha"]
        )
    
    async def fetch_diff(self, repo: str, pr_number: int) -> str:
        owner, repo_name = repo.split("/")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo_name}/pulls/{pr_number}.diff",
                headers={"Authorization": f"token {self.token}"}
            )
            response.raise_for_status()
            return response.text
    
    async def post_comment(self, repo: str, pr_number: int, comment: Comment):
        owner, repo_name = repo.split("/")
        
        if comment.path and comment.line:
            # Post inline comment
            await self._post_inline_comment(
                owner, repo_name, pr_number, comment
            )
        else:
            # Post review comment
            await self._post_review(
                owner, repo_name, pr_number, comment.body
            )
```

---

## Gitea vs. GitHub

Gitea's API is **very similar to GitHub's** (intentionally):
- Same endpoint structure
- Same request/response formats
- HMAC signature (minor difference: no `sha256=` prefix)

**Key Differences:**
- Base URL is self-hosted
- Pull request ID is called `index` instead of `number`
- Some advanced features may not be available

---

## References

- [Gitea API Docs](https://docs.gitea.io/en-us/api-usage/)
- [Gitea Webhooks](https://docs.gitea.io/en-us/webhooks/)
- [Pull Requests API](https://docs.gitea.io/en-us/api-usage/#pull-requests)
