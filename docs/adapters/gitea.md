# Gitea / Forgejo Integration

This guide covers setting up Loom with Gitea and Forgejo (community fork).

## Table of Contents

- [Overview](#overview)
- [Quick Setup](#quick-setup)
- [OAuth Application](#oauth-application)
- [Access Tokens](#access-tokens)
- [Webhook Configuration](#webhook-configuration)
- [Troubleshooting](#troubleshooting)

## Overview

Gitea and Forgejo are lightweight, self-hosted Git services. Loom supports both with the same adapter.

## Quick Setup

### 1. Create Access Token

1. User Settings → Applications → Generate New Token
2. Select permissions:
   - `repository`: Read and Write
   - `user`: Read

### 2. Configure Loom

```bash
GITEA_HOST=https://gitea.your-company.com
GITEA_TOKEN=your-access-token
```

### 3. Create Webhook

Repository Settings → Webhooks → Add Webhook → Gitea

## OAuth Application

### Create Application

1. User Settings → Applications → Manage OAuth2 Applications
2. Create application:
   - **Name**: Loom Code Reviews
   - **Redirect URI**: `https://your-loom/api/auth/callback/gitea`

### Configure

```bash
GITEA_HOST=https://gitea.your-company.com
GITEA_CLIENT_ID=your-client-id
GITEA_CLIENT_SECRET=your-client-secret
```

## Access Tokens

### Personal Access Token

1. User Settings → Applications
2. Generate token with scopes:
   - `repo` - Repository access
   - `read:user` - User info

### Configure

```bash
GITEA_HOST=https://gitea.your-company.com
GITEA_TOKEN=your-personal-token
```

## Webhook Configuration

### Create Webhook

1. Repository → Settings → Webhooks
2. Add Webhook → Gitea
3. Configure:
   - **Target URL**: `https://your-loom/api/webhooks/gitea`
   - **HTTP Method**: POST
   - **Content Type**: application/json
   - **Secret**: Generate random string
   - **Trigger On**:
     - ✅ Pull Request
     - ✅ Pull Request Comment

### Set Secret

```bash
GITEA_WEBHOOK_SECRET=your-webhook-secret
```

## Forgejo

Forgejo is a fork of Gitea with the same API. Use the Gitea adapter:

```bash
# Same configuration, just point to Forgejo instance
GITEA_HOST=https://forgejo.your-company.com
GITEA_TOKEN=your-token
```

## Permissions

| Scope | Why |
|-------|-----|
| `repo` | Read code, read/write PRs |
| `read:user` | Read user info for auth |

## Troubleshooting

### Connection refused

- Verify GITEA_HOST is correct
- Check firewall allows connection
- Verify SSL certificate

### Webhook not triggering

1. Check webhook delivery log in repository settings
2. Verify URL is accessible from Gitea server
3. Check secret matches

### API version issues

Loom requires Gitea 1.16+ or Forgejo 1.18+. Check version:
```bash
curl https://gitea.your-company.com/api/v1/version
```
