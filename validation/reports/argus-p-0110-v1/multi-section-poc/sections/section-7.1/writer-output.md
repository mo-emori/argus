## 7.1 Verification

### Premise

The command-line interface provides `help`, `status`, `budget`, and `system`, and echoes absolute time. Operators are not expected to memorize commands.

### Problem

Names alone do not establish the scope or strength of Capability Verification (CV), Regression Verification (RV), the Minimum Vertical Slice (MVS), point-in-time data (PIT), compare-and-swap (CAS), or fail-closed behavior. Treating a design description or self-report as a measured pass, or treating a component test as proof that a closed loop is complete, can promote a capability that has not been established. Likewise, treating different verification types as the same kind of pass obscures the limits of capability, regression, historical, and operational evaluation.

Every verification identifier therefore needs an explicit subject and decision boundary. Otherwise, a result that is not run or only partly successful can be elevated to an overall pass. A capability cannot be accepted merely because it exists in the design: real-environment constraints and failure behavior must be measured. The completion assessment also needs gates that can expose defective derived labels, repeated instances of the same semantic type, and defects in the Prompt Artifact.

### Purpose

This section defines the core verification and implementation concepts, their differences, and their decision limits. It separates what each verification observes, how its criteria are fixed, and who retains decision authority. It defines frozen-basis CV and RV, the MVS gate, the complete `CV-00` through `CV-50` scope, the `RV-01` through `RV-35` scope, and Gates A through R for Structured Design Data and the Prompt Artifact. Every CV is decided from measured evidence, not from design presence or assertion.

### Verification concepts and boundaries

| Concept | Meaning and subject | Required boundary |
|---|---|---|
| CV | Capability or gate verification of local capability, contracts, gateways, storage, and related behavior. It measures pre-fixed requirements, inputs, expected results, and acceptance criteria in the real environment. | It is not post-change regression. The range is `CV-00`–`CV-50`. |
| RV | Regression verification that an already established capability has not been broken by a change. Core, Affected, and Full sets are defined by the Test Strategy. | `NOT_RUN` is not `PASS`. The range is `RV-01`–`RV-35`. |
| MVS | The Minimum Vertical Slice that carries a flow from `BUY` through `SELL`, complete liquidation, and restoration after restart. | A successful individual component or generation of a SELL Proposal does not complete the slice. `RV-16` is the applicable gate. |
| PIT | Point-in-time data that was available at the simulated time. | Later revisions and the current Universe must not be mixed into historical validation. |
| CAS | Server-side conditional write / compare-and-swap required for a future cloud backend. | It must not weaken the local OS/filesystem-lock plus atomic-replace design into a simple read-then-write sequence. |
| Fail Closed | A safety behavior that prevents a subsequent hazardous operation when required Policy, Cost, Identity, Data, or another prerequisite is not established. | It does not mean refusing all work until Facts have been received. It applies to Risk, Budget, and Binding controls. |

The verification types are intentionally non-interchangeable:

| Verification type | What it establishes | Constraint or authority boundary |
|---|---|---|
| CV | Measured local capability and contract conformance | Uses criteria frozen before execution. |
| RV | Absence of regression in established capability | A missing run remains `NOT_RUN`, never `PASS`. |
| Quant Backtest | Deterministic numerical-logic behavior | Future data is completely excluded. |
| Model Historical Replay | Reference evaluation of past-time workflow and reasoning | Learned future knowledge cannot be completely removed; the result must not be called pure out-of-sample evaluation. |
| Paper Trading | Prospective operational-performance evaluation | Uses no real funds; execution rules are frozen in advance and results carry `SIMULATED`. |
| Live Readiness | Whether real-fund operation may begin | Separate from design completion; a human makes the final start decision. |

MVS and Deferred Scope are verification-scope distinctions, not substitutes for CV or RV. Human, ARGUS, and Broker authority remains separated; in particular, measured readiness does not transfer the final Live Readiness decision away from the human.

