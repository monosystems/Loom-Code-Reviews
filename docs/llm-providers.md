# LLM Providers

Loom supports multiple LLM providers. This guide covers setup for each provider and how to use custom/self-hosted models.

## Table of Contents

- [Overview](#overview)
- [OpenAI](#openai)
- [Anthropic (Claude)](#anthropic-claude)
- [Google (Gemini)](#google-gemini)
- [Ollama (Local)](#ollama-local)
- [Groq](#groq)
- [Together AI](#together-ai)
- [OpenRouter](#openrouter)
- [Azure OpenAI](#azure-openai)
- [AWS Bedrock](#aws-bedrock)
- [Custom/Self-Hosted](#customself-hosted)
- [Multiple Providers](#multiple-providers)
- [Cost Optimization](#cost-optimization)

## Overview

Loom uses the **OpenAI-compatible API** as its primary interface. Most providers support this format, making integration straightforward.

```yaml
models:
  my-model:
    provider: openai-compatible  # Works with most providers
    base_url: https://api.provider.com/v1
    model: model-name
    api_key_env: PROVIDER_API_KEY
```

## OpenAI

The default and most common provider.

### Setup

1. Get API key from [platform.openai.com](https://platform.openai.com/api-keys)
2. Set environment variable:
   ```bash
   OPENAI_API_KEY=sk-...
   ```

### Configuration

```yaml
models:
  default:
    provider: openai-compatible
    base_url: https://api.openai.com/v1  # Optional, this is default
    model: gpt-4o
    api_key_env: OPENAI_API_KEY
    temperature: 0.1
    max_tokens: 4096
```

### Available Models

| Model | Best For | Context | Cost |
|-------|----------|---------|------|
| `gpt-4o` | Best quality | 128k | $$ |
| `gpt-4o-mini` | Good balance | 128k | $ |
| `gpt-4-turbo` | Complex tasks | 128k | $$$ |
| `gpt-3.5-turbo` | Fast, cheap | 16k | ¢ |

### Recommended Setup

```yaml
models:
  # High quality for security/complex reviews
  quality:
    provider: openai-compatible
    model: gpt-4o
    api_key_env: OPENAI_API_KEY
    
  # Fast and cheap for simple checks
  fast:
    provider: openai-compatible
    model: gpt-4o-mini
    api_key_env: OPENAI_API_KEY
```

## Anthropic (Claude)

Claude models excel at code understanding and following complex instructions.

### Setup

1. Get API key from [console.anthropic.com](https://console.anthropic.com/)
2. Set environment variable:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-...
   ```

### Configuration

```yaml
models:
  claude:
    provider: anthropic
    model: claude-sonnet-4-20250514
    api_key_env: ANTHROPIC_API_KEY
    max_tokens: 8192
```

### Available Models

| Model | Best For | Context | Cost |
|-------|----------|---------|------|
| `claude-sonnet-4-20250514` | Best balance | 200k | $$ |
| `claude-opus-4-20250514` | Complex reasoning | 200k | $$$$ |
| `claude-3-5-haiku-20241022` | Fast, efficient | 200k | $ |

### Recommended Setup

```yaml
models:
  # Best for security reviews (Claude excels here)
  security:
    provider: anthropic
    model: claude-sonnet-4-20250514
    api_key_env: ANTHROPIC_API_KEY
```

## Google (Gemini)

Google's Gemini models offer competitive performance at lower cost.

### Setup

1. Get API key from [aistudio.google.com](https://aistudio.google.com/apikey)
2. Set environment variable:
   ```bash
   GOOGLE_AI_API_KEY=...
   ```

### Configuration

```yaml
models:
  gemini:
    provider: google
    model: gemini-1.5-pro
    api_key_env: GOOGLE_AI_API_KEY
```

### Available Models

| Model | Best For | Context | Cost |
|-------|----------|---------|------|
| `gemini-1.5-pro` | Best quality | 1M | $$ |
| `gemini-1.5-flash` | Fast, cheap | 1M | $ |
| `gemini-2.0-flash` | Latest fast model | 1M | $ |

## Ollama (Local)

Run models locally for complete privacy - your code never leaves your infrastructure.

### Setup

1. Install Ollama: [ollama.com](https://ollama.com/)
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. Pull a model:
   ```bash
   ollama pull codellama:34b
   # or
   ollama pull deepseek-coder:33b
   # or
   ollama pull qwen2.5-coder:32b
   ```

3. Ollama runs on `http://localhost:11434` by default

### Configuration

```yaml
models:
  local:
    provider: openai-compatible
    base_url: http://localhost:11434/v1
    model: codellama:34b
    # No api_key_env needed for local Ollama
```

### Docker Setup

If running Loom in Docker, connect to Ollama on host:

```yaml
# docker-compose.yml
services:
  web:
    environment:
      - OLLAMA_HOST=http://host.docker.internal:11434
```

```yaml
# .loom/config.yaml
models:
  local:
    provider: openai-compatible
    base_url: ${OLLAMA_HOST}/v1
    model: codellama:34b
```

### Recommended Models for Code Review

| Model | Size | RAM Required | Quality |
|-------|------|--------------|---------|
| `qwen2.5-coder:32b` | 32B | 24GB+ | Excellent |
| `deepseek-coder:33b` | 33B | 24GB+ | Excellent |
| `codellama:34b` | 34B | 24GB+ | Very Good |
| `codellama:13b` | 13B | 12GB+ | Good |
| `codellama:7b` | 7B | 8GB+ | Acceptable |

## Groq

Extremely fast inference, great for development and high-volume use.

### Setup

1. Get API key from [console.groq.com](https://console.groq.com/)
2. Set environment variable:
   ```bash
   GROQ_API_KEY=gsk_...
   ```

### Configuration

```yaml
models:
  fast:
    provider: openai-compatible
    base_url: https://api.groq.com/openai/v1
    model: llama-3.1-70b-versatile
    api_key_env: GROQ_API_KEY
```

### Available Models

| Model | Speed | Quality |
|-------|-------|---------|
| `llama-3.1-70b-versatile` | Very Fast | Good |
| `llama-3.1-8b-instant` | Extremely Fast | Acceptable |
| `mixtral-8x7b-32768` | Very Fast | Good |

## Together AI

Wide model selection with competitive pricing.

### Setup

1. Get API key from [api.together.xyz](https://api.together.xyz/)
2. Set environment variable:
   ```bash
   TOGETHER_API_KEY=...
   ```

### Configuration

```yaml
models:
  together:
    provider: openai-compatible
    base_url: https://api.together.xyz/v1
    model: meta-llama/Llama-3.1-70B-Instruct-Turbo
    api_key_env: TOGETHER_API_KEY
```

## OpenRouter

Access multiple providers through a single API.

### Setup

1. Get API key from [openrouter.ai](https://openrouter.ai/)
2. Set environment variable:
   ```bash
   OPENROUTER_API_KEY=sk-or-...
   ```

### Configuration

```yaml
models:
  router:
    provider: openai-compatible
    base_url: https://openrouter.ai/api/v1
    model: anthropic/claude-3.5-sonnet  # Use provider/model format
    api_key_env: OPENROUTER_API_KEY
    headers:
      HTTP-Referer: https://your-loom-instance.com
      X-Title: Loom Code Reviews
```

### Benefits

- Single API key for multiple providers
- Automatic fallback if a provider is down
- Usage tracking across providers

## Azure OpenAI

Enterprise Azure deployment of OpenAI models.

### Setup

1. Create Azure OpenAI resource
2. Deploy a model
3. Get endpoint and key

### Configuration

```yaml
models:
  azure:
    provider: openai-compatible
    base_url: https://your-resource.openai.azure.com/openai/deployments/your-deployment
    model: gpt-4o  # Deployment name
    api_key_env: AZURE_OPENAI_API_KEY
    headers:
      api-version: "2024-02-15-preview"
```

Or using the full URL:

```yaml
models:
  azure:
    provider: openai-compatible
    base_url: https://your-resource.openai.azure.com/openai/deployments/gpt-4o
    api_key_env: AZURE_OPENAI_API_KEY
    query_params:
      api-version: "2024-02-15-preview"
```

## AWS Bedrock

Access models through AWS Bedrock.

### Setup

Use a proxy like [LiteLLM](https://github.com/BerriAI/litellm) to expose Bedrock as OpenAI-compatible:

```bash
# Run LiteLLM proxy
litellm --model bedrock/anthropic.claude-v2
```

### Configuration

```yaml
models:
  bedrock:
    provider: openai-compatible
    base_url: http://localhost:4000/v1  # LiteLLM proxy
    model: bedrock/anthropic.claude-v2
    api_key_env: LITELLM_API_KEY
```

## Custom/Self-Hosted

Any OpenAI-compatible API works with Loom.

### vLLM

```bash
# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
  --model codellama/CodeLlama-34b-Instruct-hf \
  --port 8000
```

```yaml
models:
  vllm:
    provider: openai-compatible
    base_url: http://your-vllm-server:8000/v1
    model: codellama/CodeLlama-34b-Instruct-hf
```

### LiteLLM Proxy

```bash
# Run LiteLLM as a unified proxy
litellm --config config.yaml
```

```yaml
models:
  litellm:
    provider: openai-compatible
    base_url: http://your-litellm-proxy:4000/v1
    model: gpt-4  # LiteLLM routes to configured provider
    api_key_env: LITELLM_API_KEY
```

### LocalAI

```yaml
models:
  localai:
    provider: openai-compatible
    base_url: http://your-localai:8080/v1
    model: codellama
```

### Custom API with Headers

```yaml
models:
  custom:
    provider: openai-compatible
    base_url: https://api.your-company.com/v1
    model: custom-model
    api_key_env: CUSTOM_API_KEY
    headers:
      X-Tenant-ID: your-tenant
      X-Custom-Auth: additional-auth
    timeout: 120000  # 2 minutes
```

## Multiple Providers

Use different models for different purposes:

```yaml
models:
  # Security reviews need the best model
  security:
    provider: anthropic
    model: claude-sonnet-4-20250514
    api_key_env: ANTHROPIC_API_KEY
    
  # General quality can use a good balance
  quality:
    provider: openai-compatible
    model: gpt-4o
    api_key_env: OPENAI_API_KEY
    
  # Simple checks can use fast/cheap
  fast:
    provider: openai-compatible
    base_url: https://api.groq.com/openai/v1
    model: llama-3.1-70b-versatile
    api_key_env: GROQ_API_KEY
    
  # Sensitive code uses local model
  local:
    provider: openai-compatible
    base_url: http://localhost:11434/v1
    model: codellama:34b

pipelines:
  - name: security
    model: security  # Uses Claude
    
  - name: quality
    model: quality   # Uses GPT-4o
    
  - name: docs
    model: fast      # Uses Groq
    
  - name: sensitive
    model: local     # Uses Ollama
    include_paths:
      - "src/secrets/**"
      - "src/crypto/**"
```

## Cost Optimization

### Strategy 1: Tiered Models

```yaml
models:
  # Expensive but best
  premium:
    model: gpt-4o
    
  # Cheaper but still good
  standard:
    model: gpt-4o-mini
    
pipelines:
  # Only use premium for security
  - name: security
    model: premium
    
  # Use standard for everything else
  - name: quality
    model: standard
```

### Strategy 2: Skip Large PRs

```yaml
triggers:
  max_changes: 1000  # Skip huge PRs
  max_files: 30
```

### Strategy 3: Limit Reviews

```yaml
output:
  max_comments: 15  # Cap output
```

### Strategy 4: Use Local for Development

```yaml
models:
  default:
    provider: openai-compatible
    base_url: ${LLM_BASE_URL:-http://localhost:11434/v1}
    model: ${LLM_MODEL:-codellama:34b}
```

Development: `LLM_BASE_URL` not set → uses Ollama
Production: `LLM_BASE_URL=https://api.openai.com/v1` → uses OpenAI

### Estimated Costs

| Provider | Model | ~Cost per Review* |
|----------|-------|-------------------|
| OpenAI | gpt-4o | $0.02 - $0.10 |
| OpenAI | gpt-4o-mini | $0.002 - $0.01 |
| Anthropic | claude-3.5-sonnet | $0.02 - $0.08 |
| Groq | llama-3.1-70b | $0.001 - $0.005 |
| Ollama | Any | $0 (hardware only) |

*Varies by PR size and number of pipelines
