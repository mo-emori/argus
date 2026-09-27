## 9 用語・詳細仕様への参照

重要用語を概念種別ごとに定義し、相違と利用関係を示す。 本節では、個々の条件を列挙するのではなく、相互の関係と運用上の境界が読み取れる順序で整理する。

### 設計の狙い

ARGUS固有語を未定義または同義として扱うと、Entity、状態、権限、処理の境界を誤解し得る。 表の存在や代表節の確認だけでは、無名文章、意味型混在、Source欠落を見逃し得る。 成果物の正本関係、構造化範囲、未確定事項、生成対象外が不明だと、後続工程がAuthorityを誤る。 重要用語を概念種別ごとに定義し、相違と利用関係を示す。 Structured Design Data全体をGate A〜Nで検証し、構造化完了の根拠を記録する。 Structured Design Data自身の変換状態と境界を明示する。

### 判断を支える関係

| 観点 | 設計上の内容 |
|---|---|
| problems | ARGUS固有語を未定義または同義として扱うと、Entity、状態、権限、処理の境界を誤解し得る。 ／ 表の存在や代表節の確認だけでは、無名文章、意味型混在、Source欠落を見逃し得る。 ／ 成果物の正本関係、構造化範囲、未確定事項、生成対象外が不明だと、後続工程がAuthorityを誤る。 |
| purposes | 重要用語を概念種別ごとに定義し、相違と利用関係を示す。 ／ Structured Design Data全体をGate A〜Nで検証し、構造化完了の根拠を記録する。 ／ Structured Design Data自身の変換状態と境界を明示する。 |
| processes | 主体、状態、`Data`、Workflow、Policy、Commit、分析・検証概念。 ／ Source複製、単独完全性、用語、共通Header、Process、State、表、意味型、関係、具体性、Authority、全節走査、Source照合。 ／ Source複製、用語、型、locator、Authority、未確定事項、Human System Design。 ／ ／ Design Source本文複製 ／ なし ／ Source全文、付録、詳細層、連続章節コピーを含めていない ／ ／ ／ 用語・概念体系 ／ 作成済み ／ §2で主体、状態、Fact、Command、Workflow、Policy、Commit等を関係付き整理 ／ ／ ／ 型別構造 ／ 作成済み ／ 処理、状態、規則、制約、データ、主体、Service、Gate、Failure、Boundary、Verification、Changeを分離 ／ ／ ／ Source locator ／ 保持 ／ 各主要表・処理・規則に設計元位置を付与 ／ ／ ／ Authority / 責務 / 境界 ／ 変化なし ／ §4、§16、§24で明示 ／ ／ ／ 未確定事項 ／ 未確定のまま保持 ／ §15でTBD、UNCONFIGURED、候補、将来検討を分離 ／ ／ ／ Human System Design ／ 未生成 ／ 本書は構造化設計データで停止 ／ |
| actors_authorities | Human ／ ARGUS |
| boundaries | ／ Authority / 責務 / 境界 ／ 変化なし ／ §4、§16、§24で明示 ／ |
| relations | Source複製、単独完全性、用語、共通Header、Process、State、表、意味型、関係、具体性、Authority、全節走査、Source照合。 ／ ／ 用語・概念体系 ／ 作成済み ／ §2で主体、状態、Fact、Command、Workflow、Policy、Commit等を関係付き整理 ／ |

### 適用時の注意

主体、状態、`Data`、Workflow、Policy、Commit、分析・検証概念。 Source複製、単独完全性、用語、共通Header、Process、State、表、意味型、関係、具体性、Authority、全節走査、Source照合。 Source複製、用語、型、locator、Authority、未確定事項、Human System Design。 ／ Design Source本文複製 ／ なし ／ Source全文、付録、詳細層、連続章節コピーを含めていない ／ ／ 用語・概念体系 ／ 作成済み ／ §2で主体、状態、Fact、Command、Workflow、Policy、Commit等を関係付き整理 ／ ／ 型別構造 ／ 作成済み ／ 処理、状態、規則、制約、データ、主体、Service、Gate、Failure、Boundary、Verification、Changeを分離 ／ ／ Source locator ／ 保持 ／ 各主要表・処理・規則に設計元位置を付与 ／ ／ Authority / 責務 / 境界 ／ 変化なし ／ §4、§16、§24で明示 ／ ／ 未確定事項 ／ 未確定のまま保持 ／ §15でTBD、UNCONFIGURED、候補、将来検討を分離 ／ ／ Human System Design ／ 未生成 ／ 本書は構造化設計データで停止 ／ Human ARGUS ／ Authority / 責務 / 境界 ／ 変化なし ／ §4、§16、§24で明示 ／ Source複製、単独完全性、用語、共通Header、Process、State、表、意味型、関係、具体性、Authority、全節走査、Source照合。 ／ 用語・概念体系 ／ 作成済み ／ §2で主体、状態、Fact、Command、Workflow、Policy、Commit等を関係付き整理 ／
