# Faran roadmap

## First local slice

Journey: seed synthetic university roles → create a mock hardening course task → run its offline exercise → independently evaluate deterministic output → save a JSON report.

Acceptance: Python standard library only; deterministic idempotent 2,000-role seed; 12 sample active roles; repeatable task ID and result; independent evaluator flags invalid output; no real student/HR/finance data; schedule disabled; Paperclip disconnected; marketing copy remains draft.

Visual direction: temporary, accessible Persian-first RTL command-line output and JSON reports. No final dashboard design is claimed until the owner supplies the Chrome bookmark references.

## Dependencies and later work

1. Local mock core (this slice): CLI, seed, task execution, evaluation, JSON report.
2. Reliability: durable leases, retry, crash recovery, budget and concurrency limits.
3. Paperclip adapter: pin a release and exercise real create/read/execute integration.
4. Dashboard: accessible RTL states for organization, tasks, runs, costs, evaluations, and schedules.
5. Load and recovery evaluation: measure 2,000 mock identities and staged concurrency.
6. Deployment package: only after destination, budget, secrets, and operations are specified.
