# Jira Story Template (INV Style)

## Title
`<team-or-service> <clear outcome-focused summary>`

## Heading Style Rule
- All section titles must be **bold** and **blue**.
- Jira rendering target: bold + text color `#4C9AFF` (or nearest Jira blue).

## **🎯 Objective** (Blue + Bold)
Definition: Business goal and expected outcome of this story.
`<What this story delivers and why>`

## **⚙️ Core Logic & Workflow** (Blue + Bold)
Definition: End-to-end processing flow, success path, and failure path behavior.

### **🔄 1. Functional Flow** (Blue + Bold)
Definition: Ordered steps describing how the feature works in normal flow.
- `<step-1>`
- `<step-2>`
- `<step-3>`

### **✅ 2. Success Path Handling** (Blue + Bold)
Definition: Expected system behavior and state updates when processing succeeds.
- `<expected successful behavior>`
- `<state updates / data updates>`
- `<downstream trigger or stub>`

### **❌ 3. Failure Path Handling** (Blue + Bold)
Definition: Error handling, retries, and fallback behavior when processing fails.
- `<failure behavior>`
- `<error/log handling>`
- `<retry/fallback behavior>`

### **📊 4. Observability & Logging** (Blue + Bold)
Definition: Logs, metrics, traces, and alerts required for operational visibility.
- `<required logs>`
- `<metrics/traces/alerts>`

## **🧩 Technical Specification** (Blue + Bold)
Definition: Technical impacts, architecture notes, dependencies, and constraints.
- Project: `<project-name>`
- Requirement Source: `<FDR / Confluence / PDF / text>`
- Related Epic: `<EPIC-KEY or N/A>`
- Frontend Impact: `<details or N/A>`
- Backend Impact: `<details or N/A>`
- UI/UX Impact: `<details or N/A>`
- Mobile Impact: `<details or N/A>`
- Data/API Contracts: `<details or N/A>`
- Security/Compliance: `<details or N/A>`
- Dependencies: `<details or N/A>`
- Risks: `<details or N/A>`

## **☑️ Acceptance Criteria** (Blue + Bold)
Definition: Checklist items that must be completed for story acceptance.
- [ ] `<criterion-1 in checklist style>`
- [ ] `<criterion-2 in checklist style>`
- [ ] `<criterion-3 in checklist style>`
- [ ] `<non-functional criterion if needed>`

## **🧪 Test Scenarios** (Blue + Bold)
Definition: Validation scenarios for functional and non-functional behavior.
- `<test-scenario-1>`
- `<test-scenario-2>`

## **🏁 Definition of Done** (Blue + Bold)
Definition: Completion checklist required before closing the story.
- [ ] Code complete and peer-reviewed
- [ ] Unit/integration tests updated
- [ ] QA validation completed
- [ ] Documentation updated
- [ ] Rollback plan documented
