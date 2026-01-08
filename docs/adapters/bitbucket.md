# Bitbucket Integration

This guide covers setting up Loom with Bitbucket Cloud and Bitbucket Server (Data Center).

## Table of Contents

- [Overview](#overview)
- [Bitbucket Cloud](#bitbucket-cloud)
- [Bitbucket Server / Data Center](#bitbucket-server--data-center)
- [Webhook Configuration](#webhook-configuration)
- [Troubleshooting](#troubleshooting)

## Overview

Loom supports both Bitbucket products:
- **Bitbucket Cloud** (bitbucket.org)
- **Bitbucket Server / Data Center** (self-hosted)

## Bitbucket Cloud

### OAuth Consumer

1. Go to Workspace Settings → OAuth consumers
2. Add consumer:
   - **Name**: Loom Code Reviews
   - **Callback URL**: `https://your-loom/api/auth/callback/bitbucket`
   - **Permissions**:
     - Account: Read
     - Repositories: Read, Write
     - Pull requests: Read, Write
3. Save Key and Secret

### Configure Loom

```bash
BITBUCKET_CLIENT_ID=your-oauth-key
BITBUCKET_CLIENT_SECRET=your-oauth-secret
```

### App Password (Alternative)

For simpler setups:

1. Personal Settings → App passwords
2. Create password with:
   - **Label**: Loom
   - **Permissions**:
     - Account: Read
     - Repositories: Read, Write
     - Pull requests: Read, Write

```bash
BITBUCKET_USERNAME=your-username
BITBUCKET_APP_PASSWORD=your-app-password
```

## Bitbucket Server / Data Center

### Personal Access Token

1. User Settings → Personal access tokens
2. Create token:
   - **Name**: Loom Code Reviews
   - **Permissions**: Repository read, write

### Configure Loom

```bash
BITBUCKET_SERVER_HOST=https://bitbucket.your-company.com
BITBUCKET_SERVER_TOKEN=your-personal-access-token
```

### HTTP Access Token (Project/Repo Level)

1. Repository Settings → Access tokens
2. Create token with appropriate permissions

## Webhook Configuration

### Bitbucket Cloud

1. Repository Settings → Webhooks
2. Add webhook:
   - **URL**: `https://your-loom/api/webhooks/bitbucket`
   - **Triggers**:
     - Pull Request: Created, Updated
     - Pull Request: Comment added

### Bitbucket Server

1. Repository Settings → Webhooks
2. Add webhook:
   - **URL**: `https://your-loom/api/webhooks/bitbucket-server`
   - **Events**:
     - `pr:opened`
     - `pr:from_ref_updated`
     - `pr:comment:added`

### Set Secret

```bash
BITBUCKET_WEBHOOK_SECRET=your-webhook-secret
```

## Permissions

### Required

| Permission | Why |
|------------|-----|
| Repository Read | Read code and PR info |
| Repository Write | Post PR comments |
| Pull Request Read | Access PR details |
| Pull Request Write | Post reviews |

## Troubleshooting

### "401 Unauthorized"

- App password or token expired
- Insufficient permissions
- Two-factor authentication issues

### Webhook issues

- Bitbucket Cloud: Check webhook history in repository settings
- Verify URL is publicly accessible
- Check for IP allowlist restrictions

### Rate Limiting

Bitbucket Cloud limits:
- 1,000 requests per hour

If hitting limits:
- Use workspace-level tokens
- Enable caching in Loom

### SSL Issues (Server)

```bash
NODE_EXTRA_CA_CERTS=/path/to/ca-cert.pem
```
