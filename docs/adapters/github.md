# GitHub Integration

This guide covers setting up Loom with GitHub (Cloud and Enterprise).

## Table of Contents

- [Overview](#overview)
- [Quick Setup](#quick-setup)
- [GitHub App (Recommended)](#github-app-recommended)
- [OAuth App](#oauth-app)
- [Personal Access Token](#personal-access-token)
- [Webhook Configuration](#webhook-configuration)
- [Permissions](#permissions)
- [GitHub Enterprise](#github-enterprise)
- [Troubleshooting](#troubleshooting)

## Overview

Loom integrates with GitHub in two ways:

1. **OAuth** - For user authentication (login with GitHub)
2. **GitHub App or PAT** - For repository access (reading code, posting reviews)

```
┌─────────────────┐      OAuth      ┌─────────────────┐
│     User        │ ───────────────▶│      Loom       │
└─────────────────┘                 └─────────────────┘
                                           │
                                           │ GitHub App / PAT
                                           ▼
                                    ┌─────────────────┐
                                    │     GitHub      │
                                    └─────────────────┘
```

## Quick Setup

### 1. Create OAuth App (for login)

1. Go to GitHub → Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in:
   - **Application name**: Loom Code Reviews
   - **Homepage URL**: `https://your-loom-instance.com`
   - **Authorization callback URL**: `https://your-loom-instance.com/api/auth/callback/github`
4. Save Client ID and Client Secret

### 2. Set Environment Variables

```bash
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-client-secret
```

### 3. Connect a Repository

1. Log in to Loom
2. Go to Dashboard → Repositories → Add Repository
3. Authorize Loom to access your repositories
4. Select repositories to enable

## GitHub App (Recommended)

GitHub Apps provide fine-grained permissions and higher rate limits.

### Create a GitHub App

1. Go to GitHub → Settings → Developer settings → GitHub Apps
2. Click "New GitHub App"
3. Fill in:

**Basic Information**
- **GitHub App name**: Loom Code Reviews (your-org)
- **Homepage URL**: `https://your-loom-instance.com`
- **Callback URL**: `https://your-loom-instance.com/api/auth/callback/github-app`
- **Setup URL** (optional): `https://your-loom-instance.com/setup/github`
- **Webhook URL**: `https://your-loom-instance.com/api/webhooks/github`
- **Webhook secret**: Generate a random string

**Permissions**

| Category | Permission | Access |
|----------|------------|--------|
| Repository | Contents | Read |
| Repository | Pull requests | Read & Write |
| Repository | Metadata | Read |
| Repository | Webhooks | Read & Write |

**Subscribe to Events**
- Pull request
- Pull request review
- Pull request review comment

**Where can this GitHub App be installed?**
- Select "Any account" for public app
- Select "Only on this account" for private app

4. Create the app
5. Generate a private key (download .pem file)
6. Note the App ID

### Configure Loom

```bash
# Environment variables
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----"
GITHUB_WEBHOOK_SECRET=your-webhook-secret
```

Or reference the key file:

```bash
GITHUB_APP_PRIVATE_KEY_PATH=/path/to/private-key.pem
```

### Install the App

1. Go to your GitHub App settings
2. Click "Install App"
3. Select the account/organization
4. Choose "All repositories" or select specific ones
5. Click "Install"

## OAuth App

Simpler setup, uses the user's permissions.

### Create OAuth App

1. Go to GitHub → Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in:
   - **Application name**: Loom Code Reviews
   - **Homepage URL**: `https://your-loom-instance.com`
   - **Authorization callback URL**: `https://your-loom-instance.com/api/auth/callback/github`

### Configure Loom

```bash
GITHUB_CLIENT_ID=Iv1.abc123...
GITHUB_CLIENT_SECRET=secret123...
```

### Scopes

Loom requests these OAuth scopes:
- `repo` - Full repository access
- `read:user` - Read user profile
- `user:email` - Read user email

## Personal Access Token

For simple setups or CI environments.

### Create a PAT

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` - Full repository access
4. Generate and copy the token

### Configure Loom

```bash
GITHUB_TOKEN=ghp_...
```

### Fine-grained PAT (Recommended)

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Click "Generate new token"
3. Configure:
   - **Repository access**: Select repositories
   - **Permissions**:
     - Contents: Read
     - Pull requests: Read and Write
     - Metadata: Read

## Webhook Configuration

Webhooks notify Loom when PRs are opened or updated.

### Automatic (GitHub App)

If using a GitHub App, webhooks are configured automatically during installation.

### Manual (OAuth/PAT)

1. Go to your repository → Settings → Webhooks
2. Click "Add webhook"
3. Configure:
   - **Payload URL**: `https://your-loom-instance.com/api/webhooks/github`
   - **Content type**: `application/json`
   - **Secret**: Generate and save a random string
   - **Events**: Select "Let me select individual events"
     - Pull requests
     - Pull request reviews
     - Pull request review comments

4. Set the webhook secret in Loom:
   ```bash
   GITHUB_WEBHOOK_SECRET=your-webhook-secret
   ```

### Webhook Events

| Event | Description |
|-------|-------------|
| `pull_request.opened` | PR created - triggers review |
| `pull_request.synchronize` | PR updated - triggers re-review |
| `pull_request.reopened` | PR reopened - triggers review |
| `pull_request_review_comment.created` | Comment on review - future: respond |

## Permissions

### Minimum Required

| Permission | Why |
|------------|-----|
| Contents (Read) | Read `.loom/config.yaml` and code |
| Pull Requests (Read & Write) | Read PR info, post review comments |
| Metadata (Read) | List repositories |

### Optional

| Permission | Why |
|------------|-----|
| Checks (Read & Write) | Create check runs for reviews |
| Issues (Read & Write) | Create issues from reviews |

## GitHub Enterprise

Loom supports GitHub Enterprise Server.

### Configuration

```bash
# Set your GHE host
GITHUB_ENTERPRISE_HOST=github.your-company.com

# OAuth
GITHUB_CLIENT_ID=your-ghe-oauth-client-id
GITHUB_CLIENT_SECRET=your-ghe-oauth-client-secret

# Or PAT
GITHUB_TOKEN=ghp_...

# For GitHub App
GITHUB_APP_ID=123
GITHUB_APP_PRIVATE_KEY="..."
```

### API URL Override

If your GHE uses a non-standard API path:

```bash
GITHUB_API_URL=https://github.your-company.com/api/v3
```

### Self-Signed Certificates

If your GHE uses self-signed certificates:

```bash
NODE_TLS_REJECT_UNAUTHORIZED=0  # Not recommended for production
# Or
NODE_EXTRA_CA_CERTS=/path/to/ca-cert.pem
```

## Troubleshooting

### Webhook not triggering

1. **Check webhook delivery**: Repository → Settings → Webhooks → Recent Deliveries
2. **Verify URL**: Must be publicly accessible
3. **Check secret**: Must match `GITHUB_WEBHOOK_SECRET`
4. **Check logs**: `docker logs loom 2>&1 | grep webhook`

### "Resource not accessible by integration"

- GitHub App doesn't have required permissions
- Re-install the app with correct permissions

### "Bad credentials"

- Token expired or revoked
- Wrong token type for the operation
- Check `GITHUB_TOKEN` or app credentials

### Rate limiting

GitHub API rate limits:
- Unauthenticated: 60 requests/hour
- OAuth token: 5,000 requests/hour
- GitHub App: 5,000 requests/hour per installation

If hitting limits:
- Use a GitHub App (higher limits)
- Enable response caching in Loom
- Reduce review frequency

### Can't see private repositories

- OAuth: User must have access to the repo
- GitHub App: Must be installed on the repository
- PAT: Must be created by user with access

### Comments not appearing

1. Check Loom has write access to Pull Requests
2. Verify the PR is not from a fork (different permissions)
3. Check for API errors in logs

### "Hook delivery failed"

Common causes:
- Loom not reachable from GitHub
- SSL certificate issues
- Webhook secret mismatch
- Loom returning 500 error

Debug steps:
1. Check webhook payload in GitHub
2. Test URL accessibility: `curl https://your-loom/api/webhooks/github`
3. Check Loom logs for errors
