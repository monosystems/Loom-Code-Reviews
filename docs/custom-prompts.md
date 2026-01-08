# Custom Prompts

Loom allows you to write your own review prompts to customize what the AI looks for and how it provides feedback.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Prompt Structure](#prompt-structure)
- [Template Variables](#template-variables)
- [Best Practices](#best-practices)
- [Examples](#examples)
- [System Prompts](#system-prompts)
- [Troubleshooting](#troubleshooting)

## Overview

Prompts are Markdown files that define:
1. **What** the AI should look for
2. **How** it should analyze the code
3. **What format** the response should be in

Loom loads prompts from your repository (`.loom/prompts/`) or falls back to built-in system prompts.

```
.loom/
├── config.yaml
└── prompts/
    ├── security.md       # Security-focused review
    ├── quality.md        # Code quality review
    ├── docs.md           # Documentation check
    └── custom.md         # Your custom prompt
```

## Quick Start

### 1. Create a Prompt File

Create `.loom/prompts/quality.md`:

```markdown
# Code Quality Review

You are a senior software engineer reviewing a pull request.

## Your Task

Review the following code changes and identify:
- Bugs or logical errors
- Performance issues
- Code that could be simplified
- Missing error handling

## Guidelines

- Be specific - reference exact line numbers
- Explain WHY something is an issue, not just what
- Suggest concrete fixes when possible
- Prioritize issues by severity

## Response Format

Respond with a JSON array of comments:

```json
[
  {
    "file": "path/to/file.ts",
    "line": 42,
    "severity": "warning",
    "message": "Description of the issue and suggested fix"
  }
]
```

## Code Changes

{{diff}}
```

### 2. Reference in Config

```yaml
# .loom/config.yaml
pipelines:
  - name: quality
    model: default
    prompt_file: .loom/prompts/quality.md
```

## Prompt Structure

A well-structured prompt has these sections:

### 1. Role Definition

Tell the AI who it is:

```markdown
You are a security expert specializing in web applications.
You have 15 years of experience finding vulnerabilities.
```

### 2. Task Description

What should it do:

```markdown
## Your Task

Analyze the code changes for security vulnerabilities including:
- SQL injection
- XSS (Cross-Site Scripting)
- Authentication bypasses
- Secrets in code
```

### 3. Guidelines

How to do it:

```markdown
## Guidelines

- Focus on high-severity issues
- Ignore style/formatting issues
- Reference OWASP Top 10 when relevant
- Be concise but thorough
```

### 4. Context (Optional)

Additional context:

```markdown
## Project Context

This is a Node.js/Express application using PostgreSQL.
Authentication is handled via JWT tokens.

{{#each context}}
### {{this.name}}
```
{{this.content}}
```
{{/each}}
```

### 5. Response Format

How to format output:

```markdown
## Response Format

Respond with JSON only. No additional text.

```json
{
  "summary": "Brief overall assessment",
  "comments": [
    {
      "file": "string",
      "line": number,
      "severity": "blocker|warning|info",
      "message": "string"
    }
  ]
}
```
```

### 6. Code Changes

The actual diff:

```markdown
## Code Changes

{{diff}}
```

## Template Variables

Loom uses [Handlebars](https://handlebarsjs.com/) for templating.

### Available Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{diff}}` | Full unified diff | `+const x = 1;` |
| `{{files}}` | List of changed files | `['src/index.ts', 'lib/utils.ts']` |
| `{{additions}}` | Lines added | `42` |
| `{{deletions}}` | Lines deleted | `13` |
| `{{pr.title}}` | PR title | `"Add user authentication"` |
| `{{pr.description}}` | PR description | `"This PR adds..."` |
| `{{pr.author}}` | PR author | `"johndoe"` |
| `{{pr.number}}` | PR number | `123` |
| `{{pr.branch}}` | Source branch | `"feature/auth"` |
| `{{pr.base}}` | Target branch | `"main"` |
| `{{context}}` | Context files array | `[{name, content}]` |
| `{{persona}}` | Active persona config | `{tone, focus, instructions}` |

### Conditionals

```markdown
{{#if pr.description}}
## PR Description
{{pr.description}}
{{else}}
*No PR description provided.*
{{/if}}
```

### Loops

```markdown
## Changed Files
{{#each files}}
- {{this}}
{{/each}}
```

### Context Files

If you specify context files in your pipeline:

```yaml
pipelines:
  - name: quality
    context:
      - file: CONTRIBUTING.md
      - file: .eslintrc.js
```

Access them in the prompt:

```markdown
## Project Guidelines

{{#each context}}
### {{this.name}}
```
{{this.content}}
```

{{/each}}
```

### Persona Integration

If a persona is active:

```markdown
{{#if persona}}
## Review Style

Tone: {{persona.tone}}

Focus areas:
{{#each persona.focus}}
- {{this}}
{{/each}}

{{#if persona.instructions}}
Additional instructions:
{{persona.instructions}}
{{/if}}
{{/if}}
```

## Best Practices

### 1. Be Specific About Output Format

Bad:
```markdown
List any issues you find.
```

Good:
```markdown
Respond with a JSON array. Each item must have:
- file: Path to the file
- line: Line number (integer)
- severity: One of "blocker", "warning", "info"
- message: Description and fix suggestion

Example:
```json
[{"file": "src/index.ts", "line": 42, "severity": "warning", "message": "..."}]
```
```

### 2. Provide Examples

```markdown
## Examples

### Good Comment
```json
{
  "file": "src/auth.ts",
  "line": 15,
  "severity": "blocker",
  "message": "Password is logged to console. Remove `console.log(password)` to prevent credential leakage."
}
```

### Bad Comment (too vague)
```json
{
  "file": "src/auth.ts",
  "line": 15,
  "severity": "warning",
  "message": "This looks wrong"
}
```
```

### 3. Define Severity Levels

```markdown
## Severity Definitions

- **blocker**: Must be fixed before merge. Security issues, data loss, crashes.
- **warning**: Should be fixed. Bugs, performance issues, maintainability.
- **info**: Nice to fix. Style suggestions, minor improvements.
```

### 4. Set Boundaries

```markdown
## What NOT to Comment On

- Code style (covered by linters)
- Formatting (covered by prettier)
- Minor naming preferences
- Changes in files not part of this PR
```

### 5. Keep It Focused

One prompt = one purpose. Don't try to check everything in one prompt.

```yaml
pipelines:
  - name: security
    prompt_file: .loom/prompts/security.md
  - name: performance
    prompt_file: .loom/prompts/performance.md
  - name: docs
    prompt_file: .loom/prompts/docs.md
```

## Examples

### Security Review Prompt

```markdown
# Security Code Review

You are a senior application security engineer performing a security-focused code review.

## Your Task

Analyze the code changes for security vulnerabilities. Focus on:

1. **Injection Attacks**: SQL, NoSQL, Command, LDAP
2. **Authentication Issues**: Weak auth, session problems
3. **Authorization Flaws**: Missing checks, IDOR
4. **Data Exposure**: Sensitive data in logs, responses
5. **Cryptography**: Weak algorithms, hardcoded keys
6. **Input Validation**: Missing or insufficient validation

## Guidelines

- Only report actual security issues, not style
- Rate severity based on exploitability and impact
- Provide specific remediation steps
- Reference CWE IDs when applicable

## Severity Definitions

- **blocker**: Exploitable vulnerability. Must fix before merge.
- **warning**: Potential vulnerability or security smell. Should investigate.
- **info**: Security best practice suggestion.

## Response Format

```json
{
  "summary": "Overall security assessment (1-2 sentences)",
  "risk_level": "high|medium|low|none",
  "comments": [
    {
      "file": "path/to/file",
      "line": 42,
      "severity": "blocker|warning|info",
      "category": "injection|auth|authz|exposure|crypto|validation",
      "cwe": "CWE-89",
      "message": "Description of vulnerability and remediation"
    }
  ]
}
```

If no security issues found, return:
```json
{
  "summary": "No security issues identified in these changes.",
  "risk_level": "none",
  "comments": []
}
```

## Code Changes

{{diff}}
```

### Documentation Check Prompt

```markdown
# Documentation Review

You are a technical writer reviewing code changes for documentation completeness.

## Your Task

Check if the code changes are properly documented:

1. **Public APIs**: Do new functions/classes have JSDoc/docstrings?
2. **Complex Logic**: Is complex code explained with comments?
3. **Breaking Changes**: Is the changelog/migration guide updated?
4. **README**: If behavior changes, is README updated?

## Guidelines

- Only comment on documentation issues
- Suggest specific documentation to add
- Keep severity low (info or warning)

## Response Format

```json
[
  {
    "file": "path/to/file",
    "line": 42,
    "severity": "warning",
    "message": "Function `processUser` is exported but lacks JSDoc. Add parameter and return type documentation."
  }
]
```

Return an empty array if documentation is sufficient.

## Code Changes

{{diff}}
```

### Team-Specific Prompt

```markdown
# Acme Corp Code Review

You are reviewing code for Acme Corp, following our internal standards.

## Our Stack

- TypeScript + React + Next.js
- PostgreSQL with Prisma
- Jest for testing

## Our Standards

{{#each context}}
{{#if (eq this.name "CONTRIBUTING.md")}}
### Contributing Guidelines
{{this.content}}
{{/if}}
{{/each}}

## Review Focus

1. Follow our TypeScript strict mode settings
2. All database queries must use Prisma (no raw SQL)
3. React components must have prop types
4. Business logic must have unit tests

## Response Format

```json
[
  {
    "file": "string",
    "line": number,
    "severity": "blocker|warning|info",
    "message": "string"
  }
]
```

## Code Changes

{{diff}}
```

## System Prompts

Loom includes built-in system prompts as fallbacks:

| Prompt | Purpose |
|--------|---------|
| `security` | Security vulnerability detection |
| `quality` | General code quality |
| `docs` | Documentation completeness |
| `summary` | PR summary generation |

To use a system prompt, omit `prompt_file`:

```yaml
pipelines:
  - name: security
    model: default
    # No prompt_file = uses system prompt named "security"
```

Or explicitly reference it:

```yaml
pipelines:
  - name: security
    model: default
    prompt: system:security
```

## Troubleshooting

### Prompt Not Loading

1. Check file path is correct relative to repo root
2. Verify file is committed (Loom reads from git, not local)
3. Check for YAML syntax errors in config

### Bad Output Format

1. Be more explicit about JSON structure
2. Add examples of expected output
3. Use "Respond with JSON only. No additional text."

### Too Many/Few Comments

1. Adjust severity definitions
2. Add "What NOT to comment on" section
3. Use `max_comments` in output config

### Context Not Available

1. Verify context files exist in repo
2. Check file paths are correct
3. Context files are loaded before prompt rendering

### Template Errors

1. Check Handlebars syntax (`{{variable}}` not `{variable}`)
2. Verify variable names are correct
3. Use `{{#if variable}}` for optional sections
