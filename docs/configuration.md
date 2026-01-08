# Configuration Reference

Loom is configured via a `.loom/config.yaml` file in your repository. This document covers all available options.

## Table of Contents

- [Quick Start](#quick-start)
- [Full Example](#full-example)
- [Triggers](#triggers)
- [Models](#models)
- [Pipelines](#pipelines)
- [Output](#output)
- [Personas](#personas)
- [Advanced](#advanced)

## Quick Start

Create `.loom/config.yaml` in your repository root:

```yaml
# Minimal configuration
models:
  default:
    provider: openai-compatible
    model: gpt-4o
    api_key_env: OPENAI_API_KEY

pipelines:
  - name: review
    model: default
```

That's it! Loom will use the default system prompt for reviews.

## Full Example

```yaml
# .loom/config.yaml - Complete example with all options

# ============================================================
# TRIGGERS - When to run reviews
# ============================================================
triggers:
  # Only review PRs targeting these branches
  branches:
    - main
    - develop
    - "release/*"
  
  # Ignore these file patterns (glob syntax)
  ignore_paths:
    - "*.lock"
    - "*.min.js"
    - "*.min.css"
    - "docs/**"
    - "**/*.generated.ts"
    - ".loom/**"
  
  # Only review these paths (if set, overrides default "all files")
  include_paths:
    - "src/**"
    - "packages/**"
  
  # Skip PRs from these authors
  ignore_authors:
    - dependabot[bot]
    - renovate[bot]
    - github-actions[bot]
  
  # Only review PRs with these labels (if set)
  require_labels:
    - needs-review
  
  # Skip PRs with these labels
  ignore_labels:
    - skip-review
    - wip
  
  # Size limits
  min_changes: 5        # Skip PRs with fewer changed lines
  max_changes: 2000     # Skip PRs with more changed lines (too large)
  max_files: 50         # Skip PRs with more files changed

# ============================================================
# MODELS - LLM provider configurations
# ============================================================
models:
  # Default model for most reviews
  default:
    provider: openai-compatible
    base_url: https://api.openai.com/v1
    model: gpt-4o
    api_key_env: OPENAI_API_KEY
    temperature: 0.1
    max_tokens: 4096
  
  # Security-focused reviews (more capable model)
  security:
    provider: anthropic
    model: claude-sonnet-4-20250514
    api_key_env: ANTHROPIC_API_KEY
    temperature: 0.0
    max_tokens: 8192
  
  # Local model for sensitive code
  local:
    provider: openai-compatible
    base_url: http://localhost:11434/v1
    model: codellama:34b
    # No api_key_env needed for local Ollama
  
  # Fast model for simple checks
  fast:
    provider: openai-compatible
    base_url: https://api.groq.com/openai/v1
    model: llama-3.1-70b-versatile
    api_key_env: GROQ_API_KEY
  
  # Custom/self-hosted model
  company:
    provider: openai-compatible
    base_url: https://llm.internal.company.com/v1
    model: company-codereview-v2
    api_key_env: COMPANY_LLM_KEY
    headers:
      X-Custom-Header: some-value

# ============================================================
# PIPELINES - Review checks to run
# ============================================================
pipelines:
  # Security review - highest priority
  - name: security
    model: security
    prompt_file: .loom/prompts/security.md
    severity: blocker
    description: "Security vulnerability detection"
    
    # Only run on certain files
    include_paths:
      - "src/**"
      - "packages/**"
    
    # Skip test files for security review
    ignore_paths:
      - "**/*.test.ts"
      - "**/*.spec.ts"
  
  # Code quality review
  - name: quality
    model: default
    prompt_file: .loom/prompts/quality.md
    severity: warning
    description: "Code quality and best practices"
    
    # Provide additional context files
    context:
      - file: CONTRIBUTING.md
      - file: .eslintrc.js
      - file: tsconfig.json
  
  # Documentation check
  - name: docs
    model: fast
    prompt_file: .loom/prompts/docs.md
    severity: info
    description: "Documentation completeness"
    
    # Only check when source files change
    include_paths:
      - "src/**/*.ts"
      - "packages/**/*.ts"
  
  # Custom script check (non-LLM)
  - name: lint-check
    run: "npm run lint:check -- --format json"
    parse_output: json
    severity: warning
    description: "ESLint results"
  
  # Another script example
  - name: type-check
    run: "npx tsc --noEmit 2>&1 || true"
    parse_output: text
    severity: blocker
    description: "TypeScript type errors"
  
  # Conditional pipeline
  - name: migration-review
    model: default
    prompt_file: .loom/prompts/migration.md
    severity: blocker
    description: "Database migration review"
    
    # Only run when migration files are changed
    condition: "files.any(f => f.includes('/migrations/'))"

# ============================================================
# OUTPUT - How to format and post reviews
# ============================================================
output:
  # Output format: github-review, gitlab-note, inline-comments, json
  format: github-review
  
  # Group comments by severity or file
  group_by: severity  # or: file, pipeline
  
  # Maximum comments to post (prevents spam)
  max_comments: 20
  
  # Maximum inline comments per file
  max_comments_per_file: 5
  
  # Include a summary comment
  include_summary: true
  
  # Custom summary template (optional)
  summary_template: .loom/templates/summary.md
  
  # Review action: comment, approve, request_changes
  # - comment: Always post as comment
  # - approve: Approve if no blockers
  # - request_changes: Request changes if blockers found
  review_action: comment
  
  # Minimum severity to request changes
  request_changes_threshold: blocker

# ============================================================
# PERSONAS - Review styles/tones
# ============================================================
personas:
  # Strict reviewer for critical paths
  strict:
    tone: "Direct and concise"
    focus:
      - "Security vulnerabilities"
      - "Performance issues"
      - "Breaking changes"
    instructions: |
      Be very strict. Only mention significant issues.
      Do not comment on style or minor improvements.
      Every comment should be actionable.
  
  # Mentor for junior developers
  mentor:
    tone: "Encouraging and educational"
    focus:
      - "Best practices"
      - "Code readability"
      - "Learning opportunities"
    instructions: |
      Explain why something is an issue, not just what.
      Provide links to documentation when relevant.
      Acknowledge good practices you see.
  
  # Default persona (used if not specified)
  default:
    tone: "Professional and helpful"
    focus:
      - "Bugs and errors"
      - "Code quality"
      - "Documentation"

# ============================================================
# ADVANCED - Additional settings
# ============================================================
advanced:
  # Cache configuration responses (seconds)
  config_cache_ttl: 300
  
  # Retry failed LLM calls
  llm_retries: 2
  
  # Timeout for LLM calls (ms)
  llm_timeout: 60000
  
  # Enable debug logging for this repo
  debug: false
  
  # Custom environment variables to pass to scripts
  script_env:
    NODE_ENV: production
    CI: true
```

## Triggers

Control when Loom reviews PRs.

### branches

```yaml
triggers:
  branches:
    - main
    - develop
    - "feature/*"      # Glob patterns supported
    - "release/**"     # Double star for recursive
```

If not specified, all branches are reviewed.

### ignore_paths / include_paths

```yaml
triggers:
  # Ignore these paths
  ignore_paths:
    - "*.lock"
    - "vendor/**"
    - "node_modules/**"
  
  # Or explicitly include only these
  include_paths:
    - "src/**"
    - "lib/**"
```

Glob patterns follow [micromatch](https://github.com/micromatch/micromatch) syntax.

### ignore_authors

```yaml
triggers:
  ignore_authors:
    - dependabot[bot]
    - renovate[bot]
    - my-ci-bot
```

### Labels

```yaml
triggers:
  # Only review if one of these labels is present
  require_labels:
    - needs-review
    - ready-for-review
  
  # Skip if any of these labels is present
  ignore_labels:
    - wip
    - draft
    - skip-review
```

### Size Limits

```yaml
triggers:
  min_changes: 5      # Skip tiny PRs
  max_changes: 2000   # Skip huge PRs (probably needs human review)
  max_files: 50       # Skip PRs touching too many files
```

## Models

Configure LLM providers.

### OpenAI-Compatible (Most Providers)

```yaml
models:
  my-model:
    provider: openai-compatible
    base_url: https://api.openai.com/v1  # Optional, this is default
    model: gpt-4o
    api_key_env: OPENAI_API_KEY          # Environment variable name
    temperature: 0.1                      # Optional, default 0.1
    max_tokens: 4096                      # Optional
```

**Compatible Providers:**
- OpenAI (`https://api.openai.com/v1`)
- Ollama (`http://localhost:11434/v1`)
- Groq (`https://api.groq.com/openai/v1`)
- Together (`https://api.together.xyz/v1`)
- Fireworks (`https://api.fireworks.ai/inference/v1`)
- OpenRouter (`https://openrouter.ai/api/v1`)
- vLLM (`http://your-vllm-server/v1`)
- LiteLLM (`http://your-litellm-proxy/v1`)
- Azure OpenAI (`https://your-resource.openai.azure.com/openai/deployments/your-deployment`)
- Any OpenAI-compatible API

### Anthropic

```yaml
models:
  claude:
    provider: anthropic
    model: claude-sonnet-4-20250514
    api_key_env: ANTHROPIC_API_KEY
    max_tokens: 8192
```

### Google

```yaml
models:
  gemini:
    provider: google
    model: gemini-1.5-pro
    api_key_env: GOOGLE_AI_API_KEY
```

### Custom Headers

```yaml
models:
  custom:
    provider: openai-compatible
    base_url: https://api.custom.com/v1
    model: custom-model
    api_key_env: CUSTOM_API_KEY
    headers:
      X-Custom-Auth: some-value
      X-Tenant-ID: my-tenant
```

## Pipelines

Define the review checks to run.

### LLM-based Pipeline

```yaml
pipelines:
  - name: security              # Unique identifier
    model: security             # Reference to models section
    prompt_file: .loom/prompts/security.md  # Custom prompt
    severity: blocker           # blocker, warning, info
    description: "Security review"
    
    # Optional: limit to certain files
    include_paths:
      - "src/**"
    ignore_paths:
      - "**/*.test.ts"
    
    # Optional: provide context files
    context:
      - file: SECURITY.md
      - file: .env.example
```

### Script-based Pipeline

```yaml
pipelines:
  - name: custom-check
    run: "python scripts/my_check.py"
    parse_output: json          # json, text, sarif
    severity: warning
    description: "Custom check"
    
    # Optional: working directory
    workdir: .
    
    # Optional: timeout (ms)
    timeout: 30000
```

**Script Output Formats:**

JSON:
```json
{
  "comments": [
    {
      "file": "src/index.ts",
      "line": 42,
      "message": "Issue description",
      "severity": "warning"
    }
  ]
}
```

SARIF:
```json
{
  "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
  "version": "2.1.0",
  "runs": [...]
}
```

Text: Each line is treated as a comment.

### Conditional Pipeline

```yaml
pipelines:
  - name: migration-review
    model: default
    prompt_file: .loom/prompts/migration.md
    condition: "files.any(f => f.includes('/migrations/'))"
```

**Available in condition:**
- `files` - Array of changed file paths
- `files.any(predicate)` - True if any file matches
- `files.all(predicate)` - True if all files match
- `files.count` - Number of changed files
- `additions` - Total lines added
- `deletions` - Total lines deleted
- `author` - PR author username
- `title` - PR title
- `labels` - Array of PR labels

## Output

Configure how reviews are posted.

### Format

```yaml
output:
  format: github-review  # Platform-specific review
  # or: inline-comments  # Only inline comments
  # or: summary-only     # Only summary comment
  # or: json             # Output JSON (for CI integration)
```

### Grouping

```yaml
output:
  group_by: severity  # Group comments by severity
  # or: file          # Group by file
  # or: pipeline      # Group by pipeline name
  # or: none          # No grouping
```

### Limits

```yaml
output:
  max_comments: 20           # Total max comments
  max_comments_per_file: 5   # Max per file
```

### Summary

```yaml
output:
  include_summary: true
  summary_template: .loom/templates/summary.md  # Optional custom template
```

### Review Action

```yaml
output:
  review_action: comment  # Always comment
  # or: approve           # Approve if no blockers
  # or: request_changes   # Request changes if blockers found
  
  request_changes_threshold: blocker  # or: warning
```

## Personas

Define review styles.

```yaml
personas:
  strict:
    tone: "Direct and concise"
    focus:
      - "Security"
      - "Performance"
    instructions: |
      Be strict. Focus on critical issues only.
      Do not suggest style changes.

pipelines:
  - name: security
    model: security
    persona: strict  # Use this persona
```

## Advanced

### Debug Mode

```yaml
advanced:
  debug: true  # Enable verbose logging for this repo
```

### LLM Settings

```yaml
advanced:
  llm_retries: 2       # Retry failed calls
  llm_timeout: 60000   # Timeout in ms
```

### Script Environment

```yaml
advanced:
  script_env:
    NODE_ENV: production
    MY_VAR: some-value
```

## Config Inheritance

You can extend a base config:

```yaml
# .loom/config.yaml
extends: https://raw.githubusercontent.com/my-org/loom-configs/main/base.yaml

# Override or add to base config
pipelines:
  - name: custom
    model: default
    prompt_file: .loom/prompts/custom.md
```

## Environment Variable Substitution

Use `${VAR}` or `${VAR:-default}` syntax:

```yaml
models:
  default:
    base_url: ${LLM_BASE_URL:-https://api.openai.com/v1}
    model: ${LLM_MODEL:-gpt-4o}
```

## Validation

Validate your config without running a review:

```bash
# Using CLI (when available)
loom config validate

# Or via API
curl -X POST https://your-loom/api/config/validate \
  -H "Content-Type: application/json" \
  -d '{"yaml": "..."}'
```
