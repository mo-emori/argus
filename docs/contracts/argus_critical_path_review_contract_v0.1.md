# argus — Critical Path Review Contract v0.1

**review_contract_id:** `ARGUS-CRITICAL-PATH-REVIEW`  
**review_contract_version:** `0.1`  
**Status:** ACCEPTED

------------------------------------------------------------------------

## 1. Purpose

Critical Path capabilityについて、Frozen TestのPASSだけでは検出できないContract violation、fail-open behavior、invariant weakness、overimplementation、dependency violation、hidden coercion / inference、Contract / Test coverage gap、Critical Path regression riskを独立Reviewerが確認する。

ReviewはAutomated Test、Static Analysis、CV、RVの代替ではない。Test PASSをContract complianceの代替にせず、Unit Test結果からCV / RV statusを過大評価しない。

## 2. Required review procedure

Reviewerは次をすべて行う。

1. Applicable Contractを読む。
2. Production implementationを読む。
3. Frozen Testを読む。
4. GREEN verification resultを確認する。
5. Test PASSをContract complianceの代替にしない。
6. Contract requirementとProductionを独立比較する。
7. Frozen Testで未検出のContract requirementを探す。
8. fail-closed / fail-open境界を確認する。
9. hidden coercion、inference、default、repairを確認する。
10. Critical Path上のdependency boundaryを確認する。
11. overimplementationを確認する。
12. CV / RV statusをUnit Test結果から過大評価しない。

## 3. Findings

Finding severityは次のclosed setとする。

``` text
CRITICAL
HIGH
MODERATE
MINOR
```

ReviewはFindingを提示するが、Dispositionを決定しない。Findingは後続のHuman / Codex disposition processへ渡し、Test Strategy §24.4に従ってDispositionする。

各Findingは最低限、識別子、severity、対象file / symbol、Contract requirement、observed implementation、failure mode、Frozen Testによる検出可否、推奨対応を含む。

## 4. Review Input Manifest

Review開始前に、Review対象artifactを列挙したReview Input Manifestを作成する。ManifestはTest Strategy §18.1のcanonical JSON artifactとし、最低限次を保持する。

``` text
capability_id
review_contract_id
review_contract_version
contract.path / sha256
frozen_test.path / sha256
production[].path / sha256
baseline.path / sha256
green_run.path / sha256
evidence_refs[].path / sha256 / kind
code_commit
working_tree_state
```

Manifest artifact自体のSHA-256を`review_input_manifest_hash`とする。複数hashの文字列連結等から暗黙生成してはならない。

Review後に作られたDisposition、Evidence、文書変更を過去Reviewの入力として追加しない。Temporal provenanceを維持する。

## 5. Review provenance

Review recordはTest Strategy §24.4のmetadataを保持する。Reviewer-reported provenanceとexternal-observer provenanceを区別し、external observer logが利用可能な場合は後者を時刻・message identityの正本として優先する。

`reviewed_at`はReview response本文を保持するexternal observer recordのtimestampとする。推測値、現在時刻、Reviewerが本文中でtyped textとして申告した時刻で代用しない。取得不能な場合はReview provenance incompleteとしてCritical Path CapabilityをCloseしない。

Claude Code session JSONLでは、`review_source_record_sha256`をReview response本文を保持するoriginal JSONL record 1件のraw bytesから計算する。

``` text
record scope  = JSONL record 1件
trailing LF   = excluded
reserialize   = prohibited
copied text   = prohibited
whole log hash = prohibited
```

`review_source_ref`は最低限、`source_type / log_path / session_id / record_id / message_id`を保持する。SHA-256表現は`sha256:<64 lowercase hex>`とする。

## 6. Retrospective contract assignment

本Contractの確定前に実施されたReviewへ`ARGUS-CRITICAL-PATH-REVIEW / 0.1`を遡及割当てできるのは、元Review promptと入力が§2〜§5の要求を実質的に満たしていたことをEvidenceで確認できる場合だけとする。

遡及割当てでは、少なくとも次を記録する。

``` text
retrospective_assignment = true
assigned_at
assignment_basis
original_review_record_ref
review_input_manifest_ref
```

要求を満たさないReviewへversionを遡及付与しない。その場合はCapability CloseをBLOCKする。
