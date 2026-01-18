# Configuration Schema

**Version:** 0.1.0  
**Status:** Design Phase  
**Last Updated:** 2026-01-18

---

## Overview

Loom is configured through a `.loom/config.yaml` file in each repository. This file defines:
- **LLM models** to use (OpenAI, Claude, Ollama, etc.)
- **Review pipelines** (what to check, with which prompts)
- **Trigger rules** (when to run reviews)
- **Output settings** (comment formatting, severity filters)

---

## Configuration File Location

```
your-repository/
├── .loom/
│   ├── config.yaml          ← Main configuration
│   └── prompts/             ← Custom prompt templates
│       ├── security.md
│       ├── quality.md
│       └── custom.md
├── src/
└── ...
```

**File:** `.loom/config.yaml`

---

## Complete JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Loom Configuration",
  "description": "Configuration for Loom code reviews",
  "type": "object",
  "required": ["models", "pipelines"],
  "properties": {
    "models": {
      "type": "object",
      "description": "LLM model configurations",
      "minProperties": 1,
      "patternProperties": {
        "^[a-zA-Z0-9_-]+$": {
          "type": "object",
          "required": ["base_url", "model"],
          "properties": {
            "base_url": {
              "type": "string",
              "format": "uri",
              "description": "OpenAI-compatible API base URL"
            },
            "api_key_env": {
              "type": "string",
              "description": "Environment variable name for API key",
              "pattern": "^[A-Z0-9_]+$"
            },
            "model": {
              "type": "string",
              "description": "Model identifier (e.g., gpt-4, claude-sonnet-4)"
            },
            "temperature": {
              "type": "number",
              "minimum": 0.0,
              "maximum": 2.0,
              "default": 0.0,
              "description": "Sampling temperature for responses"
            },
            "max_tokens": {
              "type": "integer",
              "minimum": 1,
              "maximum": 128000,
              "default": 4000,
              "description": "Maximum tokens in response"
            },
            "timeout": {
              "type": "integer",
              "minimum": 1,
              "maximum": 300,
              "default": 60,
              "description": "Request timeout in seconds"
            }
          }
        }
      }
    },
    "pipelines": {
      "type": "array",
      "description": "Review pipelines to execute",
      "minItems": 1,
      "maxItems": 20,
      "items": {
        "type": "object",
        "required": ["name", "model"],
        "properties": {
          "name": {
            "type": "string",
            "pattern": "^[a-z0-9-]+$",
            "description": "Pipeline identifier (lowercase, hyphens)"
          },
          "model": {
            "type": "string",
            "description": "Reference to model in 'models' section"
          },
          "prompt_file": {
            "type": "string",
            "description": "Path to prompt template (relative to .loom/)",
            "default": "prompts/{name}.md"
          },
          "severity": {
            "type": "string",
            "enum": ["blocker", "warning", "info"],
            "default": "warning",
            "description": "Default severity for findings"
          },
          "enabled": {
            "type": "boolean",
            "default": true,
            "description": "Whether this pipeline is enabled"
          },
          "include_paths": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Only review files matching these patterns"
          },
          "exclude_paths": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Exclude files matching these patterns"
          }
        }
      }
    },
    "triggers": {
      "type": "object",
      "description": "When to trigger reviews",
      "properties": {
        "branches": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Only review PRs targeting these branches"
        },
        "ignore_authors": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Skip reviews for these authors (e.g., bots)"
        },
        "ignore_paths": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Skip PRs that only change these files"
        },
        "min_changes": {
          "type": "integer",
          "minimum": 1,
          "description": "Minimum lines changed to trigger review"
        },
        "max_changes": {
          "type": "integer",
          "minimum": 1,
          "default": 5000,
          "description": "Maximum lines changed (skip larger PRs)"
        },
        "max_files": {
          "type": "integer",
          "minimum": 1,
          "default": 100,
          "description": "Maximum files changed"
        }
      }
    },
    "output": {
      "type": "object",
      "description": "Output formatting options",
      "properties": {
        "summary": {
          "type": "boolean",
          "default": true,
          "description": "Post summary comment on PR"
        },
        "inline_comments": {
          "type": "boolean",
          "default": true,
          "description": "Post inline comments on code"
        },
        "min_severity": {
          "type": "string",
          "enum": ["blocker", "warning", "info"],
          "default": "info",
          "description": "Minimum severity to post"
        },
        "max_comments": {
          "type": "integer",
          "minimum": 1,
          "maximum": 100,
          "default": 50,
          "description": "Maximum total comments to post"
        },
        "max_comments_per_file": {
          "type": "integer",
          "minimum": 1,
          "maximum": 50,
          "default": 10,
          "description": "Maximum comments per file"
        },
        "group_by_file": {
          "type": "boolean",
          "default": false,
          "description": "Group findings by file in summary"
        }
      }
    },
    "advanced": {
      "type": "object",
      "description": "Advanced configuration options",
      "properties": {
        "parallel_pipelines": {
          "type": "boolean",
          "default": true,
          "description": "Run pipelines in parallel"
        },
        "cache_config": {
          "type": "boolean",
          "default": true,
          "description": "Cache config for faster subsequent reviews"
        },
        "retry_on_error": {
          "type": "boolean",
          "default": true,
          "description": "Retry LLM calls on transient errors"
        },
        "max_retries": {
          "type": "integer",
          "minimum": 0,
          "maximum": 5,
          "default": 3,
          "description": "Maximum retry attempts"
        }
      }
    }
  }
}
```

---

## Configuration Sections

### 1. models

Defines LLM models that can be used in pipelines.

**Required Fields:**
- `base_url` - API endpoint (OpenAI-compatible)
- `model` - Model identifier

**Optional Fields:**
- `api_key_env` - Environment variable for API key
- `temperature` - Sampling temperature (0.0 = deterministic)
- `max_tokens` - Maximum response length
- `timeout` - Request timeout in seconds

**Example:**
```yaml
models:
  gpt4:
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
    model: gpt-4
    temperature: 0.0
    max_tokens: 4000
    timeout: 60
  
  claude:
    base_url: https://api.anthropic.com/v1
    api_key_env: ANTHROPIC_API_KEY
    model: claude-sonnet-4-20250514
    temperature: 0.0
    max_tokens: 4000
  
  local-llama:
    base_url: http://localhost:11434/v1
    api_key_env: OLLAMA_API_KEY  # Can be empty
    model: codellama:13b
    temperature: 0.0
    max_tokens: 2000
