# PROTracker Invoice Intake - Technical Specification (Phase 1 Draft)

## 1. Context
- Project: PROTracker
- Jira Project Key: TER
- Scope: Phase 1 only
- Source Documents:
  - https://gpcprod.atlassian.net/wiki/spaces/DM1/pages/3401908226/ProTracker+Invoice+Intake+flow
  - https://gpcprod.atlassian.net/wiki/spaces/DM1/pages/3483730061/Protracker+Invoice+Intake+Functional+Spec

## 2. Objective
Define technical behavior for invoice intake from Invoice Domain into PROTracker, including ingestion, validation, status gatekeeping, void handling, and invoice-tab visual indicators for dispatch readiness risk.

## 3. Phase 1 Scope
### In Scope
- Invoice ingestion via TAMS -> Invoice Domain -> Pub/Sub -> PROTracker intake.
- Support and handling rules for:
  - Standard invoices.
  - NXP invoices (manual readiness behavior; no automatic NXP hold behavior in updated logic).
  - EJOEI invoices (existing flow retained).
- Exclusion handling for invoice types:
  - ROA.
  - CRD.
- State transition gatekeeping:
  - Invoiced, On Hold, Ready, Routing, To Track.
- Void/cancellation delta handling based on invoice status condition.
- Invoice tab visual escalation indicators based on ETA proximity thresholds.
- Mandatory field validations and delivery expectation handling.

### Out of Scope (Phase 1)
- Contract changes to Invoice Domain payload.
- Weight/dimensions/hazmat processing.
- 3D cubing and vehicle capacity constraints.
- Story-level Jira breakdown (excluded per current request).

## 4. Existing Functional Inputs and Interfaces
## 4.1 Upstream
- Source system: TAMS / Invoice Domain.
- Transport: Google Cloud Pub/Sub event feed.
- Trigger pattern: AutoInvoice/print when inventory is available; updates and voids continue as domain events.

## 4.2 Downstream / Internal
- PROTracker intake processor validates and enriches invoice data.
- Dispatch-facing workflow depends on readiness states and visual risk cues.
- Route optimization process starts from Ready -> Routing.

## 5. Functional Rules (Phase 1)
## 5.1 Invoice Type Rules
- Standard:
  - Keep existing behavior unchanged.
- NXP:
  - Keep visible until replenishment occurs.
  - Remove automatic hold behavior for NXP path.
  - Allow manual hold behavior.
  - Dispatcher manually marks Ready after parts are received/picked.
- EJOEI:
  - Keep existing behavior unchanged.
  - Follow standard inventory-ready flow.
  - No automatic hold unless manually triggered.
- InterStore:
  - Business confirmation required per source; keep as gated/open decision area.
- Excluded types:
  - ROA, CRD must not receive new processing logic in this module.

## 5.2 Status Transition and Gatekeeping
- Initial state: Invoiced.
- On Hold: Dispatcher/manual or hold logic entry point.
- Ready: Dispatcher marks invoice Ready for optimization eligibility.
- Routing: Optimization in progress.
- To Track: Post-routing status (source marks this as needing final confirmation behavior).

## 5.3 Delta / Void Handling
- Case A (Departed/Delivered):
  - Ignore incoming void; preserve history.
- Case B (Invoiced/Ready/Routed but not departed):
  - Execute void behavior.
  - Remove from routing scope.
  - Notify mobile route context when applicable.

## 5.4 Validation and Delivery Expectation
- Mandatory fields:
  - Customer address fields: Street, City, Zip.
  - Delivery expectation (SLA) fields from source.
- SLA handling:
  - Missing SLA -> default Standard.
  - Standard -> retrieve customer SLA from Customer Domain.
  - Deliver Together / No Rush -> explicitly marked TBD in source and retained as open item.

## 5.5 UI/UX Risk Indicator Behavior
- Applies to non-Ready invoices for targeted tiers.
- Time-based escalation:
  - >10 min: Green.
  - 10-5 min: Orange.
  - <=5 min: Red.
  - Past deadline: Flashing Red.
- Notes in source indicate icon behavior adjustments and business-approved UX references.

## 6. Technical Design (Phase 1)
## 6.1 Intake Processing Pipeline
1. Consume invoice events from Pub/Sub.
2. Validate mandatory payload fields and invoice-type eligibility.
3. Apply invoice-type rules.
4. Persist/refresh invoice state in PROTracker.
5. Apply gatekeeping transitions.
6. Surface invoice UI indicators based on ETA proximity and tier eligibility.
7. Process deltas (void/cancellation updates) via conditional rules.

## 6.2 Data and State Responsibilities
- Persist current invoice lifecycle state for decisioning.
- Maintain immutable/auditable behavior for ignored-void scenarios (departed/delivered).
- Ensure routing eligibility reflects only Ready and non-voided valid invoices.

## 6.3 Non-Functional Expectations
- Reliability:
  - Event handling must be idempotent for repeated or out-of-order updates.
- Observability:
  - Log intake decisions (accepted/rejected/void/ignored) with status and reason.
- Safety:
  - Preserve rollback/guard controls noted in intake flow references.

## 7. Open Items (Source-Carried, No Assumptions)
- InterStore scope and behavior final approval required.
- Deliver Together detailed grouping logic marked TBD.
- No Rush handling details marked TBD.
- Confirmation needed for EJOEI identifier and ETA availability path.
- Clarification of final status behavior after route creation (To Track transition condition).
- Clarification of handling when optimized routes are actioned near/outside SLA window.

## 8. Phase 1 Acceptance Targets (Technical)
- Intake supports Standard, NXP, EJOEI as defined without breaking existing Standard/EJOEI behavior.
- Excluded types (ROA, CRD) remain outside processing scope.
- Gatekeeping states operate per defined transition triggers.
- Void handling follows status-conditional behavior with correct routing impact.
- Invoice tab risk indicators render correctly for defined thresholds and eligible cases.
- Mandatory field and SLA default logic are enforced.

## 9. References
- ProTracker Invoice Intake flow:
  - https://gpcprod.atlassian.net/wiki/spaces/DM1/pages/3401908226/ProTracker+Invoice+Intake+flow
- Protracker Invoice Intake Functional Spec:
  - https://gpcprod.atlassian.net/wiki/spaces/DM1/pages/3483730061/Protracker+Invoice+Intake+Functional+Spec
