# Data Flow

**Version:** 0.1.0  
**Status:** Design Phase

---

## Complete Request Flow

This document describes the end-to-end flow from webhook reception to review completion.

---

## Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. Developer Opens/Updates PR                                    │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ 2. Git Platform Sends Webhook                                    │
│    POST /webhooks/{platform}                                     │
│    - Signature in headers                                        │
│    - Event payload in body                                       │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ 3. Webhook Handler (FastAPI)                                     │
│    ├─ Verify signature (HMAC/token)                              │
│    ├─ Parse payload → WebhookEvent                               │
│    ├─ Check if repo is enabled                                   │
│    ├─ Apply trigger rules (branches, paths, etc.)                │
│    └─ Create Job record in database                              │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ 4. Queue Job (Redis + Celery)                                    │
│    ├─ Job ID generated                                           │
│    ├─ Priority determined (severity)                             │
│    ├─ Enqueue to appropriate queue                               │
│    └─ Return 200 OK to git platform                              │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ 5. Worker Picks Up Job (Celery Worker)                           │
│    ├─ Dequeue job from Redis                                     │
│    ├─ Update job status: "processing"                            │
│    └─ Start review process                                       │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ 6. Fetch PR Data (via Adapter)                                   │
│    ├─ Get PR/MR info (title, author, etc.)                       │
│    ├─ Fetch diff                                                 │
│    └─ List changed files                                         │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ 7. Load Configuration (via Adapter)                              │
│    ├─ Fetch .loom/config.yaml from repo                          │
│    ├─ Parse YAML → Config object                                 │
│    ├─ Validate config schema                                     │
│    └─ Fetch prompt templates (.loom/prompts/*.md)                │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ 8. Execute Review Pipelines (Parallel/Sequential)                │
│    For each pipeline in config:                                  │
│      ├─ Load prompt template                                     │
│      ├─ Inject diff into template                                │
│      ├─ Call LLM API                                             │
│      ├─ Parse LLM response (JSON)                                │
│      └─ Collect findings                                         │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ 9. Aggregate Results                                             │
│    ├─ Combine findings from all pipelines                        │
│    ├─ De-duplicate similar findings                              │
│    ├─ Apply severity filters                                     │
│    └─ Format comments for platform                               │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ 10. Post Comments (via Adapter)                                  │
│     ├─ General summary comment                                   │
│     ├─ Inline comments on specific lines                         │
│     └─ Update job status: "completed"                            │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ 11. Developer Sees Review                                        │
│     └─ Comments appear on PR/MR                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Detailed Steps

### Step 1-2: Webhook Trigger

**Trigger Events:**
- PR/MR opened
- New commits pushed to PR/MR
- PR/MR reopened

**Example GitHub Webhook:**
```json
{
  "action": "opened",
  "number": 42,
  "pull_request": {
    "id": 123456,
    "number": 42,
    "title": "Add new feature",
    "state": "open",
    "user": {"login": "developer"},
    "head": {
      "ref": "feature/new-feature",
      "sha": "abc123def456"
    },
    "base": {
      "ref": "main",
      "sha": "789012ghi345"
    }
  },
  "repository": {
    "full_name": "owner/repo"
  }
}
```

---

### Step 3: Webhook Handler

**Code:**
```python
@router.post("/webhooks/{platform}")
async def handle_webhook(platform: str, request: Request):
    # 1. Get adapter
    adapter = get_adapter(platform)
    
    # 2. Verify signature
    if not await adapter.verify_webhook(request):
        raise HTTPException(401, "Invalid signature")
    
    # 3. Parse payload
    payload = await request.json()
    event = await adapter.parse_webhook(payload)
    
    # 4. Check repo enabled
    repo = await db.get_repo(event.repo_full_name, platform)
    if not repo or not repo.is_active:
        return {"success": False, "reason": "repo_not_enabled"}
    
    # 5. Apply trigger rules
    config = await fetch_config(event, adapter)
    if not should_review(event, config):
        return {"success": False, "reason": "triggers_not_matched"}
    
    # 6. Create job
    job = await db.create_job(
        repo_id=repo.id,
        pr_number=event.pr_number,
        head_sha=event.head_sha,
        status="queued"
    )
    
    # 7. Enqueue
    review_task.apply_async(
        args=[job.id, event.dict()],
        queue="review.normal"
    )
    
    return {"success": True, "job_id": job.id}
```

**Trigger Rules Check:**
```python
def should_review(event: WebhookEvent, config: Config) -> bool:
    # Check branches
    if config.triggers.branches:
        if event.target_branch not in config.triggers.branches:
            return False
    
    # Check ignored authors
    if event.pr_author in config.triggers.ignore_authors:
        return False
    
    # Check changed files (requires fetching diff)
    # ...
    
    return True
```

---

### Step 4-5: Job Queuing & Processing

**Celery Task:**
```python
@celery_app.task(bind=True, max_retries=3)
def review_task(self, job_id: str, event_data: dict):
    try:
        # Update status
        db.update_job(job_id, status="processing")
        
        # Execute review
        result = await execute_review(job_id, event_data)
        
        # Update status
        db.update_job(
            job_id,
            status="completed",
            completed_at=datetime.now(),
            result=result
        )
        
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
```

---

### Step 6-7: Data Fetching

**Fetch PR Data:**
```python
async def fetch_pr_data(event: WebhookEvent, adapter: GitAdapter):
    # Get PR info
    pr_info = await adapter.get_pr_info(
        event.repo_full_name,
        event.pr_number
    )
    
    # Get diff
    diff = await adapter.fetch_diff(
        event.repo_full_name,
        event.pr_number
    )
    
    # Get config file
    config_yaml = await adapter.fetch_file(
        event.repo_full_name,
        ".loom/config.yaml",
        event.head_sha
    )
    
    return pr_info, diff, config_yaml
```

**Parse Configuration:**
```python
from pydantic import BaseModel
import yaml

def parse_config(config_yaml: str) -> Config:
    data = yaml.safe_load(config_yaml)
    config = Config(**data)  # Pydantic validation
    return config
```

---

### Step 8: LLM Review Execution

**For Each Pipeline:**
```python
async def execute_pipeline(
    pipeline: Pipeline,
    diff: str,
    config: Config
) -> List[Finding]:
    # 1. Load prompt template
    prompt_template = await load_prompt(pipeline.prompt_file)
    
    # 2. Inject diff
    prompt = prompt_template.replace("{{diff}}", diff)
    
    # 3. Get LLM config
    llm_config = config.models[pipeline.model]
    
    # 4. Call LLM
    response = await call_llm(llm_config, prompt)
    
    # 5. Parse response
    findings = parse_llm_response(response)
    
    # 6. Tag with pipeline info
    for finding in findings:
        finding.pipeline = pipeline.name
        finding.severity = pipeline.severity
    
    return findings
```

**LLM API Call:**
```python
async def call_llm(config: LLMConfig, prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{config.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": config.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": config.temperature,
                "max_tokens": config.max_tokens
            },
            timeout=60.0
        )
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
```

**Parse Response:**
```python
def parse_llm_response(response: str) -> List[Finding]:
    # Expected format: JSON array
    # [
    #   {
    #     "file": "src/main.py",
    #     "line": 42,
    #     "severity": "blocker",
    #     "message": "SQL injection vulnerability..."
    #   }
    # ]
    
    try:
        findings_data = json.loads(response)
        findings = [Finding(**f) for f in findings_data]
        return findings
    except (json.JSONDecodeError, ValidationError) as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return []
```

---

### Step 9: Result Aggregation

**Combine Findings:**
```python
def aggregate_findings(
    pipeline_results: Dict[str, List[Finding]]
) -> List[Finding]:
    all_findings = []
    
    for pipeline_name, findings in pipeline_results.items():
        all_findings.extend(findings)
    
    # De-duplicate
    unique_findings = deduplicate_findings(all_findings)
    
    # Sort by severity and file/line
    sorted_findings = sorted(
        unique_findings,
        key=lambda f: (
            SEVERITY_ORDER[f.severity],
            f.file or "",
            f.line or 0
        )
    )
    
    return sorted_findings

def deduplicate_findings(findings: List[Finding]) -> List[Finding]:
    """Remove duplicate findings based on file + line + message similarity"""
    seen = set()
    unique = []
    
    for finding in findings:
        key = (finding.file, finding.line, finding.message[:50])
        if key not in seen:
            seen.add(key)
            unique.append(finding)
    
    return unique
```

---

### Step 10: Comment Posting

**Format Comments:**
```python
def format_summary_comment(findings: List[Finding]) -> str:
    """Create summary comment for PR"""
    blockers = [f for f in findings if f.severity == "blocker"]
    warnings = [f for f in findings if f.severity == "warning"]
    info = [f for f in findings if f.severity == "info"]
    
    comment = f"""## 🧵 Loom Code Review
    
**Summary:** {len(findings)} findings

- 🚫 {len(blockers)} blockers
- ⚠️ {len(warnings)} warnings
- ℹ️ {len(info)} suggestions

### Details
"""
    
    for finding in findings[:10]:  # Top 10
        emoji = SEVERITY_EMOJI[finding.severity]
        comment += f"\n{emoji} **{finding.file}:{finding.line}** - {finding.message[:100]}..."
    
    if len(findings) > 10:
        comment += f"\n\n*...and {len(findings) - 10} more findings*"
    
    return comment

def format_inline_comment(finding: Finding) -> str:
    """Create inline comment for specific line"""
    emoji = SEVERITY_EMOJI[finding.severity]
    return f"{emoji} **{finding.severity.upper()}**: {finding.message}"
```

**Post to PR:**
```python
async def post_review_comments(
    adapter: GitAdapter,
    repo: str,
    pr_number: int,
    findings: List[Finding]
):
    # 1. Post summary comment
    summary = format_summary_comment(findings)
    await adapter.post_comment(
        repo, pr_number,
        Comment(body=summary, path=None, line=None)
    )
    
    # 2. Post inline comments
    for finding in findings:
        if finding.file and finding.line:
            comment = format_inline_comment(finding)
            await adapter.post_comment(
                repo, pr_number,
                Comment(
                    body=comment,
                    path=finding.file,
                    line=finding.line
                )
            )
```

---

## Timing & Performance

**Expected Timings (typical PR < 500 lines):**

| Step | Duration | Notes |
|------|----------|-------|
| Webhook → Queue | < 100ms | Signature verification, DB write |
| Queue → Worker | < 1s | Depends on worker availability |
| Fetch PR Data | 1-3s | API calls to git platform |
| Load Config | 1-2s | Fetch YAML + prompts |
| LLM Processing | 10-30s | Depends on diff size, model |
| Parse Response | < 100ms | JSON parsing |
| Post Comments | 2-5s | Multiple API calls |
| **Total** | **15-45s** | Most time is LLM processing |

**Optimization Strategies:**
- Parallel pipeline execution
- Cache config files (5min TTL)
- Batch comment posting
- Stream LLM responses (future)

---

## Error Handling

**Failures at Each Step:**

| Step | Failure | Action |
|------|---------|--------|
| Webhook verification | Invalid signature | Return 401, log attempt |
| Repo not found | Missing DB entry | Return 200 (silent skip) |
| Config not found | Missing .loom/config.yaml | Use default config |
| Config invalid | YAML parse error | Post error comment |
| LLM API error | Timeout, rate limit | Retry with backoff |
| LLM response invalid | JSON parse error | Log error, skip pipeline |
| Comment posting failed | API error | Retry, then fail job |

**Retry Strategy:**
```python
@celery_app.task(
    bind=True,
    max_retries=3,
    autoretry_for=(APIError, TimeoutError),
    retry_backoff=True,  # Exponential backoff
    retry_backoff_max=600,  # Max 10 minutes
    retry_jitter=True
)
def review_task(self, job_id: str, event_data: dict):
    # ...
```

---

## Monitoring & Observability

**Metrics to Track:**
- Webhook processing time
- Job queue depth
- Worker processing time
- LLM API latency
- Error rates per step
- Cost per review (LLM tokens)

**Logging:**
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "webhook_received",
    platform="github",
    repo="owner/repo",
    pr_number=42,
    event="opened"
)

logger.info(
    "review_completed",
    job_id=job_id,
    duration_seconds=elapsed,
    findings_count=len(findings),
    llm_tokens_used=tokens
)
```

---

## Future Optimizations

- [ ] Incremental reviews (only changed files)
- [ ] Parallel pipeline execution
- [ ] LLM response streaming
- [ ] Smart config caching
- [ ] Batch comment posting
- [ ] Worker auto-scaling

---

## References

- [Architecture Overview](overview.md)
- [Adapter Pattern](adapter-pattern.md)
- [Configuration Schema](../configuration/config-schema.md)