```

**Supported Providers:**
- **OpenAI:** `https://api.openai.com/v1`
- **Anthropic:** `https://api.anthropic.com/v1`
- **Ollama:** `http://localhost:11434/v1`
- **Groq:** `https://api.groq.com/openai/v1`
- **Together.ai:** `https://api.together.xyz/v1`
- **OpenRouter:** `https://openrouter.ai/api/v1`
- Any OpenAI-compatible endpoint

---

### 2. pipelines

Defines review pipelines to execute on each PR.

**Required Fields:**
- `name` - Unique identifier (lowercase, hyphens only)
- `model` - Reference to model name from `models` section

**Optional Fields:**
- `prompt_file` - Custom prompt template path
- `severity` - Default severity: `blocker`, `warning`, or `info`
- `enabled` - Whether to run this pipeline
- `include_paths` - Only review matching files
- `exclude_paths` - Exclude matching files

**Example:**
```yaml
pipelines:
  - name: security
    model: gpt4
    prompt_file: prompts/security.md
    severity: blocker
    enabled: true
  
  - name: code-quality
    model: claude
    prompt_file: prompts/quality.md
    severity: warning
    include_paths:
      - "src/**/*.py"
      - "src/**/*.ts"
    exclude_paths:
      - "src/**/*.test.py"
  
  - name: documentation
    model: gpt4
    severity: info
    include_paths:
      - "**/*.py"
```

**Path Patterns:**
- `**/*.py` - All Python files recursively
- `src/**/*.ts` - All TypeScript files in src/
- `*.lock` - Lock files in root
- `docs/**` - Everything in docs/

---

### 3. triggers

Controls when reviews are triggered.

**Optional Fields:**
- `branches` - Only review PRs to these branches
- `ignore_authors` - Skip PRs from these users
- `ignore_paths` - Skip PRs only touching these paths
- `min_changes` - Minimum lines changed
- `max_changes` - Maximum lines changed
- `max_files` - Maximum files changed

