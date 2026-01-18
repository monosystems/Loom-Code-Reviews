# GitHub Adapter

**Version:** 0.1.0  
**Status:** Design Phase  
**Last Updated:** 2026-01-18

---

## Overview

The GitHub adapter handles all interactions with GitHub's API and webhook system. It supports:
- Pull request webhook events
- PR diff fetching
- File content retrieval
- Comment posting (summary + inline)
- Webhook signature verification (HMAC-SHA256)

---

## API Details

### Base URL

```
https://api.github.com
```

### Authentication

**Personal Access Token (PAT):**
```http
Authorization: Bearer ghp_...
```

Or legacy format:
```http
Authorization: token ghp_...
```

**Required Scopes:**
- `repo` - Full repository access
- `pull_request` - PR read/write access

### Rate Limits

**Authenticated:**
- 5,000 requests per hour
- Per-user basis
- Resets at top of hour

**Headers:**
```http
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4999
X-RateLimit-Reset: 1705592400
```

**Check Rate Limit:**
```bash
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/rate_limit
```

---

## Webhook Format

### Event Types

**Supported:**
- `pull_request` with actions:
  - `opened`
  - `synchronize` (new commits)
  - `reopened`

**Headers:**
```http
X-GitHub-Event: pull_request
X-GitHub-Delivery: 12345678-1234-1234-1234-123456789012
X-Hub-Signature-256: sha256=abc123...
Content-Type: application/json
User-Agent: GitHub-Hookshot/...
```

### Payload Structure

**Pull Request Opened:**
```json
{
  "action": "opened",
  "number": 42,
  "pull_request": {
    "id": 123456789,
    "node_id": "MDExOlB1bGxSZXF1ZXN0MTIzNDU2Nzg5",
    "number": 42,
    "state": "open",
    "locked": false,
    "title": "Add user authentication",
    "user": {
      "login": "developer",
      "id": 987654,
      "type": "User"
    },
    "body": "This PR adds JWT-based authentication...",
    "created_at": "2026-01-18T14:30:00Z",
    "updated_at": "2026-01-18T14:30:00Z",
    "head": {
      "label": "developer:feature/auth",
      "ref": "feature/auth",
      "sha": "abc123def456789012345678901234567890abcd",
      "user": {
        "login": "developer"
      },
      "repo": {
        "id": 111222333,
        "name": "repo",
        "full_name": "owner/repo"
      }
    },
    "base": {
      "label": "owner:main",
      "ref": "main",
      "sha": "789012ghi345jkl678901234567890mnop123",
      "repo": {
        "id": 111222333,
        "name": "repo",
        "full_name": "owner/repo"
      }
    },
    "draft": false,
    "merged": false,
    "mergeable": true,
    "mergeable_state": "clean",
    "changed_files": 5,
    "additions": 120,
    "deletions": 30,
    "commits": 3,
    "diff_url": "https://github.com/owner/repo/pull/42.diff",
    "patch_url": "https://github.com/owner/repo/pull/42.patch"
  },
  "repository": {
    "id": 111222333,
    "node_id": "MDEwOlJlcG9zaXRvcnkxMTEyMjIzMzM=",
    "name": "repo",
    "full_name": "owner/repo",
    "private": false,
    "owner": {
      "login": "owner",
      "id": 555666
    },
    "html_url": "https://github.com/owner/repo",
    "default_branch": "main"
  },
  "organization": {
    "login": "org",
    "id": 777888
  },
  "sender": {
    "login": "developer",
    "id": 987654
  }
}
```

**Pull Request Synchronized:**
```json
{
  "action": "synchronize",
  "number": 42,
  "before": "old123sha456...",
  "after": "new123sha456...",
  "pull_request": {
    // Same structure as above
    "head": {
      "sha": "new123sha456..."  // Updated SHA
    }
  },
  "repository": {
    // Same as above
  }
}
```

---

## Signature Verification

### Algorithm

GitHub uses **HMAC-SHA256** with the webhook secret.

### Implementation

```python
import hmac
import hashlib
from fastapi import Request, HTTPException

async def verify_github_webhook(request: Request) -> bool:
    """Verify GitHub webhook signature using HMAC-SHA256"""
    
    # Get signature from header
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(401, "Missing signature")
    
    # Get webhook secret from environment
    secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    if not secret:
        raise HTTPException(500, "Webhook secret not configured")
    
    # Read raw body
    body = await request.body()
    
    # Calculate expected signature
    expected = "sha256=" + hmac.new(
        secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    # Compare using constant-time comparison
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(401, "Invalid signature")
    
    return True
```

### Testing Signature

```python
import hmac
import hashlib
import json

secret = "my-webhook-secret"
payload = json.dumps({"action": "opened", "number": 42})

signature = "sha256=" + hmac.new(
    secret.encode(),
    payload.encode(),
    hashlib.sha256
).hexdigest()

print(signature)
# sha256=abc123...
```

