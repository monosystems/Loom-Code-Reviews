# Getting Started with Loom

This tutorial walks you through setting up Loom for the first time and running your first AI code review.

## Table of Contents

- [What You'll Need](#what-youll-need)
- [Quick Start (5 minutes)](#quick-start-5-minutes)
- [Step-by-Step Setup](#step-by-step-setup)
- [Your First Review](#your-first-review)
- [Customizing Reviews](#customizing-reviews)
- [Next Steps](#next-steps)

## What You'll Need

- **Docker** installed (or Node.js 20+ for development)
- **API key** from at least one LLM provider:
  - [OpenAI](https://platform.openai.com/api-keys) (recommended for beginners)
  - [Anthropic](https://console.anthropic.com/) (Claude)
  - [Ollama](https://ollama.com/) (local, free)
- **Git platform account**:
  - GitHub (personal or organization)
  - GitLab, Bitbucket, etc. (see adapter docs)

**Time required:** 5-15 minutes

## Quick Start (5 minutes)

The fastest way to try Loom:

### 1. Start Loom

```bash
docker run -d \
  --name loom \
  -p 3000:3000 \
  -v loom-data:/data \
  -e BETTER_AUTH_SECRET=$(openssl rand -hex 32) \
  -e OPENAI_API_KEY=sk-your-key-here \
  ghcr.io/loom-reviews/loom:latest
```

### 2. Open Dashboard

Open http://localhost:3000 in your browser.

### 3. Connect GitHub

1. Click **"Sign in with GitHub"**
2. Authorize Loom to access your repositories
3. Select a repository to enable reviews

### 4. Open a Test PR

Open or create a pull request in your connected repository. Loom will automatically review it!

**That's it!** You've completed your first AI code review. Continue reading to customize and optimize your setup.

---

## Step-by-Step Setup

### Step 1: Get an LLM API Key

Choose your provider:

<details>
<summary><strong>OpenAI (Recommended for beginners)</strong></summary>

1. Go to https://platform.openai.com/api-keys
2. Click **"Create new secret key"**
3. Name it "Loom Code Reviews"
4. Copy the key (starts with `sk-...`)
5. Keep it safe - you'll need it in Step 3

**Cost:** ~$0.02-0.10 per review with GPT-4o
</details>

<details>
<summary><strong>Anthropic (Claude) - Best for security reviews</strong></summary>

1. Go to https://console.anthropic.com/
2. Navigate to API Keys
3. Create a new key
4. Copy the key (starts with `sk-ant-...`)

**Cost:** ~$0.02-0.08 per review with Claude Sonnet
</details>

<details>
<summary><strong>Ollama (Local, Free) - Best for privacy</strong></summary>

1. Install Ollama: https://ollama.com/
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
2. Pull a code model:
   ```bash
   ollama pull codellama:13b
   ```
3. Ollama runs on http://localhost:11434 - no API key needed!

**Cost:** Free (requires GPU/powerful CPU)
</details>

### Step 2: Choose Deployment Method

<details>
<summary><strong>Option A: Docker (Recommended)</strong></summary>

**Requirements:** Docker 20.10+

```bash
# Create a volume for data persistence
docker volume create loom-data

# Generate a secure secret
export LOOM_SECRET=$(openssl rand -hex 32)

# Start Loom
docker run -d \
  --name loom \
  -p 3000:3000 \
  -v loom-data:/data \
  -e BETTER_AUTH_SECRET=$LOOM_SECRET \
  -e BETTER_AUTH_URL=http://localhost:3000 \
  -e OPENAI_API_KEY=sk-your-key-here \
  --restart unless-stopped \
  ghcr.io/loom-reviews/loom:latest
```

**Verify it's running:**
```bash
docker ps | grep loom
docker logs loom
```

Access at: http://localhost:3000
</details>

<details>
<summary><strong>Option B: Docker Compose (Production)</strong></summary>

**Requirements:** Docker Compose 2.0+

**1. Create project directory:**
```bash
mkdir loom && cd loom
```

**2. Create docker-compose.yml:**
```yaml
version: '3.8'

services:
  web:
    image: ghcr.io/loom-reviews/loom:latest
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://loom:loom@db:5432/loom
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - BETTER_AUTH_URL=${BETTER_AUTH_URL:-http://localhost:3000}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  worker:
    image: ghcr.io/loom-reviews/loom-worker:latest
    environment:
      - DATABASE_URL=postgres://loom:loom@db:5432/loom
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=loom
      - POSTGRES_PASSWORD=loom
      - POSTGRES_DB=loom
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U loom"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  postgres-data:
```

**3. Create .env file:**
```bash
# Generate secret
echo "BETTER_AUTH_SECRET=$(openssl rand -hex 32)" > .env

# Add other variables
cat >> .env << EOF
BETTER_AUTH_URL=http://localhost:3000
OPENAI_API_KEY=sk-your-key-here
EOF
```

**4. Start services:**
```bash
docker compose up -d
```

**5. Check logs:**
```bash
docker compose logs -f
```

Access at: http://localhost:3000
</details>

<details>
<summary><strong>Option C: Development Setup</strong></summary>

**Requirements:** Node.js 20+, pnpm 9+

```bash
# Clone repository
git clone https://github.com/loom-reviews/loom-reviews.git
cd loom-reviews

# Install dependencies
pnpm install

# Create .env file
cp .env.example .env

# Edit .env with your settings
nano .env  # or your preferred editor

# Run database migrations
pnpm db:migrate

# Start development server
pnpm dev
```

Access at: http://localhost:3000
</details>

### Step 3: Configure Environment Variables

At minimum, set these in your `.env` file or Docker environment:

```bash
# Required
BETTER_AUTH_SECRET=your-32-char-secret-here
DATABASE_URL=file:/data/loom.db  # SQLite (Docker) or Postgres

# LLM Provider (at least one)
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...
# or for Ollama
OLLAMA_HOST=http://localhost:11434
```

**For production deployments, also set:**
```bash
BETTER_AUTH_URL=https://loom.yourdomain.com
```

### Step 4: Access the Dashboard

1. Open http://localhost:3000 (or your configured URL)
2. You should see the Loom welcome screen

**First time?** You'll need to create an account:
- Click **"Sign in with GitHub"** (easiest)
- Or use email/password signup

### Step 5: Connect Your First Repository

**Using GitHub:**

1. After signing in, click **"Add Repository"**
2. You'll be redirected to GitHub to authorize Loom
3. Select repositories to give Loom access to
4. Click **"Install"** or **"Authorize"**
5. Back in Loom, select a repository from the list
6. Click **"Enable Reviews"**

**The repository is now connected!** Loom will automatically review new pull requests.

**Using other platforms?** See:
- [GitLab Setup](adapters/gitlab.md)
- [Bitbucket Setup](adapters/bitbucket.md)
- [Gitea Setup](adapters/gitea.md)
- [Azure DevOps Setup](adapters/azure-devops.md)

---

## Your First Review

### Test with a Sample PR

Let's create a test pull request to see Loom in action.

**1. Create a new branch:**
```bash
git checkout -b test/loom-review
```

**2. Make a simple change:**
```bash
# Add a file with a potential issue
cat > test.js << EOF
function processUser(user) {
  console.log("Processing: " + user.name);
  
  // SQL injection vulnerability (intentional for testing)
  const query = "SELECT * FROM users WHERE id = " + user.id;
  
  return query;
}
EOF

git add test.js
git commit -m "Add user processing function"
git push origin test/loom-review
```

**3. Create a pull request:**
- Go to your repository on GitHub/GitLab
- Create a PR from `test/loom-review` to `main`
- Wait a few seconds...

**4. See the review:**

Loom will:
1. Detect the new PR via webhook
2. Fetch the code changes
3. Analyze them with your LLM
4. Post review comments

You should see:
- ✅ A comment on the SQL injection vulnerability
- ✅ A summary of the review
- ✅ Inline comments on specific lines

**Example comment:**
> ⚠️ **Security Issue**: SQL Injection Vulnerability
> 
> Line 5: Building SQL queries with string concatenation is vulnerable to SQL injection attacks. Use parameterized queries instead.
>
> **Suggested fix:**
> ```javascript
> const query = "SELECT * FROM users WHERE id = ?";
> db.query(query, [user.id]);
> ```

### Understanding the Review

**What happened behind the scenes:**

```
1. PR opened → Webhook sent to Loom
2. Loom fetches .loom/config.yaml (or uses defaults)
3. Loom gets the diff from GitHub
4. Loom sends diff to OpenAI/Claude/etc
5. LLM analyzes and returns findings
6. Loom posts comments back to the PR
```

**Review took too long?** Check:
```bash
docker logs loom | grep -i error
```

**No review appeared?** See [Troubleshooting Guide](troubleshooting.md)

---

## Customizing Reviews

Now that you have a basic review working, let's customize it!

### Create a Custom Prompt

**1. In your repository, create `.loom/prompts/security.md`:**

```markdown
# Security Code Review

You are a security expert reviewing code for vulnerabilities.

## Focus Areas

Look for these security issues:
- SQL injection
- XSS (Cross-Site Scripting)
- Authentication bypasses
- Hardcoded secrets
- Unsafe deserialization

## Guidelines

- Only report actual security issues
- Explain the risk and impact
- Suggest specific fixes
- Reference CWE IDs when applicable

## Response Format

Respond with JSON only:

\```json
[
  {
    "file": "path/to/file",
    "line": 42,
    "severity": "blocker",
    "message": "Description and fix"
  }
]
\```

## Code Changes

{{diff}}
```

**2. Create `.loom/config.yaml`:**

```yaml
models:
  default:
    provider: openai-compatible
    model: gpt-4o
    api_key_env: OPENAI_API_KEY

pipelines:
  - name: security
    model: default
    prompt_file: .loom/prompts/security.md
    severity: blocker
```

**3. Commit and push:**

```bash
git add .loom/
git commit -m "Add custom Loom security review"
git push
```

**4. Open a new PR** - it will now use your custom prompt!

### Add Multiple Review Types

```yaml
# .loom/config.yaml
models:
  default:
    provider: openai-compatible
    model: gpt-4o
    api_key_env: OPENAI_API_KEY

pipelines:
  # Security review - highest priority
  - name: security
    model: default
    prompt_file: .loom/prompts/security.md
    severity: blocker
    
  # Code quality
  - name: quality
    model: default
    prompt_file: .loom/prompts/quality.md
    severity: warning
    
  # Documentation check
  - name: docs
    model: default
    prompt_file: .loom/prompts/docs.md
    severity: info
```

Create the corresponding prompt files in `.loom/prompts/`.

### Filter What Gets Reviewed

```yaml
# .loom/config.yaml
triggers:
  # Only review PRs to these branches
  branches:
    - main
    - develop
  
  # Ignore these files
  ignore_paths:
    - "*.lock"
    - "node_modules/**"
    - "docs/**"
  
  # Skip PRs from bots
  ignore_authors:
    - dependabot[bot]
    - renovate[bot]
  
  # Size limits
  max_changes: 1000  # Skip huge PRs
```

### Use Different Models

```yaml
models:
  # Fast model for simple checks
  fast:
    provider: openai-compatible
    model: gpt-4o-mini
    api_key_env: OPENAI_API_KEY
  
  # Best model for security
  security:
    provider: anthropic
    model: claude-sonnet-4-20250514
    api_key_env: ANTHROPIC_API_KEY
  
  # Local model for sensitive code
  local:
    provider: openai-compatible
    base_url: http://localhost:11434/v1
    model: codellama:13b

pipelines:
  - name: security
    model: security  # Uses Claude
    
  - name: quality
    model: fast      # Uses GPT-4o Mini
```

**See also:**
- [Full Configuration Reference](configuration.md)
- [Custom Prompts Guide](custom-prompts.md)
- [LLM Providers Setup](llm-providers.md)

---

## Next Steps

### Explore Features

- **[Custom Prompts](custom-prompts.md)** - Write sophisticated review logic
- **[Multiple LLM Providers](llm-providers.md)** - Mix and match models
- **[Platform Adapters](adapters/)** - GitLab, Bitbucket, Azure DevOps
- **[Configuration Reference](configuration.md)** - All available options

### Production Deployment

- **[Self-Hosting Guide](self-hosting.md)** - Docker Compose, Kubernetes
- **[Reverse Proxy Setup](self-hosting.md#reverse-proxy-setup)** - Nginx, Caddy
- **[Backup & Restore](self-hosting.md#backup-and-restore)** - Protect your data

### Advanced Usage

- **[Architecture Overview](architecture.md)** - How Loom works internally
- **[Contributing Guide](../CONTRIBUTING.md)** - Help improve Loom
- **[Migration Guide](migration.md)** - Switch from other tools

### Get Help

- **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions
- **GitHub Issues**: [Report bugs or request features](https://github.com/loom-reviews/loom-reviews/issues)
- **Discussions**: [Ask questions](https://github.com/loom-reviews/loom-reviews/discussions)

---

## Common Questions

<details>
<summary><strong>Can I use Loom without OpenAI?</strong></summary>

Yes! Loom supports:
- Anthropic (Claude)
- Google (Gemini)
- Ollama (local, free)
- Groq, Together AI, OpenRouter
- Any OpenAI-compatible API

See [LLM Providers](llm-providers.md) for setup.
</details>

<details>
<summary><strong>Does Loom store my code?</strong></summary>

No. Loom:
- Fetches code only when reviewing
- Processes it in memory
- Sends it to your chosen LLM
- Discards it after review

Only review results (comments, summaries) are stored.
</details>

<details>
<summary><strong>How much does it cost?</strong></summary>

Loom itself is free (AGPL license). Costs:
- **LLM API**: ~$0.02-0.10 per review (varies by provider/model)
- **Infrastructure**: $5-50/month for hosting (depends on scale)
- **Ollama**: Free (but requires hardware)

See [Cost Optimization](llm-providers.md#cost-optimization) for tips.
</details>

<details>
<summary><strong>Can I run this for a team?</strong></summary>

Yes! Loom supports:
- Multiple users
- Organizations/teams
- Shared configurations
- Multiple repositories

Use Docker Compose or Kubernetes for team deployments.
</details>

<details>
<summary><strong>What if my PRs are too large?</strong></summary>

Configure size limits:
```yaml
triggers:
  max_changes: 1000
  max_files: 30
```

Large PRs will be skipped automatically.
</details>

<details>
<summary><strong>How do I update Loom?</strong></summary>

**Docker:**
```bash
docker pull ghcr.io/loom-reviews/loom:latest
docker stop loom && docker rm loom
# Re-run with same options
```

**Docker Compose:**
```bash
docker compose pull
docker compose up -d
```

Migrations run automatically on startup.
</details>

---

## What's Next?

You now have a working Loom setup! Here are some ideas:

1. **Customize your prompts** to match your team's standards
2. **Add more repositories** to expand coverage
3. **Experiment with different LLMs** to find the best fit
4. **Set up production deployment** with HTTPS and backups
5. **Join the community** and share your experience

**Happy reviewing! 🧵**
