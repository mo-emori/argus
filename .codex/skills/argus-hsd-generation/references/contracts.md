# Contracts

## Exact value

各定義は `id`, `canonical`, `accepted`, `label`, `source_locator` を持つ。`canonical` は `accepted` に必ず含める。日本語 Gate と Exact Value Gate は同じ catalog object を受け取る。

## Planning approval

承認記録は `status=APPROVED`, `approved_by`, `approved_at`, `planning_digest` を持つ。digest は canonical JSON の SHA-256 とし、計画変更後の承認流用を防ぐ。

## Semantic review

結果語は `FINDINGS` と `NO_FINDINGS` の closed set である。機械 Gate の成功を Semantic Review が代替せず、Semantic Review も Human Approval を代替しない。

## Coverage

状態は `UNMAPPED`, `PRESERVED`, `REFERENCED`, `REVIEW`。登録と更新は CoverageLedger だけが行う。Writer / reviewer へは読み取り専用 tuple を渡す。

## Translation

Translation Contractはsource/target language、source draft digest、Formal Identifier・literal・state・path・numeric value、terminology rules、structure lock、LLM Translator provenanceを持つ。Translator inputはsource draftとこの契約だけのclosed envelopeとする。

terminology rulesは、machine-facing literal、Human-facing technical concept、general prose vocabularyを区別する。literalは原表記を保持する。technical conceptは必要に応じて初出時に「日本語説明（Original Term）」の対応を示し、不確かな場合は一般語へ意訳せず原語を保持する。説明によって新しい設計条件・責務・因果・規範を追加してはならない。具体的な対訳はPythonへ固定しない。意味妥当性を機械判定できないsemantic risk termは独立Semantic Reviewへ送る。

Translation text artifactの永続化は、protected valueの文字列完全一致、strict UTF-8 encode/decode round-trip、生成digest、JSON内contentとMarkdown contentの一致をcommit前に検証する。検証後はUTF-8 bytesを一時ファイルへ書き、strict UTF-8で再読込してから置換する。失敗した出力を文字置換で修復せず、永続化前にfail closedとする。

Translation Preservationの判定語は`PRESERVED`, `REVIEW`, `MISSING`, `DISTORTED`, `INVENTED`である。`MISSING / DISTORTED / INVENTED`はFAIL、`REVIEW`も理由必須で自動PASSしない。WriterとTranslatorのsession一致、source draft digest不一致、生成artifact digest不一致はfail closedとする。

## Translation semantic review

独立Reviewの最終判定は`PASS / REVIEW / FAIL`とする。Review provenanceはsection、English/Japanese draft digest、Translation Contract digest/version、reviewer session、producer、timestamp、result、findings、versionを持つ。Reviewer sessionはWriter/Translatorの双方と異なる必要がある。Review必須なのに結果なし、binding不一致、producer不一致、未確定結果、`REVIEW`残存時のPASSはfail closedとする。
