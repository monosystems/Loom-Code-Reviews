# Migration Guide

This guide helps you migrate from other AI code review tools to Loom.

## Table of Contents

- [Why Migrate to Loom?](#why-migrate-to-loom)
- [From PR-Agent](#from-pr-agent)
- [From CodeRabbit](#from-coderabbit)
- [From Amazon CodeGuru](#from-amazon-codeguru)
- [From Sourcery](#from-sourcery)
- [From GitHub Copilot Reviews](#from-github-copilot-reviews)
- [From Custom Scripts](#from-custom-scripts)
- [General Migration Steps](#general-migration-steps)
- [Comparison Matrix](#comparison-matrix)

---

## Why Migrate to Loom?

| Feature | Loom | Others |
|---------|------|--------|
| **Self-hosted** | ✅ Full control | ❌ SaaS only |
| **Any LLM** | ✅ OpenAI, Claude, Ollama, etc. | ❌ Locked to one |
| **Custom prompts** | ✅ Full control | ⚠️ Limited |
| **Open source** | ✅ AGPL-3.0 | ❌ Proprietary |
| **No seat limits** | ✅ Unlimited | ❌ Per-user pricing |
| **Data privacy** | ✅ Your infrastructure | ❌ Third-party |
| **Multi-platform** | ✅ GitHub, GitLab, etc. | ⚠️ Usually GitHub-only |

---

## From PR-Agent

[PR-Agent](https://github.com/Codium-ai/pr-agent) is an open-source AI code reviewer by Qodo (formerly CodiumAI).

### Similarities

✅ Both are open source  
✅ Both support custom prompts  
✅ Both support multiple LLM providers  
✅ Both work with GitHub  

### Differences

| Feature | PR-Agent | Loom |
|---------|----------|------|
| Architecture | CLI/bot | Web app + worker |
| Config format | TOML | YAML |
| Dashboard | ❌ No | ✅ Yes |
| Self-hosted UI | ❌ No | ✅ Yes |
| Database | ❌ Stateless | ✅ Persistent |

### Migration Steps

**1. Map your PR-Agent config to Loom:**

**PR-Agent** (`.pr_agent.toml`):
```toml
[config]
model = "gpt-4"
max_model_tokens = 8000

[pr_reviewer]
require_score_review = true
require_tests_review = true
```

**Loom** (`.loom/config.yaml`):
```yaml
models:
  default:
    provider: openai-compatible
    model: gpt-4
    max_tokens: 8000

pipelines:
  - name: code-review
    model: default
    prompt_file: .loom/prompts/review.md
  - name: test-coverage
    model: default
    prompt_file: .loom/prompts/tests.md
```

**2. Convert custom prompts:**

PR-Agent uses custom instructions. Loom uses full Markdown prompts.

**PR-Agent:**
```toml
[pr_reviewer]
extra_instructions = """
Focus on security issues.
Check for SQL injection.
"""
```

**Loom** (`.loom/prompts/review.md`):
```markdown
# Code Review

Focus on these areas:
- Security issues
- SQL injection vulnerabilities

## Response Format

\```json
[
  {"file": "...", "line": 1, "severity": "blocker", "message": "..."}
]
\```

## Code Changes

{{diff}}
```

**3. Set up webhooks:**

PR-Agent uses GitHub Actions or bot comments. Loom uses webhooks.

Remove PR-Agent GitHub Action and configure Loom webhook instead (see [Getting Started](getting-started.md)).

**4. Feature mapping:**

| PR-Agent Command | Loom Equivalent |
|------------------|-----------------|
| `/review` | Automatic on PR open |
| `/describe` | Add to pipeline with summary prompt |
| `/improve` | Use quality.md prompt |
| `/ask` | Not supported (yet) |
| `/update_changelog` | Custom script in pipeline |

### Example: PR-Agent → Loom

**Before (PR-Agent GitHub Action):**
```yaml
# .github/workflows/pr-agent.yml
name: PR Agent
on: pull_request

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: Codium-ai/pr-agent@main
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

**After (Loom):**
```yaml
# .loom/config.yaml
models:
  default:
    provider: openai-compatible
    model: gpt-4
    api_key_env: OPENAI_API_KEY

pipelines:
  - name: review
    model: default
```

Then install Loom as described in [Getting Started](getting-started.md).

---

## From CodeRabbit

CodeRabbit is a popular SaaS AI code review service.

### Key Differences

| Feature | CodeRabbit | Loom |
|---------|------------|------|
| Hosting | SaaS only | Self-hosted |
| Pricing | $12/user/month | Free (self-host) |
| LLM | Proprietary | Your choice |
| Customization | Limited | Full control |
| Data | On their servers | On your servers |

### Migration Steps

**1. Export data** (if possible):

CodeRabbit doesn't provide data export. Review history will be lost.

**2. Recreate configuration:**

**CodeRabbit settings** (UI-based):
- Review rules
- Ignored files
- Team preferences

**Loom** (`.loom/config.yaml`):
```yaml
triggers:
  branches: ["main", "develop"]
  ignore_paths: ["*.lock", "dist/**"]
  ignore_authors: ["dependabot[bot]"]

models:
  default:
    provider: openai-compatible
    model: gpt-4o
    api_key_env: OPENAI_API_KEY

pipelines:
  - name: security
    prompt_file: .loom/prompts/security.md
    severity: blocker
  - name: quality
    prompt_file: .loom/prompts/quality.md
    severity: warning
```

**3. Recreate custom rules:**

CodeRabbit's custom rules become Loom prompts:

**CodeRabbit:**  
*"Always check for SQL injection in database queries"*

**Loom** (`.loom/prompts/security.md`):
```markdown
# Security Review

## Focus Areas

1. **SQL Injection**
   - Check all database queries
   - Ensure parameterized queries are used
   - Flag any string concatenation in SQL

## Code Changes

{{diff}}
```

**4. Team rollout:**

1. Deploy Loom (see [Self-Hosting](self-hosting.md))
2. Connect repositories
3. Disable CodeRabbit on those repos
4. Announce to team with migration guide

### Cost Comparison

**CodeRabbit:**
- 10 developers = $120/month = $1,440/year

**Loom (self-hosted):**
- Server: $20/month = $240/year
- LLM API: ~$50/month = $600/year
- **Total:** $840/year

**Savings:** $600/year (42%)

---

## From Amazon CodeGuru

Amazon CodeGuru Reviewer is AWS's AI code review service.

### Migration Steps

**1. Feature mapping:**

| CodeGuru | Loom Equivalent |
|----------|-----------------|
| Security detector | `security.md` prompt |
| Code quality | `quality.md` prompt |
| Resource leak detection | Custom prompt |
| AWS best practices | Custom prompt for AWS |

**2. Config conversion:**

**CodeGuru:**  
Configured via AWS Console

**Loom:**
```yaml
# .loom/config.yaml
models:
  default:
    provider: openai-compatible
    model: gpt-4o
    api_key_env: OPENAI_API_KEY

pipelines:
  - name: security
    prompt_file: .loom/prompts/security.md
    
  - name: aws-best-practices
    prompt_file: .loom/prompts/aws.md
```

**3. AWS-specific prompt:**

Create `.loom/prompts/aws.md`:
```markdown
# AWS Best Practices Review

Check for:
- Hardcoded AWS credentials
- Public S3 buckets
- Overly permissive IAM policies
- Missing encryption on RDS/S3
- Resources in default VPC
- Missing CloudWatch logging

## Code Changes

{{diff}}
```

**4. Cost comparison:**

**CodeGuru:**
- $30 per 100,000 lines reviewed
- Expensive for large codebases

**Loom:**
- Fixed hosting + LLM costs
- Predictable pricing

---

## From Sourcery

Sourcery is a Python code improvement tool.

### Migration Steps

**1. Recreate Sourcery rules as Loom prompts:**

**Sourcery** (`.sourcery.yaml`):
```yaml
rules:
  - id: no-long-functions
    description: Functions should be less than 50 lines
    pattern: ...
```

**Loom** (`.loom/prompts/python.md`):
```markdown
# Python Code Review

## Rules

1. **Function Length**
   - Functions should be < 50 lines
   - Report functions > 50 lines with severity "warning"

2. **Type Hints**
   - All functions should have type hints
   - Report missing hints with severity "info"

## Code Changes

{{diff}}
```

**2. Language-specific focus:**

Loom works with any language. For Python:

```yaml
pipelines:
  - name: python-quality
    prompt_file: .loom/prompts/python.md
    include_paths:
      - "**/*.py"
```

---

## From GitHub Copilot Reviews

GitHub Copilot recently added PR review capabilities.

### Migration Steps

**1. Why switch?**

- **Self-hosted:** Keep code on your infrastructure
- **Custom prompts:** Define your own review criteria
- **Multi-platform:** Not locked to GitHub
- **Cost:** Free vs. Copilot Enterprise pricing

**2. Configuration:**

GitHub Copilot reviews are automatic with no config. In Loom:

```yaml
# .loom/config.yaml
models:
  default:
    provider: openai-compatible
    model: gpt-4o
    api_key_env: OPENAI_API_KEY

pipelines:
  - name: review
    model: default
```

**3. Advantages:**

- Loom gives you **full control** over prompts
- Can use **any LLM** (Claude often better for code)
- **Self-hosted** for data privacy
- **Persistent history** in dashboard

---

## From Custom Scripts

Many teams have built custom review scripts using ChatGPT/Claude API.

### Migration Path

**Your custom script:**
```python
import openai

def review_pr(diff):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a code reviewer."},
            {"role": "user", "content": f"Review this:\n{diff}"}
        ]
    )
    return response.choices[0].message.content
```

**Equivalent Loom setup:**

**`.loom/config.yaml`:**
```yaml
models:
  default:
    provider: openai-compatible
    model: gpt-4
    api_key_env: OPENAI_API_KEY

pipelines:
  - name: review
    model: default
    prompt_file: .loom/prompts/review.md
```

**`.loom/prompts/review.md`:**
```markdown
# Code Review

You are an expert code reviewer.

## Your Task

Review the following code changes for:
- Bugs
- Security issues
- Code quality

## Response Format

\```json
[
  {"file": "...", "line": 1, "severity": "warning", "message": "..."}
]
\```

## Code Changes

{{diff}}
```

**Advantages of migrating:**

✅ **No script maintenance** - Loom handles webhooks, parsing, posting  
✅ **Dashboard** - See review history, analytics  
✅ **Team collaboration** - Shared prompts, configs  
✅ **Reliability** - Job queue, retries, error handling  

---

## General Migration Steps

### Phase 1: Preparation (1-2 days)

1. **Inventory current setup:**
   - What tool are you using?
   - What customizations/rules?
   - What integrations?

2. **Plan Loom deployment:**
   - Choose hosting (Docker/Kubernetes/Cloud)
   - Decide on LLM provider
   - Plan network access (webhooks)

3. **Map configurations:**
   - Convert rules to prompts
   - Recreate ignore patterns
   - Document custom workflows

### Phase 2: Testing (3-5 days)

1. **Deploy Loom** in test environment
2. **Connect test repository**
3. **Create custom prompts** based on old rules
4. **Test with sample PRs:**
   - Compare old vs new reviews
   - Tune prompts
   - Adjust severity levels

5. **Validate results** with team

### Phase 3: Rollout (1-2 weeks)

1. **Deploy production Loom**
2. **Connect repositories** one at a time:
   - Start with low-traffic repos
   - Monitor and adjust
   - Roll out to critical repos

3. **Disable old tool** once confident

4. **Document for team:**
   - New workflow
   - How to customize
   - Where to get help

### Phase 4: Optimization (Ongoing)

1. **Gather feedback** from team
2. **Refine prompts** based on false positives/negatives
3. **Add new pipelines** as needed
4. **Monitor costs** and optimize

---

## Comparison Matrix

| Feature | Loom | PR-Agent | CodeRabbit | CodeGuru | Copilot |
|---------|------|----------|------------|----------|---------|
| **Open Source** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Self-hosted** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Any LLM** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Custom Prompts** | ✅ Full | ⚠️ Limited | ⚠️ Limited | ❌ | ❌ |
| **Dashboard** | ✅ | ❌ | ✅ | ✅ | ✅ |
| **GitHub** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **GitLab** | ✅ | ⚠️ Limited | ❌ | ❌ | ❌ |
| **Bitbucket** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Pricing** | Free* | Free | $12/user | Pay-per-use | $39/user |
| **Review History** | ✅ | ❌ | ✅ | ✅ | ⚠️ |
| **Team Features** | ✅ | ❌ | ✅ | ✅ | ✅ |
| **Local Models** | ✅ Ollama | ✅ | ❌ | ❌ | ❌ |

*Self-hosting costs + LLM API costs

---

## Common Migration Questions

### "Will I lose review history?"

Most tools don't provide data export. You'll start fresh with Loom, but:
- Old reviews stay in your git platform
- Loom builds new history going forward
- Consider exporting key metrics before switching

### "How long does migration take?"

Typical timeline:
- Simple setup: 1 day
- With custom prompts: 3-5 days
- Full team rollout: 1-2 weeks

### "Can I run both tools simultaneously?"

Yes, during transition:
- Keep old tool for critical repos
- Test Loom on less critical repos
- Gradually shift as confidence grows

### "What about team training?"

Loom is straightforward:
- Reviews appear automatically (like before)
- Config is in repository (version controlled)
- Dashboard is intuitive

Provide team with:
- [Getting Started Guide](getting-started.md)
- Access to Loom dashboard
- Custom prompt examples

### "How do costs compare?"

**SaaS tools** (per user/month):
- CodeRabbit: $12/user
- Copilot Enterprise: $39/user
- 10 developers = $120-390/month

**Loom (self-hosted)**:
- Hosting: $10-50/month
- LLM API: $30-100/month
- **Total:** $40-150/month (fixed)

**Break-even:** 2-4 developers

---

## Migration Support

Need help migrating?

1. **Read the docs:**
   - [Getting Started](getting-started.md)
   - [Configuration Reference](configuration.md)
   - [Custom Prompts](custom-prompts.md)

2. **Community support:**
   - [GitHub Discussions](https://github.com/loom-reviews/loom-reviews/discussions)
   - [Discord](https://discord.gg/loom-reviews)

3. **Professional services:**
   - Email: migrate@loom-reviews.dev
   - We can help with:
     - Migration planning
     - Prompt creation
     - Deployment setup
     - Team training

---

## Success Stories

> "Migrated from CodeRabbit to Loom in 2 days. Saved $1,200/year and got better reviews with custom prompts."
> — Engineering team at SaaS startup

> "PR-Agent was great, but we needed a dashboard and better team collaboration. Loom gives us both."
> — Senior DevOps Engineer

> "Running Loom with Ollama locally. Zero API costs and complete data privacy."
> — FinTech company

**Share your story!** Submit a PR to add your migration experience.

---

## Next Steps

1. ✅ Choose migration path based on your current tool
2. ✅ Read [Getting Started](getting-started.md)
3. ✅ Deploy test instance
4. ✅ Convert your custom rules to prompts
5. ✅ Test and refine
6. ✅ Roll out to team

**Ready to migrate?** [Get started now →](getting-started.md)
