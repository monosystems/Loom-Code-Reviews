# Prompt Template Format

**Version:** 0.1.0  
**Status:** Design Phase  
**Last Updated:** 2026-01-18

---

## Overview

Loom prompts are **Markdown files** that instruct the LLM how to review code. They support:
- Plain Markdown text
- Variable substitution (mustache-style)
- Structured output requirements
- Multi-section organization

---

## File Location

Prompts are stored in `.loom/prompts/` directory:

```
your-repository/
└── .loom/
    ├── config.yaml
    └── prompts/
        ├── security.md
        ├── quality.md
        ├── performance.md
        └── custom.md
```

---

## Basic Structure

```markdown
# [Prompt Title]

[Brief description of what this review checks for]

## Focus Areas

[List of specific things to look for]

## Guidelines

[How to evaluate the code]

## Response Format

[Expected output structure - MUST be JSON]

## Code Changes

{{diff}}
```

---

## Required Sections

### 1. Title and Description

```markdown
# Security Code Review

You are a senior application security engineer reviewing code for vulnerabilities.
```

**Purpose:** Sets context for the LLM

### 2. Response Format

**CRITICAL:** Must specify JSON output format.

```markdown
## Response Format

Respond with a JSON array of findings. Each finding must have:
- `file`: File path (string)
- `line`: Line number (integer, optional)
- `severity`: "blocker", "warning", or "info"
- `message`: Finding description (string)

Example:
\```json
[
  {
    "file": "src/auth.py",
    "line": 42,
    "severity": "blocker",
    "message": "SQL injection vulnerability..."
  }
]
\```

If no issues found, return an empty array: `[]`
```

### 3. Code Changes Variable

```markdown
## Code Changes

{{diff}}
```

**Purpose:** Placeholder where the actual PR diff is injected

---

## Template Variables

### {{diff}}

The PR/MR diff is injected here.

**Example diff content:**
```diff
diff --git a/src/auth.py b/src/auth.py
index abc123..def456 100644
--- a/src/auth.py
+++ b/src/auth.py
@@ -10,7 +10,7 @@ def login(username, password):
-    query = "SELECT * FROM users WHERE username = '" + username + "'"
+    query = "SELECT * FROM users WHERE username = ?"
+    cursor.execute(query, (username,))
```

### Future Variables (Planned)

```markdown
{{files}}           # List of changed files
{{pr_title}}        # PR title
{{pr_description}}  # PR description
{{pr_author}}       # Author username
{{target_branch}}   # Base branch
{{context}}         # Additional context from repo
```

---

## Complete Example: Security Review

**File:** `.loom/prompts/security.md`

```markdown
# Security Code Review

You are a senior application security engineer with expertise in OWASP Top 10 and secure coding practices.

## Your Task

Analyze the code changes below for security vulnerabilities. Focus on finding actual exploitable issues, not theoretical concerns.

## Focus Areas

### 1. Injection Attacks
- SQL injection
- NoSQL injection  
- Command injection
- LDAP injection
- XPath injection

### 2. Authentication & Authorization
- Weak password validation
- Missing authorization checks
- Session management issues
- Token handling problems
- Insecure direct object references

### 3. Data Exposure
- Sensitive data in logs
- Hardcoded secrets/credentials
- PII exposure
- Excessive data in API responses
- Unencrypted sensitive data

### 4. Cryptography
- Weak algorithms (MD5, SHA1 for passwords)
- Hardcoded encryption keys
- Improper IV usage
- Weak random number generation

### 5. Input Validation
- Missing input validation
- Improper sanitization
- Type confusion vulnerabilities

## Guidelines

- **Be specific:** Reference exact file and line number
- **Explain impact:** Why is this a security issue?
- **Suggest fixes:** Provide concrete remediation
- **Severity rules:**
  - `blocker`: Directly exploitable, high impact
  - `warning`: Requires specific conditions or medium impact
  - `info`: Best practice recommendation

## Response Format

Respond with ONLY a JSON array. No other text.

Structure:
\```json
[
  {
    "file": "path/to/file",
    "line": 42,
    "severity": "blocker",
    "message": "Issue description and recommended fix"
  }
]
\```

If no security issues found, return: `[]`

## Code Changes

{{diff}}
```

---

## Complete Example: Code Quality

**File:** `.loom/prompts/quality.md`

```markdown
# Code Quality Review

You are an experienced software engineer reviewing code for maintainability and best practices.

## Review Criteria

### 1. Code Smells
- Duplicate code
- Long functions (>50 lines)
- Too many parameters (>4)
- Deep nesting (>3 levels)
- Magic numbers/strings

### 2. Bugs & Logic Errors
- Off-by-one errors
- Null pointer risks
- Race conditions
- Resource leaks
- Incorrect error handling

### 3. Best Practices
- SOLID principles
- DRY (Don't Repeat Yourself)
- Clear naming
- Appropriate comments
- Proper error handling

### 4. Performance
- O(n²) algorithms when O(n) possible
- Unnecessary database queries
- Memory leaks
- Inefficient loops

## Guidelines

- Focus on significant issues, not nitpicks
- Explain WHY something is problematic
- Suggest specific improvements
- Be constructive and helpful

## Severity Levels

- `blocker`: Bugs that will cause runtime errors or data loss
- `warning`: Code smells and maintainability issues
- `info`: Minor improvements and suggestions

## Response Format

\```json
[
  {
    "file": "string",
    "line": integer,
    "severity": "blocker|warning|info",
    "message": "Clear description and suggested fix"
  }
]
\```

## Code Changes

{{diff}}
```

---

## Complete Example: Documentation

**File:** `.loom/prompts/docs.md`

