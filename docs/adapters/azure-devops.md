# Azure DevOps Adapter

**Version:** 0.1.0  
**Status:** Design Phase  
**Last Updated:** 2026-01-18

---

## Overview

The Azure DevOps adapter handles interactions with Azure DevOps Services API and service hooks.

**Supported:**
- Pull request events
- PR diff/iterations fetching
- File content retrieval  
- Comment posting via threads
- Basic Auth verification

---

## API Details

### Base URL

```
https://dev.azure.com/{organization}
```

### Authentication

**Personal Access Token (PAT):**
```http
Authorization: Basic <base64(:PAT)>
```

**Note:** Username is empty, only PAT in Basic Auth.

**Required Scopes:**
- Code: Read & Write
- Pull Request Threads: Read & Write

### Rate Limits

Complex rate limiting based on:
- TSTUs (Team Services Time Units)
- Varies by resource type
- Typically 200 requests per user per organization

---

## Webhook Format (Service Hooks)

### Headers
```http
Content-Type: application/json
Authorization: Basic <credentials>
```

### Payload (Pull Request Created)
```json
{
  "subscriptionId": "12345678-1234-1234-1234-123456789012",
  "notificationId": 1,
  "id": "abcd1234-ab12-cd34-ef56-abcdef123456",
  "eventType": "git.pullrequest.created",
  "publisherId": "tfs",
  "message": {
    "text": "Developer created pull request 42 in repo",
    "html": "...",
    "markdown": "..."
  },
  "detailedMessage": {
    "text": "Developer created pull request 42"
  },
  "resource": {
    "repository": {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "name": "repo",
      "url": "https://dev.azure.com/org/_apis/git/repositories/a1b2c3d4...",
      "project": {
        "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
        "name": "project",
        "url": "https://dev.azure.com/org/_apis/projects/b2c3d4e5..."
      }
    },
    "pullRequestId": 42,
    "status": "active",
    "createdBy": {
      "displayName": "Developer",
      "uniqueName": "developer@company.com",
      "id": "c3d4e5f6-a7b8-9012-cdef-123456789012"
    },
    "creationDate": "2026-01-18T14:30:00Z",
    "title": "Add user authentication",
    "description": "This PR adds...",
    "sourceRefName": "refs/heads/feature/auth",
    "targetRefName": "refs/heads/main",
    "mergeStatus": "succeeded",
    "lastMergeSourceCommit": {
      "commitId": "abc123def456789012345678901234567890abcd",
      "url": "https://dev.azure.com/org/_apis/git/repositories/.../commits/abc123..."
    },
    "lastMergeTargetCommit": {
      "commitId": "789012ghi345jkl678901234567890mnop123"
    },
    "url": "https://dev.azure.com/org/_apis/git/repositories/.../pullRequests/42"
  },
  "resourceVersion": "1.0",
  "resourceContainers": {
    "collection": {
      "id": "d4e5f6a7-b8c9-0123-def0-123456789012"
    },
    "account": {
      "id": "e5f6a7b8-c9d0-1234-ef01-234567890123"
    },
    "project": {
      "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901"
    }
  },
  "createdDate": "2026-01-18T14:30:00Z"
}
```

---

## Signature Verification

Azure DevOps uses **Basic Authentication** for service hooks:

```python
import base64

async def verify_azure_webhook(request: Request) -> bool:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Basic "):
        return False
    
    # Decode credentials
    credentials = base64.b64decode(auth_header[6:]).decode()
    
    # Format: username:password (username can be empty)
    if ":" not in credentials:
        return False
    
    _, password = credentials.split(":", 1)
    
    # Verify against stored secret
    expected = os.getenv("AZURE_DEVOPS_WEBHOOK_SECRET")
    return password == expected
```

---

## API Endpoints

### 1. Get Pull Request

**GET** `/{organization}/{project}/_apis/git/repositories/{repositoryId}/pullRequests/{pullRequestId}?api-version=7.0`

```python
async def get_pr_info(
    organization: str,
    project: str,
    repository_id: str,
    pr_id: int,
    pat: str
) -> dict:
    # Create Basic Auth (empty username, PAT as password)
    auth = base64.b64encode(f":{pat}".encode()).decode()
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repository_id}/pullRequests/{pr_id}",
            params={"api-version": "7.0"},
            headers={"Authorization": f"Basic {auth}"}
        )
        response.raise_for_status()
        return response.json()
```

**Response:**
```json
{
  "pullRequestId": 42,
  "status": "active",
  "title": "Add authentication",
  "description": "This PR adds...",
  "createdBy": {
    "displayName": "Developer"
  },
  "sourceRefName": "refs/heads/feature/auth",
  "targetRefName": "refs/heads/main",
  "lastMergeSourceCommit": {
    "commitId": "abc123..."
  }
}
```

---

### 2. Get Pull Request Iterations (Changes)

**GET** `/{organization}/{project}/_apis/git/repositories/{repositoryId}/pullRequests/{pullRequestId}/iterations?api-version=7.0`

