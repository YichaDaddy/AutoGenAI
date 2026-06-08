# 待修改清單

## TOEIC：換日判斷的競態問題（race condition）

**現象**：早上開 dashboard 時看到的多益題目沒更新，重新整理後才出現新題目。

**原因**：`v3/index.html` 的 `applyDayChange()`（約 1612 行）用瀏覽器當下日期 `todayStr()` 跟
`st.currentSet.date` 做比對來判斷要不要換新一天的題組。但題庫檔案 `skills/toeic/questions.json`
是由 launchd 在早上 6 點觸發、實際完成於 06:11–06:12 才寫入新內容。

如果使用者在 06:11 之前就打開頁面：
1. `todayStr()` 已經是「今天」
2. 但抓到的 `questions.json` 內容還是「昨天」的（檔案還沒被 cron 重新產生）
3. `applyDayChange` 判斷「日期不同 + 昨天有作答」→ 提早執行換日邏輯，用**舊內容**組成新一組，
   並把 `st.currentSet.date` 直接蓋成「今天」存檔（也會推上 Firebase 同步）
4. 之後即使檔案在 06:12 真的換成新題，`st.currentSet.date===today` 已經成立，
   後續只會做欄位補齊（如 `zh_passage`）而不重建題組——當天就一直卡在「提早鎖定的舊內容」

**修法方向**：換日判斷不要只比對瀏覽器日期字串，要同時確認 `newQ.date === todayStr()`
（也就是題庫檔案本身標記的日期已經是今天，代表後端真的已經產生當天內容）。
只有兩者都成立時才真正鎖定/重建當天題組；否則維持原本那組，避免用尚未更新的舊內容提早佔用名額。

**相關位置**：
- `v3/index.html` 的 `applyDayChange(newQ)` 函式
- 後端產題時間：`run_daily.sh` 第 140-210 行（launchd 6:00 觸發，TOEIC 約 06:11-06:12 完成）
