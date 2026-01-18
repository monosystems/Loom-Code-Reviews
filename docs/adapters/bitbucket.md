# Bitbucket Adapter

**Version:** 0.1.0  
**Status:** Design Phase  
**Last Updated:** 2026-01-18

---

## Overview

The Bitbucket adapter handles interactions with Bitbucket Cloud's API and webhooks.

**Supported:**
- Pull request events (created, updated)
- PR diff fetching
- File content retrieval
- Comment posting
- UUID-based webhook verification

---

## API Details

### Base URL
```
https://api.bitbucket.org/2.0
```

### Authentication

**App Password:**
```http
Authorization: Basic <base64(username:app_password)>
```

**Required Permissions:**
- Repository: Read
- Pull requests: Read & Write

### Rate Limits
- 1,000 requests per hour
- Per-user basis

---

## Webhook Format

### Headers
```http
X-Event-Key: pullrequest:created
X-Hook-UUID: {12345678-1234-1234-1234-123456789012}
Content-Type: application/json
```

### Payload (Pull Request Created)
```json
{
  "pullrequest": {
    "id": 42,
    "title": "Add authentication",
    "state": "OPEN",
    "author": {
      "username": "developer",
      "display_name": "Developer"
    },
    "source": {
      "branch": {"name": "feature/auth"},
      "commit": {"hash": "abc123def456"}
    },
    "destination": {
      "branch": {"name": "main"}
    },
    "links": {
      "diff": {
        "href": "https://api.bitbucket.org/2.0/repositories/owner/repo/pullrequests/42/diff"
      },
      "comments": {
        "href": "https://api.bitbucket.org/2.0/repositories/owner/repo/pullrequests/42/comments"
      }
    }
  },
  "repository": {
    "name": "repo",
    "full_name": "owner/repo",
    "uuid": "{12345678-1234-1234-1234-123456789012}"
  }
}
```

---

## Signature Verification

Bitbucket doesn't use HMAC. Instead, verify the webhook UUID:

```python
async def verify_bitbucket_webhook(request: Request) -> bool:
    webhook_uuid = request.headers.get("X-Hook-UUID")
    
    # Check if UUID is in registered webhooks
    registered_uuids = os.getenv("BITBUCKET_WEBHOOK_UUIDS", "").split(",")
    return webhook_uuid in registered_uuids
```

---

## API Endpoints

### 1. Get Pull Request
```python
async def get_pr_info(workspace: str, repo: str, pr_id: int) -> dict:
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{pr_id}"
    # ... auth headers
```

**Response:**
```json
{
  "id": 42,
  "title": "Add authentication",
  "state": "OPEN",
  "author": {"username": "developer"},
  "source": {
    "branch": {"name": "feature/auth"},
    "commit": {"hash": "abc123"}
  },
  "destination": {
    "branch": {"name": "main"}
  }
}
```

### 2. Get Pull Request Diff
```python
async def fetch_diff(workspace: str, repo: str, pr_id: int) -> str:
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{pr_id}/diff"
    # Returns unified diff format
```

### 3. Get File Contents
```python
async def fetch_file(
    workspace: str, 
    repo: str, 
    path: str, 
    commit: str
) -> str:
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/src/{commit}/{path}"
```

### 4. Post Comment
```python
async def post_comment(
    workspace: str,
    repo: str,
    pr_id: int,
    content: str
) -> dict:
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{pr_id}/comments"
    
    json_data = {
        "content": {
            "raw": content
        }
    }
```

**Note:** Bitbucket doesn't support inline comments via API (only via UI).

---

## Adapter Implementation

```python
import base64

class BitbucketAdapter:
    def __init__(self):
        self.username = os.getenv("BITBUCKET_USERNAME")
        self.app_password = os.getenv("BITBUCKET_APP_PASSWORD")
        self.webhook_uuids = os.getenv("BITBUCKET_WEBHOOK_UUIDS", "").split(",")
        
        # Create Basic Auth header
        credentials = f"{self.username}:{self.app_password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        self.auth_header = f"Basic {encoded}"
    
    async def verify_webhook(self, request: Request) -> bool:
        webhook_uuid = request.headers.get("X-Hook-UUID")
        return webhook_uuid in self.webhook_uuids
    
    async def parse_webhook(self, payload: dict) -> WebhookEvent:
        pr = payload["pullrequest"]
        repo = payload["repository"]
        
        return WebhookEvent(
            platform="bitbucket",
            event_type="pull_request",
            action="opened" if "created" in request.headers.get("X-Event-Key") else "updated",
            repo_full_name=repo["full_name"],
            pr_number=pr["id"],
            pr_title=pr["title"],
            pr_author=pr["author"]["username"],
            source_branch=pr["source"]["branch"]["name"],
            target_branch=pr["destination"]["branch"]["name"],
            head_sha=pr["source"]["commit"]["hash"]
        )
    
    async def fetch_diff(self, repo: str, pr_id: int) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.bitbucket.org/2.0/repositories/{repo}/pullrequests/{pr_id}/diff",
                headers={"Authorization": self.auth_header}
            )
            response.raise_for_status()
            return response.text
    
    async def post_comment(self, repo: str, pr_id: int, comment: Comment):
        # Bitbucket doesn't support inline comments via API
        # Post as general comment only
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.bitbucket.org/2.0/repositories/{repo}/pullrequests/{pr_id}/comments",
                headers={
                    "Authorization": self.auth_header,
                    "Content-Type": "application/json"
                },
                json={
                    "content": {
                        "raw": comment.body
                    }
                }
            )
```

---

## Limitations

⚠️ **No Inline Comments:** Bitbucket Cloud API doesn't support posting inline/line-specific comments programmatically. All comments are general PR comments.

**Workaround:** Include file path and line number in comment body:
```
📁 src/auth.py:42
🚫 BLOCKER: SQL injection vulnerability...
```

---

## References

- [Bitbucket API Docs](https://developer.atlassian.com/cloud/bitbucket/rest/)
- [Bitbucket Webhooks](https://support.atlassian.com/bitbucket-cloud/docs/manage-webhooks/)
- [Pull Requests API](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-pullrequests/)