### Capability verification catalogue

Before any CV runs, its requirement, input, expected result, acceptance criteria, environment, and trial count are fixed. After execution, the record contains the observed result, success count, latency distribution, Evidence, and one of `PASS`, `PARTIAL`, or `FAIL`. Anything not executed is `NOT_RUN`.

| ID | Verification subject | Required observation or invariant | Decision limit, prohibition, or recovery expectation |
|---|---|---|---|
| `CV-00` | Local host, path, permission, and API configuration | Record the target environment in the Manifest. | Do not expose Secrets in Logs. |
| `CV-01` | Loop, wait, Due, Sleep, and Offline recovery | Detect missed execution and perform Catch-up. | This does not prove continuous monitoring. |
| `CV-02`–`CV-05` | Web, market, J-Quants, EDINET, price, and financial-result material | Verify acquisition, freshness, and missing-data behavior. | The paid TDnet API is out of scope. |
| `CV-06` | Canonical persistence | Retrieve the latest version from another Run. | Do not promote an old copy to canonical status. |
| `CV-07` | Atomic State | Verify atomic and durable updates. | Record the guarantees actually provided by Windows and the filesystem. |
| `CV-08`–`CV-09` | Markdown, Queue, and Incident | Verify persistence and regeneration. | A Projection must not become canonical. |
| `CV-10`–`CV-11` | Notification | Verify Adapter, time, and Status control. | Keep delivery separate from `ACK`. |
| `CV-12`–`CV-13` | Concurrency | Verify exclusion, version conflict, and recalculation by attempting concurrent updates from the same version. | Concurrent writers must not silently succeed from the same base version. |
| `CV-14` | Polling and cursor | Exercise gaps, missed items, and Catch-up. | Do not conceal omissions. |
| `CV-15` | Provenance | Retain source, query, hash, Prompt, Code, and Config. | The record must remain traceable later. |
| `CV-16A` | Validator calculation | Exercise `BOOTSTRAP`, `REPAIR`, and `SELL` exceptions. | Establish numerical correctness. |
| `CV-16B` | Validator enforcement | Test bypass and tamper resistance and Validation Integrity. | Do not claim that the Hard Gate is enforced unless this is verified. |
| `CV-17`–`CV-19` | PIT Data | Exercise delisted instruments, historical Universe, publication, and revision behavior. | Detect future leakage. |
| `CV-20` | Interruption recovery | Interrupt write, communication, Sleep, kill, Log, Order, and restart paths. | Recovery must not apply an action twice. |
| `CV-21` | Retry classification | Verify the next Cycle after `MAX_RETRY` and verify idempotency. | Do not discard work permanently. |
| `CV-22` | Human CLI | Exercise Approval, Reject, Paste, `request_id`, `trade_hash`, and Slot Commit. | Bind the decision to the specific Trade. |
| `CV-23` | Budget Gate | Exercise job, run, daily, monthly, Catch-up, and quota limits. | Do not start a Call that exceeds a limit. |
| `CV-24` | Secret and Privacy | Verify non-output, Allowlist, Denylist, and redaction. | Inspect debug dumps as well. |
| `CV-25` | Runner lock | Exercise duplicate startup, stale ownership, and heartbeat. | Do not seize the lock without establishing that doing so is safe. |
| `CV-26` | Durable Stage | Reuse a durable result after Commit failure. | Avoid charging again for the same completed stage. |
| `CV-27` | Archive | Exercise rotation, compaction, and rebuild. | Establish the boundary that prevents unbounded Current Envelope growth. |
| `CV-28` | Restore | Keep `BUY` and `ADD` stopped until Reconciliation completes. | Do not resume from stale Facts. |
| `CV-29` | Clock | Exercise wall and monotonic clocks, Sleep, and timezone behavior. | Detect and report `CLOCK_DISCONTINUITY`. |
| `CV-30` | After-close handling | Revalidate on the next business day. | Require reapproval when the Trade changes. |
| `CV-31` | Windows behavior | Exercise atomic replace, lock, and kill recovery. | State the supported range in the Manifest. |
| `CV-32` | Status and Lease | Verify Mapping, today/week boundaries, and transition to `NORMAL`. | Do not transition automatically to `FREE`. |
| `CV-33` | Status conflict | Race a human reset against Lease expiry. | Reject a stale automatic transition. |
| `CV-34` | Pre-submit budget failure | Exercise `HOLD`, Incident, `hold_ttl`, and release. | Do not place an order after incomplete revalidation. |
| `CV-35` | Alert | Exercise Queue, Popup, `ACK`, restart, and Window. | Verify the interaction with Maintenance. |
| `CV-36` | CLI | Exercise `help`, `status`, `budget`, `system`, and absolute-time echo. | Command memorization must not be a prerequisite. |
| `CV-37` | External Data Storage | Exercise connection, disconnection, reconnection, and capacity warning. | Perform Catch-up after recovery. |
| `CV-38` | Development/runtime separation | Verify manual Deploy, Schema handling, and prevention of state/data overwrite. | Update only after Runtime has stopped. |
| `CV-39` | Raw and Normalized data | Verify provenance, JSONL, originals, and regeneration. | Raw data is immutable. |
| `CV-40` | Runner Lifecycle | Verify `INIT` → `RUNNING` → `END`, abnormal-exit recovery through `INIT` → `RESUMING` → `RUNNING`, and Graceful Exit. | Crash is not a persisted state; recovery occurs on the next startup. |
| `CV-41` | Shared Service | While not `RUNNING`, permit Status, Help, and System Status; reject Execution Paste; use the same Validator and Writer. | Do not fork behavior among CLI, Tray, and Runner. |
| `CV-42` | Severity and Priority | Verify the closed class, the three Override states, and deduplication. | An Investment Event must not bypass the control. |
| `CV-43` | Config Snapshot | Fix the hash at the Job boundary and exercise a lowered limit. | Do not inject configuration midway through a Job. |
| `CV-44` | Storage and Environment Identity | Exercise a different disk using the same `L:` drive letter, marker mismatch, and recovery. | Reject writes on mismatch. |
| `CV-45` | Paid Governance | Exercise absent approval, upgrade, fallback, and Correction. | Any increased Commitment requires reapproval. |
| `CV-46` | Gateway | Verify retry, cost, audit, error handling, and the Adapter boundary. | Business Logic must not depend directly on the external service. |
| `CV-47` | Backup and Pressure | Exercise local backup, stale data, degradation order, and Minimum Data. | Protect Canonical and Audit data. |
| `CV-48` | J-Quants Free | Verify authentication, schema, raw/normalize handling, retry, and bulk structure. | Do not mark Operational capability `PASS`. |
| `CV-49` | J-Quants Light | Verify coverage, update timing, bulk behavior, rate limit, and latency. | Measure only after human contract approval. |
| `CV-50` | Service Registry | Exercise expiry, authentication, stale data, freshness, and health. | An HTTP success alone does not establish `Healthy`. |

