# Configuration Examples

This directory contains ready-to-use Loom configurations for common scenarios.

---

## Quick Start

1. Copy an example to your repository:
```bash
mkdir -p .loom
cp examples/minimal.yaml .loom/config.yaml
```

2. Set environment variables:
```bash
export OPENAI_API_KEY=sk-...
```

3. Push a PR and watch Loom review it!

---

## Available Examples

### [minimal.yaml](minimal.yaml)
**Best for:** Getting started quickly

The simplest possible configuration. Uses GPT-4 with a single review pipeline.

**Features:**
- Single LLM model (OpenAI GPT-4)
- One generic review pipeline
- Default settings

**Cost:** ~$0.10 per review (typical PR)

---

### [multi-llm.yaml](multi-llm.yaml)
**Best for:** Optimizing cost and quality

Uses different LLM providers for different review types:
- GPT-4 for security (highest quality)
- Claude for code quality (excellent at code)
- Ollama for documentation (free, runs locally)

**Features:**
- 3 different LLM providers
- Cost-optimized pipeline assignment
- Local model for non-critical checks

**Cost:** ~$0.15 per review (mixed models)

---

### [enterprise.yaml](enterprise.yaml)
**Best for:** Large teams, production environments

Comprehensive configuration with 8 different pipelines covering:
- Security (OWASP, secrets detection)
- Code quality (style, clean code)
- Performance (algorithms, database queries)
- Documentation (API docs, README updates)

**Features:**
- Multiple severity levels
- Path filtering per pipeline
- Comprehensive trigger rules
- Comment limits to avoid spam
- Parallel pipeline execution

**Cost:** ~$0.40 per review (many pipelines)

---

### [python.yaml](python.yaml)
**Best for:** Python projects (Django, Flask, FastAPI)

Python-specific reviews:
- Security (SQL injection, XSS, etc.)
- PEP 8 style compliance
- Type hints validation
- Framework-specific patterns (Django/Flask)

**Features:**
- Python-focused prompts
- Excludes test files appropriately
- Checks migrations and models

**Cost:** ~$0.12 per review

---

### [javascript.yaml](javascript.yaml)
**Best for:** Node.js and React projects

JavaScript/TypeScript reviews:
- JS security (XSS, prototype pollution)
- React best practices
- TypeScript type safety
- Node.js backend patterns

**Features:**
- Separate checks for frontend/backend
- React component patterns
- TypeScript strict mode compliance

**Cost:** ~$0.15 per review

---

### [security-focused.yaml](security-focused.yaml)
**Best for:** Security-critical applications

Maximum security focus with 9 security pipelines:
- OWASP Top 10
- Injection attacks
- Authentication/Authorization
- Cryptography
- Secrets detection
- Input validation
- API security
- Database security
- Dependency vulnerabilities

**Features:**
- ALL findings are blockers
- No author exclusions
- Reviews even 1-line changes
- High comment limits (100+ comments)
- No config caching

**Cost:** ~$0.80 per review (comprehensive security)

---

### [alternative-providers.yaml](alternative-providers.yaml)
**Best for:** Cost optimization, avoiding vendor lock-in

Uses alternative LLM providers:
- **Groq** - Ultra-fast inference (70B Llama model)
- **Together.ai** - Open models, good pricing
- **OpenRouter** - Unified API for many models
- **Ollama** - Local, completely free

**Features:**
- Mix of cloud and local models
- Cost-effective options
- Fast inference with Groq
- Zero cost option with Ollama

**Cost:** ~$0.05 per review (much cheaper!)

---

### [monorepo.yaml](monorepo.yaml)
**Best for:** Projects with multiple services/packages

Handles complex monorepo structures:
- Backend service (Python)
- Frontend service (React)
- Mobile app (React Native)
- Shared libraries
- Infrastructure as Code (Terraform, K8s)

**Features:**
- Path-based pipeline routing
- Service-specific checks
- IaC security reviews
- Shared library type checking

**Cost:** ~$0.30 per review

---

## Customization Guide

### 1. Choose a Base Configuration

Pick the example closest to your needs:
- Solo developer? → `minimal.yaml`
- Team project? → `enterprise.yaml`
- Specific language? → `python.yaml` or `javascript.yaml`
- Security focus? → `security-focused.yaml`
- Budget-conscious? → `alternative-providers.yaml`

