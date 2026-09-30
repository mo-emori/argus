# argus Architecture Decision Records v0.1

**Document Role:** `ADR`

**Status:** ACTIVE  
**Created:** 2026-09-06  
**Scope:** AI Investment Agentにおける外部Data / LLM Service、Provider境界、費用Commitmentの主要Architecture Decisionを記録する。  
**Rule:** ADRは「なぜその選択をしたか」を保存する。契約・登録・API Key設定等の手順はSetup文書へ分離する。既存ADRを後から書き換えて意思決定履歴を消さず、変更時はSupersedeする。

---

# ADR-001 Market Data Provider Selection

**Status:** ACCEPTED FOR DEVELOPMENT / OPERATIONAL GATE PENDING  
**Decision:** J-Quantsを日本株Structured Market / Financial Dataの第一Providerとする。開発初期はFreeを使用可能とし、Paper Trading開始前にLight以上をHuman approval付きで導入する。

## Context

Investment Agentは日本株Universeを広く探索し、日足、財務、銘柄情報等を定期取得する必要がある。特定銘柄だけを監視するAPIより、全市場規模のbulk取得と安定したProvider契約が重要である。

## Evaluation Criteria

| Criterion | Importance |
|---|---:|
| 日本株Coverage | Critical |
| 全Universeを現実的なRequest数で取得可能 | Critical |
| 利用規約上の自動取得可否 | Critical |
| Data品質 / Provider信頼性 | Critical |
| Historical range | High |
| Rate limit | High |
| Pythonからの利用容易性 | High |
| 月額 / 従量Cost | High |
| Provider変更時の移植性 | High |
| Intraday data | Low for initial version |

## Alternatives Considered

| Option | Evaluation | Decision |
|---|---|---|
| J-Quants | JPX系の日本株向けStructured Data。bulk取得を前提に設計可能 | **SELECTED** |
| Yahoo! Finance Japan scraping | 自動取得の規約・運用リスクが大きい | REJECTED |
| yfinance | 開発試験には便利だが非公式依存、欠損/制限/運用安定性を正本Providerとして受容しにくい | REJECTED FOR PRODUCTION |
| 証券会社API | 特定銘柄監視・発注には強いが、全Universe Screening用途とは目的が異なる | REJECTED AS PRIMARY MARKET DATA |
| 海外Market Data API | 日本株Coverage / Cost / Currency面で優位性が薄い | REJECTED FOR INITIAL VERSION |
| TDnet paid API | Market price Providerではなく、かつ費用要件不一致 | EXCLUDED |

## Decision Details

1. Development / Adapter TestではJ-Quants Freeを許容する。
2. Freeの遅延DataはPaper / Live相当運用には使わない。
3. Paper Trading開始前にLight以上を導入する。
4. Plan契約・UpgradeはPaid Service Governanceに従いHuman explicit approvalを必須とする。
5. 銘柄ごとの大量Requestではなく、可能なbulk endpointを利用し、Raw保存後にLocal Universe Filterを行う。
6. Plan / rate limit / update timing / Dataset coverageはCapability Verificationで実測・記録する。
7. Lightで不足するDatasetが見つかっても、自動でStandard / PremiumへUpgradeしない。Cost / Benefitを再評価してHuman Decisionとする。

## Consequences

- Provider固有処理は`JQuantsProvider`内に閉じ込める。
- Selection / AnalysisはNormalized schemaのみ参照する。
- Paper Trading Gateに「Operational Provider Plan configured」を追加する。
- J-Quants障害時に未承認有料Providerへ自動Fallbackしない。

## Revisit Conditions

- 必須DatasetがLightで取得不能
- Provider update latencyがStrategy Required Latencyを満たさない
- Data品質 / 欠損率がAcceptance Criteriaを満たさない
- API仕様 / Plan / Priceの大幅変更
- 対象市場を日本株以外へ拡張

---

# ADR-002 Disclosure Data Provider Selection

