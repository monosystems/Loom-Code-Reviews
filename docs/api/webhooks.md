# Webhook API

**Version:** 0.1.0  
**Status:** Design Phase  
**Last Updated:** 2026-01-18

---

## Overview

Loom receives webhooks from git platforms (GitHub, GitLab, Bitbucket, Gitea, Azure DevOps) and triggers code reviews. Each platform has a dedicated endpoint that handles platform-specific webhook formats and signature verification.

---

## Base URL

```
https://your-loom-instance.com
```

For local development:
```
http://localhost:8000
```

---

## Endpoints

### Health Check

**GET** `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-01-18T14:30:00Z"
}
```

**Status Codes:**
- `200` - Service is healthy
- `503` - Service unavailable

---

### GitHub Webhook

**POST** `/webhooks/github`

Receives webhook events from GitHub.

#### Headers

```http
X-GitHub-Event: pull_request
X-GitHub-Delivery: 12345678-1234-1234-1234-123456789012
X-Hub-Signature-256: sha256=abc123...
Content-Type: application/json
```

**Required Headers:**
- `X-GitHub-Event` - Event type (e.g., `pull_request`)
- `X-Hub-Signature-256` - HMAC signature for verification
- `Content-Type` - Must be `application/json`

#### Request Body

**Pull Request Opened:**
```json
{
  "action": "opened",
  "number": 42,
  "pull_request": {
    "id": 123456789,
    "number": 42,
    "state": "open",
    "title": "Add user authentication",
    "user": {
      "login": "developer"
    },
    "head": {
      "ref": "feature/auth",
      "sha": "abc123def456789012345678901234567890abcd"
    },
    "base": {
      "ref": "main",
      "sha": "789012ghi345jkl678901234567890mnop123"
    },
    "diff_url": "https://github.com/owner/repo/pull/42.diff",
    "changed_files": 5,
    "additions": 120,
    "deletions": 30
  },
  "repository": {
    "id": 987654321,
    "name": "repo",
    "full_name": "owner/repo",
    "owner": {
      "login": "owner"
    }
  }
}
```

**Pull Request Synchronized (new commits):**
```json
{
  "action": "synchronize",
  "number": 42,
  "pull_request": {
    "id": 123456789,
    "number": 42,
    "head": {
      "sha": "new123sha456..."
    }
    // ... same structure as above
  },
  "repository": {
    // ... same as above
  }
}
```

#### Response

**Success:**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Review job queued"
}
```

**Ignored (repo not enabled):**
```json
{
  "success": false,
  "reason": "repo_not_enabled",
  "message": "Repository is not enabled for reviews"
}
```

**Ignored (triggers not matched):**
```json
{
  "success": false,
  "reason": "triggers_not_matched",
  "message": "PR does not match trigger rules"
}
```

#### Status Codes
- `200` - Webhook received (success or ignored)
- `401` - Invalid signature
- `400` - Invalid payload
- `500` - Internal server error

#### Signature Verification

GitHub uses HMAC-SHA256:

```python
import hmac
import hashlib

secret = os.getenv("GITHUB_WEBHOOK_SECRET").encode()
signature = request.headers.get("X-Hub-Signature-256")
body = await request.body()

expected = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()

if not hmac.compare_digest(signature, expected):
    raise HTTPException(401, "Invalid signature")
```

---

### GitLab Webhook

**POST** `/webhooks/gitlab`

Receives webhook events from GitLab.

#### Headers

```http
X-Gitlab-Event: Merge Request Hook
X-Gitlab-Token: your-secret-token
Content-Type: application/json
```

**Required Headers:**
- `X-Gitlab-Event` - Event type
- `X-Gitlab-Token` - Secret token for verification

#### Request Body

**Merge Request Opened:**
```json
{
  "object_kind": "merge_request",
  "event_type": "merge_request",
  "user": {
    "username": "developer"
  },
  "project": {
    "id": 123,
    "name": "repo",
    "path_with_namespace": "owner/repo"
  },
  "object_attributes": {
    "id": 456,
    "iid": 42,
    "title": "Add user authentication",
    "state": "opened",
    "action": "open",
    "source_branch": "feature/auth",
    "target_branch": "main",
    "last_commit": {
      "id": "abc123def456789012345678901234567890abcd"
    }
  },
  "changes": {
    "total_count": 5,
    "added_lines": 120,
    "removed_lines": 30
  }
}
```

**Merge Request Updated:**
```json
{
  "object_kind": "merge_request",
  "object_attributes": {
    "action": "update",
    // ... same structure
  }
}
```

#### Response

Same structure as GitHub webhook.

#### Status Codes

Same as GitHub webhook.

#### Signature Verification

GitLab uses simple token comparison:

```python
token = request.headers.get("X-Gitlab-Token")
expected = os.getenv("GITLAB_WEBHOOK_SECRET")

