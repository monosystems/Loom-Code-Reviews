<div align="center">

# 🧵 Loom Code Reviews

**The programmable, self-hosted AI code review agent**

Weave better code reviews with customizable prompts, any LLM provider, and full control over your data.

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](LICENSE)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[Quick Start](#-quick-start) • [Features](#-features) • [Documentation](#-documentation) • [Self-Hosting](#-self-hosting) • [Contributing](#-contributing)

</div>

---

## 🎯 Why Loom?

Most AI code review tools are **black boxes**. You get what you get. Loom is different:

| Problem | Loom's Solution |
|---------|-----------------|
| Locked into one LLM provider | **Use any LLM** - OpenAI, Claude, Ollama, or your own |
| Generic, noisy reviews | **Custom prompts** - Define exactly what to check |
| Data privacy concerns | **Self-hosted** - Your code never leaves your infrastructure |
| One-size-fits-all | **Configurable pipelines** - Different checks for different files |
| Expensive per-seat pricing | **Open source** - Free forever, no seat limits |

## ✨ Features

### Core
- 🔍 **AI-Powered PR Reviews** - Intelligent analysis of code changes
- 📝 **Custom Prompts** - Write your own review prompts in Markdown
- 🔌 **Any LLM Provider** - OpenAI, Anthropic, Ollama, or any OpenAI-compatible API
- 🌐 **Multi-Platform** - GitHub, GitLab, Bitbucket, Gitea, Azure DevOps
- 🏠 **Self-Hosted** - Run on your own infrastructure
- ⚡ **Pipeline Architecture** - Chain multiple review checks

### Configuration
- 📄 **YAML Config** - Simple `.loom/config.yaml` in your repo
- 🎭 **Review Personas** - "Strict security reviewer" or "Helpful mentor"
- 🎯 **Smart Filtering** - Review only what matters (paths, labels, size)
- 🔧 **Custom Scripts** - Run your own checks alongside AI

### Integrations
- 💬 **Inline Comments** - Feedback directly on the code
- 📊 **PR Summaries** - Auto-generated change descriptions
- 🔗 **Webhook Support** - Real-time PR notifications
- 🏢 **Team Features** - Organizations, shared prompts (self-managed)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Pull and run with SQLite (simplest setup)
docker run -d \
  -p 3000:3000 \
  -v loom-data:/data \
  -e OPENAI_API_KEY=your-key \
  ghcr.io/loom-reviews/loom:latest
```

Open `http://localhost:3000` and connect your first repository.

### Option 2: Docker Compose

```bash
# Clone the repository
git clone https://github.com/loom-reviews/loom-reviews.git
cd loom-reviews

# Copy environment template
cp .env.example .env
# Edit .env with your settings

# Start all services
docker compose up -d
```

### Option 3: Development Setup

```bash
# Prerequisites: Node.js 20+, pnpm 9+

# Clone and install
git clone https://github.com/loom-reviews/loom-reviews.git
cd loom-reviews
pnpm install

# Setup environment
cp .env.example .env

# Run database migrations
pnpm db:migrate

# Start development server
pnpm dev
```

## 📖 Documentation

| Guide | Description |
|-------|-------------|
| [Architecture](docs/architecture.md) | System design and components |
| [Self-Hosting](docs/self-hosting.md) | Deployment options and requirements |
| [Configuration](docs/configuration.md) | Complete YAML config reference |
| [Custom Prompts](docs/custom-prompts.md) | Writing your own review prompts |
| [LLM Providers](docs/llm-providers.md) | Setting up different AI providers |

### Platform Adapters
| Platform | Guide |
|----------|-------|
| GitHub | [docs/adapters/github.md](docs/adapters/github.md) |
| GitLab | [docs/adapters/gitlab.md](docs/adapters/gitlab.md) |
| Bitbucket | [docs/adapters/bitbucket.md](docs/adapters/bitbucket.md) |
| Gitea / Forgejo | [docs/adapters/gitea.md](docs/adapters/gitea.md) |
| Azure DevOps | [docs/adapters/azure-devops.md](docs/adapters/azure-devops.md) |

## ⚙️ Configuration Example

Create `.loom/config.yaml` in your repository:

```yaml
# Trigger rules
triggers:
  branches: ["main", "develop"]
  ignore_paths: ["*.lock", "docs/**"]
  ignore_authors: ["dependabot", "renovate"]

# LLM models
models:
  default:
    provider: openai-compatible
    base_url: https://api.openai.com/v1
    model: gpt-4o
    api_key_env: OPENAI_API_KEY
  
  local:
    provider: openai-compatible
    base_url: http://localhost:11434/v1
    model: codellama

# Review pipeline
pipelines:
  - name: security
    model: default
    prompt_file: .loom/prompts/security.md
    severity: blocker
    
  - name: code-quality
    model: default
    prompt_file: .loom/prompts/quality.md
    
  - name: docs-check
    run: "python scripts/check_docs.py"
    parse_output: json

# Output settings
output:
  format: github-review
  max_comments: 15
  group_by: severity
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Git Platform                             │
│            (GitHub / GitLab / Bitbucket / etc.)             │
└─────────────────────────────────────────────────────────────┘
                              │ Webhook
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Loom Web App                            │
│                   (Next.js Dashboard)                        │
├─────────────────────────────────────────────────────────────┤
│  • Webhook receivers     • Dashboard UI                      │
│  • API endpoints         • Team management                   │
│  • Job scheduling        • Prompt library                    │
└─────────────────────────────────────────────────────────────┘
                              │ Queue
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Loom Worker                             │
│                 (Background Processor)                       │
├─────────────────────────────────────────────────────────────┤
│  • Load repo config      • Execute pipelines                 │
│  • Call LLM providers    • Post review comments              │
│  • Run custom scripts    • Update job status                 │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │  OpenAI  │   │  Claude  │   │  Ollama  │
        └──────────┘   └──────────┘   └──────────┘
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | Next.js 14 (App Router) |
| **Language** | TypeScript |
| **Database** | SQLite (default) / PostgreSQL |
| **ORM** | Drizzle |
| **Auth** | Better Auth |
| **UI** | shadcn/ui + Tailwind CSS |
| **API** | tRPC (internal) + REST (webhooks) |
| **Queue** | Database-backed job queue |
| **Monorepo** | Turborepo |

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development

```bash
# Install dependencies
pnpm install

# Start development
pnpm dev

# Run tests
pnpm test

# Type check
pnpm typecheck

# Lint
pnpm lint
```

### Project Structure

```
loom-reviews/
├── apps/
│   ├── web/              # Next.js dashboard
│   └── worker/           # Background job processor
├── packages/
│   ├── core/             # Review engine
│   ├── adapters/         # Git platform adapters
│   ├── db/               # Database schema
│   ├── queue/            # Job queue
│   ├── llm/              # LLM client abstraction
│   ├── config/           # YAML parser
│   └── ui/               # Shared components
└── docs/                 # Documentation
```

## 📜 License

Loom Code Reviews is licensed under the [GNU Affero General Public License v3.0](LICENSE).

This means:
- ✅ Free to use, modify, and distribute
- ✅ Free for commercial use
- ✅ Free to self-host
- ⚠️ Modifications must be open-sourced under AGPL
- ⚠️ Network use counts as distribution

## 🙏 Acknowledgments

Inspired by and learned from:
- [PR-Agent](https://github.com/qodo-ai/pr-agent) - The original open-source PR reviewer
- [CodeRabbit](https://coderabbit.ai/) - For pushing the AI review space forward

---

<div align="center">

**[Documentation](docs/)** • **[Report Bug](https://github.com/loom-reviews/loom-reviews/issues)** • **[Request Feature](https://github.com/loom-reviews/loom-reviews/issues)**

Made with 🧵 by the Loom community

</div>
