# ARGUS-P-0095-v1 Major Chapter 3 Semantic Review

## 総合判定

**FINDINGS**

本査読はHuman Review前の独立Semantic Reviewであり、受入承認、修理、freezeは行っていない。

## 査読範囲と方法

- 指定された5ファイルだけを参照した。
- Writer Inputの208 Coverage Unit（3.1: 33、3.2: 27、3.3: 15、3.4: 73、3.5: 40、3.6: 20）を、標本ではなく全件について本文の文章、表、図へ照合した。
- Coverage Mapは全208件が機械判定`REVIEW`であるため、同Mapを受入根拠にはせず、設計意味、固定値、状態、Authority、禁止、例外、未確定性の保存を独立に確認した。

## Findings

### F-01 — 実装段階7〜16の段階番号と成立境界の対応が失われている

- **Severity:** MAJOR
- **位置:** `major-chapter-3.md` 3.1、実装・確認段階表の「7〜13」「14〜16」行（27〜28行付近）
- **根拠:** Writer InputのSDD-L1552〜SDD-L1561は、段階7から16までを個別の段階として固定し、各段階に成立させる機能と確認境界を一対一で割り当てている。本文は7段階分と3段階分をそれぞれ一行へ連結したため、たとえば段階8がBudget Gate、段階9がAlert Queue、段階10がDurable Stage、段階16がHuman承認によるJ-Quants Lightであるという対応を復元できない。項目自体は列挙されているが、順序と段階境界という設計意味が保存されていない。
- **推奨対応:** 段階7〜16を個別行へ戻すか、各機能群に段階番号を明記し、各段階と確認境界の一対一対応を保存する。

### F-02 — 継続実行におけるEvent処理の入力・出力・復旧経路が具体化されていない

- **Severity:** MAJOR
- **位置:** `major-chapter-3.md` 3.2全体、特にフロー図（38〜52行付近）と周期Job表（57〜62行付近）
- **根拠:** SDD-L1318とSDD-L1320は、定期処理だけでなくEvent処理についても入力、出力、失敗・復旧、次処理を明示し、Event取得、Watch、再分析、Queueを扱うことを要求している。本文は冒頭で「周期とイベント入力」に触れるだけで、表はDaily、Weekly、Monthly、Quarterlyの周期Jobに限定され、Event取得からWatch、再分析、Queueへ至る経路や復旧時の扱いを追えない。Coverage Unitの目的が実質的に未充足である。
- **推奨対応:** 周期Jobとは別にEvent処理の入力、処理、出力、失敗・復旧、次処理を示す。既存フローへ統合する場合もEvent固有の入口と後続を判別可能にする。

### F-03 — 3.4のData / Artifact一覧からUser StatusとWorkflowのAuthority条件が脱落している

- **Severity:** MAJOR
- **位置:** `major-chapter-3.md` 3.4、「状態とデータ」の表および119行付近の正本・派生物説明
- **根拠:** SDD-L0379はUser Statusについて、生成元を`StatusChangeCommand`、保存先を`user_status.json`、版を`status_version`とし、直接編集を通常操作にしないと固定している。SDD-L0383はWorkflowについて、Queue、Approval、Order、Reservation、Watchが生成・利用し、Proposal、Order、Incident等を独立状態として保持すると固定している。本文はUser Statusの値と`human_capacity`との関係、および`portfolio.json`がWorkflow正本であることまでは記すが、上記の更新Authority、識別子、直接編集禁止、独立状態保持を記していない。
- **推奨対応:** User StatusとWorkflowをData / Artifactの関係として明示し、`StatusChangeCommand`、`user_status.json`、`status_version`、直接編集禁止、およびProposal、Order、Incident等の独立状態保持を保存する。

### F-04 — Runtime Identityの除外境界とConfigurationの内容・版管理が弱まり、accepted artifactから回帰している

- **Severity:** MODERATE
- **位置:** `major-chapter-3.md` 3.4、119行付近。比較対象`section-3.4.md`の34行付近
- **根拠:** SDD-L0153、SDD-L0154、SDD-L0377、SDD-L0378では、Configurationが人の明示するJob、Policy、Budget、通知等の単一正本でversion/hashを持つこと、Runtime Identityがpath、Secret、Status、Domain Stateを含まずDeployment Identity、Run Identityとも分離されることが示される。現本文は`config.json`が単一正本であることと、Runtime Identityがpathや設定値を含まないことだけに圧縮している。accepted artifactはJob、Policy、Budget、通知規則、version/hash、Job開始後snapshot、およびIdentityからのSecret、人の状態、Domain Stateの除外を明記しており、現本文は意味の明確さが回帰している。3.6にConfig snapshotの説明はあるが、3.4のArtifact定義として欠落した条件をすべて補ってはいない。
- **推奨対応:** 3.4のArtifact定義へConfigurationの対象とversion/hash、Runtime Identityの全除外対象およびIdentity種別間の分離を戻す。3.6を参照させる場合も、3.4だけでAuthority境界が読める最小定義を残す。

### F-05 — 保存Artifactを圧縮した結果、個別不変条件が失われている

