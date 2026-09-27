## 3.1 Startup

Startup must keep identity, configuration, entry resolution, and orchestration as distinct responsibilities. Combining them into a single mechanism would obscure both the causes of Identity, Config, and Binding failures and the Authority responsible for each. The startup sequence therefore fixes the responsibility and invocation order of four subsystems and preserves typed failures at each boundary.

| Order | Subsystem | Responsibility | Boundary constraint | Related design section |
|---:|---|---|---|---|
| 1 | `RUNTIME-IDENTITY-DOCUMENT` | Provides the logical instance identity. | Must not contain variable Configuration or paths. | §4.0 |
| 2 | `RUNTIME-CONFIG-MECHANISM` | Loads and validates Configuration, then creates a snapshot. | Resolution of Secret values remains the responsibility of the Subsystem that uses them. | §4.0 |
| 3 | `RUNTIME-ENTRY-RESOLUTION` | Resolves the startup target and Binding inputs. | Must not infer the environment from a directory. | §4.0 |
| 4 | `RUNTIME-BOOTSTRAP-ORCHESTRATOR` | Orders the Subsystems and calls the Environment Binding API. | Must not turn a startup token into persistent write authorization. | §4.0, §4.2 |

Each Subsystem retains its own typed failures. At the upper boundary, those failures are mapped to the existing startup outcome or Incident. A single, large failure enum shared by all Subsystems must not be introduced.

### Dependency-led implementation sequence

Investment analysis must not precede the safety, cost, and State foundations: doing so would accumulate implementation whose conditions for viability cannot be verified. Implementation and verification therefore proceed incrementally from the Runtime foundation and follow the dependency order below, spanning the Design baseline, Runtime foundation, MVS, Historical, Paper, Live, and Multi-branch expansion. The sequence is rooted in §49.

| Step | Scope | Purpose or gate established |
|---:|---|---|
| 0 | Design / ADR baseline; separation of Test Strategy | Establish Authority and test criteria first. |
| 1 | OpenAI, J-Quants Free, and EDINET setup | Prepare external Capabilities. |
| 2 | Separation of Dev / Runtime / Test Data; Windows Manifest; Secret; Config Schema | Establish the Environment safety boundary. |
| 3 | Shared Service; Status Writer; CLI status / help | Establish the Human operation entry point. |
| 4 | Runner single instance; Lifecycle; clock; wait; Lease | Establish the Runtime foundation. |
| 5 | Writer lock; Atomic Commit; recovery; Config Snapshot; Correction | Establish State integrity. |
| 6 | Gateway; Paid Governance; Service Registry | Establish the external-dependency boundary. |
| 7 | Stub Provider; Test Dataset Generator | Provide safe test input. |
| 8 | Budget Gate; Usage; Review; Circuit Breaker | Establish cost and Retry control. |
| 9 | Alert Queue; Severity / Priority; Override; Popup; ACK | Establish the Human notification path. |
| 10 | Durable Stage; retry resume | Address repeat charging and recovery. |
| 11 | External Storage; marker; growth; dual backup | Establish Data protection. |
| 12 | J-Quants Free / EDINET Adapter CV | Verify the Provider structure. |
| 13 | CV fixture; frozen criteria | Establish Validation Integrity. |
| 14 | Risk Validator; Decision Queue | Establish the Trade safety Gate. |
| 15 | Single-ticker slice; Historical Test | Establish the end-to-end MVS. |
| 16 | J-Quants Light with Human approval; Capability Verification | Establish the Paper Provider Gate. |
| 17〜18 | Realtime Paper; Live Readiness | Make the decision only after operational measurement. |
| 19 | Multi-branch expansion | Expand only after the foundation has been established. |

Investment-analysis Agents must not be added ahead of this sequence. Human Approval, Cost, State integrity, and Retry economy must be closed first.
