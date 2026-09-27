# argus Structured Design Model Prompt v0.2

Design Source、ADR、Contract、Test Strategy を入力として Structured Design Model を再生成する。Actor と Role、State/Data/Update/History、Function/Process/Step を別型にし、各関係へ `contains`、`uses`、`produces` 等の明示した関係型を付ける。表は単一 entity type 又は明示した共通 process step のみを行に置く。ソースにない運用判断は Human Review として分離し、canonical source を変更しない。

