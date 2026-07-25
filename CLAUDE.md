# AutoGenAI 專案規則

## 最重要：動手前必須先問

**每次要修改程式碼之前，先說明你打算怎麼改，等用戶確認後才能動手。**

不管任務大小，都要遵守這個流程：
1. 說明計畫（要改什麼、為什麼這樣改）
2. 等用戶回「繼續」或「ok」
3. 才開始實作

違反這條規則已經被用戶明確糾正過多次，不可再犯。

## 加班費國定假日維護規則

修改 `TW_HOLIDAYS` / `HOLIDAYS` 假日清單時，有三個陷阱必須同時注意：

1. **兩個檔案都要改**：假日資料同時存在 `v3/index.html`（加班費 modal）和 `overtime.html`（獨立頁面），任何更新都要兩邊同步。

2. **key 格式必須補零**：`v3/index.html` 裡的 `dk()` 函式生成的 key 是 `'YYYY-MM-DD'`（月份和日期都補零，如 `'2026-06-19'`）。HOLIDAYS 物件的 key **必須使用相同格式**，否則查找永遠失敗、所有假日都顯示「平日」。`overtime.html` 也是同樣格式。

3. **改完要推到 gh-pages**：GitHub Pages 從 `gh-pages` branch 提供服務，不是從 `main`。改 `v3/index.html` 後，只 push main 是不夠的——必須同時觸發 deploy workflow 或手動把更新推到 `gh-pages` branch。目前 `.github/workflows/deploy_v2.yml` 已設定：當 `v3/index.html` 或 `v2/index.html` 有變動 push 到 main 時，會自動同步到 gh-pages。

假日清單依據：行政院人事行政總處每年公布的辦公日曆表（含補假日），勿自行推算農曆節日日期。

## Dashboard 設計慣例

修改或新增 `v3/index.html` 的 UI/UX 之前，先讀 `skills/frontend-design/DASHBOARD_CONVENTIONS.md`——
裡面記錄了已經鎖定的配色/圓角/陰影系統，以及和用戶討論定案的互動習慣（opt-in 而非自動判斷、延後揭曉答案、輔助資訊預設收合、跨裝置同步尊重既有進度等）。新功能應該融入既有視覺語言，不要另起一套。

## 自動化排程與系統故障診斷 CheckList

排查「日報停更」或「自動化排程失效」時，必須嚴格遵守以下驗證順序，切勿憑單一本機測試結果做結論：

1. **先確認真實的數據管線 (Data Pipeline)**：
   - 檢查 Git Commit 作者（7 月起日報主要由雲端 Routine 執行，Commit Author 為 `Claude <noreply@anthropic.com>`）。
   - 本機 `run_daily.sh` / `launchd` 檔為已退役的備援路徑，非主要運作管線。

2. **時間軸與日誌交叉比對 (歷史數據鏈驗證)**：
   - 務必先比對 `logs/` 目錄的歷史日誌檔案時間。若發現數週完全沒有本機日誌但 Git 依然每日有 commit，代表本機路徑早已未在使用。
   - **嚴禁將手動測試本機舊腳本拋出的錯誤 (如 401 OAuth token expired) 誤診為雲端停更的原因**。

3. **雲端 Routine 中斷的正確處置**：
   - 若 GitHub 近期沒有新 commit，主因是雲端 Routine 停擺，應引導至 Claude 控制台重新啟動/觸發雲端 Routine，毋須更動本機已停用的 `launchd` 設定。


## 自動化排程與系統故障診斷 CheckList

排查「日報停更」或「自動化排程失效」時，必須嚴格遵守以下驗證順序，切勿憑單一本機測試結果做結論：

1. **先確認真實的數據管線 (Data Pipeline)**：
   - 檢查 Git Commit 作者（7 月起日報主要由雲端 Routine 執行，Commit Author 為 `Claude <noreply@anthropic.com>`）。
   - 本機 `run_daily.sh` / `launchd` 檔為已退役的備援路徑，非主要運作管線。

2. **時間軸與日誌交叉比對 (歷史數據鏈驗證)**：
   - 務必先比對 `logs/` 目錄的歷史日誌檔案時間。若發現數週完全沒有本機日誌但 Git 依然每日有 commit，代表本機路徑早已未在使用。
   - **嚴禁將手動測試本機舊腳本拋出的錯誤 (如 401 OAuth token expired) 誤診為雲端停更的原因**。

3. **雲端 Routine 中斷的正確處置**：
   - 若 GitHub 近期沒有新 commit，主因是雲端 Routine 停擺，應引導至 Claude 控制台重新啟動/觸發雲端 Routine，毋須更動本機已停用的 `launchd` 設定。