**Status:** ACCEPTED FOR DEVELOPMENT / COVERAGE VERIFICATION REQUIRED  
**Decision:** 法定開示はEDINET APIを第一Providerとする。TDnet有料APIは明確に除外する。TDnet由来EventのうちJ-Quantsで代替可能な範囲をCapability Verificationで確定する。

## Context

Position Watch / Candidate Watchには決算、業績修正、法定開示、株主変化等のEventが必要である。一方、TDnet有料APIの固定費は本システムの個人運用Cost要件に適合しない。

## Alternatives

| Option | Role | Decision |
|---|---|---|
| EDINET API | 法定開示 / 原本取得 | **SELECTED** |
| J-Quants financial / TDnet-origin datasets | Structured Event / Summaryの代替候補 | **VERIFY / USE WHERE SUFFICIENT** |
| TDnet paid API | 適時開示API | **EXCLUDED** |
| 公開Web scraping | 規約・安定性・再利用条件を個別確認する必要 | NOT DEFAULT |

## Decision Details

- EDINET Adapterは取得原本をRaw保存し、必要項目をNormalized JSONへ変換する。
- TDnet有料APIを将来の通常候補として保持しない。
- TDnet由来情報が必要な場合、まずJ-Quants / EDINET等の既存承認Providerで代替可能か確認する。
- 代替不能なCritical EventがStrategy成立性を損なう場合はBreak対象とする。

## Revisit Conditions

- 必須EventのCoverage不足
- Provider latencyがStrategyを成立させない
- 合法・安価で安定した新Providerが登場
- System objective / investment horizonが変更

---

# ADR-003 External Service Abstraction

**Status:** ACCEPTED
**Decision:** 外部APIは`ExternalServiceGateway`とDomain Provider AdapterでWrappingし、Business Logicからの直接APIアクセスを禁止する。

## Context

Market Data、Disclosure、LLM、NewsはProvider変更、料金変更、Rate Limit、認証方式変更が起こりうる。上位AgentがProvider固有SDK / Response Schemaへ依存すると差替えコストが高くなる。

## Decision

```text
Application / Agent
        ↓
Domain Service Interface
        ↓
ExternalServiceGateway
        ├─ MarketDataProvider
        ├─ DisclosureProvider
        ├─ ModelProvider
        └─ NewsProvider
```

### Gateway Common Responsibilities

- enabled / configured validation
- Paid Service approval validation
- Secret reference
- Budget / cost governance
- rate limit
- retry / circuit breaker
- request_id / audit / provenance
- normalized error classification

### Provider Responsibilities

Market / Disclosure:
`Fetch → Validate → Raw Save → Normalize → JSON/JSONL Save → FetchResult`

Model:
`Request Build → Cost Estimate / Reserve → API Call → Usage Settle → Durable Stage → Normalized ModelResult`

## Consequences

- Provider差替え時にBusiness Logic変更を最小化できる。
- RawとNormalizedを分離できる。
- Cost / retry / auditの共通規則を強制できる。
- Wrapper自体が単一点になり得るため、Contract Testを必須とする。

---

# ADR-004 Paid External Service Governance

**Status:** ACCEPTED / HARD GOVERNANCE RULE  
**Decision:** システムはユーザーの明示承認なしに新しいCost Commitmentを発生させない。

## Applies To

- 新規有料API / SaaS
- Free → Paid Plan
- Paid Plan Upgrade
- 有料Add-on
- 従量課金上限増額
- Model API Budget増額
- 障害時の有料Fallback
- Auto recharge等の継続課金設定変更

## Required Before Activation

- Service / Provider
- Purpose
- Pricing model
- Initial / recurring / usage-based cost
- Expected monthly cost
- Configured upper bound
- Cancellation / downgrade procedure
- Free / cheaper alternatives
- Operational dependency
- Human approval reference

## Enforcement

- `paid=true`かつenabledなのに`human_approval_ref`が無ければConfiguration Validation Error。
- SystemはBudget不足やRate Limitを理由に自動Upgradeしない。
- Systemは未承認有料Providerへ自動Fallbackしない。
- 必要時は`PAID_SERVICE_REQUIRED`、Budget Review、Break Proposalを生成する。
- Human approvalは費用Commitmentの範囲を明示する。範囲外の増額には再承認が必要。