- **Severity:** MAJOR
- **位置:** `major-chapter-3.md` 3.5冒頭段落（133行付近）
- **根拠:** SDD-L1136〜SDD-L1147はArtifactごとに異なる不変条件を持つ。本文では多数のArtifactを一段落へ集約したため、少なくとも次が欠落している。（a）`performance.json`が計算条件と参照Commitを持つこと（SDD-L1137）、（b）`logs/decisions`等が`event_id / commit_id`で重複排除されApplication Logで代替されないこと（SDD-L1140）、（c）`reports/`がHuman-facing Artifactで正本ではないこと（SDD-L1142）。単に「派生物」とまとめるだけでは、再計算、監査、重複排除に必要な個別条件を保存できない。
- **推奨対応:** Artifact対応表を用いるなどして、各Artifactの生成元、利用先、保持条件、不変条件を個別に復元する。

### F-06 — 秘密情報を露出させない範囲がaccepted artifactより狭くなっている

- **Severity:** MODERATE
- **位置:** `major-chapter-3.md` 3.4末尾〜3.5（119、135、137行付近）。比較対象`section-3.4.md`の53行付近
- **根拠:** 現本文はApplication LogにSecret、Credential、Tokenを記録しないことと、BackupへSecretを平文で含めないことを明記する。一方、accepted artifactは秘密情報をCanonical State、Projection、Log、Report、Backupのいずれにも露出させない境界を明示していた。現本文ではCanonical State、Projection、Reportに対する非露出条件を確認できず、安全境界が狭く読める。Writer Input内でもConfiguration、Secret、State、Identityの分離（SDD-L0153）およびRuntime IdentityからのSecret除外（SDD-L0377）が要求されており、広い非混在境界を維持する必要がある。
- **推奨対応:** 秘密情報の非露出対象をCanonical State、Projection、Application / Audit Log、Report、Backupまで一貫して明示し、Backupだけはさらに「平文を含めない」という条件を区別する。

## 観点別評価

### 1. Reader journeyと6 child section collection

6子節はすべて存在し、起動、継続実行、中断・再開、状態とデータ、保存・復旧、Deploymentという時間順・依存順の導線は明確である。章冒頭と節末の接続も概ね自然で、Human Structure PlanおよびChapter Contractに適合する。ただしF-02により、継続実行の「周期」と「Event」のうち後者が導線上で薄い。

### 2. SDD dump / catalog化

全体は問題、理由、境界を先に述べており、単純なSDD dumpではない。3.2と3.3の図は処理上の非対称性と状態遷移を説明している。3.1の段階表と3.5のArtifact列挙はcatalog性が高いが、必要な対応関係を示すための表現自体は妥当である。問題はcatalogであることより、F-01とF-05のように圧縮で対応関係を失った点にある。

### 3. 設計意味・固定値・状態の保存

状態名、Data Root、2TB / 1.8TBの候補性、Clock、Runner状態、Research / Thesis / Holding遷移、Retry state、Deployment versionは概ね正確に保存されている。208 Coverage Unitの全件照合では、F-01〜F-05に示した意味脱落を確認したため、完全保存とは判定できない。Coverage Mapの全件`REVIEW`は独立査読によって解消されるべき機械状態であり、本文の完全性を保証していない。

### 4. Invented meaning

設計にない新規Authority、状態、固定閾値、有料Fallback、自動発注などの明白な発明は確認しなかった。3.6の「Schema確認後に再起動する」は入力表の次工程`Restart`を文章化した範囲であり、発明とは判定しない。

### 5. 章境界・重複・相互参照

投資判断、Human approval、Risk、通知の内部仕様へ踏み込まず、章境界は維持されている。章内参照は許可された3.2、3.3、3.5に限られ、外部節番号やCoverage IDも本文へ露出していない。3.2〜3.5間には必要な重複が少量あるが、実行フロー、状態、Authority、保存という異なる観点であり許容範囲である。

### 6. 表・図の導入と有用性

3.2のフロー図は外部副作用、Stage、Commit、Projection、Retryの順序を、3.3の状態図はcrashが`END`遷移ではないことを有効に示す。各表にも直前の導入があり、概ね自然である。一方、3.1の段階集約表はF-01、3.5の一段落列挙はF-05のとおり、視認性より意味対応を損なっている。

### 7. 自然な日本語

文体は一貫し、意味の異なる概念を短文と表で区切っており、概ね自然である。「Canonical情報」「Human操作入口」など英日混在は多いがformal identifier中心で、理解を妨げるほどではない。3.5冒頭は情報密度が高く、Artifactごとの差異を読み分けにくい。

### 8. P0090 section 3.4との回帰比較

現3.4はaccepted artifactより簡潔で、三つのDomain lifecycleを一表ずつに圧縮しつつ主要遷移を保っている点は良い。FactのTTL / Policy違反時の非拒否、Observation provenance、Correction禁止、Canonical更新境界なども保持されている。一方、F-04とF-06のとおり、Configuration / Runtime Identityの定義と秘密情報の非露出範囲が回帰している。またaccepted artifactにあった更新フロー図は現章では3.2のより詳細なフローへ移されており、この移動自体は重複回避として妥当である。

## 結論

章構成、読者導線、主要な状態機械、固定値、章境界、図表選択には大きな長所がある。しかし、段階番号、Event処理、User Status / Workflow Authority、Artifact固有の不変条件、およびaccepted artifactが保持していた安全境界に意味脱落があるため、総合判定は`FINDINGS`とする。本判定は受入承認ではない。
