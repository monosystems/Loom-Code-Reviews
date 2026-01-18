# Feature TODOs

## 🚀 Critical (Mentioned in Docs but Missing)

### CLI Tool
**Priority:** High  
**Mentioned in:** `configuration.md`, `getting-started.md`

- [ ] Design CLI interface
- [ ] Implement config validation
  ```bash
  loom config validate
  loom config test --file .loom/config.yaml
  ```
- [ ] Implement prompt testing
  ```bash
  loom prompt test --prompt .loom/prompts/security.md --diff sample.diff
  ```
- [ ] Repository management commands
  ```bash
  loom repos list
  loom repos add github:org/repo
  loom repos sync
  ```
- [ ] Review management
  ```bash
  loom reviews list --repo=org/repo
  loom reviews retry <review-id>
  ```
- [ ] Package as npm/pip package
- [ ] Add to documentation

### Response to Comments
**Priority:** Medium  
**Status:** Marked as "future: respond" in architecture.md

- [ ] Design interaction model
- [ ] Detect @loom mentions in PR comments
- [ ] Parse follow-up questions
- [ ] Generate contextual responses
- [ ] Post replies
- [ ] Rate limiting for responses
- [ ] Document the feature

### Helm Chart
**Priority:** High (for enterprise)  
**Status:** Mentioned but no concrete chart

- [ ] Create helm chart structure
- [ ] Values.yaml with all options
- [ ] Templates for deployments
- [ ] ConfigMaps and Secrets
- [ ] Service and Ingress
- [ ] PostgreSQL subchart option
- [ ] NOTES.txt with setup instructions
- [ ] Publish to chart repository
- [ ] Document in self-hosting.md

### GitHub Check Runs
**Priority:** Medium  
**Status:** Listed as "optional" in github.md

- [ ] Implement check run creation
- [ ] Map review status to check status
- [ ] Detailed annotations on code
- [ ] Summary in check run
- [ ] Update on review completion
- [ ] Configuration option
- [ ] Document the feature

### GitHub Issue Creation
**Priority:** Low  
**Status:** Listed as "optional" in github.md

- [ ] Create issues from blocker findings
- [ ] Template for issue body
- [ ] Auto-assign to PR author
- [ ] Link to original PR
- [ ] Configuration options
- [ ] Document the feature

---

## 💼 Enterprise Features (Post-v1.0)

### Compliance & Security

**SOC 2 Compliance**
- [ ] Audit logging system
- [ ] Access control logs
- [ ] Change tracking
- [ ] Compliance reports
- [ ] Security controls documentation

**SSO/SAML Integration**
- [ ] SAML 2.0 support
- [ ] Okta integration
- [ ] Azure AD integration
- [ ] Google Workspace SSO
- [ ] JIT provisioning

**RBAC (Role-Based Access Control)**
- [ ] Define role hierarchy
  - Super Admin
  - Org Admin
  - Org Member
  - Viewer
- [ ] Permission system
- [ ] Resource-level permissions
- [ ] API integration
- [ ] UI for role management

**Audit Logging**
- [ ] Log all API calls
- [ ] Log configuration changes
- [ ] Log user actions
- [ ] Searchable audit trail
- [ ] Export capabilities
- [ ] Retention policies

### Team Collaboration

**Shared Prompt Library UI**
- [ ] Browse shared prompts
- [ ] Create/edit prompts in dashboard
- [ ] Version history for prompts
- [ ] Import/export prompts
- [ ] Prompt categories/tags
- [ ] Search and filter

**Team Policies**
- [ ] Org-wide configuration enforcement
- [ ] Required pipelines
- [ ] Blocked file patterns
- [ ] Branch protection rules
- [ ] Approval workflows

**Review Analytics Dashboard**
- [ ] Review volume over time
- [ ] Average review time
- [ ] Common findings
- [ ] Repository comparison
- [ ] Team performance metrics
- [ ] Cost tracking per repo

**Budget & Cost Tracking**
- [ ] Track LLM costs per repo
- [ ] Budget alerts
- [ ] Cost allocation by team
- [ ] Spending trends
- [ ] Provider comparison

---

## 🧪 Testing & Quality

### Test Infrastructure
- [ ] E2E test suite setup
  - Playwright/Cypress tests
  - Test all critical flows
  - CI integration
  
- [ ] Integration tests
  - Adapter tests (all platforms)
  - LLM provider tests
  - Database tests
  
