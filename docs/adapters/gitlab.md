# GitLab Adapter

**Version:** 0.1.0  
**Status:** Design Phase  
**Last Updated:** 2026-01-18

---

## Overview

The GitLab adapter handles all interactions with GitLab's API and webhook system. It supports:
- Merge request webhook events
- MR diff fetching
- File content retrieval
- Comment posting (notes + discussions)
- Webhook token verification

---

## API Details

### Base URLs

**GitLab.com:**
```
https://gitlab.com/api/v4
```

**Self-Hosted:**
```
https://gitlab.yourcompany.com/api/v4
```

### Authentication

**Personal Access Token (PAT):**
```http
PRIVATE-TOKEN: glpat-...
```

Or Bearer token:
```http
Authorization: Bearer glpat-...
```

**Required Scopes:**
- `api` - Full API access
- Or: `read_repository` + `write_repository`

### Rate Limits

**GitLab.com (Free):**
- 2,000 requests per minute
- Per-user basis

**GitLab.com (Premium/Ultimate):**
- 10,000 requests per minute

**Self-Hosted:**
- Configurable (default: unlimited)

**Headers:**
```http
RateLimit-Limit: 2000
RateLimit-Remaining: 1999
RateLimit-Reset: 1705592460
```

---

## Webhook Format

### Event Types

**Supported:**
- `Merge Request Hook` with actions:
  - `open`
  - `update`
  - `reopen`

**Headers:**
```http
X-Gitlab-Event: Merge Request Hook
X-Gitlab-Token: your-secret-token
Content-Type: application/json
User-Agent: GitLab/...
```

### Payload Structure

**Merge Request Opened:**
```json
{
  "object_kind": "merge_request",
  "event_type": "merge_request",
  "user": {
    "id": 123,
    "name": "Developer",
    "username": "developer",
    "email": "dev@example.com"
  },
  "project": {
    "id": 456,
    "name": "repo",
    "path_with_namespace": "owner/repo",
    "web_url": "https://gitlab.com/owner/repo",
    "namespace": "owner",
    "default_branch": "main"
  },
  "object_attributes": {
    "id": 789,
    "iid": 42,
    "target_branch": "main",
    "source_branch": "feature/auth",
    "source_project_id": 456,
    "title": "Add user authentication",
    "description": "This MR adds JWT-based authentication...",
    "state": "opened",
    "merge_status": "can_be_merged",
    "draft": false,
    "work_in_progress": false,
    "action": "open",
    "author_id": 123,
    "created_at": "2026-01-18 14:30:00 UTC",
    "updated_at": "2026-01-18 14:30:00 UTC",
    "last_commit": {
      "id": "abc123def456789012345678901234567890abcd",
      "message": "Add JWT authentication",
      "timestamp": "2026-01-18T14:29:00+00:00",
      "author": {
        "name": "Developer",
        "email": "dev@example.com"
      }
    },
    "url": "https://gitlab.com/owner/repo/-/merge_requests/42",
    "source": {
      "name": "repo",
      "path_with_namespace": "owner/repo",
      "web_url": "https://gitlab.com/owner/repo",
      "default_branch": "feature/auth"
    },
    "target": {
      "name": "repo",
      "path_with_namespace": "owner/repo",
      "web_url": "https://gitlab.com/owner/repo",
      "default_branch": "main"
    }
  },
  "labels": [],
  "changes": {
    "total_count": 5,
    "added_lines": 120,
    "removed_lines": 30
  },
  "repository": {
    "name": "repo",
    "url": "git@gitlab.com:owner/repo.git",
    "homepage": "https://gitlab.com/owner/repo"
  }
}
```

**Merge Request Updated:**
```json
{
  "object_kind": "merge_request",
  "object_attributes": {
    "action": "update",
    "oldrev": "old123sha456...",
    // Same structure as above
  }
}
```

---

## Signature Verification

### Algorithm

