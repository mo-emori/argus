## 4.2 Provider

marker identityを検証し、容量圧迫時に重要度順で安全に縮退する。 本節では、個々の条件を列挙するのではなく、相互の関係と運用上の境界が読み取れる順序で整理する。

### 守るべき原則

大容量Data Root初期値は`L:\emori\InvestmentAgentData`。 drive letterだけのBindingや偶発的な容量枯渇は、別Diskへの誤書込みや重要Dataの先行喪失を招き得る。 契約、承認、期限、認証、鮮度、Healthを追跡できないと、失効Serviceやstale Dataを利用し得る。

### 停止と例外

| 観点 | 設計上の内容 |
|---|---|
| premises | 大容量Data Root初期値は`L:\emori\InvestmentAgentData`。 |
| problems | drive letterだけのBindingや偶発的な容量枯渇は、別Diskへの誤書込みや重要Dataの先行喪失を招き得る。 ／ 契約、承認、期限、認証、鮮度、Healthを追跡できないと、失効Serviceやstale Dataを利用し得る。 |
| purposes | marker identityを検証し、容量圧迫時に重要度順で安全に縮退する。 ／ 外部ServiceのLifecycleと運用状態を判定できるRegistry属性を定義する。 |
| processes | `Data` Root、marker、Environment Binding、Storage Pressure Degradation、Position Watch Minimum `Data`。 ／ ／ 1 ／ News / optional raw、Historical expansion、Discovery bulk、non-critical report ／ 最初に停止 ／ ／ ／ 2 ／ Application Log、Candidate raw、non-critical archive / derived regeneration ／ Canonical情報より先に縮退。Application Logは保持量を有限にする ／ ／ ／ 3 ／ Canonical State、Human Decision / Correction / Execution Fact、Audit / Incident、Queue / reservation、recent local backup ／ 最後まで保護 ／ ／ ／ 4 ／ Position Watch Minimum `Data` ／ 重大Risk監視のため最後まで取得・Normalizeを優先 ／ ／ ／ 5 ／ Minimum Dataも保存不能 ／ `POSITION_WATCH_DATA_UNAVAILABLE`をInvestment P0 Incident化し、監視継続を装わない ／ ／ 単独の書込み失敗はCanonical Commitまたは投資Canonical処理を失敗させず、可能な範囲で観測可能にする。同一Storage障害がCanonical安全性を損なう場合はStorage Fail Closedを適用する。外付けData Rootに加え、内蔵SSD上のCanonical State、直近Backup、Application Logについてvolume free、directory usage、growthを監視する。警告閾値とApplication Logの具体的保持期間・cleanup方法は未確定である。 ／ §4.1、§4.7。 ／ Service identity、plan、approval、時刻、接続、鮮度、health。 ／ ／ service_id / provider ／ Service identity ／ Adapter / Gateway選択 ／ §4.0、§37A ／ ／ ／ plan_tier / paid / enabled ／ 契約・有効状態 ／ Paid GovernanceとConfiguration Validation ／ §4.0、§37A ／ ／ ／ human_approval_ref ／ 費用Authority根拠 ／ paid有効化時必須 ／ §37A ／ ／ ／ activated_at / renewal_or_expiry_at ／ Lifecycle時刻 ／ 期限接近・失効Warning ／ §4.0、§37A ／ ／ ／ last_successful_call_at / last_auth_success_at ／ 接続・認証観測 ／ 継続失敗と過期を区別 ／ §4.0、§37A ／ ／ ／ expected / observed_data_freshness ／ 鮮度契約と実測 ／ HTTP成功でもstaleならHealthyにしない ／ §4.0、§37A ／ ／ ／ health ／ Connectivity / Authentication / Contract / Freshness / Coverageの総合状態 ／ Warning / Incidentへ接続 ／ §4.0、§37A ／ |
| rules |  |
| abnormal_handling | 不一致は`DATA_STORAGE_IDENTITY_MISMATCH`または`ENVIRONMENT_BINDING_MISMATCH`としてwriteを停止する。 |
| actors_authorities | Human |

### 運用上の確認

marker identityを検証し、容量圧迫時に重要度順で安全に縮退する。 外部ServiceのLifecycleと運用状態を判定できるRegistry属性を定義する。 `Data` Root、marker、Environment Binding、Storage Pressure Degradation、Position Watch Minimum `Data`。 ／ 1 ／ News / optional raw、Historical expansion、Discovery bulk、non-critical report ／ 最初に停止 ／ ／ 2 ／ Application Log、Candidate raw、non-critical archive / derived regeneration ／ Canonical情報より先に縮退。Application Logは保持量を有限にする ／ ／ 3 ／ Canonical State、Human Decision / Correction / Execution Fact、Audit / Incident、Queue / reservation、recent local backup ／ 最後まで保護 ／ ／ 4 ／ Position Watch Minimum `Data` ／ 重大Risk監視のため最後まで取得・Normalizeを優先 ／ ／ 5 ／ Minimum Dataも保存不能 ／ `POSITION_WATCH_DATA_UNAVAILABLE`をInvestment P0 Incident化し、監視継続を装わない ／ 単独の書込み失敗はCanonical Commitまたは投資Canonical処理を失敗させず、可能な範囲で観測可能にする。同一Storage障害がCanonical安全性を損なう場合はStorage Fail Closedを適用する。外付けData Rootに加え、内蔵SSD上のCanonical State、直近Backup、Application Logについてvolume free、directory usage、growthを監視する。警告閾値とApplication Logの具体的保持期間・cleanup方法は未確定である。 §4.1、§4.7。 Service identity、plan、approval、時刻、接続、鮮度、health。 ／ service_id / provider ／ Service identity ／ Adapter / Gateway選択 ／ §4.0、§37A ／ ／ plan_tier / paid / enabled ／ 契約・有効状態 ／ Paid GovernanceとConfiguration Validation ／ §4.0、§37A ／ ／ human_approval_ref ／ 費用Authority根拠 ／ paid有効化時必須 ／ §37A ／ ／ activated_at / renewal_or_expiry_at ／ Lifecycle時刻 ／ 期限接近・失効Warning ／ §4.0、§37A ／ ／ last_successful_call_at / last_auth_success_at ／ 接続・認証観測 ／ 継続失敗と過期を区別 ／ §4.0、§37A ／ ／ expected / observed_data_freshness ／ 鮮度契約と実測 ／ HTTP成功でもstaleならHealthyにしない ／ §4.0、§37A ／ ／ health ／ Connectivity / Authentication / Contract / Freshness / Coverageの総合状態 ／ Warning / Incidentへ接続 ／ §4.0、§37A ／  不一致は`DATA_STORAGE_IDENTITY_MISMATCH`または`ENVIRONMENT_BINDING_MISMATCH`としてwriteを停止する。 Human
