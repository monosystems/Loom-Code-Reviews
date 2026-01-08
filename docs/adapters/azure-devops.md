# Azure DevOps Integration

This guide covers setting up Loom with Azure DevOps (Cloud and Server).

## Table of Contents

- [Overview](#overview)
- [Quick Setup](#quick-setup)
- [OAuth App Registration](#oauth-app-registration)
- [Personal Access Token](#personal-access-token)
- [Service Hooks](#service-hooks)
- [Azure DevOps Server](#azure-devops-server)
- [Troubleshooting](#troubleshooting)

## Overview

Loom integrates with Azure DevOps using:
- OAuth or Personal Access Tokens for API access
- Service Hooks for webhook notifications

## Quick Setup

### 1. Create Personal Access Token

1. Azure DevOps → User Settings → Personal Access Tokens
2. New Token:
   - **Name**: Loom Code Reviews
   - **Organization**: Select your org
   - **Expiration**: Set appropriate date
   - **Scopes**:
     - Code: Read
     - Pull Request Threads: Read & Write

### 2. Configure Loom

```bash
AZURE_DEVOPS_ORG=your-organization
AZURE_DEVOPS_TOKEN=your-pat-token
```

### 3. Create Service Hook

Project Settings → Service Hooks → Create subscription

## OAuth App Registration

### Register Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Azure Active Directory → App registrations → New registration
3. Configure:
   - **Name**: Loom Code Reviews
   - **Redirect URI**: `https://your-loom/api/auth/callback/azure-devops`
   - **Supported account types**: Accounts in this organizational directory only

### Configure API Permissions

1. API permissions → Add permission → Azure DevOps
2. Add:
   - `vso.code` - Code read
   - `vso.code_write` - Code write (for reviews)

### Configure Loom

```bash
AZURE_DEVOPS_CLIENT_ID=your-app-id
AZURE_DEVOPS_CLIENT_SECRET=your-client-secret
AZURE_DEVOPS_TENANT_ID=your-tenant-id
AZURE_DEVOPS_ORG=your-organization
```

## Personal Access Token

### Create PAT

1. Azure DevOps → User Settings (top right) → Personal Access Tokens
2. New Token:
   - **Organization**: All accessible organizations (or specific)
   - **Scopes** (Custom defined):
     - Code: Read
     - Pull Request Threads: Read & Write
     - Build: Read (optional)

### Configure

```bash
AZURE_DEVOPS_ORG=your-organization
AZURE_DEVOPS_TOKEN=your-pat-token
```

## Service Hooks

Azure DevOps uses Service Hooks instead of traditional webhooks.

### Create Service Hook

1. Project Settings → Service Hooks
2. Create subscription → Web Hooks
3. Configure:

**Trigger:**
- Pull request created
- Pull request updated

**Action:**
- **URL**: `https://your-loom/api/webhooks/azure-devops`
- **HTTP headers**: (optional) Add auth header
- **Resource details**: Send all

### Multiple Events

Create separate hooks for each event type:
- Pull request created
- Pull request updated
- Pull request commented on

### Secure Webhook

Add basic auth or custom header:

```bash
# In Loom
AZURE_DEVOPS_WEBHOOK_USERNAME=loom
AZURE_DEVOPS_WEBHOOK_PASSWORD=your-secret

# In Service Hook URL
https://loom:your-secret@your-loom/api/webhooks/azure-devops
```

## Azure DevOps Server

For on-premises Azure DevOps Server:

### Configure

```bash
AZURE_DEVOPS_HOST=https://devops.your-company.com
AZURE_DEVOPS_COLLECTION=DefaultCollection
AZURE_DEVOPS_TOKEN=your-pat-token
```

### SSL Certificates

```bash
NODE_EXTRA_CA_CERTS=/path/to/ca-cert.pem
```

## Permissions

### Required PAT Scopes

| Scope | Why |
|-------|-----|
| Code (Read) | Read repository content |
| Pull Request Threads (Read & Write) | Read PRs, post comments |

### Optional Scopes

| Scope | Why |
|-------|-----|
| Build (Read) | Check build status |
| Work Items (Read) | Link to work items |

## API Details

### Base URL Structure

```
https://dev.azure.com/{organization}/{project}/_apis/
```

### Git API

```
https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repositoryId}/pullRequests
```

## Troubleshooting

### "TF401019: The Git repository does not exist"

- Check project and repository names
- Verify token has access to the repository

### "TF400813: The user is not authorized"

- Token doesn't have required scopes
- Token expired
- User removed from project

### Service Hook not triggering

1. Check Service Hook history: Project Settings → Service Hooks → Select hook → History
2. Verify URL is accessible from Azure DevOps
3. Check for network/firewall issues

### Rate Limiting

Azure DevOps limits:
- 200 requests per 10 seconds (per PAT)

If hitting limits:
- Use separate tokens per project
- Enable caching in Loom

### Organization vs Collection

- **Azure DevOps Services (Cloud)**: Use organization name
- **Azure DevOps Server**: Use collection name (usually "DefaultCollection")

```bash
# Cloud
AZURE_DEVOPS_ORG=my-organization

# Server
AZURE_DEVOPS_HOST=https://devops.company.com
AZURE_DEVOPS_COLLECTION=DefaultCollection
```