### 2. Adjust LLM Models

```yaml
models:
  your-model:
    base_url: https://api.provider.com/v1
    api_key_env: YOUR_API_KEY_ENV_VAR
    model: model-name
    temperature: 0.0  # 0.0 = deterministic
    max_tokens: 4000  # Response length
```

### 3. Configure Pipelines

```yaml
pipelines:
  - name: your-check
    model: your-model
    prompt_file: prompts/your-check.md
    severity: blocker|warning|info
    include_paths:  # Optional
      - "src/**/*.py"
    exclude_paths:  # Optional
      - "tests/**"
```

### 4. Set Triggers

```yaml
triggers:
  branches:  # Which branches to review
    - main
    - develop
  
  ignore_authors:  # Skip these users
    - bot-name[bot]
  
  max_changes: 2000  # Skip huge PRs
```

### 5. Configure Output

```yaml
output:
  summary: true  # Post summary comment
  inline_comments: true  # Post inline code comments
  min_severity: warning  # Filter by severity
  max_comments: 30  # Limit total comments
```

---

## Environment Variables

All examples require API keys as environment variables:

```bash
# OpenAI
export OPENAI_API_KEY=sk-...

# Anthropic (Claude)
export ANTHROPIC_API_KEY=sk-ant-...

# Groq
export GROQ_API_KEY=gsk-...

# Together.ai
export TOGETHER_API_KEY=...

# OpenRouter
export OPENROUTER_API_KEY=sk-or-...

# Ollama (local - no key needed)
# Just start Ollama: ollama serve
```

---

## Cost Comparison

Estimated costs per typical review (500 lines changed):

| Configuration | Cost/Review | Speed | Quality |
|---------------|-------------|-------|---------|
| minimal.yaml | $0.10 | Fast | Good |
| multi-llm.yaml | $0.15 | Fast | Excellent |
| enterprise.yaml | $0.40 | Medium | Excellent |
| python.yaml | $0.12 | Fast | Very Good |
| javascript.yaml | $0.15 | Fast | Very Good |
| security-focused.yaml | $0.80 | Slow | Excellent |
| alternative-providers.yaml | $0.05 | Very Fast | Good |
| monorepo.yaml | $0.30 | Medium | Excellent |

**Notes:**
- Costs assume OpenAI GPT-4 pricing (~$0.03/1k input tokens)
- Actual costs vary by PR size
- Alternative providers can be 10x cheaper
- Ollama is completely free (local)

---

## Testing Your Configuration

Before deploying, test your config:

1. **Validate syntax:**
```bash
# Install yamllint
pip install yamllint

# Check syntax
yamllint .loom/config.yaml
```

2. **Dry run:**
```bash
# Test on a sample PR (when Loom CLI is available)
loom review --dry-run --pr 123
```

3. **Start small:**
- Begin with 1-2 pipelines
- Add more gradually
- Monitor costs

---

## Common Modifications

### Add a New Pipeline

```yaml
pipelines:
  - name: accessibility
    model: default
    prompt_file: prompts/a11y.md
    severity: warning
    include_paths:
      - "src/**/*.tsx"
      - "src/**/*.jsx"
```

### Change Severity Levels

```yaml
pipelines:
  - name: security
    severity: blocker  # Was: warning
```

### Exclude More Paths

```yaml
triggers:
  ignore_paths:
    - "*.md"
    - "docs/**"
    - "*.lock"
    - "vendor/**"  # NEW
    - "third_party/**"  # NEW
```

### Increase Comment Limits

```yaml
output:
  max_comments: 100  # Was: 30
  max_comments_per_file: 20  # Was: 10
```

---

## Next Steps

1. Copy an example: `cp examples/minimal.yaml .loom/config.yaml`
2. Create prompts: See [Prompt Format Guide](../prompt-format.md)
3. Set API keys: Export environment variables
4. Test: Open a PR and watch Loom work!

---

## Support

- **Documentation:** [Configuration Schema](../config-schema.md)
- **Prompts:** [Prompt Format](../prompt-format.md)
- **Issues:** [GitHub Issues](https://github.com/your-org/loom/issues)