GitLab uses **simple token comparison** (not HMAC).

### Implementation

```python
from fastapi import Request, HTTPException
import os

async def verify_gitlab_webhook(request: Request) -> bool:
    """Verify GitLab webhook token"""
    
    # Get token from header
    token = request.headers.get("X-Gitlab-Token")
    if not token:
        raise HTTPException(401, "Missing webhook token")
    
    # Get expected token from environment
    expected = os.getenv("GITLAB_WEBHOOK_SECRET")
    if not expected:
        raise HTTPException(500, "Webhook secret not configured")
    
    # Simple comparison (not HMAC)
    if token != expected:
        raise HTTPException(401, "Invalid webhook token")
    
    return True
```

**Note:** GitLab doesn't use HMAC signatures like GitHub. The token is sent as-is in the header.

---

## API Endpoints

### 1. Get Merge Request

**GET** `/projects/{id}/merge_requests/{merge_request_iid}`

Fetch MR metadata.

```python
async def get_mr_info(
    project_id: int,
    mr_iid: int,
    token: str,
    base_url: str = "https://gitlab.com/api/v4"
) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/projects/{project_id}/merge_requests/{mr_iid}",
            headers={
                "PRIVATE-TOKEN": token
            }
        )
        response.raise_for_status()
        return response.json()
```

**Response:**
```json
{
  "id": 789,
  "iid": 42,
  "project_id": 456,
  "title": "Add user authentication",
  "description": "This MR adds...",
  "state": "opened",
  "merged_by": null,
  "merge_user": null,
  "merged_at": null,
  "created_at": "2026-01-18T14:30:00.000Z",
  "updated_at": "2026-01-18T14:30:00.000Z",
  "target_branch": "main",
  "source_branch": "feature/auth",
  "author": {
    "id": 123,
    "username": "developer",
    "name": "Developer"
  },
  "sha": "abc123def456789012345678901234567890abcd",
  "web_url": "https://gitlab.com/owner/repo/-/merge_requests/42",
  "changes_count": "5",
  "user_notes_count": 0,
  "diff_refs": {
    "base_sha": "789012...",
    "head_sha": "abc123...",
    "start_sha": "789012..."
  }
}
```

---

### 2. Get Merge Request Changes (Diff)

**GET** `/projects/{id}/merge_requests/{merge_request_iid}/changes`

Fetch MR changes (diff).

```python
async def fetch_diff(
    project_id: int,
    mr_iid: int,
    token: str,
    base_url: str = "https://gitlab.com/api/v4"
) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/projects/{project_id}/merge_requests/{mr_iid}/changes",
            headers={
                "PRIVATE-TOKEN": token
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # Construct unified diff from changes
        diff_parts = []
        for change in data.get("changes", []):
            diff_parts.append(change["diff"])
        
        return "\n".join(diff_parts)
```

**Response:**
```json
{
  "id": 789,
  "iid": 42,
  "changes": [
    {
      "old_path": "src/auth.py",
      "new_path": "src/auth.py",
      "a_mode": "100644",
      "b_mode": "100644",
      "new_file": false,
      "renamed_file": false,
      "deleted_file": false,
      "diff": "@@ -10,7 +10,12 @@ def login(username, password):\n-    query = \"SELECT * FROM users WHERE username = '\" + username + \"'\"\n+    query = \"SELECT * FROM users WHERE username = ?\"\n+    cursor.execute(query, (username,))"
    }
  ]
}
```

---

### 3. Get File Contents

**GET** `/projects/{id}/repository/files/{file_path}/raw?ref={ref}`

Fetch file content at specific ref.

```python
import urllib.parse

async def fetch_file(
    project_id: int,
    file_path: str,
    ref: str,
    token: str,
    base_url: str = "https://gitlab.com/api/v4"
) -> str:
    # URL encode the file path
    encoded_path = urllib.parse.quote(file_path, safe='')
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{base_url}/projects/{project_id}/repository/files/{encoded_path}/raw",
            params={"ref": ref},
            headers={
                "PRIVATE-TOKEN": token
            }
        )
        response.raise_for_status()
        return response.text
```

