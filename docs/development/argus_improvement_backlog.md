# Argus Improvement Backlog

## 1. 目的と権限

本Backlogは、有用だが現在承認されているdevelopment loopを安全に進めるための必須条件ではない改善事項を保持する、軽量な外部記憶である。ここに記録されたBacklog entryについてはrepository上のCanonical Sourceであり、Notionやconversationは索引として利用できるが代替にはならない。

Entryはimplementation authorization、Contract decision、Finding resolution、または完了証跡ではない。

## 2. Entry model

各entryは次の項目を記録する。

- `ID`
- `Type`
- `Summary`
- `Reason / Memo`
- `Timing`
- `Status`
- `Source / Ref`

許可する`Type`値:

- `REQUIREMENT`
- `DESIGN`
- `TEST`
- `OPERATIONS`
- `AUTOMATION`
- `TRACEABILITY`

許可する`Timing`値:

- `NEXT_VERSION`
- `BEFORE_PAPER`
- `BEFORE_LIVE`
- `WEB_MIGRATION`
- `AFTER_STABILIZATION`
- `SOMEDAY`

許可する`Status`値:

- `OPEN`
- `RESOLVED`
- `SUPERSEDED`

## 3. Immediate issueとBacklogの区別

次を判断基準とする。**この項目を解消しなくても、次のdevelopment loopを正常かつauthority-safeに進められるか。**

- `YES`: 本Backlogへ記録または保持する。
- `NO`: immediate blockerまたは必要なdecisionである。本Backlogへ隠さず、該当するContract、Test Strategy、Design Authority、またはHuman approval processへescalateする。

## 4. Backlog