if token != expected:
    raise HTTPException(401, "Invalid token")
```

---

### Bitbucket Webhook

**POST** `/webhooks/bitbucket`

Receives webhook events from Bitbucket Cloud.

#### Headers

```http
X-Event-Key: pullrequest:created
X-Hook-UUID: {12345678-1234-1234-1234-123456789012}
Content-Type: application/json
```

**Required Headers:**
- `X-Event-Key` - Event type
- `X-Hook-UUID` - Webhook UUID

#### Request Body

**Pull Request Created:**
```json
{
  "pullrequest": {
    "id": 42,
    "title": "Add user authentication",
    "state": "OPEN",
    "author": {
      "username": "developer"
    },
    "source": {
      "branch": {
        "name": "feature/auth"
      },
      "commit": {
        "hash": "abc123def456"
      }
    },
    "destination": {
      "branch": {
        "name": "main"
      }
    },
    "links": {
      "diff": {
        "href": "https://api.bitbucket.org/2.0/repositories/owner/repo/pullrequests/42/diff"
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

**Pull Request Updated:**
```json
{
  "pullrequest": {
    "id": 42,
    "state": "OPEN",
    // ... same structure
  }
}
```

#### Response

Same structure as GitHub webhook.

#### Status Codes

Same as GitHub webhook.

#### Signature Verification

Bitbucket verification is optional (webhook UUID):

```python
webhook_uuid = request.headers.get("X-Hook-UUID")

# Verify UUID is in registered webhooks
if webhook_uuid not in registered_webhooks:
    raise HTTPException(401, "Unknown webhook")
```

---

### Gitea Webhook

**POST** `/webhooks/gitea`

Receives webhook events from Gitea.

#### Headers

```http
X-Gitea-Event: pull_request
X-Gitea-Signature: abc123def456...
Content-Type: application/json
```

**Required Headers:**
- `X-Gitea-Event` - Event type
- `X-Gitea-Signature` - HMAC signature

#### Request Body

**Pull Request Opened:**
```json
{
  "action": "opened",
  "number": 42,
  "pull_request": {
    "id": 123,
    "number": 42,
    "title": "Add user authentication",
    "state": "open",
    "user": {
      "login": "developer"
    },
    "head": {
      "ref": "feature/auth",
      "sha": "abc123def456789012345678901234567890abcd"
    },
    "base": {
      "ref": "main",
      "sha": "789012ghi345jkl678901234567890mnop123"
    }
  },
  "repository": {
    "id": 456,
    "name": "repo",
    "full_name": "owner/repo",
    "owner": {
      "login": "owner"
    }
  }
}
```

#### Response

Same structure as GitHub webhook.

#### Status Codes

Same as GitHub webhook.

#### Signature Verification

Gitea uses HMAC-SHA256 (similar to GitHub):

```python
import hmac
import hashlib

secret = os.getenv("GITEA_WEBHOOK_SECRET").encode()
signature = request.headers.get("X-Gitea-Signature")
body = await request.body()

expected = hmac.new(secret, body, hashlib.sha256).hexdigest()

if not hmac.compare_digest(signature, expected):
    raise HTTPException(401, "Invalid signature")
```

---

### Azure DevOps Webhook

**POST** `/webhooks/azure-devops`

Receives webhook events from Azure DevOps Services.

#### Headers

```http
Content-Type: application/json
Authorization: Basic <base64-encoded-credentials>
```

**Authentication:**
Azure DevOps uses Basic Auth for webhooks.

#### Request Body

**Pull Request Created:**
```json
{
  "subscriptionId": "12345678-1234-1234-1234-123456789012",
  "eventType": "git.pullrequest.created",
  "resource": {
    "pullRequestId": 42,
    "status": "active",
    "title": "Add user authentication",
    "createdBy": {
      "displayName": "Developer",
      "uniqueName": "developer@company.com"
    },
    "sourceRefName": "refs/heads/feature/auth",
    "targetRefName": "refs/heads/main",
    "lastMergeSourceCommit": {
      "commitId": "abc123def456789012345678901234567890abcd"
    },
    "repository": {
      "id": "789",
      "name": "repo",
      "project": {
        "name": "project"
      }
    }
  }
}
```

**Pull Request Updated:**
```json
{
  "eventType": "git.pullrequest.updated",
  "resource": {
    // ... same structure
  }
}
```

#### Response

Same structure as GitHub webhook.

#### Status Codes

Same as GitHub webhook.

#### Signature Verification

Azure DevOps uses Basic Auth:

```python
import base64

auth_header = request.headers.get("Authorization")
if not auth_header or not auth_header.startswith("Basic "):
    raise HTTPException(401, "Missing authorization")

# Decode and verify credentials
credentials = base64.b64decode(auth_header[6:]).decode()
username, password = credentials.split(":", 1)

expected_password = os.getenv("AZURE_DEVOPS_WEBHOOK_SECRET")
if password != expected_password:
    raise HTTPException(401, "Invalid credentials")
```

---

## Common Response Formats

### Success Response

```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Review job queued",
  "repository": "owner/repo",
  "pr_number": 42
}
```

### Ignored Response

```json
{
  "success": false,
  "reason": "repo_not_enabled|triggers_not_matched|pr_too_large|branch_excluded",
  "message": "Human-readable explanation"
}
```

### Error Response

```json
{
  "success": false,
  "error": "invalid_signature|invalid_payload|internal_error",
  "message": "Detailed error message"
}
```

---

## Webhook Event Types

### Supported Events

Each platform triggers reviews on these events:

**GitHub:**
- `pull_request.opened`
- `pull_request.synchronize` (new commits)
- `pull_request.reopened`

**GitLab:**
- `merge_request.open`
- `merge_request.update`
- `merge_request.reopen`

**Bitbucket:**
- `pullrequest:created`
- `pullrequest:updated`

**Gitea:**
- `pull_request.opened`
- `pull_request.synchronized`
- `pull_request.reopened`

**Azure DevOps:**
- `git.pullrequest.created`
- `git.pullrequest.updated`

### Ignored Events

These events are received but ignored:
- `pull_request.closed` / `merged`
- `pull_request.labeled`
- `pull_request.assigned`
- Comments, reviews (not PR changes)

---

## Rate Limiting

### Per Repository

- **Limit:** 100 webhook requests per hour
- **Window:** Rolling 1-hour window
- **Response:** 429 Too Many Requests

**Response:**
```json
{
  "success": false,
  "error": "rate_limit_exceeded",
  "message": "Too many webhook requests. Limit: 100/hour",
  "retry_after": 3600
}
```

### Global

- **Limit:** 1000 webhook requests per hour across all repos
- **Window:** Rolling 1-hour window

---

## Webhook Setup Guide

### GitHub

1. Go to repository settings → Webhooks
2. Click "Add webhook"
3. **Payload URL:** `https://your-loom.com/webhooks/github`
4. **Content type:** `application/json`
5. **Secret:** Your webhook secret
6. **Events:** Select "Pull requests"
7. Click "Add webhook"

**Environment Variable:**
```bash
GITHUB_WEBHOOK_SECRET=your-secret-here
```

### GitLab

1. Go to repository settings → Webhooks
2. **URL:** `https://your-loom.com/webhooks/gitlab`
3. **Secret token:** Your webhook secret
4. **Trigger:** Check "Merge request events"
5. Click "Add webhook"

**Environment Variable:**
```bash
GITLAB_WEBHOOK_SECRET=your-secret-here
```

### Bitbucket

1. Go to repository settings → Webhooks
2. Click "Add webhook"
3. **Title:** "Loom Code Reviews"
4. **URL:** `https://your-loom.com/webhooks/bitbucket`
5. **Triggers:** Select "Pull Request Created" and "Pull Request Updated"
6. Click "Save"

**Environment Variable:**
```bash
BITBUCKET_WEBHOOK_UUID={your-webhook-uuid}
```

### Gitea

1. Go to repository settings → Webhooks
2. Click "Add Webhook" → Gitea
3. **Target URL:** `https://your-loom.com/webhooks/gitea`
4. **Secret:** Your webhook secret
5. **Trigger:** Select "Pull Request"
6. Click "Add Webhook"

**Environment Variable:**
```bash
GITEA_WEBHOOK_SECRET=your-secret-here
```

### Azure DevOps

1. Go to Project Settings → Service hooks
2. Click "Create subscription"
3. Select "Web Hooks"
4. **Event:** "Pull request created" and "Pull request updated"
5. **URL:** `https://your-loom.com/webhooks/azure-devops`
6. **Basic authentication:** username + password
7. Click "Finish"

**Environment Variables:**
```bash
AZURE_DEVOPS_USERNAME=your-username
AZURE_DEVOPS_WEBHOOK_SECRET=your-password
```

---

## Testing Webhooks

### Manual Testing

```bash
# GitHub
curl -X POST https://your-loom.com/webhooks/github \
  -H "X-GitHub-Event: pull_request" \
  -H "X-Hub-Signature-256: sha256=..." \
  -H "Content-Type: application/json" \
  -d @github-pr-opened.json

# GitLab
curl -X POST https://your-loom.com/webhooks/gitlab \
  -H "X-Gitlab-Event: Merge Request Hook" \
  -H "X-Gitlab-Token: your-secret" \
  -H "Content-Type: application/json" \
  -d @gitlab-mr-opened.json
```

### Sample Payloads

Sample payload files are available in `/tests/fixtures/`:
- `github-pr-opened.json`
- `github-pr-synchronized.json`
- `gitlab-mr-opened.json`
- `bitbucket-pr-created.json`
- `gitea-pr-opened.json`
- `azure-pr-created.json`

### Platform Test Webhooks

Most platforms have a "Test" button to send sample webhooks:
- **GitHub:** Webhook settings → "Recent Deliveries" → "Redeliver"
- **GitLab:** Webhook settings → "Test" → "Merge Request events"
- **Bitbucket:** Webhook settings → "View requests" → Test
- **Gitea:** Webhook settings → "Test Delivery"

---

## Monitoring & Debugging

### Webhook Logs

All webhook requests are logged:

```json
{
  "timestamp": "2026-01-18T14:30:00Z",
  "platform": "github",
  "event": "pull_request.opened",
  "repository": "owner/repo",
  "pr_number": 42,
  "signature_valid": true,
  "job_created": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "processing_time_ms": 45
}
```

### Failed Webhooks

Check logs for common issues:
- ❌ Invalid signature → Check webhook secret
- ❌ Repository not found → Enable repository in Loom
- ❌ 500 error → Check database/Redis connectivity

### Webhook Delivery

Platforms show delivery status:
- **GitHub:** Settings → Webhooks → Recent Deliveries
- **GitLab:** Settings → Webhooks → View request details
- Response codes and bodies are shown

---

## Security Best Practices

### 1. Always Verify Signatures

```python
# REQUIRED: Always verify webhook signatures
if not await adapter.verify_webhook(request):
    raise HTTPException(401, "Invalid signature")
```

### 2. Use HTTPS

All webhook URLs must use HTTPS in production:
```
✅ https://loom.company.com/webhooks/github
❌ http://loom.company.com/webhooks/github
```

### 3. Rotate Secrets Regularly

Rotate webhook secrets every 90 days:
1. Generate new secret
2. Update in git platform
3. Update environment variable
4. Restart Loom

### 4. Limit Webhook Sources

If possible, restrict webhook sources by IP:
- **GitHub:** [GitHub IP ranges](https://api.github.com/meta)
- **GitLab:** Self-hosted IPs only
- **Bitbucket:** [Atlassian IPs](https://support.atlassian.com/organization-administration/docs/ip-addresses-and-domains-for-atlassian-cloud-products/)

### 5. Rate Limiting

Always implement rate limiting to prevent abuse.

---

## OpenAPI Specification

See [openapi.yaml](openapi.yaml) for complete OpenAPI 3.0 specification.

---

## References

- [GitHub Webhooks Docs](https://docs.github.com/webhooks)
- [GitLab Webhooks Docs](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html)
- [Bitbucket Webhooks Docs](https://support.atlassian.com/bitbucket-cloud/docs/manage-webhooks/)
- [Gitea Webhooks Docs](https://docs.gitea.io/en-us/webhooks/)
- [Azure DevOps Service Hooks](https://learn.microsoft.com/en-us/azure/devops/service-hooks/)
- [Adapter Pattern](../architecture/adapter-pattern.md)
- [Data Flow](../architecture/data-flow.md)