## Rationale

投資判断のHard Riskだけでなく、システム自身が外部固定費・従量費を勝手に増やすRiskもHuman-controlledにする。

---

# ADR-005 LLM Provider Boundary

**Status:** ACCEPTED  
**Decision:** OpenAI APIを初期Model Provider候補とするが、AgentはOpenAI固有APIへ直接依存せず`ModelProvider`を通す。

## Context

LLM APIは有料・従量課金であり、Model名、pricing、token accounting、tool interface、rate limit等が変更されうる。他Provider / Local Modelへの差替え余地も残す。

## Decision Details

`OpenAIProvider`は少なくとも以下を担当する。

- API authentication
- request / tool schema mapping
- timeout / retry / 429 classification
- token / usage capture
- cost estimate / budget reservation / settlement
- pricing manifest reference
- Durable Stage保存
- normalized `ModelResult`
- provider/model provenance

Analysis / Selection / Break Agentは`ModelProvider` interfaceを利用する。

## Consequences

- OpenAI→別LLM / Local Modelへの差替えをArchitecture上許容。
- Providerごとの能力差は完全には抽象化できないため、Capability Manifestを別途持つ。
- Provider変更は同一結果を保証しない。Historical Replay / Regression Testを再実行する。

## Revisit Conditions

- Model capability / price / latencyの大幅変化
- Required tool / context capability不足
- Privacy / data residency requirement変更
- Local Modelが必要品質を満たす

---

# ADR-006 Data Persistence Boundary

**Status:** ACCEPTED  
**Decision:** 外部取得DataはRaw immutableとProvider-independent Normalized Dataに分ける。大容量Data Rootは`L:\emori\InvestmentAgentData`とする。

## Layout

```text
L:\emori\InvestmentAgentData\
├─ raw\
├─ normalized\
├─ historical\
├─ archive\
├─ reports\
└─ backups\
```

Canonical Portfolio / Config / Status等の現在Stateは内蔵側Runtimeに保持する。

## Storage Identity

Drive letterだけを信用せず、Data Root直下の`data_root_marker.json`で`state_id` / `data_root_id`を照合する。不一致時は`DATA_STORAGE_IDENTITY_MISMATCH`として書込み停止。

## Capacity

約2TBは「使用可能な運用上限目安」であり必要容量見積りではない。Dataset確定後に再見積りする。監視対象は絶対使用量だけでなくfree space、directory別容量、日次/週次増加率を含む。

## Consequences

- Parser / Normalizer不具合時にRawから再生成可能。
- Provider変更後もNormalized schemaを維持できる。
- 外付けHDD切断時はData acquisitionを縮退させるが、Canonical Stateを失わない。

---

# ADR-007 Portable Runtime Config Read-Failure Classification

**Status:** ACCEPTED
**Decision:** Runtime Config v0.1はportableなabsence / non-absence read-failure分類だけを定義し、dangling symlink等のOS固有filesystem entry semanticsを規範化しない。

## Context

Frozen Test `RC-L1-003`がreal NTFS dangling file symlinkを作成したため、Windows symlink privilegeへの依存が生じた。provenance trace `ARGUS-RUNTIME-CONFIG-DANGLING-SYMLINK-PROVENANCE-20260930-001`により、このspecific requirementはRuntime Config Contract §7.2 step 3で初めて導入され、上位のDesign Source、System Design、SDD、既存ADR、Bootstrap、Environment Bindingに要求根拠がないことを確認した。現行のauthoritative threat modelにもdangling-symlink-specific behaviorを要求するsecurity requirementは確認されていない。

## Decision

- genuine config absenceは`UNCONFIGURED` + `CONFIG_NOT_FOUND`とする。
- genuine absence以外のload/read failureは`ERROR` + `CONFIG_READ_ERROR`とする。
- loadに成功したbytesはL0へ渡す。
- Runtime Config v0.1はdirectory、dangling symlink、junction、reparse pointその他のOS固有filesystem entry typeを規範的に列挙しない。
- platform/security-specific behaviorは、将来のthreat modeling、exploit prevention、TOCTOU、trust boundary、platform compatibilityまたは実運用要件に裏付けられた明示requirementとADRがある場合にだけ追加する。
- `data_root`についてsymlink/junction/reparse targetを追跡またはcanonicalizeしない独立規則は変更しない。