---

## API Endpoints

### 1. Get Pull Request

**GET** `/repos/{owner}/{repo}/pulls/{pull_number}`

Fetch PR metadata.

```python
async def get_pr_info(
    owner: str,
    repo: str,
    pr_number: int,
    token: str
) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
        )
        response.raise_for_status()
        return response.json()
```

**Response:**
```json
{
  "id": 123456789,
  "number": 42,
  "state": "open",
  "title": "Add user authentication",
  "user": {"login": "developer"},
  "head": {
    "ref": "feature/auth",
    "sha": "abc123..."
  },
  "base": {
    "ref": "main",
    "sha": "789012..."
  },
  "changed_files": 5,
  "additions": 120,
  "deletions": 30
}
```

---

### 2. Get Pull Request Diff

**GET** `/repos/{owner}/{repo}/pulls/{pull_number}`

Fetch PR diff as plain text.

```python
async def fetch_diff(
    owner: str,
    repo: str,
    pr_number: int,
    token: str
) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.diff"  # Important!
            }
        )
        response.raise_for_status()
        return response.text
```

**Response:**
```diff
diff --git a/src/auth.py b/src/auth.py
index abc123..def456 100644
--- a/src/auth.py
+++ b/src/auth.py
@@ -10,7 +10,12 @@ def login(username, password):
-    query = "SELECT * FROM users WHERE username = '" + username + "'"
+    query = "SELECT * FROM users WHERE username = ?"
+    cursor.execute(query, (username,))
```

---

### 3. Get File Contents

**GET** `/repos/{owner}/{repo}/contents/{path}?ref={sha}`

Fetch file content at specific commit.

```python
async def fetch_file(
    owner: str,
    repo: str,
    path: str,
    ref: str,
    token: str
) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
            params={"ref": ref},
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # Decode base64 content
        import base64
        content = base64.b64decode(data["content"]).decode("utf-8")
        return content
```

**Response:**
```json
{
  "name": "config.yaml",
  "path": ".loom/config.yaml",
  "sha": "abc123...",
  "size": 1234,
  "content": "bW9kZWxzOg0KICBkZWZhdWx0Og0K...",  // base64
  "encoding": "base64"
}
```

---

### 4. Post Issue Comment

**POST** `/repos/{owner}/{repo}/issues/{issue_number}/comments`

Post summary comment on PR (PRs are issues).

```python
async def post_summary_comment(
    owner: str,
    repo: str,
    pr_number: int,
    body: str,
    token: str
) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json"
            },
            json={"body": body}
        )
        response.raise_for_status()
        return response.json()
```

**Request:**
```json
{
  "body": "## 🧵 Loom Code Review\n\n**Summary:** 3 findings\n..."
}
```

**Response:**
```json
{
  "id": 987654321,
  "node_id": "IC_kwDOABCD...",
  "html_url": "https://github.com/owner/repo/issues/42#issuecomment-987654321",
  "body": "## 🧵 Loom Code Review...",
  "created_at": "2026-01-18T14:35:00Z"
}
```

---

### 5. Post Review Comment (Inline)

**POST** `/repos/{owner}/{repo}/pulls/{pull_number}/comments`

Post inline comment on specific line.

```python
async def post_inline_comment(
    owner: str,
    repo: str,
    pr_number: int,
    commit_id: str,
    path: str,
    line: int,
    body: str,
    token: str
) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json"
            },
            json={
                "body": body,
                "commit_id": commit_id,
                "path": path,
                "line": line,
                "side": "RIGHT"  # Comment on new code
            }
        )
        response.raise_for_status()
        return response.json()
```

**Request:**
```json
{
  "body": "🚫 **BLOCKER**: SQL injection vulnerability. Use parameterized queries.",
  "commit_id": "abc123def456789012345678901234567890abcd",
  "path": "src/auth.py",
  "line": 42,
  "side": "RIGHT"
}
```

**Response:**
```json
{
  "id": 111222333,
  "html_url": "https://github.com/owner/repo/pull/42#discussion_r111222333",
  "path": "src/auth.py",
  "line": 42,
  "body": "🚫 **BLOCKER**: SQL injection...",
  "created_at": "2026-01-18T14:36:00Z"
}
```

---

## Adapter Implementation

### Class Structure

