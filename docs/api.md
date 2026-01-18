# API Documentation

Loom provides both a **tRPC API** (for the dashboard) and **REST webhooks** (for git platforms).

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [tRPC API](#trpc-api)
- [REST Webhooks](#rest-webhooks)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

---

## Overview

Loom exposes two types of APIs:

### tRPC API (Internal)
- **Purpose:** Dashboard UI ↔ Backend communication
- **Protocol:** tRPC over HTTP
- **Auth:** Session-based (cookies)
- **Base URL:** `/api/trpc`
- **Type-safe:** Full TypeScript types

### REST Webhooks (External)
- **Purpose:** Git platforms → Loom notifications
- **Protocol:** REST (JSON)
- **Auth:** HMAC signatures or tokens
- **Base URLs:** `/api/webhooks/*`

---

## Authentication

### Dashboard (tRPC API)

**Session-based authentication** using Better Auth:

1. **Login:**
   ```typescript
   POST /api/auth/sign-in/email
   
   {
     "email": "user@example.com",
     "password": "password"
   }
   ```

2. **OAuth Login:**
   ```
   GET /api/auth/sign-in/github
   GET /api/auth/sign-in/gitlab
   ```

3. **Session Cookie:**
   - Set automatically after login
   - Included in all subsequent requests
   - HttpOnly, Secure (in production)

### Webhooks (REST API)

**Platform-specific verification:**

| Platform | Method |
|----------|--------|
| GitHub | HMAC SHA256 signature in `x-hub-signature-256` |
| GitLab | Token in `x-gitlab-token` |
| Bitbucket | Custom header or basic auth |
| Azure DevOps | Basic auth or custom header |

See [Platform Adapters](adapters/) for details.

---

## tRPC API

### Overview

The tRPC API is primarily for internal use by the dashboard, but can be called programmatically.

**Base URL:** `https://your-loom-instance.com/api/trpc`

**Type definitions:** Available in `packages/web/src/server/api/root.ts`

### Using tRPC from TypeScript

```typescript
import { createTRPCProxyClient, httpBatchLink } from '@trpc/client';
import type { AppRouter } from '@loom/web/server/api/root';

const client = createTRPCProxyClient<AppRouter>({
  links: [
    httpBatchLink({
      url: 'https://your-loom-instance.com/api/trpc',
      headers: {
        cookie: 'session=...',  // Your session cookie
      },
    }),
  ],
});

// Type-safe API calls
const repos = await client.repos.list.query();
const review = await client.reviews.get.query({ id: 'review-123' });
```

### Main Routers

#### `repos` - Repository Management

**List repositories:**
```typescript
repos.list.query()

// Returns:
{
  repos: [
    {
      id: string;
      name: string;
      fullName: string;
      platform: 'github' | 'gitlab' | ...;
      isActive: boolean;
      webhookSecret: string;
    }
  ]
}
```

**Get repository:**
```typescript
repos.get.query({ id: 'repo-123' })

// Returns: Repository details
```

**Add repository:**
```typescript
repos.add.mutate({
  platform: 'github',
  platformId: '12345',
  name: 'my-repo',
  fullName: 'org/my-repo'
})
```

**Update repository:**
```typescript
repos.update.mutate({
  id: 'repo-123',
  isActive: true,
  webhookSecret: 'new-secret'
})
```

**Delete repository:**
```typescript
repos.delete.mutate({ id: 'repo-123' })
```

#### `reviews` - Review History

**List reviews:**
```typescript
reviews.list.query({
  repoId: 'repo-123',
  limit: 20,
  offset: 0
})

// Returns:
{
  reviews: [
    {
      id: string;
      prNumber: number;
      prTitle: string;
      status: 'pending' | 'completed' | 'failed';
      summary: string;
      commentCount: number;
      llmTokensUsed: number;
      durationMs: number;
      createdAt: Date;
      completedAt: Date | null;
    }
  ],
  total: number;
}
```

**Get review details:**
```typescript
reviews.get.query({ id: 'review-123' })

// Returns: Full review with comments
{
  id: string;
  prNumber: number;
  status: string;
  summary: string;
  comments: [
    {
      file: string;
      line: number;
      severity: 'blocker' | 'warning' | 'info';
      message: string;
      pipelineName: string;
    }
  ],
  metadata: {
    llmProvider: string;
    llmModel: string;
    tokensUsed: number;
    durationMs: number;
  }
}
```

**Retry review:**
```typescript
reviews.retry.mutate({ id: 'review-123' })
```

**Cancel review:**
```typescript
reviews.cancel.mutate({ id: 'review-123' })
```

#### `prompts` - Prompt Library

**List prompts:**
```typescript
prompts.list.query({
  orgId: 'org-123',  // Optional
  isSystem: false    // Optional
})

// Returns:
{
  prompts: [
    {
      id: string;
      name: string;
      description: string;
      content: string;
      isSystem: boolean;
      createdAt: Date;
      updatedAt: Date;
    }
  ]
}
```

**Get prompt:**
```typescript
prompts.get.query({ id: 'prompt-123' })
```

**Create prompt:**
```typescript
prompts.create.mutate({
  name: 'Security Review',
  description: 'Focuses on security vulnerabilities',
  content: '# Security Review\n\n...'
})
```

**Update prompt:**
```typescript
prompts.update.mutate({
  id: 'prompt-123',
  content: 'Updated prompt content...'
})
```

**Delete prompt:**
```typescript
prompts.delete.mutate({ id: 'prompt-123' })
```

#### `orgs` - Organization Management

**List organizations:**
```typescript
orgs.list.query()

// Returns: Organizations user is member of
```

**Get organization:**
```typescript
orgs.get.query({ id: 'org-123' })
```

**Create organization:**
```typescript
orgs.create.mutate({
  name: 'My Company',
  slug: 'my-company'
})
```

**Update organization:**
```typescript
orgs.update.mutate({
  id: 'org-123',
  name: 'Updated Name'
})
```

**Manage members:**
```typescript
// Add member
orgs.addMember.mutate({
  orgId: 'org-123',
  userId: 'user-456',
  role: 'member'  // 'owner' | 'admin' | 'member'
})

// Update member role
orgs.updateMember.mutate({
  orgId: 'org-123',
  userId: 'user-456',
  role: 'admin'
})

// Remove member
orgs.removeMember.mutate({
  orgId: 'org-123',
  userId: 'user-456'
})
```

#### `config` - Configuration Management

**Validate config:**
```typescript
config.validate.mutate({
  yaml: `
models:
  default:
    provider: openai-compatible
    model: gpt-4o
pipelines:
  - name: review
    model: default
  `
})

// Returns:
{
  valid: boolean;
  errors?: [
    { path: string; message: string; }
  ];
  warnings?: [
    { path: string; message: string; }
  ];
}
```

**Get repo config:**
```typescript
config.get.query({
  repoId: 'repo-123'
})

// Fetches .loom/config.yaml from repo
```

#### `jobs` - Job Management

**List jobs:**
```typescript
jobs.list.query({
  repoId: 'repo-123',
  status: 'pending'  // Optional filter
})
```

**Get job:**
```typescript
jobs.get.query({ id: 'job-123' })
```

**Cancel job:**
```typescript
jobs.cancel.mutate({ id: 'job-123' })
```

#### `user` - User Settings

**Get current user:**
```typescript
user.me.query()

// Returns:
{
  id: string;
  email: string;
  name: string;
  avatarUrl: string;
}
```

**Update profile:**
```typescript
user.update.mutate({
  name: 'New Name'
})
```

### Error Handling

tRPC errors follow this format:

```typescript
try {
  await client.repos.get.query({ id: 'invalid' });
} catch (error) {
  if (error instanceof TRPCClientError) {
    console.log(error.message);  // User-friendly message
    console.log(error.data?.code);  // Error code
    console.log(error.data?.httpStatus);  // HTTP status
  }
}
```

**Common error codes:**
- `UNAUTHORIZED` - Not logged in
- `FORBIDDEN` - Insufficient permissions
- `NOT_FOUND` - Resource doesn't exist
- `BAD_REQUEST` - Invalid input
- `INTERNAL_SERVER_ERROR` - Server error

---

## REST Webhooks

### GitHub Webhook

**Endpoint:** `POST /api/webhooks/github`

**Headers:**
```
Content-Type: application/json
X-Hub-Signature-256: sha256=...
X-GitHub-Event: pull_request
```

**Payload:**
```json
{
  "action": "opened",
  "number": 123,
  "pull_request": {
    "id": 123456,
    "number": 123,
    "title": "Add new feature",
    "user": {
      "login": "developer"
    },
    "head": {
      "ref": "feature/new-feature",
      "sha": "abc123..."
    },
    "base": {
      "ref": "main"
    }
  },
  "repository": {
    "id": 789,
    "full_name": "org/repo"
  }
}
```

**Response:**
```json
{
  "success": true,
  "jobId": "job-abc123"
}
```

**Events handled:**
- `pull_request.opened` - New PR
- `pull_request.synchronize` - PR updated
- `pull_request.reopened` - PR reopened
- `pull_request_review_comment.created` - Comment added

### GitLab Webhook

**Endpoint:** `POST /api/webhooks/gitlab`

**Headers:**
```
Content-Type: application/json
X-Gitlab-Token: your-webhook-secret
X-Gitlab-Event: Merge Request Hook
```

**Payload:**
```json
{
  "object_kind": "merge_request",
  "event_type": "merge_request",
  "object_attributes": {
    "id": 123,
    "iid": 45,
    "title": "Add new feature",
    "state": "opened",
    "source_branch": "feature/new-feature",
    "target_branch": "main"
  },
  "project": {
    "id": 789,
    "path_with_namespace": "org/repo"
  }
}
```

### Bitbucket Webhook

**Endpoint:** `POST /api/webhooks/bitbucket`

**Headers:**
```
Content-Type: application/json
X-Event-Key: pullrequest:created
```

### Azure DevOps Service Hook

**Endpoint:** `POST /api/webhooks/azure-devops`

**Headers:**
```
Content-Type: application/json
```

**Authentication:** Basic auth or custom header

### Webhook Testing

**Test webhook delivery:**

```bash
# GitHub
curl -X POST https://your-loom.com/api/webhooks/github \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: ping" \
  -d '{"zen": "Test"}'

# Should return: {"success": true}
```

---

## Rate Limiting

### tRPC API

**Limits:**
- 100 requests per minute per user (authenticated)
- 10 requests per minute per IP (unauthenticated)

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

**Error when exceeded:**
```json
{
  "error": {
    "code": "TOO_MANY_REQUESTS",
    "message": "Rate limit exceeded. Try again in 30 seconds."
  }
}
```

### Webhooks

**Limits:**
- 1000 webhooks per hour per repository
- Prevents spam/abuse

**Response when exceeded:**
```json
{
  "success": false,
  "error": "Rate limit exceeded"
}
```

---

## Examples

### Example 1: Programmatic Repository Management

```typescript
import { createTRPCProxyClient, httpBatchLink } from '@trpc/client';
import type { AppRouter } from '@loom/web/server/api/root';

const client = createTRPCProxyClient<AppRouter>({
  links: [
    httpBatchLink({
      url: 'https://loom.company.com/api/trpc',
      headers: {
        cookie: process.env.LOOM_SESSION_COOKIE,
      },
    }),
  ],
});

async function enableReviewsForAllRepos() {
  const { repos } = await client.repos.list.query();
  
  for (const repo of repos) {
    if (!repo.isActive) {
      await client.repos.update.mutate({
        id: repo.id,
        isActive: true,
      });
      console.log(`Enabled reviews for ${repo.fullName}`);
    }
  }
}

enableReviewsForAllRepos();
```

### Example 2: Export Review Analytics

```typescript
async function exportReviewStats() {
  const allRepos = await client.repos.list.query();
  
  const stats = [];
  
  for (const repo of allRepos.repos) {
    const { reviews, total } = await client.reviews.list.query({
      repoId: repo.id,
      limit: 1000,
    });
    
    const completed = reviews.filter(r => r.status === 'completed');
    const avgTokens = completed.reduce((sum, r) => sum + r.llmTokensUsed, 0) / completed.length;
    const avgDuration = completed.reduce((sum, r) => sum + r.durationMs, 0) / completed.length;
    
    stats.push({
      repo: repo.fullName,
      totalReviews: total,
      avgTokensPerReview: Math.round(avgTokens),
      avgDurationSeconds: Math.round(avgDuration / 1000),
    });
  }
  
  console.table(stats);
}

exportReviewStats();
```

### Example 3: Webhook Handler (Custom Integration)

```typescript
import express from 'express';
import crypto from 'crypto';

const app = express();

app.post('/loom-webhook-proxy', express.json(), (req, res) => {
  // Verify signature
  const signature = req.headers['x-hub-signature-256'];
  const payload = JSON.stringify(req.body);
  const secret = process.env.GITHUB_WEBHOOK_SECRET;
  
  const expectedSignature = 'sha256=' + 
    crypto.createHmac('sha256', secret)
      .update(payload)
      .digest('hex');
  
  if (signature !== expectedSignature) {
    return res.status(401).send('Invalid signature');
  }
  
  // Forward to Loom
  fetch('https://loom.company.com/api/webhooks/github', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Hub-Signature-256': signature,
      'X-GitHub-Event': req.headers['x-github-event'],
    },
    body: payload,
  });
  
  // Also log to internal analytics
  logToAnalytics({
    repo: req.body.repository.full_name,
    pr: req.body.pull_request.number,
    action: req.body.action,
  });
  
  res.json({ success: true });
});

app.listen(3001);
```

### Example 4: CLI Tool for Config Validation

```typescript
#!/usr/bin/env node
import { readFileSync } from 'fs';
import { createTRPCProxyClient, httpBatchLink } from '@trpc/client';
import type { AppRouter } from '@loom/web/server/api/root';

const configPath = process.argv[2] || '.loom/config.yaml';
const yaml = readFileSync(configPath, 'utf-8');

const client = createTRPCProxyClient<AppRouter>({
  links: [
    httpBatchLink({
      url: process.env.LOOM_URL + '/api/trpc',
      headers: {
        cookie: process.env.LOOM_SESSION,
      },
    }),
  ],
});

const result = await client.config.validate.mutate({ yaml });

if (result.valid) {
  console.log('✅ Configuration is valid');
} else {
  console.error('❌ Configuration errors:');
  result.errors?.forEach(err => {
    console.error(`  - ${err.path}: ${err.message}`);
  });
  process.exit(1);
}

if (result.warnings?.length) {
  console.warn('⚠️  Warnings:');
  result.warnings.forEach(warn => {
    console.warn(`  - ${warn.path}: ${warn.message}`);
  });
}
```

---

## SDK Libraries

Currently, Loom does not provide official SDKs, but tRPC makes it easy to create type-safe clients in TypeScript.

**Community SDKs (unofficial):**
- JavaScript/TypeScript: Use tRPC client directly
- Python: Coming soon
- Go: Coming soon

**Want to build an SDK?** See [Contributing Guide](../CONTRIBUTING.md)

---

## OpenAPI / Swagger

tRPC APIs can be exposed as REST using `@trpc/server/adapters/standalone`:

```typescript
// Convert tRPC to OpenAPI (future feature)
import { generateOpenApiDocument } from 'trpc-openapi';

const openApiDocument = generateOpenApiDocument(appRouter, {
  title: 'Loom API',
  version: '1.0.0',
  baseUrl: 'https://loom.company.com/api',
});

// Serve at /api/openapi.json
```

**Status:** Planned for future release

---

## GraphQL

Loom does not currently support GraphQL, but tRPC can be adapted:

```typescript
// Future feature: GraphQL adapter
import { trpcToGraphQL } from '@trpc/graphql';
```

**Status:** Not currently planned

---

## Need Help?

- **Questions:** [GitHub Discussions](https://github.com/loom-reviews/loom-reviews/discussions)
- **Bugs:** [GitHub Issues](https://github.com/loom-reviews/loom-reviews/issues)
- **Examples:** See `examples/` directory (coming soon)