**Example:**
```yaml
triggers:
  branches:
    - main
    - develop
    - release/*
  
  ignore_authors:
    - dependabot[bot]
    - renovate[bot]
  
  ignore_paths:
    - "*.lock"
    - "package-lock.json"
    - "yarn.lock"
    - "*.md"
  
  min_changes: 5
  max_changes: 2000
  max_files: 50
```

**Behavior:**
- If `branches` is empty/omitted: Review all PRs
- If PR doesn't match triggers: Skip silently
- If PR exceeds limits: Skip with comment

---

### 4. output

Configures how findings are posted to PRs.

**Optional Fields:**
- `summary` - Post summary comment
- `inline_comments` - Post inline code comments
- `min_severity` - Filter findings by severity
- `max_comments` - Cap total comments
- `max_comments_per_file` - Cap comments per file
- `group_by_file` - Group findings by file

**Example:**
```yaml
output:
  summary: true
  inline_comments: true
  min_severity: warning  # Skip "info" findings
  max_comments: 30
  max_comments_per_file: 5
  group_by_file: true
```

**Severity Filtering:**
- `blocker` - Only blockers
- `warning` - Blockers + warnings
- `info` - All findings (default)

---

### 5. advanced

Advanced tuning options.

**Optional Fields:**
- `parallel_pipelines` - Run pipelines concurrently
- `cache_config` - Cache config to avoid re-fetching
- `retry_on_error` - Retry on transient LLM errors
- `max_retries` - Maximum retry attempts

**Example:**
```yaml
advanced:
  parallel_pipelines: true
  cache_config: true
  retry_on_error: true
  max_retries: 3
```

---

## Minimal Configuration

The simplest possible config:

```yaml
# .loom/config.yaml
models:
  default:
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
    model: gpt-4

pipelines:
  - name: review
    model: default
```

**Prompt file:** `.loom/prompts/review.md` (auto-detected)

---

## Complete Example

A production-ready configuration:

```yaml
# .loom/config.yaml

# LLM Models
models:
  gpt4-security:
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
    model: gpt-4
    temperature: 0.0
    max_tokens: 4000
  
  claude-quality:
    base_url: https://api.anthropic.com/v1
    api_key_env: ANTHROPIC_API_KEY
    model: claude-sonnet-4-20250514
    temperature: 0.0
    max_tokens: 4000
  
  local-llama:
    base_url: http://localhost:11434/v1
    model: codellama:13b
    temperature: 0.0
    max_tokens: 2000

# Review Pipelines
pipelines:
  # Security review (highest priority)
  - name: security
    model: gpt4-security
    prompt_file: prompts/security.md
    severity: blocker
    enabled: true
  
  # Code quality review
  - name: quality
    model: claude-quality
    prompt_file: prompts/quality.md
    severity: warning
    include_paths:
      - "src/**/*.py"
      - "src/**/*.ts"
    exclude_paths:
      - "**/*.test.*"
      - "**/__tests__/**"
  
  # Documentation check
  - name: documentation
    model: gpt4-security
    prompt_file: prompts/docs.md
    severity: info
    include_paths:
      - "src/**/*.py"
      - "src/**/*.ts"
  
  # Performance review (on-demand)
  - name: performance
    model: local-llama
    prompt_file: prompts/performance.md
    severity: warning
    enabled: false  # Enable manually when needed

# Trigger Rules
triggers:
  # Only review PRs to these branches
  branches:
    - main
    - develop
    - release/*
  
  # Skip bot PRs
  ignore_authors:
    - dependabot[bot]
    - renovate[bot]
  
  # Skip PRs that only touch these files
  ignore_paths:
    - "*.lock"
    - "*.md"
    - "docs/**"
  
  # Size limits
  min_changes: 10
  max_changes: 1500
  max_files: 50

# Output Settings
output:
  summary: true
  inline_comments: true
  min_severity: warning  # Skip info-level in comments
  max_comments: 25
  max_comments_per_file: 5
  group_by_file: true

# Advanced Options
advanced:
  parallel_pipelines: true
  cache_config: true
  retry_on_error: true
  max_retries: 3
```

---

## Configuration Validation

Loom validates configuration on load:

**Validation Rules:**
1. ✅ At least one model defined
2. ✅ At least one pipeline defined
3. ✅ Each pipeline references valid model
4. ✅ Prompt files exist (if specified)
5. ✅ No duplicate pipeline names
6. ✅ Valid severity values
7. ✅ Valid path patterns