```python
from abc import ABC, abstractmethod
from typing import Optional
import httpx
import os

class GitHubAdapter:
    """GitHub platform adapter"""
    
    def __init__(self):
        self.token = os.getenv("GITHUB_API_TOKEN")
        self.webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        self.base_url = "https://api.github.com"
    
    async def verify_webhook(self, request: Request) -> bool:
        """Verify webhook signature"""
        signature = request.headers.get("X-Hub-Signature-256")
        if not signature:
            return False
        
        body = await request.body()
        expected = "sha256=" + hmac.new(
            self.webhook_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected)
    
    async def parse_webhook(self, payload: dict) -> WebhookEvent:
        """Parse webhook payload into standard event"""
        pr = payload["pull_request"]
        repo = payload["repository"]
        
        return WebhookEvent(
            platform="github",
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
        """Fetch PR diff"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{repo}/pulls/{pr_number}",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/vnd.github.diff"
                }
            )
            response.raise_for_status()
            return response.text
    
    async def fetch_file(
        self, 
        repo: str, 
        path: str, 
        ref: str
    ) -> str:
        """Fetch file content"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{repo}/contents/{path}",
                params={"ref": ref},
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/vnd.github+json"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            import base64
            return base64.b64decode(data["content"]).decode("utf-8")
    
    async def post_comment(
        self,
        repo: str,
        pr_number: int,
        comment: Comment
    ):
        """Post comment (summary or inline)"""
        if comment.path and comment.line:
            # Inline comment
            await self._post_inline_comment(
                repo, pr_number, comment
            )
        else:
            # Summary comment
            await self._post_summary_comment(
                repo, pr_number, comment.body
            )
    
    async def _post_summary_comment(
        self,
        repo: str,
        pr_number: int,
        body: str
    ):
        """Post summary comment"""
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.base_url}/repos/{repo}/issues/{pr_number}/comments",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/vnd.github+json",
                    "Content-Type": "application/json"
                },
                json={"body": body}
            )
    
    async def _post_inline_comment(
        self,
        repo: str,
        pr_number: int,
        comment: Comment
    ):
        """Post inline review comment"""
        # Get PR info for commit SHA
        pr_info = await self.get_pr_info(repo, pr_number)
        commit_sha = pr_info["head"]["sha"]
        
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.base_url}/repos/{repo}/pulls/{pr_number}/comments",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/vnd.github+json",
                    "Content-Type": "application/json"
                },
                json={
                    "body": comment.body,
                    "commit_id": commit_sha,
                    "path": comment.path,
                    "line": comment.line,
                    "side": "RIGHT"
                }
            )
    
    async def get_pr_info(self, repo: str, pr_number: int) -> dict:
        """Get PR metadata"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{repo}/pulls/{pr_number}",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/vnd.github+json"
                }
            )
            response.raise_for_status()
            return response.json()
```

---

## Error Handling

### Common Errors

**401 Unauthorized:**
```json
{
  "message": "Bad credentials",
  "documentation_url": "https://docs.github.com/rest"
}
```

**403 Forbidden (Rate Limit):**
```json
{
  "message": "API rate limit exceeded",
  "documentation_url": "https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting"
}
```

**404 Not Found:**
```json
{
  "message": "Not Found",
  "documentation_url": "https://docs.github.com/rest"
}
```

**422 Unprocessable Entity:**
```json
{
  "message": "Validation Failed",
  "errors": [
    {
      "resource": "PullRequestReviewComment",
      "code": "invalid",
      "field": "line"
    }
  ]
}
```

### Retry Strategy

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def fetch_with_retry(url: str, headers: dict) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        # Retry on rate limit or server errors
        if response.status_code in [429, 500, 502, 503, 504]:
            response.raise_for_status()
        
        return response
```

---

## Testing

### Mock Webhook

```python
import pytest
from fastapi.testclient import TestClient

def test_github_webhook():
    payload = {
        "action": "opened",
        "number": 42,
        "pull_request": {
            "id": 123,
            "number": 42,
            "title": "Test PR",
            "user": {"login": "test"},
            "head": {"ref": "test", "sha": "abc123"},
            "base": {"ref": "main"}
        },
        "repository": {
            "id": 456,
            "full_name": "test/repo"
        }
    }
    
    signature = generate_signature(payload, "test-secret")
    
    response = client.post(
        "/webhooks/github",
        json=payload,
        headers={
            "X-GitHub-Event": "pull_request",
            "X-Hub-Signature-256": signature
        }
    )
    
    assert response.status_code == 200
    assert response.json()["success"] == True
```

### Integration Tests

```python
@pytest.mark.integration
async def test_github_adapter_real_api():
    """Test against real GitHub API (requires token)"""
    adapter = GitHubAdapter()
    
    # Fetch PR info
    pr_info = await adapter.get_pr_info("owner/repo", 1)
    assert pr_info["number"] == 1
    
    # Fetch diff
    diff = await adapter.fetch_diff("owner/repo", 1)
    assert diff.startswith("diff --git")
```

---

## References

- [GitHub REST API Docs](https://docs.github.com/rest)
- [GitHub Webhooks](https://docs.github.com/webhooks)
- [Webhook Signature Verification](https://docs.github.com/webhooks/using-webhooks/validating-webhook-deliveries)
- [Rate Limiting](https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting)
- [Adapter Pattern](../architecture/adapter-pattern.md)
