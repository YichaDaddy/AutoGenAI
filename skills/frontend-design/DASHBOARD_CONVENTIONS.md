# v3 Dashboard 設計慣例

本檔案記錄 `v3/index.html`（單檔 HTML + 原生 CSS + Vanilla JS dashboard）已經建立起來的視覺語言與互動習慣。修改或新增功能時，優先沿用這裡的慣例，不要另起一套風格。

## 視覺系統（已鎖定，勿混用其他配色/圓角）

```css
--bg-a:#F8F5EE; --bg-b:#F6EFDD; --bg-c:#F2E7C9;   /* 米杏漸層底色 */
--card:#FFFFFF; --card-soft:#FBF9F3;               /* 卡片：純白 / 米白 */
--ink:#1C1B19; --ink-soft:#6E6A62; --ink-faint:#A8A39A;
--line:rgba(28,27,25,.08); --line-strong:rgba(28,27,25,.14);
--accent:#F4C84A; --accent-deep:#E8B321; --gold-ink:#9A7410;  /* 唯一強調色：暖金 */
--up:#E0453B; --down:#1F9D63;                      /* 漲跌色，僅金融類數據用 */
--r:26px; --r-sm:16px; --r-xs:11px;                /* 圓角三階：卡片/區塊/小元件 */
--sh:0 4px 26px rgba(46,40,20,.055);               /* 陰影染上背景的暖色調，不用純黑 */
--mono:'JetBrains Mono',monospace;
--cjk:'Noto Serif TC';
font-family: 'Plus Jakarta Sans', var(--cjk), system-ui, sans-serif;
```

- **單一強調色**：全站只用暖金 `--accent`/`--accent-deep`/`--gold-ink`，不要在某個區塊另外引入新的主色。
- **圓角分級**：卡片用 `--r`/`--r-sm`，互動按鈕/標籤用 pill（`border-radius:20px`），小徽章用 `--r-xs`。三層用途固定，不要混搭。
- **陰影染色**：陰影一律帶暖色調（`rgba(46,40,20,...)`），不要用純黑陰影。
- **字體分工**：英文/數字用 Plus Jakarta Sans，中文用 Noto Serif TC（`--cjk`），數據/代號用 JetBrains Mono（`--mono`）。

## 元件慣例

- **卡片**：白底、`1px solid var(--line)`、`border-radius:var(--r-sm)`、`box-shadow:var(--sh)`。
- **按鈕/標籤（pill）**：`border-radius:20px`、細邊框 `var(--line-strong)`、transition `.15s–.18s`，hover 時填入 `--accent` 並把文字轉為 `--ink`（例：`.tq-navbtn.primary:hover`、`.tq-add-btn:hover`）。
- **互動回饋**：顏色/底色漸變為主，避免位移造成跳動；過場時間統一在 150–250ms 之間。
- **輔助說明區塊**（如解析卡 `.tq-exp`）：左側加 3px 強調色邊條 + 淡色底，與一般卡片做出層級區隔。

## 互動設計習慣（從 TOEIC 功能討論中確立）

這些是和使用者多次討論後定下來的原則，新功能設計時可以直接套用同樣邏輯：

1. **使用者自主權優先於系統判斷**：答對不代表真的會了（可能用猜的），所以系統不自動歸類，而是提供「＋ 加入複習」這種低調的 opt-in 按鈕，讓使用者自己決定要不要加入錯題本。
2. **延後揭曉，避免干擾作答**：像 PART 6 多格填空，要等使用者「全部作答完」才顯示解析（`allDone` 判斷），避免提早看到答案影響後續作答。未完成時顯示中性的提示文字（`.tq-pending-note`），不是空白也不是答案。
3. **輔助資訊預設收合**：中文翻譯這類輔助內容用可展開/收合的方式呈現（`.tq-zh-wrap` + toggle 按鈕），且只在「使用者已經自己嘗試過」之後才出現，保持畫面整潔、不喧賓奪主。
4. **跨裝置同步尊重既有進度**：透過 Firebase 同步時，不要粗暴覆蓋——`applyDayChange()` 的邏輯是只有在使用者「真的作答過」才換題，未答完的題目和錯題本優先保留與延續。
5. **獨立捲動區塊**：左右分欄（如 PART 6 展開後的「文章 / 題目」）各自獨立捲動，避免長文章把作答區擠出視窗（`.tqm-split` 固定高度 + 兩側 `overflow-y:auto`）。

## 給未來修改的提醒

- 新增 UI 前先確認是否已有相同用途的元件 class 可重用（卡片、pill 按鈕、解析區塊樣式都已固定）。
- 不要為了「看起來更精緻」引入新的配色或圓角系統——本專案已經建立起一致的暖金 + 米杏視覺語言，新增功能應該融入而非另開一套。
- 互動流程設計時，優先考慮「會不會干擾使用者當下的任務」（如作答中途跳出答案、同步時蓋掉進度），這比視覺上的花俏更重要。
