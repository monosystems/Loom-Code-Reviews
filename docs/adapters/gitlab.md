# GitLab Integration

This guide covers setting up Loom with GitLab (Cloud and Self-Managed).

## Table of Contents

- [Overview](#overview)
- [Quick Setup](#quick-setup)
- [OAuth Application](#oauth-application)
- [Personal Access Token](#personal-access-token)
- [Project Access Token](#project-access-token)
- [Webhook Configuration](#webhook-configuration)
- [GitLab Self-Managed](#gitlab-self-managed)
- [Troubleshooting](#troubleshooting)

## Overview

Loom integrates with GitLab using:

1. **OAuth** - For user authentication
2. **Access Tokens** - For API access (reading code, posting reviews)

## Quick Setup

### 1. Create OAuth Application

1. Go to GitLab → Preferences → Applications (for personal) or Admin → Applications (for group)
2. Create new application:
   - **Name**: Loom Code Reviews
   - **Redirect URI**: `https://your-loom-instance.com/api/auth/callback/gitlab`
   - **Scopes**: `api`, `read_user`, `read_repository`
3. Save Application ID and Secret

### 2. Configure Loom

```bash
GITLAB_CLIENT_ID=your-application-id
GITLAB_CLIENT_SECRET=your-secret
```

### 3. Add Repository

1. Log in to Loom with GitLab
2. Go to Dashboard → Repositories → Add Repository
3. Select your GitLab projects

## OAuth Application

### User-Level Application

For personal use:

1. Go to GitLab → User Settings → Applications
2. Create application with:
   - **Name**: Loom
   - **Redirect URI**: `https://your-loom/api/auth/callback/gitlab`
   - **Confidential**: Yes
   - **Scopes**: `api`, `read_user`

### Group-Level Application

For organization use:

1. Go to Group → Settings → Applications
2. Create application (same settings as above)

### Instance-Level Application (Admin)

For GitLab Self-Managed:

1. Admin Area → Applications
2. Create application with:
   - **Trusted**: Optional (skips user confirmation)
   - **Scopes**: `api`, `read_user`

### Environment Variables

```bash
GITLAB_CLIENT_ID=your-app-id
GITLAB_CLIENT_SECRET=your-secret
# For self-managed:
GITLAB_HOST=https://gitlab.your-company.com
```

## Personal Access Token

For simple setups:

### Create PAT

1. GitLab → User Settings → Access Tokens
2. Create token:
   - **Name**: Loom Code Reviews
   - **Expiration**: Set appropriate date
   - **Scopes**: `api`, `read_repository`, `write_repository`

### Configure

```bash
GITLAB_TOKEN=glpat-...
```

## Project Access Token

For per-project access:

### Create Token

1. Project → Settings → Access Tokens
2. Create token:
   - **Name**: Loom
   - **Role**: Developer or Maintainer
   - **Scopes**: `api`, `read_repository`, `write_repository`

### Configure in Loom Dashboard

Add the token when connecting the repository in Loom's dashboard.

## Webhook Configuration

### Create Webhook

1. Project → Settings → Webhooks
2. Configure:
   - **URL**: `https://your-loom-instance.com/api/webhooks/gitlab`
   - **Secret token**: Generate random string
   - **Trigger**:
     - ✅ Merge request events
     - ✅ Comments
   - **SSL verification**: Enable

### Set Secret in Loom

```bash
GITLAB_WEBHOOK_SECRET=your-webhook-secret
```

### Webhook Events

| Event | Description |
|-------|-------------|
| `merge_request` opened | MR created - triggers review |
| `merge_request` updated | MR updated - triggers re-review |
| `note` (on MR) | Comment added - future: respond |

## GitLab Self-Managed

### Configuration

```bash
# Your GitLab instance URL
GITLAB_HOST=https://gitlab.your-company.com

# OAuth
GITLAB_CLIENT_ID=your-app-id
GITLAB_CLIENT_SECRET=your-secret

# Or use token
GITLAB_TOKEN=glpat-...
```

### API Version

Loom uses GitLab API v4. Ensure your GitLab version is 9.0 or higher.

### Self-Signed Certificates

```bash
# Trust custom CA
NODE_EXTRA_CA_CERTS=/path/to/ca-bundle.crt

# Or disable verification (not recommended)
NODE_TLS_REJECT_UNAUTHORIZED=0
```

## Permissions

### Required Scopes

| Scope | Why |
|-------|-----|
| `api` | Full API access |
| `read_repository` | Read code and MR info |
| `write_repository` | Post review comments |

### Minimum Role

For project access tokens, minimum role is **Developer** for:
- Reading merge requests
- Posting comments
- Reading repository content

## Troubleshooting

### "401 Unauthorized"

- Token expired or revoked
- Insufficient scopes
- Wrong token for the project

### Webhook not triggering

1. Check webhook logs: Project → Settings → Webhooks → Edit → Recent Deliveries
2. Verify URL is accessible from GitLab
3. Check secret matches

### "403 Forbidden"

- User/token doesn't have access to the project
- Project visibility settings
- IP restrictions on GitLab

### Rate Limiting

GitLab rate limits:
- 2,000 requests per minute (authenticated)
- 500 requests per minute (unauthenticated)

If hitting limits:
- Use project access tokens (per-project limits)
- Enable caching in Loom
- Reduce review frequency

### Comments not appearing

1. Verify write access to repository
2. Check MR is not in a read-only state
3. Ensure MR is not from a fork with restricted access

### Self-Managed Connection Issues

1. Verify GITLAB_HOST is correct
2. Check firewall allows connection
3. Verify SSL certificate is valid or CA is trusted
4. Test API manually:
   ```bash
   curl -H "PRIVATE-TOKEN: your-token" \
     https://gitlab.your-company.com/api/v4/projects
   ```