The formal states exposed by these checks are `INIT`, `RUNNING`, `RESUMING`, `END`, `NORMAL`, `FREE`, and `PENDING`; their subjects must remain distinct. In particular, the Runner lifecycle uses `INIT`, `RUNNING`, `RESUMING`, and `END`, while Status/Lease verification uses `NORMAL` and `FREE`. `PENDING` identifies the review state used by the completion gates below.

### Structured Design Data and Prompt Artifact completion gates

Gates A through R check structure, semantic typing, relations, Authority, source reconciliation, the Prompt Artifact, and change scope. The recorded automated or structural result does not replace human review: every gate remains `PENDING` for that review unless stated otherwise.

| Gate | Subject | Recorded result | Completion condition or finding | Review status and required follow-up |
|---|---|---|---|---|
| A | Source duplication | `PASS` | Excludes the full Source, large continuous Source passages, any layer that houses Source prose, and appendices. | `PENDING` — awaiting Human Review. |
| B | Standalone completeness | `PASS` | Terms, processes, states, Data, Constraint, Failure, and Verification can be obtained without copying Source prose. | `PENDING` — awaiting Human Review. |
| C | Terminology | `PASS` | Classification axes are separated in Section 2, and Universe, Hard Risk, CV, RV, MVS, PIT, and similar terms are defined before use. | `PENDING` — awaiting Human Review. |
| D | Premise, problem, purpose, and subject | `PASS` | Every chapter, section, and subsection with design content places the common headers in order; a premise appears only when supported by the Source; problem and purpose remain non-synonymous. | `PENDING` — awaiting Human Review. |
| E | Standard semantic types | `PASS` | Design statements outside tables use the standard vocabulary or an explicitly approved abnormal-handling label. | `PENDING` — awaiting Human Review. |
| F | Consolidation of identical semantic types | `PASS` | Identical semantic types in one section are consolidated under one label as a list or table. | `PENDING` — awaiting Human Review. |
| G | Process | `PASS` | Core Lifecycle, Retryable Job, Execution Paste, MVS, Bootstrap, Event, Restore, and Deploy are decomposed into process tables. | `PENDING` — awaiting Human Review. |
| H | State | `PASS` | Runtime, User Status, Policy, Research, Thesis, Proposal, Order, Holding, Incident, and Notification states are separated by subject. | `PENDING` — awaiting Human Review. |
| I | Table semantics | `PASS` | State, classification, severity, priority, and other meanings use separate tables with consistent row sets and column attributes. | `PENDING` — awaiting Human Review. |
| J | Unlabelled prose | `PASS` | Every design statement, including prose before and after tables, has an explicit semantic type. | `PENDING` — awaiting Human Review. |
| K | Type separation | `PASS` | Gateway responsibility, Budget, Storage, Break, Version, and other concerns are separated by semantic type. | `PENDING` — awaiting Human Review. |
| L | Relations | `PASS` | Problem → purpose → means, input-process-output, state transition, Authority, Policy → Constraint, Failure → Recovery, and Data producer/consumer relations are traceable. | `PENDING` — awaiting Human Review. |
| M | Specificity | `PASS` | Numbers, times, thresholds, exceptions, prohibitions, failure behavior, unresolved matters, and design reasons are retained. | `PENDING` — awaiting Human Review. |
| N | Authority | `PASS` | The responsibilities, powers, and boundaries of the human, ARGUS, LLM, Writer, Broker, and external Service are preserved. | `PENDING` — awaiting Human Review. |
| O | Full-section scan | `PASS` | Every heading is scanned individually for common headers, synonymous repetition, standard labels, same-type consolidation, Process, State, and post-table prose. | `PENDING` — awaiting Human Review. |
| P | Source reconciliation | `PASS` | The Source is semantically reconciled from beginning to end, and omissions are restored to the appropriate structure rather than by copying Source prose. | `PENDING` — awaiting Human Review. |
| Q | Prompt Artifact | `REVIEW` | The current Transformation Prompt targets the former Structured Design Model and normatively inherits Prompt v0.1.4 / v0.1.5. Its consistency with the current SDD Artifact Role, the semantic type “abnormal handling,” and standalone completeness cannot be established from the artifact itself. | `PENDING` — changing the Prompt is outside the permitted change scope; Design Authority must decide. |
| R | Change scope | `PASS` | The recorded change is limited to the Design Source and Structured Design Data. | `PENDING` — awaiting Human Review. |

These gates preserve the distinction between a recorded `PASS` and review completion. In particular, Gate Q remains `REVIEW`, and no `PENDING` Human Review is silently promoted to completion.
