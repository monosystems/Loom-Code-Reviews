# Contributing to Loom

Thank you for your interest in contributing to Loom Code Reviews! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Making Changes](#making-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Types of Contributions

We welcome:
- 🐛 **Bug fixes** - Found a bug? Please report or fix it!
- ✨ **Features** - Have an idea? Open an issue first to discuss
- 📖 **Documentation** - Improvements, typos, examples
- 🌍 **Translations** - Help make Loom accessible
- 🧪 **Tests** - Increase coverage, edge cases
- 🔌 **Adapters** - New git platform integrations
- 🤖 **LLM Providers** - New model integrations

### First Time?

Look for issues labeled [`good first issue`](https://github.com/loom-reviews/loom-reviews/labels/good%20first%20issue) or [`help wanted`](https://github.com/loom-reviews/loom-reviews/labels/help%20wanted).

## Development Setup

### Prerequisites

- Node.js 20+
- pnpm 9+
- Docker (for testing)
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/loom-reviews/loom-reviews.git
cd loom-reviews

# Install dependencies
pnpm install

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Setup database
pnpm db:push

# Start development
pnpm dev
```

### Running Specific Apps

```bash
# Web app only
pnpm dev --filter=web

# Worker only
pnpm dev --filter=worker

# Specific package
pnpm dev --filter=@loom/core
```

### Environment Variables

Minimum for development:

```bash
# Required
BETTER_AUTH_SECRET=development-secret-min-32-chars
DATABASE_URL=file:./dev.db

# For testing LLM features
OPENAI_API_KEY=sk-...

# For testing GitHub integration
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
```

## Project Structure

```
loom-reviews/
├── apps/
│   ├── web/              # Next.js dashboard
│   └── worker/           # Background processor
├── packages/
│   ├── core/             # Review engine
│   ├── adapters/         # Git platform adapters
│   ├── db/               # Database schema
│   ├── queue/            # Job queue
│   ├── llm/              # LLM abstraction
│   ├── config/           # YAML parser
│   ├── auth/             # Better Auth config
│   ├── ui/               # Shared components
│   └── shared/           # Shared types/utils
├── docs/                 # Documentation
└── docker/               # Docker files
```

### Package Dependencies

```
ui ← web
shared ← core, adapters, db, queue, llm, config
db ← core, web, worker
queue ← core, worker
llm ← core
config ← core
adapters ← core, web
core ← worker
auth ← web
```

## Making Changes

### Branch Naming

```
feature/description    # New feature
fix/description        # Bug fix
docs/description       # Documentation
refactor/description   # Refactoring
test/description       # Tests
chore/description      # Maintenance
```

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting, no code change
- `refactor` - Code restructuring
- `test` - Adding tests
- `chore` - Maintenance

**Examples:**
```
feat(adapters): add Gitea support

fix(core): handle empty diffs gracefully

docs(readme): add Docker Compose example

refactor(llm): simplify provider interface
```

## Coding Standards

### TypeScript

```typescript
// ✅ Good: Explicit types for public APIs
export function parseConfig(yaml: string): LoomConfig {
  // ...
}

// ❌ Bad: Any types
export function parseConfig(yaml: any): any {
  // ...
}
```

### Imports

```typescript
// ✅ Good: Organized imports
import { useState, useEffect } from 'react';

import { Button } from '@loom/ui';
import { parseConfig } from '@loom/config';

import { localHelper } from './helpers';
import type { LocalType } from './types';
```

### Error Handling

```typescript
// ✅ Good: Specific errors
if (!config.models.default) {
  throw new ConfigError('No default model configured');
}

// ❌ Bad: Generic errors
if (!config.models.default) {
  throw new Error('Config error');
}
```

### File Organization

```typescript
// 1. Types/Interfaces
interface ReviewOptions {
  maxComments: number;
}

// 2. Constants
const DEFAULT_MAX_COMMENTS = 20;

// 3. Main export
export function createReview(options: ReviewOptions) {
  // ...
}

// 4. Helper functions (private)
function formatComment(comment: Comment): string {
  // ...
}
```

### Linting & Formatting

```bash
# Check formatting
pnpm format:check

# Fix formatting
pnpm format

# Lint
pnpm lint

# Lint and fix
pnpm lint:fix

# Type check
pnpm typecheck
```

## Testing

### Running Tests

```bash
# All tests
pnpm test

# Specific package
pnpm test --filter=@loom/core

# Watch mode
pnpm test:watch

# Coverage
pnpm test:coverage
```

### Writing Tests

```typescript
// packages/core/src/__tests__/engine.test.ts
import { describe, it, expect } from 'vitest';
import { ReviewEngine } from '../review/engine';

describe('ReviewEngine', () => {
  it('should execute pipeline', async () => {
    const engine = new ReviewEngine(mockConfig);
    const result = await engine.execute(mockDiff);
    
    expect(result.comments).toHaveLength(2);
    expect(result.summary).toBeDefined();
  });

  it('should handle empty diffs', async () => {
    const engine = new ReviewEngine(mockConfig);
    const result = await engine.execute('');
    
    expect(result.comments).toHaveLength(0);
  });
});
```

### Test Structure

```
packages/core/
├── src/
│   ├── review/
│   │   ├── engine.ts
│   │   └── __tests__/
│   │       └── engine.test.ts
```

## Submitting Changes

### Pull Request Process

1. **Fork & Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/loom-reviews.git
   ```

2. **Create Branch**
   ```bash
   git checkout -b feature/my-feature
   ```

3. **Make Changes**
   - Write code
   - Add tests
   - Update docs

4. **Verify**
   ```bash
   pnpm typecheck
   pnpm lint
   pnpm test
   pnpm build
   ```

5. **Commit**
   ```bash
   git commit -m "feat(scope): description"
   ```

6. **Push & PR**
   ```bash
   git push origin feature/my-feature
   # Open PR on GitHub
   ```

### PR Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Checklist
- [ ] Tests pass locally
- [ ] Lint passes
- [ ] Types check
- [ ] Documentation updated
- [ ] Conventional commit message

## Related Issues
Closes #123
```

### Review Process

1. CI checks must pass
2. At least one maintainer approval
3. No unresolved conversations
4. Up to date with main branch

## Release Process

Releases are automated via GitHub Actions:

1. Maintainer merges to `main`
2. Changeset bot creates release PR
3. Maintainer merges release PR
4. GitHub Actions:
   - Bumps versions
   - Updates CHANGELOG
   - Creates GitHub release
   - Publishes Docker images
   - Publishes npm packages

### Versioning

We use [Semantic Versioning](https://semver.org/):
- **MAJOR** - Breaking changes
- **MINOR** - New features (backwards compatible)
- **PATCH** - Bug fixes

### Creating a Changeset

When making changes that should be released:

```bash
pnpm changeset
```

This will prompt you for:
1. Which packages changed
2. Semver bump type
3. Description for CHANGELOG

## Getting Help

- **Discord**: [Join our Discord](https://discord.gg/loom-reviews)
- **Discussions**: [GitHub Discussions](https://github.com/loom-reviews/loom-reviews/discussions)
- **Issues**: [GitHub Issues](https://github.com/loom-reviews/loom-reviews/issues)

## Recognition

Contributors are recognized in:
- README.md Contributors section
- GitHub releases
- Our website

Thank you for contributing to Loom! 🧵
