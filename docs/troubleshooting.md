# Troubleshooting Guide

This guide covers common issues and their solutions when running Loom Code Reviews.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [Authentication Problems](#authentication-problems)
- [Webhook Issues](#webhook-issues)
- [LLM Provider Issues](#llm-provider-issues)
- [Review Problems](#review-problems)
- [Performance Issues](#performance-issues)
- [Database Issues](#database-issues)
- [Configuration Errors](#configuration-errors)
- [Platform-Specific Issues](#platform-specific-issues)
- [Getting Help](#getting-help)

---

## Quick Diagnostics

### Health Check

```bash
# Docker
docker exec loom curl -f http://localhost:3000/api/health

# Docker Compose
docker compose exec web curl -f http://localhost:3000/api/health
```

**Expected response:**
```json
{"status": "ok", "database": "connected", "worker": "running"}
```

### View Logs

```bash
# Docker - Last 100 lines
docker logs --tail 100 loom

# Docker - Follow live
docker logs -f loom

# Docker Compose
docker compose logs -f web
docker compose logs -f worker

# Filter for errors
docker logs loom 2>&1 | grep -i error
```

### Check Running Services

```bash
# Docker
docker ps | grep loom

# Docker Compose
docker compose ps
```

---

## Installation Issues

### "Loom won't start"

**Symptoms:** Container exits immediately after starting

**Check logs:**
```bash
docker logs loom
```

**Common causes:**

<details>
<summary><strong>Missing BETTER_AUTH_SECRET</strong></summary>

**Error in logs:**
```
Error: BETTER_AUTH_SECRET is required
```

**Fix:**
```bash
# Generate a secret
export SECRET=$(openssl rand -hex 32)

# Add to docker run
docker run -e BETTER_AUTH_SECRET=$SECRET ...

# Or add to .env file
echo "BETTER_AUTH_SECRET=$SECRET" >> .env
```
</details>

<details>
<summary><strong>Invalid DATABASE_URL</strong></summary>

**Error in logs:**
```
Error: Invalid DATABASE_URL format
```

**Fix - SQLite:**
```bash
DATABASE_URL=file:/data/loom.db
```

**Fix - PostgreSQL:**
```bash
DATABASE_URL=postgres://user:password@host:5432/database
```

Check connection string format:
- Username and password are correct
- Host and port are reachable
- Database exists
</details>

<details>
<summary><strong>Port already in use</strong></summary>

**Error in logs:**
```
Error: listen EADDRINUSE: address already in use :::3000
```

**Fix - Use different port:**
```bash
docker run -p 3001:3000 ...  # Host port 3001 instead
```

**Or - Stop conflicting service:**
```bash
# Find what's using port 3000
lsof -i :3000  # Linux/Mac
netstat -ano | findstr :3000  # Windows

# Stop the service or kill the process
```
</details>

### "Cannot connect to database"

**Symptoms:** Web app starts but can't access database

**For PostgreSQL:**

```bash
# Test connection from container
docker exec loom pg_isready -h db -U loom

# Test with psql
docker exec -it loom psql $DATABASE_URL
```

**Common fixes:**
- Database not ready yet - add `depends_on` with health check
- Wrong credentials in DATABASE_URL
- Firewall blocking connection
- Database not accepting connections from container network

**For SQLite:**

```bash
# Check file permissions
docker exec loom ls -la /data/
```

**Fix permissions:**
```bash
docker exec loom chown -R 1000:1000 /data
```

### "Pull access denied" when pulling Docker image

**Error:**
```
Error response from daemon: pull access denied for ghcr.io/loom-reviews/loom
```

**Fixes:**
1. Check image name is correct
2. Try `docker login ghcr.io` if using private images
3. Pull latest tag explicitly: `ghcr.io/loom-reviews/loom:latest`
4. Check internet connection

---

## Authentication Problems

### "Cannot sign in with GitHub"

**Symptoms:** Redirect loop, OAuth error, or "unauthorized client"

**Checklist:**

1. **Verify OAuth credentials:**
   ```bash
   # These must be set
   echo $GITHUB_CLIENT_ID
   echo $GITHUB_CLIENT_SECRET
   ```

2. **Check callback URL:**
   - In GitHub OAuth App settings
   - Must match: `https://your-loom-instance.com/api/auth/callback/github`
   - Use `http://localhost:3000` for local testing
   - Protocol (http/https) must match exactly

3. **Verify BETTER_AUTH_URL:**
   ```bash
   # Must match your actual URL
   BETTER_AUTH_URL=https://loom.yourdomain.com
   ```

4. **Check application approval:**
   - GitHub App might require admin approval
   - Check organization settings if using org account

**GitHub Enterprise:**
```bash
# Set your GHE host
GITHUB_ENTERPRISE_HOST=github.your-company.com
```

### "Session expired" repeatedly

**Causes:**
- BETTER_AUTH_SECRET changed (invalidates all sessions)
- Cookie domain mismatch
- Time sync issues

**Fixes:**
```bash
# Clear browser cookies for the domain
# Or use incognito/private window

# Ensure consistent secret
echo $BETTER_AUTH_SECRET  # Should be 32+ characters

# Check server time
docker exec loom date
```

### "Email/password signup not working"

**Check SMTP configuration:**
```bash
# Required for email verification
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
EMAIL_FROM=noreply@your-domain.com
```

**Test SMTP:**
```bash
# From within container
docker exec -it loom sh
nc -zv $SMTP_HOST $SMTP_PORT
```

---

## Webhook Issues

### "Webhooks not triggering reviews"

**Symptoms:** PRs opened but no review appears

**Diagnostic steps:**

**1. Check webhook delivery (GitHub):**
- Repository → Settings → Webhooks → Your webhook
- Click "Recent Deliveries"
- Look for failed deliveries (red X)

**2. Verify webhook URL:**
```bash
# Must be publicly accessible from git platform
curl https://your-loom-instance.com/api/webhooks/github

# Should return "Method not allowed" (POST required)
```

**3. Check webhook secret:**
```bash
# Must match in both places
echo $GITHUB_WEBHOOK_SECRET

# In GitHub webhook settings
# In Loom environment
```

**4. Check Loom logs:**
```bash
docker logs loom 2>&1 | grep webhook
docker logs loom 2>&1 | grep "POST /api/webhooks"
```

**Common issues:**

<details>
<summary><strong>Webhook URL not accessible</strong></summary>

**Problem:** GitHub can't reach your Loom instance

**Fixes:**
- Not on localhost? Use ngrok for testing:
  ```bash
  ngrok http 3000
  # Use the ngrok URL in webhook settings
  ```
- Check firewall allows inbound HTTPS
- Verify DNS resolves correctly
- Check reverse proxy configuration
</details>

<details>
<summary><strong>Invalid signature</strong></summary>

**Error in logs:**
```
Webhook signature verification failed
```

**Fix:**
```bash
# Regenerate webhook secret
NEW_SECRET=$(openssl rand -hex 32)

# Update in GitHub webhook settings
# Update in Loom environment
export GITHUB_WEBHOOK_SECRET=$NEW_SECRET
docker restart loom
```
</details>

<details>
<summary><strong>Webhook delivered but no review</strong></summary>

**Check:**
1. Repository is enabled in Loom dashboard
2. PR matches trigger rules (branch, paths, size)
3. Worker is running:
   ```bash
   docker compose ps worker
   docker compose logs worker
   ```
4. Job is in queue:
   ```bash
   # Check database
   docker exec -it loom-db psql -U loom -c \
     "SELECT id, status, created_at FROM jobs ORDER BY created_at DESC LIMIT 5;"
   ```
</details>

### "Webhook secret mismatch"

**Different platforms use different methods:**

| Platform | Header | Method |
|----------|--------|--------|
| GitHub | `x-hub-signature-256` | HMAC SHA256 |
| GitLab | `x-gitlab-token` | Token comparison |
| Bitbucket | Custom header | Token comparison |

**Verify you're using correct secret variable:**
```bash
GITHUB_WEBHOOK_SECRET=...
GITLAB_WEBHOOK_SECRET=...
BITBUCKET_WEBHOOK_SECRET=...
```

---

## LLM Provider Issues

### "OpenAI API calls failing"

**Check API key:**
```bash
# Verify key is set
echo $OPENAI_API_KEY

# Test key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Common errors:**

<details>
<summary><strong>401 Unauthorized</strong></summary>

**Causes:**
- Invalid API key
- Key revoked
- Wrong key format

**Fix:**
- Regenerate key at platform.openai.com
- Ensure no extra spaces/quotes in env var
- Check key starts with `sk-`
</details>

<details>
<summary><strong>429 Rate Limited</strong></summary>

**Error:**
```
Rate limit exceeded
```

**Fixes:**
- Wait and retry (Loom does this automatically)
- Upgrade your OpenAI plan
- Use different model (cheaper = higher limits)
- Reduce review frequency
</details>

<details>
<summary><strong>Network timeout</strong></summary>

**Check network connectivity:**
```bash
docker exec loom curl -I https://api.openai.com
```

**If blocked:**
- Check firewall allows outbound HTTPS
- Use HTTP proxy if needed:
  ```bash
  HTTP_PROXY=http://proxy.company.com:8080
  HTTPS_PROXY=http://proxy.company.com:8080
  ```
</details>

### "Anthropic/Claude not working"

**Check API key:**
```bash
# Test key
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```

**Verify configuration:**
```yaml
models:
  claude:
    provider: anthropic  # Must be "anthropic" not "openai-compatible"
    model: claude-sonnet-4-20250514
    api_key_env: ANTHROPIC_API_KEY
```

### "Ollama connection refused"

**Symptoms:** Can't connect to local Ollama

**If Loom in Docker, Ollama on host:**
```yaml
# DON'T use localhost
base_url: http://localhost:11434  # ❌ Won't work

# DO use host.docker.internal
base_url: http://host.docker.internal:11434  # ✅ Works

# Or use host IP
base_url: http://192.168.1.100:11434  # ✅ Works
```

**Check Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

**Allow network access (if needed):**
```bash
# Linux
OLLAMA_HOST=0.0.0.0:11434 ollama serve

# Check it's accessible
curl http://YOUR_HOST_IP:11434/api/tags
```

### "LLM responses are garbage"

**Symptoms:** Reviews don't make sense, wrong format, hallucinations

**Fixes:**

1. **Lower temperature:**
   ```yaml
   models:
     default:
       temperature: 0.0  # More deterministic
   ```

2. **Better prompt:**
   - Be more specific about output format
   - Add examples of good vs bad responses
   - Use "Respond with JSON only, no other text"

3. **Try different model:**
   ```yaml
   model: gpt-4o  # Instead of gpt-3.5-turbo
   # Or
   model: claude-sonnet-4-20250514  # Claude often better at following instructions
   ```

4. **Check max_tokens:**
   ```yaml
   max_tokens: 4096  # May need more for complex reviews
   ```

---

## Review Problems

### "Reviews never complete"

**Check worker status:**
```bash
# Docker Compose
docker compose logs -f worker

# Look for:
# - Job started
# - Job completed/failed
```

**Check job queue:**
```bash
# How many pending jobs?
docker exec loom-db psql -U loom -d loom -c \
  "SELECT status, COUNT(*) FROM jobs GROUP BY status;"
```

**Common causes:**

<details>
<summary><strong>Worker not running</strong></summary>

**Fix:**
```bash
# Docker Compose
docker compose up -d worker

# Check it's running
docker compose ps worker
```
</details>

<details>
<summary><strong>Job timeout</strong></summary>

**Large PRs may exceed timeout**

**Increase timeout:**
```bash
JOB_TIMEOUT_MS=600000  # 10 minutes instead of 5
```

**Or skip large PRs:**
```yaml
triggers:
  max_changes: 1000
```
</details>

<details>
<summary><strong>Config parsing error</strong></summary>

**Check worker logs for:**
```
Error parsing .loom/config.yaml
```

**Validate your config:**
```bash
# Check YAML syntax
cat .loom/config.yaml | docker run -i --rm mikefarah/yq eval -

# Check for common issues
# - Indentation (use spaces, not tabs)
# - Missing colons
# - Quotes around special characters
```
</details>

### "Reviews are too slow"

**Typical review times:**
- Small PR (<100 lines): 10-30 seconds
- Medium PR (100-500 lines): 30-90 seconds
- Large PR (500+ lines): 1-5 minutes

**Optimization:**

1. **Use faster model:**
   ```yaml
   models:
     fast:
       model: gpt-4o-mini  # 5x faster than gpt-4o
   ```

2. **Reduce max_tokens:**
   ```yaml
   max_tokens: 2048  # Less generation time
   ```

3. **Limit scope:**
   ```yaml
   triggers:
     include_paths:
       - "src/**"  # Only review source code
   ```

4. **Skip trivial PRs:**
   ```yaml
   triggers:
     min_changes: 10  # Skip tiny PRs
   ```

### "Too many/too few comments"

**Too many:**
```yaml
output:
  max_comments: 10  # Limit total
  max_comments_per_file: 3  # Limit per file
```

**Too few:**
- Check LLM response in logs
- Prompt may be too restrictive
- Lower severity thresholds

**Filter by severity:**
```yaml
output:
  min_severity: warning  # Skip "info" level
```

### "Comments appear on wrong lines"

**Causes:**
- Line numbers calculated from diff
- PR updated after review started

**Mitigation:**
- Reviews are best on first commit
- Re-review if PR changes significantly

### "Reviews posted but not visible"

**Check permissions:**

**GitHub:**
- Token needs `repo` scope
- User needs write access to repository

**GitLab:**
- Token needs `api` scope
- User role: Developer or higher

**Check logs:**
```bash
docker logs loom 2>&1 | grep "post.*comment"
docker logs loom 2>&1 | grep -i "403\|401"
```

---

## Performance Issues

### "High memory usage"

**Check usage:**
```bash
docker stats loom
```

**Causes:**
- Too many concurrent workers
- Large diffs loaded in memory
- Config cache too large

**Fixes:**

1. **Reduce concurrency:**
   ```bash
   WORKER_CONCURRENCY=1  # Process 1 job at a time
   ```

2. **Limit PR size:**
   ```yaml
   triggers:
     max_changes: 2000
     max_files: 50
   ```

3. **Use PostgreSQL instead of SQLite:**
   - SQLite keeps entire DB in memory
   - PostgreSQL is more memory-efficient

4. **Set memory limits:**
   ```yaml
   # docker-compose.yml
   services:
     web:
       mem_limit: 512m
     worker:
       mem_limit: 1g
   ```

### "High CPU usage"

**Normal during reviews** (LLM processing)

**If constantly high:**
- Check for stuck jobs
- Reduce worker concurrency
- Check for infinite retry loops

### "Database growing too large"

**Clean up old data:**

```sql
-- Delete old completed jobs (PostgreSQL)
DELETE FROM jobs 
WHERE status = 'completed' 
  AND completed_at < NOW() - INTERVAL '30 days';

-- Delete old reviews
DELETE FROM reviews 
WHERE created_at < NOW() - INTERVAL '90 days';
```

**Automate cleanup:**
```bash
# Add to cron
0 2 * * 0 docker exec loom-db psql -U loom -c "DELETE FROM jobs WHERE status='completed' AND completed_at < NOW() - INTERVAL '30 days';"
```

---

## Database Issues

### "Database locked" (SQLite)

**Symptom:**
```
SQLITE_BUSY: database is locked
```

**Causes:**
- Multiple processes accessing SQLite
- Long-running transaction

**Fixes:**

1. **Use PostgreSQL for production:**
   - SQLite doesn't handle concurrency well
   - Switch to PostgreSQL

2. **Reduce concurrency:**
   ```bash
   WORKER_CONCURRENCY=1
   ```

3. **Enable WAL mode** (if staying on SQLite):
   ```sql
   PRAGMA journal_mode=WAL;
   ```

### "Migration failed"

**Symptoms:** Database schema out of date

**Fix - Run migrations manually:**
```bash
# Docker
docker exec loom pnpm db:migrate

# Kubernetes
kubectl exec -it deploy/loom-web -n loom -- pnpm db:migrate
```

**Reset database (DANGER - loses all data):**
```bash
# Backup first!
docker exec loom-db pg_dump -U loom loom > backup.sql

# Reset
docker exec loom pnpm db:push --force
```

---

## Configuration Errors

### "Invalid config.yaml"

**Error:**
```
Error: Invalid configuration at .loom/config.yaml
```

**Debug steps:**

1. **Validate YAML syntax:**
   ```bash
   cat .loom/config.yaml | docker run -i --rm mikefarah/yq eval -
   ```

2. **Check required fields:**
   - `models` must have at least one entry
   - Each pipeline needs `name` and `model`

3. **Common mistakes:**
   ```yaml
   # ❌ Wrong indentation
   models:
   default:
     provider: openai
   
   # ✅ Correct
   models:
     default:
       provider: openai
   
   # ❌ Missing quotes
   ignore_paths:
     - *.lock  # May fail if * interpreted as anchor
   
   # ✅ Correct
   ignore_paths:
     - "*.lock"
   ```

### "Prompt file not found"

**Error:**
```
Error: Could not load prompt file: .loom/prompts/security.md
```

**Fixes:**
- File must be committed to git (Loom reads from repo)
- Check path is relative to repo root
- Check file actually exists: `ls -la .loom/prompts/`

### "Model not found"

**Error:**
```
Error: Model 'default' not configured
```

**Fix:**
```yaml
# Ensure model is defined
models:
  default:  # This name must match
    provider: openai-compatible
    model: gpt-4o

pipelines:
  - name: review
    model: default  # References above
```

---

## Platform-Specific Issues

### GitHub

See detailed guide: [GitHub Troubleshooting](adapters/github.md#troubleshooting)

**Quick fixes:**
- "Resource not accessible" → Re-install GitHub App with correct permissions
- "Bad credentials" → Regenerate token/app credentials
- Rate limiting → Use GitHub App (higher limits)

### GitLab

See detailed guide: [GitLab Troubleshooting](adapters/gitlab.md#troubleshooting)

**Quick fixes:**
- "401 Unauthorized" → Check token hasn't expired
- "403 Forbidden" → User needs Developer role or higher
- Self-hosted SSL → Set `NODE_EXTRA_CA_CERTS`

### Bitbucket

See detailed guide: [Bitbucket Troubleshooting](adapters/bitbucket.md#troubleshooting)

**Quick fixes:**
- "401" → Regenerate app password
- Webhook not firing → Check webhook history in repo settings

### Gitea/Forgejo

See detailed guide: [Gitea Troubleshooting](adapters/gitea.md#troubleshooting)

**Quick fixes:**
- Connection refused → Verify GITEA_HOST
- API version → Requires Gitea 1.16+ or Forgejo 1.18+

### Azure DevOps

See detailed guide: [Azure DevOps Troubleshooting](adapters/azure-devops.md#troubleshooting)

**Quick fixes:**
- "TF401019" → Check repository exists
- "TF400813" → Token needs correct scopes
- Service Hook → Check hook delivery history

---

## Getting Help

### Before Asking for Help

Please gather this information:

1. **Loom version:**
   ```bash
   docker inspect loom | grep -i version
   ```

2. **Deployment method:**
   - Docker, Docker Compose, or Kubernetes?

3. **Logs:**
   ```bash
   docker logs loom > loom.log 2>&1
   ```

4. **Configuration:**
   - Sanitized `.env` (remove secrets!)
   - Sanitized `.loom/config.yaml`

5. **Error message:**
   - Full error from logs
   - Screenshot of error in UI

### Support Channels

- **GitHub Issues**: [Report bugs](https://github.com/loom-reviews/loom-reviews/issues)
  - Use for: Bugs, feature requests
  - Include: Version, logs, steps to reproduce

- **GitHub Discussions**: [Ask questions](https://github.com/loom-reviews/loom-reviews/discussions)
  - Use for: How-to questions, ideas
  - Search first - your question may be answered

- **Discord**: [Join the community](https://discord.gg/loom-reviews)
  - Use for: Quick questions, community help
  - Be patient - we're volunteers!

### Security Issues

**Do NOT post security vulnerabilities publicly!**

Email: security@loom-reviews.dev

See [Security Policy](../SECURITY.md) for details.

---

## Still Stuck?

If you've tried everything and still have issues:

1. **Try with minimal config:**
   ```yaml
   # Simplest possible config
   models:
     default:
       provider: openai-compatible
       model: gpt-4o
       api_key_env: OPENAI_API_KEY
   
   pipelines:
     - name: review
       model: default
   ```

2. **Test with fresh installation:**
   ```bash
   docker volume rm loom-data
   # Start fresh
   ```

3. **Enable debug mode:**
   ```bash
   LOG_LEVEL=debug
   ```
   ```yaml
   # In config.yaml
   advanced:
     debug: true
   ```

4. **Create minimal reproduction:**
   - Fresh repo
   - Simple test PR
   - Minimal config
   - Document exact steps

Then open an issue with all details!