**Note:** File path must be URL-encoded. E.g., `.loom/config.yaml` → `.loom%2Fconfig.yaml`

---

### 4. Post Note (Summary Comment)

**POST** `/projects/{id}/merge_requests/{merge_request_iid}/notes`

Post general comment on MR.

```python
async def post_note(
    project_id: int,
    mr_iid: int,
    body: str,
    token: str,
    base_url: str = "https://gitlab.com/api/v4"
) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/projects/{project_id}/merge_requests/{mr_iid}/notes",
            headers={
                "PRIVATE-TOKEN": token,
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
  "id": 111222333,
  "type": "DiscussionNote",
  "body": "## 🧵 Loom Code Review...",
  "author": {
    "id": 999,
    "username": "loom-bot"
  },
  "created_at": "2026-01-18T14:35:00.000Z",
  "system": false,
  "noteable_id": 789,
  "noteable_type": "MergeRequest"
}
```

---

### 5. Post Discussion (Inline Comment)

**POST** `/projects/{id}/merge_requests/{merge_request_iid}/discussions`

Post inline comment on specific line.

```python
async def post_inline_comment(
    project_id: int,
    mr_iid: int,
    commit_sha: str,
    old_path: str,
    new_path: str,
    old_line: Optional[int],
    new_line: int,
    body: str,
    token: str,
    base_url: str = "https://gitlab.com/api/v4"
) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/projects/{project_id}/merge_requests/{mr_iid}/discussions",
            headers={
                "PRIVATE-TOKEN": token,
                "Content-Type": "application/json"
            },
            json={
                "body": body,
                "position": {
                    "base_sha": commit_sha,
                    "start_sha": commit_sha,
                    "head_sha": commit_sha,
                    "position_type": "text",
                    "old_path": old_path,
                    "new_path": new_path,
                    "old_line": old_line,
                    "new_line": new_line
                }
            }
        )
        response.raise_for_status()
        return response.json()
```

**Request:**
```json
{
  "body": "🚫 **BLOCKER**: SQL injection vulnerability",
  "position": {
    "base_sha": "789012...",
    "start_sha": "789012...",
    "head_sha": "abc123...",
    "position_type": "text",
    "old_path": "src/auth.py",
    "new_path": "src/auth.py",
    "old_line": null,
    "new_line": 42
  }
}
```

---

## Adapter Implementation

### Class Structure

