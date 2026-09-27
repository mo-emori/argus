## 3.5.2 Application Log

Application Log は、実行環境（Runtime）、処理単位（Job）、外部接続アダプター（Adapter）、エラー（Error）、および同様の活動について、運用および障害分析のために残す記録である。これは、Canonical State、Fact、Event、および Audit Record とは別の成果物である。この成果物の境界に関する設計上の参照先は、§2.6、§4、および §28 である。保存先は `logs/application/YYYY-MM-DD/` 配下である。これを生成するコンポーネントおよび Writer の実装は、まだ決定されていない。

Application Log は、Canonical State、Fact、Event、または Audit Record の代替としてはならない。Application Log を削除しても、投資判断、状態、履歴を含む正本となる設計情報が失われてはならない。したがって、その保存優先度は Canonical State、Commit、および Audit よりも低く、保持期間には有限の上限を設ける。具体的な保持期間は未解決である。

### ローテーションと日付単位の管理

Application Log は、`Asia/Tokyo` の日付境界で日次ローテーションする。このローテーションにより、ログを日付単位で管理できるようにしなければならない。

### 記録してはならない情報

Application Log には、以下のいずれも記録してはならない。

- Secret
- Credential
- Token
- API key
- Authorization header
- マスキングや秘匿化が施されていない（unredacted）デバッグダンプ

これら既知の禁止項目以外に、禁止またはマスキングしなければならない情報の範囲は未解決である。

### 書き込み失敗の分離とストレージの安全性

Application Log への書き込みだけに影響する障害によって、Canonical Commit または正本となる投資処理が失敗してはならない。このように分離された書き込み障害は、可能な範囲で観測可能にしなければならない。

この分離は、正本の安全性に優先するものではない。同じストレージ障害が正本の安全性を損なう場合は、Storage Fail Closed を適用する。

### 環境分離

Application Log は、TEST / PAPER / LIVE 間の Runtime Identity による分離に従わなければならない。また、Development と Runtime の物理的分離にも従わなければならない。これらの分離された環境またはドメインに属するログを、互いに混在させてはならない。

TEST / PAPER / LIVE を分離し、かつ Development / Runtime を分離する具体的なパーティション方式またはパス方式は未解決である。

### 未解決の実装上の選択肢

以下の事項は未解決であり、確定した実装要件として扱ってはならない。

- 生成するコンポーネント、Writer の責務、および書き込み経路
- 具体的な保持期間、およびクリーンアップまたは削除に使用する方法
- クラッシュ直前におけるログの耐久性保証の範囲
- Runtime、Job、Adapter、および Error のそれぞれに必要な最小限の識別情報
- 環境およびドメインを分離するための具体的なパーティション方式またはパス方式
- 既知の禁止項目に加えて、禁止またはマスキングしなければならない情報
- ファイル名、ファイル形式、スキーマ、およびロギングライブラリ