| ID | Type | Summary | Reason / Memo | Timing | Status | Source / Ref |
|---|---|---|---|---|---|---|
| `ARGUS-IMP-0001` | `AUTOMATION` | Execution Status Monitoring | `REQ-AI-017`。Process安定後、manual status checkからpolling、さらにevent/webhook-driven monitoringへ段階的に発展させる。 | `AFTER_STABILIZATION` | `OPEN` | `REQ-AI-017`; `ARGUS-P-0007-v1` |
| `ARGUS-IMP-0002` | `TRACEABILITY` | Environment Binding Test Traceability | `FINDING-03`で指摘されたtrace linkを改善する。現在のdispositionは`RISK_ACCEPT`のままであり、本entryはFindingを解消・変更しない。 | `NEXT_VERSION` | `OPEN` | `EB-L1-DATA-ROOT-MARKER-STORE/FINDING-03`; canonical review record `sha256:a3e7f6789ed0bd5001483caeaf5f59d8230168e4bc1a430c820b6491979d5074` |
| `ARGUS-IMP-0003` | `TEST` | Expected Static RED robustness | Production symbol未実装時にもstrictなTest typingを維持できるContract stubまたはinterface mechanismを検討する。候補であり、承認済みDesignではない。 | `NEXT_VERSION` | `OPEN` | Test Strategy Expected Static RED experience; `ARGUS-P-0007-v1` |
| `ARGUS-IMP-0004` | `AUTOMATION` | Human-on-the-loop development orchestration | Human final authorityを維持したorchestration支援をWeb移行時に検討する。本entryにより実装または承認されたものではない。 | `WEB_MIGRATION` | `OPEN` | Canonical AI Development Operating Rules; `ARGUS-P-0007-v1` |
| `ARGUS-IMP-0005` | `AUTOMATION` | Machine-readable Capability Registry | 安定後にmachine-readableなprojectionを検討する。現時点のCanonical SourceはMarkdown Capability Registryである。 | `AFTER_STABILIZATION` | `OPEN` | `docs/development/argus_capability_registry.md`; `ARGUS-P-0007-v1` |
| `ARGUS-IMP-0006` | `OPERATIONS` | Critical Path Review canonicalization enforcement | P-0006によるCanonical化を必要としたP-0005のblocked state再発を抑えるため、明示的なenforcement/check stepを追加する。 | `NEXT_VERSION` | `OPEN` | `ARGUS-P-0005-v1`; `ARGUS-P-0006-v1`; `ARGUS-P-0007-v1` |
| `ARGUS-IMP-0007` | `OPERATIONS` | 日本語開発文書の可読性・文章品質レビュー | AI生成または翻訳された日本語文書について、意味保存に加えてHuman-readable qualityを後段で監修する軽量工程を検討する。本項目は現在のCapabilityをblockしない。 | `AFTER_STABILIZATION` | `OPEN` | User improvement request; `ARGUS-P-0009-v1` |
| `ARGUS-IMP-0008` | `TEST` | Superseded Frozen Test Pyright debt | `tests/component/test_data_root_marker_store_contract.py`（SHA-256 `1b9d148906a374027559b172989fbfceaf70adb5a0c0b23b0d607e43dd1a394b`）の既知Pyright 7 diagnostics。Current Capabilityとは非因果であり、P-0016、P-0017、P-0018で件数・severity・rule・scopeの非悪化を独立確認済み。immutable artifactを上書きせず、明示的なTest Baseline Correctionまたはcleanupで解消する。config exclusion / suppressionで隠さない。 | `NEXT_VERSION` | `OPEN` | `ARGUS-P-0015-v1`; `ARGUS-P-0016-v1`; `ARGUS-P-0017-v1`; `ARGUS-P-0018-v1`; P-0015 verification attempt `sha256:38d85be3678014618eb6600631a034cdfc0aee46bbd116ae458e3d3ff194b51d` |
| `ARGUS-IMP-0009` | `DESIGN` | Windows reserved device name / trailing-space lexical semantics | Contract §8.1の`RESERVED_DEVICE_NAME`判定と、末尾space付きbasename等のWindows lexical semanticsを将来のContract revision / Windows path-hardeningで再評価する。現Productionは現Contractに忠実でありFindingではなく、Capability CLOSE blockerでもない。Gate A lexical contractへ実Windows/NTFS physical behaviorを無条件に混入させない。physical containment、symlink/junction/reparse、8.3、device replacement、full TOCTOUとは別論点として扱う。 | `AFTER_STABILIZATION` | `OPEN` | `ARGUS-P-0018-v1`; Claude Review observation in `claude-review-record.json` (`sha256:06e6bfc4c4dc63d0c42e5195a41eff17a51d2e11f45a6c0c52dab82889e8fcbc`) |
| `ARGUS-IMP-0010` | `TRACEABILITY` | Critical Review provenance timestamp completeness | Critical Review artifact生成時に`reviewed_at`、message ID、record ID等をexternal observer provenanceから機械的に確定する仕組みを検討する。reviewerが自己取得不能な値を推測せず、Prompt Registryとcanonical Review artifact間のprovenance completenessを改善する。Review結果の有効性とは分離し、current CLOSE blockerにはしない。既存`ARGUS-IMP-0006`のcanonicalization enforcementを置換せず、timestamp/message provenanceの補完論点として追跡する。 | `NEXT_VERSION` | `OPEN` | `ARGUS-IMP-0006`; `ARGUS-P-0018-v1`; Review artifact `sha256:06e6bfc4c4dc63d0c42e5195a41eff17a51d2e11f45a6c0c52dab82889e8fcbc` |

## 5. 保守規律

- 上記Backlog判断基準を満たす場合にのみentryを追加する。
- 追跡可能なimplementation、decision、またはEvidence referenceなしに`RESOLVED`を使用しない。
- 本書を通じてReview Finding dispositionを変更しない。
- 明示的に参照した別entryまたはCanonical decisionが項目を置き換える場合は`SUPERSEDED`を使用する。
- 編集時も履歴上の意味を維持し、元の理由を黙って書き換えずclarification referenceを追記する。
