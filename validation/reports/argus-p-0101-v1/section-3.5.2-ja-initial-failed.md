## 3.5.2 Application Log

Application Log は、Runtime、Job、Adapter、Error、および同様の活動に関する運用分析および障害分析のための記録である。これは、Canonical State、Fact、Event、および Audit Record とは別の成果物である。この成果物の境界に関する設計上の参照先は、ﾂｧ2.6、ﾂｧ4、およびﾂｧ28 である。これは `logs/application/YYYY-MM-DD/` 配下に保存される。これを生成するコンポーネントおよび Writer の実装は、まだ決定されていない。

Application Log は、Canonical State、Fact、Event、または Audit Record を置き換えてはならない。Application Log を削除しても、投資判断、状態、または履歴を含む正準な設計情報が失われてはならない。したがって、その保存優先度は Canonical State、Commit、および Audit よりも低く、有限の保持期限を持つ。具体的な保持期間は未解決のままである。

### ローテーションおよび日付単位の管理

Application Log は、`Asia/Tokyo` の日付境界で毎日ローテーションする。このローテーションにより、ログを日付単位で管理可能にしなければならない。

### 記録してはならない情報

Application Log は、以下のいずれも記録してはならない。

- Secret
- Credential
- Token
- API key
- Authorization header
- マスキングされていないデバッグダンプ

これらの既知の禁止項目以外に、禁止またはマスキングしなければならない情報の範囲は未解決のままである。

### 書き込み失敗の分離およびストレージの安全性

Application Log の書き込みのみに影響する障害によって、Canonical Commit または正準な投資処理が失敗してはならない。このような分離された書き込み失敗は、可能な範囲で観測可能にしなければならない。

この分離は、正準な安全性に優先しない。同じストレージ障害が正準な安全性を損なう場合は、Storage Fail Closed が適用される。

### 環境の分離

Application Log は、TEST / PAPER / LIVE 間の Runtime Identity の分離に従わなければならない。また、Development と Runtime の物理的分離にも従わなければならない。これらの分離された環境またはドメインに属するログを、互いに混在させてはならない。

TEST / PAPER / LIVE を分離し、Development / Runtime を分離する具体的なパーティション方式またはパス方式は、未解決のままである。

### 未解決の実装上の選択肢

以下の事項は未解決のままであり、固定された実装要件として扱ってはならない。

- 生成するコンポーネント、Writer の責務、および書き込みパス
- 具体的な保持期間、およびクリーンアップまたは削除を実行するために使用する方法
- クラッシュ直前におけるログの耐久性保証の範囲
- Runtime、Job、Adapter、および Error のそれぞれについての最小限の識別情報
- 環境およびドメインの分離のための具体的なパーティション方式またはパス方式
- 既知の禁止項目に加えて、禁止またはマスキングしなければならない情報
- ファイル名、ファイル形式、スキーマ、およびロギングライブラリ