- [ ] Performance tests
  - Load testing setup
  - Benchmark suite
  - Regression detection
  
- [ ] Coverage targets
  - Backend: 80%+
  - Frontend: 70%+
  - Critical paths: 95%+

### Quality Gates
- [ ] Pre-commit hooks
- [ ] CI/CD pipeline
- [ ] Automated security scanning
- [ ] Dependency updates (Dependabot)
- [ ] Code review guidelines

---

## 🔌 Integrations (Future)

### Notifications
- [ ] Slack integration
  - Webhook notifications
  - Slash commands
  - Interactive messages
  
- [ ] Microsoft Teams
  - Webhook notifications
  - Bot integration
  
- [ ] Email notifications
  - Digest emails
  - Critical findings alerts

### Project Management
- [ ] Jira integration
  - Create tickets from findings
  - Link to PRs
  - Status sync
  
- [ ] Linear integration
  - Similar to Jira
  
- [ ] GitHub Projects
  - Auto-add cards

### Incident Management
- [ ] PagerDuty integration
  - Alert on critical findings
  - Escalation policies
  
- [ ] Opsgenie
  - Similar to PagerDuty

### Monitoring
- [ ] Datadog APM
  - Performance monitoring
  - Custom metrics
  
- [ ] New Relic
  - Application monitoring
  
- [ ] Sentry
  - Error tracking

### IDE Extensions
- [ ] VS Code extension
  - View reviews in editor
  - Trigger reviews
  - Configure from IDE
  
- [ ] JetBrains plugin
  - Similar to VS Code

### CI/CD Plugins
- [ ] GitHub Actions
  - Trigger review action
  - Status checks
  
- [ ] GitLab CI
  - Pipeline integration
  
- [ ] Jenkins plugin

---

## 🎨 UI/UX Improvements

### Dashboard Enhancements
- [ ] Dark mode
- [ ] Customizable layout
- [ ] Keyboard shortcuts
- [ ] Advanced search/filters
- [ ] Bulk actions
- [ ] Export data (CSV, JSON)

### Review Interface
- [ ] Inline code viewer
- [ ] Collapsible comments
- [ ] Filter by severity
- [ ] Comment threads
- [ ] Review comparison
- [ ] Historical trends

### Configuration UI
- [ ] Visual config editor
- [ ] Drag-and-drop pipeline builder
- [ ] Prompt playground
- [ ] Template library
- [ ] Config validation in UI
- [ ] Import/export configs

---

## 🌍 Internationalization

- [ ] i18n framework setup
- [ ] UI translations
  - [ ] German
  - [ ] French
  - [ ] Spanish
  - [ ] Japanese
  - [ ] Chinese
  
- [ ] Localized prompts
- [ ] Translation contribution guide
- [ ] RTL language support

---

## 🔍 Advanced Features (Ideas)

### AI Enhancements
- [ ] Multi-model voting (ensemble)
- [ ] Confidence scoring
- [ ] Learning from feedback
- [ ] Custom fine-tuned models
- [ ] Prompt optimization suggestions

### Smart Features
- [ ] Auto-fix suggestions (GitHub Copilot style)
- [ ] Predictive analysis (likely issues)
- [ ] Similar PR suggestions
- [ ] Review time estimation
- [ ] Risk scoring

### Automation
- [ ] Auto-merge on approval
- [ ] Scheduled reviews
- [ ] Batch reviews
- [ ] Cron-triggered checks
- [ ] Post-merge audits

---

## 📊 Feature Tracking

| Feature | Priority | Status | Target |
|---------|----------|--------|--------|
| CLI Tool | High | Not Started | v1.1 |
| Helm Chart | High | Not Started | v1.0 |
| Comment Responses | Medium | Not Started | v1.2 |
| Check Runs | Medium | Not Started | v1.1 |
| SOC 2 | High | In Progress | v2.0 |
| SSO | High | Not Started | v2.0 |
| RBAC | High | Not Started | v2.0 |
| Analytics | Medium | Not Started | v1.3 |
| E2E Tests | High | Not Started | v1.0 |

---

## 💡 Feature Ideas to Explore

- Code quality trends over time
- Developer productivity metrics
- Custom LLM fine-tuning support
- Prompt marketplace
- AI model comparison tool
- Review templates
- Scheduled reports
- API rate limit management
- Cost optimization recommendations
- Integration marketplace