## Consequences

- Runtime Config Contract、Test Strategy、`RC-L1-003`をportable classificationへ修正する。
- 現行Runtime Config v0.1 Freezeとその下流のFormal RED / GREEN evidenceは履歴として保持するが、改訂baselineのauthoritative evidenceではない。
- 改訂baselineはPre-RED → Freeze → Formal RED → GREENを順に再実行しなければならない。

---

# ADR-008 Runtime Identity Corrective Boundary

**Status:** ACCEPTED
**Decision:** Runtime Identity v0.1 の F1-F4 corrective boundary を、既存 error taxonomy を拡張せず、validation pipeline が実際に最初に検出した defect で fail closed する境界として確定する。

## Context

Runtime Identity critical-path review で、`created_at` の parser normalization、pathological JSON decoder recursion、UTC range edge の serializer exception boundary、および duplicate key と malformed JSON が同一入力に存在する場合の意味が確認された。F1-F3 は既存 Contract の実装 defect であり、F4 は Human Design Authority が解消した design ambiguity である。

## Decision

1. **F1:** `created_at` の date/time/offset component は parser 使用前に lexical form と range を検証する。hour `24`、minute `60`、second `60`、offset hour `24`、offset minute `60` を含む invalid form は、parser normalization で修復せず、既存の `INVALID_CREATED_AT` として fail closed する。既存の受理形式・range は拡張しない。
2. **F2:** `parse_runtime_identity()` は recursion/pathological JSON decoder failure を、`field_name=None` の既存 typed result `MALFORMED_JSON` へ写像する。`RecursionError` を public API 外へ漏らさず、新しい public taxonomy は追加しない。
3. **F3:** `serialize_runtime_identity()` は、UTC instant が supported datetime range 内で表現可能な publicly constructible value を canonical UTC RFC3339 として出力する。UTC `datetime.min` と `datetime.max` を boundary case とする。publicly constructible value の UTC conversion が range 外へ出る場合は `ValueError` を送出し、bytes を返さず、`OverflowError` を漏らさない。invariant を迂回した object または任意の datetime internals には保証を拡張しない。
4. **F4:** Validation は fail closed とする。defined validation pipeline が実際に最初に検出した defect で validation を終了し、その defect の既存 typed reason を返す。nested duplicate も同じ規則に従う。`DUPLICATE_FIELD` と `MALFORMED_JSON` のどちらにも global semantic precedence を与えず、v0.1 は global error-priority taxonomy を定義しない。

## Consequences

- 旧 Runtime Identity baseline と下流 evidence は immutable history として保持するが、改訂 baseline の authoritative evidence には使用しない。
- 次工程は revised Pre-RED candidate validation、revised Freeze、Human commit checkpoint、Revision RED の順とする。
- 本 decision は追加の Production 変更、Capability Registry status 遷移、Runtime Entry Resolution の開始を許可しない。

---

# ADR Index / Status

| ADR | Decision | Status |
|---|---|---|
| ADR-001 | J-QuantsをPrimary Market Data Provider | Accepted for Development / Operational Gate Pending |
| ADR-002 | EDINET primary、TDnet paid API excluded | Accepted / Verification Required |
| ADR-003 | ExternalServiceGateway + Provider Adapter | Accepted |
| ADR-004 | Paid ServiceはHuman explicit approval必須 | Accepted / Hard Rule |
| ADR-005 | LLMもModelProviderでWrapping | Accepted |
| ADR-006 | Raw / Normalized分離、Data Root外付けHDD | Accepted |
| ADR-007 | Runtime Config read failureをportableなabsence / non-absence分類とする | Accepted |
| ADR-008 | Runtime Identity corrective boundary: first defect actually detected, without global error precedence | Accepted |