```python
async def get_pr_changes(
    organization: str,
    project: str,
    repository_id: str,
    pr_id: int,
    iteration_id: int,
    pat: str
) -> dict:
    auth = base64.b64encode(f":{pat}".encode()).decode()
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repository_id}/pullRequests/{pr_id}/iterations/{iteration_id}/changes",
            params={"api-version": "7.0"},
            headers={"Authorization": f"Basic {auth}"}
        )
        response.raise_for_status()
        return response.json()
```

**Note:** Azure DevOps uses "iterations" instead of simple diffs. Each push creates a new iteration.

---

### 3. Get File Contents

**GET** `/{organization}/{project}/_apis/git/repositories/{repositoryId}/items?path={path}&version={commitId}&api-version=7.0`

```python
async def fetch_file(
    organization: str,
    project: str,
    repository_id: str,
    path: str,
    commit_id: str,
    pat: str
) -> str:
    auth = base64.b64encode(f":{pat}".encode()).decode()
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repository_id}/items",
            params={
                "path": path,
                "version": commit_id,
                "api-version": "7.0"
            },
            headers={"Authorization": f"Basic {auth}"}
        )
        response.raise_for_status()
        return response.text
```

---

### 4. Post Thread (Comment)

**POST** `/{organization}/{project}/_apis/git/repositories/{repositoryId}/pullRequests/{pullRequestId}/threads?api-version=7.0`

```python
async def post_thread(
    organization: str,
    project: str,
    repository_id: str,
    pr_id: int,
    content: str,
    pat: str
) -> dict:
    auth = base64.b64encode(f":{pat}".encode()).decode()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repository_id}/pullRequests/{pr_id}/threads",
            params={"api-version": "7.0"},
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/json"
            },
            json={
                "comments": [
                    {
                        "parentCommentId": 0,
                        "content": content,
                        "commentType": 1  # Text
                    }
                ],
                "status": 1  # Active
            }
        )
        response.raise_for_status()
        return response.json()
```

**For inline comments**, add thread context:
```json
{
  "comments": [
    {
      "parentCommentId": 0,
      "content": "Comment text",
      "commentType": 1
    }
  ],
  "status": 1,
  "threadContext": {
    "filePath": "/src/auth.py",
    "rightFileStart": {
      "line": 42,
      "offset": 1
    },
    "rightFileEnd": {
      "line": 42,
      "offset": 100
    }
  }
}
```

---

## Adapter Implementation

```python
class AzureDevOpsAdapter:
    def __init__(self, organization: str):
        self.pat = os.getenv("AZURE_DEVOPS_PAT")
        self.webhook_secret = os.getenv("AZURE_DEVOPS_WEBHOOK_SECRET")
        self.organization = organization
        self.base_url = f"https://dev.azure.com/{organization}"
        
        # Create auth header
        auth = base64.b64encode(f":{self.pat}".encode()).decode()
        self.auth_header = f"Basic {auth}"
    
    async def verify_webhook(self, request: Request) -> bool:
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Basic "):
            return False
        
        credentials = base64.b64decode(auth[6:]).decode()
        _, password = credentials.split(":", 1)
        
        return password == self.webhook_secret
    
    async def parse_webhook(self, payload: dict) -> WebhookEvent:
        resource = payload["resource"]
        repo = resource["repository"]
        
        # Extract branch names (remove refs/heads/ prefix)
        source_branch = resource["sourceRefName"].replace("refs/heads/", "")
        target_branch = resource["targetRefName"].replace("refs/heads/", "")
        
        return WebhookEvent(
            platform="azure-devops",
            event_type="pull_request",
            action="opened" if "created" in payload["eventType"] else "updated",
            repo_full_name=f"{repo['project']['name']}/{repo['name']}",
            pr_number=resource["pullRequestId"],
            pr_title=resource["title"],
            pr_author=resource["createdBy"]["uniqueName"],
            source_branch=source_branch,
            target_branch=target_branch,
            head_sha=resource["lastMergeSourceCommit"]["commitId"]
        )
    
    async def fetch_diff(self, repo: str, pr_id: int) -> str:
        # Azure DevOps doesn't provide simple diff endpoint
        # Need to fetch iterations and construct diff from changes
        # This is more complex than other platforms
        
        # Get latest iteration
        # Get changes in iteration
        # Construct unified diff format
        # ...implementation
```

---

## Complexity Notes

⚠️ **Azure DevOps is more complex than other platforms:**

1. **No simple diff endpoint** - Must fetch iterations and changes
2. **Complex URL structure** - Requires organization, project, repository ID
3. **Thread-based comments** - Different model than other platforms
4. **Rate limiting** - Based on TSTUs, not simple requests/hour

**Recommendation:** Implement Azure DevOps support after other platforms are stable.

---

## References

- [Azure DevOps REST API](https://learn.microsoft.com/en-us/rest/api/azure/devops/)
- [Git Pull Requests API](https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pull-requests/)
- [Service Hooks](https://learn.microsoft.com/en-us/azure/devops/service-hooks/)
- [Authentication](https://learn.microsoft.com/en-us/azure/devops/integrate/get-started/authentication/authentication-guidance)