```python
from typing import Optional
import httpx
import os
import urllib.parse

class GitLabAdapter:
    """GitLab platform adapter"""
    
    def __init__(self, base_url: str = "https://gitlab.com/api/v4"):
        self.token = os.getenv("GITLAB_API_TOKEN")
        self.webhook_secret = os.getenv("GITLAB_WEBHOOK_SECRET")
        self.base_url = base_url
    
    async def verify_webhook(self, request: Request) -> bool:
        """Verify webhook token"""
        token = request.headers.get("X-Gitlab-Token")
        return token == self.webhook_secret
    
    async def parse_webhook(self, payload: dict) -> WebhookEvent:
        """Parse webhook payload"""
        obj_attrs = payload["object_attributes"]
        project = payload["project"]
        user = payload["user"]
        
        return WebhookEvent(
            platform="gitlab",
            event_type="merge_request",
            action=obj_attrs["action"],
            repo_full_name=project["path_with_namespace"],
            pr_number=obj_attrs["iid"],
            pr_title=obj_attrs["title"],
            pr_author=user["username"],
            source_branch=obj_attrs["source_branch"],
            target_branch=obj_attrs["target_branch"],
            head_sha=obj_attrs["last_commit"]["id"]
        )
    
    async def fetch_diff(self, repo: str, mr_iid: int) -> str:
        """Fetch MR diff"""
        # Get project ID from path
        project_id = urllib.parse.quote(repo, safe='')
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/projects/{project_id}/merge_requests/{mr_iid}/changes",
                headers={"PRIVATE-TOKEN": self.token}
            )
            response.raise_for_status()
            data = response.json()
            
            # Combine all diffs
            diff_parts = [change["diff"] for change in data.get("changes", [])]
            return "\n".join(diff_parts)
    
    async def fetch_file(
        self, 
        repo: str, 
        path: str, 
        ref: str
    ) -> str:
        """Fetch file content"""
        project_id = urllib.parse.quote(repo, safe='')
        file_path = urllib.parse.quote(path, safe='')
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/projects/{project_id}/repository/files/{file_path}/raw",
                params={"ref": ref},
                headers={"PRIVATE-TOKEN": self.token}
            )
            response.raise_for_status()
            return response.text
    
    async def post_comment(
        self,
        repo: str,
        pr_number: int,
        comment: Comment
    ):
        """Post comment"""
        project_id = urllib.parse.quote(repo, safe='')
        
        if comment.path and comment.line:
            await self._post_inline_comment(
                project_id, pr_number, comment
            )
        else:
            await self._post_note(
                project_id, pr_number, comment.body
            )
    
    async def _post_note(
        self,
        project_id: str,
        mr_iid: int,
        body: str
    ):
        """Post general note"""
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.base_url}/projects/{project_id}/merge_requests/{mr_iid}/notes",
                headers={
                    "PRIVATE-TOKEN": self.token,
                    "Content-Type": "application/json"
                },
                json={"body": body}
            )
    
    async def _post_inline_comment(
        self,
        project_id: str,
        mr_iid: int,
        comment: Comment
    ):
        """Post inline discussion"""
        # Get MR info for commit SHAs
        mr_info = await self.get_mr_info(project_id, mr_iid)
        
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.base_url}/projects/{project_id}/merge_requests/{mr_iid}/discussions",
                headers={
                    "PRIVATE-TOKEN": self.token,
                    "Content-Type": "application/json"
                },
                json={
                    "body": comment.body,
                    "position": {
                        "base_sha": mr_info["diff_refs"]["base_sha"],
                        "start_sha": mr_info["diff_refs"]["start_sha"],
                        "head_sha": mr_info["diff_refs"]["head_sha"],
                        "position_type": "text",
                        "old_path": comment.path,
                        "new_path": comment.path,
                        "old_line": None,
                        "new_line": comment.line
                    }
                }
            )
```

---

## Error Handling

### Common Errors

**401 Unauthorized:**
```json
{
  "message": "401 Unauthorized"
}
```

**404 Not Found:**
```json
{
  "message": "404 Project Not Found"
}
```

**429 Rate Limited:**
```json
{
  "message": "429 Too Many Requests"
}
```

---

## Testing

### Mock Webhook

```python
def test_gitlab_webhook():
    payload = {
        "object_kind": "merge_request",
        "object_attributes": {
            "iid": 42,
            "title": "Test MR",
            "action": "open",
            "source_branch": "test",
            "target_branch": "main",
            "last_commit": {"id": "abc123"}
        },
        "project": {
            "id": 456,
            "path_with_namespace": "test/repo"
        },
        "user": {"username": "test"}
    }
    
    response = client.post(
        "/webhooks/gitlab",
        json=payload,
        headers={
            "X-Gitlab-Event": "Merge Request Hook",
            "X-Gitlab-Token": "test-secret"
        }
    )
    
    assert response.status_code == 200
```

---

## References

- [GitLab API Docs](https://docs.gitlab.com/ee/api/)
- [GitLab Webhooks](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html)
- [Merge Requests API](https://docs.gitlab.com/ee/api/merge_requests.html)
- [Discussions API](https://docs.gitlab.com/ee/api/discussions.html)
