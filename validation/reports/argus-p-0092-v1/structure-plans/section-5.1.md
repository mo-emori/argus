# 5.1 Human Structure Plan

{
  "section_purpose_for_reader": "Human操作を共有Command / Service Layerへ統一し、非RUNNING時にもStatus、Help、System Statusの安全な操作入口を保つ。",
  "explanation_order": [
    "要点をつかむ",
    "設計上の関係を読む",
    "運用上の境界を確認する"
  ],
  "proposed_subsections": [
    "処理の入口",
    "流れと分岐",
    "失敗時の境界"
  ],
  "candidate_counts": {
    "prose": 2,
    "table": 1,
    "diagram": 1,
    "subsections": 3
  },
  "representation": {
    "table_sources": [
      "problems",
      "purposes",
      "processes",
      "rules",
      "actors_authorities"
    ],
    "diagram_source": "processes"
  },
  "context_fields_intentionally_not_exposed": [
    "coverage_id",
    "source_locator",
    "assignment_status",
    "parser classification"
  ]
}