**Validation Errors:**
```yaml
# ERROR: Invalid model reference
pipelines:
  - name: security
    model: nonexistent-model  # ❌ Model not defined

# ERROR: Invalid severity
pipelines:
  - name: security
    severity: critical  # ❌ Must be: blocker, warning, or info

# ERROR: Duplicate names
pipelines:
  - name: security
    model: gpt4
  - name: security  # ❌ Duplicate
    model: claude
```

---

## Environment Variables

API keys should be stored as environment variables:

```bash
# .env (not committed to git!)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk-...
```

**Referenced in config:**
```yaml
models:
  default:
    api_key_env: OPENAI_API_KEY  # Reads from process.env
```

**For Ollama (no auth):**
```yaml
models:
  local:
    base_url: http://localhost:11434/v1
    # api_key_env not needed
```

---

## Default Values

If omitted, these defaults are used:

```yaml
models:
  default:
    temperature: 0.0
    max_tokens: 4000
    timeout: 60

pipelines:
  - name: review
    severity: warning
    enabled: true
    prompt_file: prompts/{name}.md  # Auto-generated path

triggers:
  # Empty = review all PRs
  max_changes: 5000
  max_files: 100

output:
  summary: true
  inline_comments: true
  min_severity: info
  max_comments: 50
  max_comments_per_file: 10
  group_by_file: false

advanced:
  parallel_pipelines: true
  cache_config: true
  retry_on_error: true
  max_retries: 3
```

---

## Pydantic Models

For code generation, use these Pydantic models:

```python
from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List, Literal
from enum import Enum

class Severity(str, Enum):
    BLOCKER = "blocker"
    WARNING = "warning"
    INFO = "info"

class LLMModel(BaseModel):
    base_url: HttpUrl
    api_key_env: Optional[str] = None
    model: str
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, ge=1, le=128000)
    timeout: int = Field(default=60, ge=1, le=300)

class Pipeline(BaseModel):
    name: str = Field(pattern="^[a-z0-9-]+$")
    model: str
    prompt_file: Optional[str] = None
    severity: Severity = Severity.WARNING
    enabled: bool = True
    include_paths: Optional[List[str]] = None
    exclude_paths: Optional[List[str]] = None
    
    @validator('prompt_file', always=True)
    def default_prompt_file(cls, v, values):
        if v is None and 'name' in values:
            return f"prompts/{values['name']}.md"
        return v

class Triggers(BaseModel):
    branches: Optional[List[str]] = None
    ignore_authors: Optional[List[str]] = None
    ignore_paths: Optional[List[str]] = None
    min_changes: Optional[int] = Field(None, ge=1)
    max_changes: int = Field(default=5000, ge=1)
    max_files: int = Field(default=100, ge=1)

class Output(BaseModel):
    summary: bool = True
    inline_comments: bool = True
    min_severity: Severity = Severity.INFO
    max_comments: int = Field(default=50, ge=1, le=100)
    max_comments_per_file: int = Field(default=10, ge=1, le=50)
    group_by_file: bool = False

class Advanced(BaseModel):
    parallel_pipelines: bool = True
    cache_config: bool = True
    retry_on_error: bool = True
    max_retries: int = Field(default=3, ge=0, le=5)

class Config(BaseModel):
    models: dict[str, LLMModel] = Field(min_items=1)
    pipelines: List[Pipeline] = Field(min_items=1, max_items=20)
    triggers: Optional[Triggers] = None
    output: Optional[Output] = Output()
    advanced: Optional[Advanced] = Advanced()
    
    @validator('pipelines')
    def validate_model_references(cls, v, values):
        if 'models' in values:
            model_names = set(values['models'].keys())
            for pipeline in v:
                if pipeline.model not in model_names:
                    raise ValueError(
                        f"Pipeline '{pipeline.name}' references "
                        f"undefined model '{pipeline.model}'"
                    )
        return v
    
    @validator('pipelines')
    def validate_unique_names(cls, v):
        names = [p.name for p in v]
        if len(names) != len(set(names)):
            raise ValueError("Pipeline names must be unique")
        return v
```

---

## References

- [Prompt Format](prompt-format.md) - Template specification
- [Example Configurations](examples/) - Ready-to-use configs
- [Architecture Overview](../architecture/overview.md)