```markdown
# Documentation Review

You are a technical writer ensuring code is properly documented.

## Check For

### 1. Public APIs
All exported/public functions, classes, and interfaces should have documentation.

### 2. Required Documentation
- Function purpose
- Parameter descriptions
- Return value description
- Exceptions/errors thrown
- Usage examples (for complex APIs)

### 3. Complex Logic
Non-obvious algorithms or business logic needs explanation.

### 4. Configuration Changes
New environment variables, config options, or feature flags.

## Guidelines

- Don't require docs for obvious code
- Focus on public APIs and complex logic
- Suggest what should be documented, not exact wording
- All findings should be severity: `info` (docs aren't blockers)

## Response Format

\```json
[
  {
    "file": "string",
    "line": integer,
    "severity": "info",
    "message": "What needs documentation and why"
  }
]
\```

## Code Changes

{{diff}}
```

---

## Response Format Requirements

### Valid JSON Structure

```json
[
  {
    "file": "src/main.py",
    "line": 42,
    "severity": "blocker",
    "message": "SQL injection vulnerability. Use parameterized queries."
  },
  {
    "file": "src/utils.py",
    "line": 15,
    "severity": "warning",
    "message": "Function is too long (75 lines). Consider breaking it down."
  }
]
```

### Required Fields

- `file` (string): Relative file path
- `severity` (string): Must be `blocker`, `warning`, or `info`
- `message` (string): Finding description

### Optional Fields

- `line` (integer): Specific line number
- `category` (string): Finding category (e.g., "security", "performance")
- `suggestion` (string): Recommended fix

### Empty Response

If no issues found:
```json
[]
```

---

## Common Patterns

### Pattern 1: Focused Review

```markdown
# Performance Review

Focus ONLY on performance issues:
- O(n²) algorithms
- N+1 queries
- Memory leaks

Ignore: security, style, documentation

## Response Format
[JSON structure]

## Code Changes
{{diff}}
```

### Pattern 2: Tiered Severity

```markdown
# Review Prompt

## Severity Guidelines

**blocker**: Will cause production outage
- Crashes
- Data loss
- Security vulnerabilities

**warning**: Will cause issues eventually
- Performance problems
- Memory leaks
- Poor error handling

**info**: Improvements
- Code style
- Better naming
- Documentation

## Response Format
[JSON structure]

## Code Changes
{{diff}}
```

### Pattern 3: Language-Specific

```markdown
# Python Best Practices

Check for Python-specific issues:
- Type hints missing
- Using `==` instead of `is` for None
- Mutable default arguments
- Not using context managers
- Bare except clauses

## Response Format
[JSON structure]

## Code Changes
{{diff}}
```

---

## Anti-Patterns

### ❌ DON'T: Request Narrative Output

```markdown
# BAD
Write a paragraph explaining what you found.
```

**Problem:** Hard to parse, inconsistent format

### ❌ DON'T: Forget Response Format

```markdown
# BAD
Review the code for issues.

## Code Changes
{{diff}}
```

**Problem:** LLM will respond in unpredictable format

### ❌ DON'T: Be Too Vague

```markdown
# BAD
Find any problems in the code.
```

**Problem:** Too broad, low-quality results

### ✅ DO: Be Specific

```markdown
# GOOD
Review for SQL injection vulnerabilities. Check:
- String concatenation in queries
- Unparameterized queries
- Dynamic SQL construction

Return JSON with file, line, and description.
```

---

## Testing Prompts

### Manual Testing

```bash
# 1. Create test diff
cat > test.diff << 'EOF'
diff --git a/src/auth.py b/src/auth.py
+    query = "SELECT * FROM users WHERE id = " + user_id
EOF

# 2. Inject into prompt
cat prompts/security.md | sed "s/{{diff}}/$(cat test.diff)/"

# 3. Send to LLM manually
# curl ...
```

### Validation Checklist

- [ ] Contains {{diff}} variable
- [ ] Specifies JSON output format
- [ ] Defines severity levels
- [ ] Provides clear guidelines
- [ ] Includes examples (optional but helpful)
- [ ] Is concise (<2000 words)

---

## Best Practices

### 1. Be Specific

❌ "Check for problems"
✅ "Check for SQL injection vulnerabilities"

### 2. Define Severity Clearly

```markdown
## Severity Levels

- **blocker**: Direct exploitability + high impact
- **warning**: Indirect issue or medium impact  
- **info**: Best practice recommendation
```

### 3. Provide Examples

```markdown
## Examples

**SQL Injection (blocker):**
\```python
query = "SELECT * FROM users WHERE id = " + user_id  # BAD
\```

Should be:
\```python
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))  # GOOD
\```
```

### 4. Keep It Focused

One prompt = one concern
- Security prompt checks security
- Quality prompt checks quality
- Don't mix concerns

### 5. Enforce JSON Output

```markdown
Respond with ONLY a JSON array. No explanations, no markdown, no other text.
```

---

## Prompt Size Limits

**Recommendations:**
- **Prompt:** < 2,000 words
- **Total (prompt + diff):** < 100,000 tokens
  - GPT-4: 128k context
  - Claude: 200k context
  - Most diffs: < 10k tokens

**If diff is too large:**
- Review will be skipped
- Configure `max_changes` in config.yaml

---

## Localization

Prompts can be in any language:

```markdown
# Sicherheits-Code-Review (German)

Du bist ein erfahrener Sicherheitsingenieur...

## Zu überprüfen

- SQL-Injection
- XSS-Schwachstellen
...
```

LLM will respond in same language (usually).

---

## Version Control

Prompts are code - version them:

```bash
git log .loom/prompts/security.md
```

**Benefits:**
- Track what changed
- Rollback if needed
- Review prompt changes in PRs

---

## References

- [Configuration Schema](config-schema.md)
- [Example Prompts](examples/)
- [LLM Providers](../architecture/overview.md#llm-api-client)
