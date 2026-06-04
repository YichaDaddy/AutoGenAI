# Handoff: AutoGenAI · 自媒體情報中心 Dashboard

> 版本：v2（2026-06 更新）— 新增「財經日報」「自選股」「加班費統計」三個完整 detail modal，連同既有的「AI 日報」modal，四張主卡皆可點開詳情頁。

## Overview
這是「AutoGenAI 自媒體情報中心」的個人化儀表板（Mac's Dashboard）。它是一個單頁總覽介面，把使用者每日需要關注的資訊集中在一個 bento grid（便當盒式網格）佈局中：AI 選題日報、財經日報、自選股即時報價、本月加班費試算、馬拉松訓練倒數，以及未來功能 roadmap。

**四張主卡可點擊開啟全螢幕 detail modal：**
1. **AI 日報** → 每日 AI 大事件的選題分析（目標受眾／痛點／標題雛形／本地化切角）。
2. **財經日報** → 與 AI 日報「完全相同的格式與風格」，內容換成財經選題。
3. **自選股** → 台股／美股即時報價追蹤盤面（卡片網格、刷新、新增、雲端同步）。
4. **本月加班費** → 互動式加班費計算機（月薪→時薪、月曆填工時、依勞基法 §24 即時試算，含「預計總薪水＝月薪＋加班費」）。

目標使用者是經營中文自媒體的創作者（Mac），介面語言為繁體中文（zh-Hant）。

---

## About the Design Files
本資料夾中的 `Mac's Dashboard.html` 是一份**以 HTML 製作的設計參考稿（design reference / prototype）**，用來表達「最終應該長什麼樣子、有什麼行為」，**並不是可以直接搬到生產環境的程式碼**。

實作任務是：**在目標專案既有的技術環境中（React / Vue / Svelte / SwiftUI / 原生等），依照該環境既有的慣例、元件庫與狀態管理方式，重新實作出這份 HTML 設計稿的視覺與功能。** 如果目前還沒有既有環境，請選擇最適合此專案的框架後再實作。

所有資料（股價、新聞標題、加班時數、月薪等）為**示意假資料（mock data）**，實作時應接真實資料來源 / 由使用者輸入。文件中標示「預期行為 / 建議」之處，是設計稿尚未完整實作、但實作時應補上的部分。

---

## Fidelity
**High-fidelity (hifi)。** 顏色、字體、間距、圓角、陰影、互動皆為最終樣式，請盡量 pixel-perfect。下方「Design Tokens」與各區塊規格中列出的數值即為實作依據。**README 與 HTML 原始碼有出入時，一律以 HTML 為準。**

---

## Layout 總體佈局

### 頁面容器
- `body`：背景為三段對角線漸層 `linear-gradient(135deg, #F8F5EE 0%, #F6EFDD 52%, #F2E7C9 100%)`，`background-attachment: fixed`，`min-height: 100vh`，padding `22px clamp(18px,3vw,40px) 40px`。
- 內容置中容器 `.wrap`：`max-width: 1340px; margin: 0 auto`。

### 三大區塊（由上到下）
1. **NAV 導覽列**
2. **HERO 區**（問候語 + 進度條 strip ＋ 右側名言 quote）
3. **BENTO 網格**（6 個卡片）

### Bento 網格結構（桌機 ≥1081px）
`display: grid; gap: 18px; grid-template-columns: repeat(3, 1fr);`

grid-template-areas：
```
"ai       finance  stocks"
"overtime roadmap  roadmap"
```
- `ai`（AI 日報）、`finance`（財經日報）、`stocks`（自選股）佔第一列三欄。
- `overtime` 這個 grid area 實際放的是一個 **`.leftstack` 直向堆疊容器**，內含「馬拉松倒數」（上）與「本月加班費」（下）兩張卡。下方的 `#overtime` 設 `flex:1` 撐滿剩餘高度。
- `roadmap` 跨第二、三欄。
- ⚠️ grid area 名稱仍叫 `overtime`（歷史命名），但該位置上方其實是馬拉松卡、下方才是加班費卡，勿被名稱誤導。

### 響應式中斷點
- `max-width: 1080px`：改為 2 欄 `"ai finance" / "stocks overtime" / "roadmap roadmap"`，導覽列中間連結隱藏。
- `max-width: 680px`：單欄堆疊 `ai → finance → stocks → overtime → roadmap`；roadmap 內格改 2 欄；名言區改靠左全寬；body padding 縮為 `16px 14px 30px`。

---

## Design Tokens

### 顏色
| Token | 值 | 用途 |
|---|---|---|
| `--bg-a` | `#F8F5EE` | 背景漸層起點（暖白） |
| `--bg-b` | `#F6EFDD` | 背景漸層中段 |
| `--bg-c` | `#F2E7C9` | 背景漸層終點（暖米黃） |
| `--card` | `#FFFFFF` | 卡片基礎白 |
| `--card-soft` | `#FBF9F3` | 柔白（hover / modal 底） |
| `--ink` | `#1C1B19` | 主文字 / 深色元件（近黑暖調） |
| `--ink-soft` | `#6E6A62` | 次要文字 |
| `--ink-faint` | `#A8A39A` | 最弱文字 / 佔位 |
| `--line` | `rgba(28,27,25,.08)` | 細分隔線 |
| `--line-strong` | `rgba(28,27,25,.14)` | 較明顯邊線 |
| `--accent` | `#F4C84A` | 主強調色（金黃） |
| `--accent-deep` | `#E8B321` | 深金（進度條 / 強調 hover / 焦點環） |
| `--gold-ink` | `#9A7410` | 金色系文字 |
| `--up` | `#E0453B` | 漲（紅）— 台股慣例「紅漲綠跌」 |
| `--down` | `#1F9D63` | 跌（綠） |

額外用到的衍生色（非 token，inline）：
- 自選股錯誤態 / 例假日淺紅：`rgba(224,69,59,.05~.12)`。
- 加班費圖例：平日 `#8C93A8`（slate）、休息日 `--accent-deep`、例假日 `#E0796F`（淺紅）、國定假日 `--up`。
- modal 內分析區塊藍色：`#2A6FDB`（目標受眾）。

> **重要：紅漲綠跌** 為台灣股市慣例，與歐美相反。上漲 = 紅 `--up`、下跌 = 綠 `--down`，全站一致。

### 圓角 / 陰影
- `--r`=`26px`（卡片）、`--r-sm`=`16px`（內層小卡 / modal 內卡）、`--r-xs`=`11px`。
- 卡片陰影 `0 6px 30px rgba(60,50,20,.06)`；hover `0 16px 44px rgba(60,50,20,.12)`。
- Modal 面板 `0 50px 130px rgba(46,40,20,.32)`；modal icon `0 10px 26px rgba(232,179,33,.42)`。

### 字體（Google Fonts）
- `Plus Jakarta Sans`（300–800）— 主要拉丁文 UI 字體（body 預設）。
- `Noto Serif TC`（300–600）— **預設 CJK 字體**（`--cjk`，宋體）。
- `Noto Sans TC`（黑體）、`LXGW WenKai TC`（文楷）— 字型切換器的另兩個選項。
- `JetBrains Mono`（400/500）— 等寬，用於數字 / 代號 / 標籤（`--mono`，class `.mono`）。

body 字體堆疊：`'Plus Jakarta Sans', var(--cjk), system-ui, sans-serif`，`letter-spacing:.012em`。

**字型切換器**：右下角固定 `.fontsw` 浮動列，切換 CJK 字體為「黑體 / 文楷 / 宋體」，做法是改寫 CSS 變數 `--cjk`，並存到 `localStorage` key `cjkFont`，載入時還原。

### 間距節奏
卡片內距多為 `24px`；網格 / 堆疊 / strip gap 多為 `18px`；內部小元素 gap `9–14px`。

---

## 卡片通用樣式（`.card`）
- 背景 `rgba(255,255,255,.5)` + `backdrop-filter:blur(12px) saturate(1.08)`；邊框 `1px solid rgba(255,255,255,.55)`；圓角 `--r`；padding 24px；`display:flex; flex-direction:column`。
- 標頭 `.ck`：`.ck-title`（18px/600）+ `.ck-sub`（12.5px，`--ink-soft`），右上常放 `.chip` 或 `.go`。
- Chip `.chip`：等寬 10.5px，變體 `.live`（紅）/`.gold`（金）/`.ghost`（灰）。
- **可點擊卡片**（`#ai,#finance,#stocks,#overtime,#marathon`）：`cursor:pointer`，hover 時 `transform:scale(1.012) translateY(-3px)`、加深陰影、金邊 `rgba(244,200,74,.5)`，過場 `cubic-bezier(.2,.7,.3,1)`。

---

## 子區塊（儀表板卡片）規格

### NAV 導覽列
Logo（膠囊外框＋深底金字 `AI` 方塊＋「AutoGenAI」）→ 中央連結膠囊（總覽/情報/市場/工具/規劃，active 為深底白字）→ 右側「⚙ 設定」深底鈕、♪ 通知鈕（紅點）、金色漸層頭像「M」。

### HERO
- 左 `.herolead`：問候 `.hello`（`clamp(34px,5vw,56px)`，「早安，**Mac**」＋日期 small）＋ 進度條 strip（三條 `.pgrow`：情報更新 100% / 選題靈感池 60% / 本月工時記錄 64%；`.fill` 變體 dark/gold/hatch）。
- 右 `.quote`：大引號 + 英文名言（CJK 斜體）+ 中文翻譯 + 等寬署名。

### 1) AI 日報卡 `#ai`
副標「AI 效率工具 · 中文自媒體選題」。`.list` 五則 `.row`（編號 `.idx` + 標題 `.h` + `.meta` 以 3px 圓點分隔的分類/標籤/時間）。row:hover 底色 `--card-soft`。**點整張卡 → 開 AI 日報 detail modal。**

### 2) 財經日報卡 `#finance`
副標「市場動態 · 台灣投資人視角」。
- 指數區 `.idxbox`：大數字 21,860 + `.up`「▲ 1.12%」+ `.idxname`「加權指數 TAIEX · +242 點」。
- `.shock`「今日 3 震撼彈」+ `.list` 三則（`.idx` 用 `!`，上紅 `.up`／下綠 `.down` 表利多利空）。
- **點整張卡 → 開財經日報 detail modal。**

### 3) 自選股卡 `#stocks`（儀表板小卡）
副標「即時報價 · 紅漲綠跌」。`.tabs`（台股/美股）+ `#stocklist`（JS 動態，僅顯示**前 4 檔**）。每列 `.srow`：名稱/代號 + sparkline（`.spark` 高 26px，色隨漲跌）+ 價格/漲跌幅。
- **分頁點擊需 `stopPropagation`**（避免冒泡觸發開卡 modal）。
- **點卡片其他區域 → 開自選股 detail modal**（顯示全部標的）。

### 4) 馬拉松倒數卡 `#marathon`（leftstack 上方）
副標「MARATHON · 08/02 比賽日」，右上 `.chip.gold` 顯示 `D-NN`。主數字（剩餘天數 + 「天後開跑」）+ 進度條（金色漸層，`.mfill` 寬 = 訓練進度%，載入時由 0 動畫滑入）。
- 計算：`RACE=2026-08-02`、`START=2026-04-12`；`total`/`elapsed`/`remain`/`pct` 依今日推算。
- 預期行為：可點開訓練計畫詳情（尚未實作）。

### 5) 本月加班費卡 `#overtime`（leftstack 下方，`flex:1`）
副標「勞基法 §24 · 自動試算」。主數字 `.otbig`（`NT$` + 金額）+ `.otsub`（時薪基準 + 已記錄天數）+ `.otgrid` 三格（平日 / 休息日 / 例假 時數）。
- **這張卡的數字由加班費計算機即時驅動**（見下方 modal「計算邏輯」與 `updateMini()`）：金額 = 該月加班費合計、三格 = 各類別時數（例假格 = 例假日＋國定假日時數合計）。
- **點整張卡 → 開加班費統計 detail modal。**

### 6) Roadmap 卡 `#roadmap`（跨兩欄）
標頭「規劃中 · Roadmap」+ `.chip.ghost`「6 項功能開發中」。`.rmgrid`（3 欄）六個 `.rmcell`（虛線框，hover 轉實線）：社群監控(Q3)、快訊中心(Q3)、選題助手(Q4)、排程發布(Q4)、數據分析(規劃中)、競品雷達(規劃中)。

---

## Detail Modal 通用結構
四個 modal 共用一套外殼 class：
- `.modal`（`position:fixed; inset:0; z-index:90`，加 `.open` 顯示）。
- `.modal-scrim`：遮罩 `rgba(28,27,25,.42)` + `blur(7px)`，淡入；點擊關閉（`data-close`）。
- `.modal-panel`：置中，`width:min(1140px, 100vw-44px)`，`max-height:90vh`，背景 `linear-gradient(180deg,#FBF9F3,#F4EEDF)`，圓角 30px，進場 `scale(.97)→scale(1)` + 淡入（`cubic-bezier(.2,.7,.3,1)`）。`display:flex; flex-direction:column; overflow:hidden`。
- `.modal-head`：`.mh-icon`（58×58 圓角金色漸層方塊 + 28~30px inline SVG）+ `.mh-title`（28px/700）+ `.mh-sub` + `.modal-close`（44×44 圓鈕，hover 旋轉 90°）。
- `.modal-body`：`overflow-y:auto` 捲動區。

**通用開關行為（`wireModal(modalId, triggerId, onOpen?)`）：**
- 開啟：點 trigger 卡 → 加 `.open`、`aria-hidden=false`、鎖 `body` 捲動（`overflow:hidden`）、執行 `onOpen`。
- 關閉：點 scrim / 關閉鈕 / 按 `Esc`，還原捲動。
- 含 `.datetabs` 的 modal（AI、財經）：點日期 `.dt` 切 `.on` 並把 body 捲回頂。
- 無障礙：`role="dialog" aria-modal="true"`，`aria-hidden` 隨開關切換。

綁定：`wireModal('modal-ai','ai')`、`wireModal('modal-finance','finance')`、`wireModal('modal-stocks','stocks', ()=>renderGrid(...))`、`wireModal('modal-overtime','overtime')`。

---

## Modal A：AI 日報 `#modal-ai`
- Head：機器人 SVG icon，標題「AI 日報」/「AI 效率工具 · 為中文自媒體選題整理」。
- `.datetabs`：07 個日期鈕（06-03…05-28），`.dt.on` 底部 2.5px 金線。切換應載入該日資料（目前僅切樣式）。
- Body：`.sec-label`（紅 `.vbar` + 「大事件」+ chip「3 則」）+ `.bcards`（`column-count:2` 瀑布流）。
- 每張 `.bcard`：左側 4px 漸層條，`.bc-top`（編號 + 來源標籤），`.bc-title`（21px/700），`.bc-desc`，下接 4 個分析區塊 `.blk`：
  - `.blk.blue` 目標受眾、`.blk.red` 痛點（兩者並排於 `.blkgrid`）、`.blk.gold` 標題雛形（內文加粗）、`.blk.green` 本地化切角。
- 三則示意：Meta WhatsApp Business AI 客服全球上線、Alphabet 募資 850 億、AI 換臉詐騙修法。

---

## Modal B：財經日報 `#modal-finance`
**與 Modal A 結構、class、版面完全相同**，僅 icon、標題與內容不同（這是刻意的「完全參照 AI 日報」需求）。
- Head：折線圖 SVG icon，標題「財經日報」/「市場動態 · 為中文自媒體選題整理」。
- `.datetabs`：同 AI（06-03…05-28）。
- `.sec-label`：「今日震撼彈」+ chip「3 則」。
- `.bcards` 三則 `.bcard`，每則同樣含 目標受眾 / 痛點 / 標題雛形 / 本地化切角 四區塊：
  1. 台積電法說會優於預期，外資單日買超 87 億（來源：經濟日報）
  2. 某電子權值股財報暴雷，盤後爆量跌停（工商時報）
  3. 央行：通膨趨緩，年底前升息機率下降（中央社）
- 設計意涵：財經新聞同樣作為自媒體「選題」素材，因此沿用 AI 日報的四格分析框架。

---

## Modal C：自選股 `#modal-stocks`
依使用者提供的截圖重製，轉為暖米色調。
- Head：折線圖 SVG icon，標題「自選股」/「台股 & ETF · 即時報價追蹤」。
- **`.wl-toolbar`（固定於 head 與 body 之間）**：
  - 左：`.tabs`（台股 / 美股）。
  - 右 `.wl-status`：`更新於 <b>上午 05:54</b>` + `.chip.ghost`「已收盤」 + `.wl-refresh`「↻ 刷新」按鈕。
- **Body**：
  - `.wl-grid`：`repeat(auto-fit,minmax(290px,1fr))`（全寬約 3 欄、中等 2 欄、窄 1 欄）。
  - 每張 `.wlc`：
    - `.wlc-top`：`.wlc-cd`（等寬金色代碼）+ `.wlc-nm`（名稱，過長截斷）。
    - `.wlc-price`：等寬 30px，`.up`紅／`.down`綠／`.err`灰。
    - `.wlc-foot`：`.wlc-pill`（漲跌膠囊，紅/綠底色）+ `.wlc-st`（狀態如「已收盤」「盤後」）。
    - **錯誤態 `.wlc.err`**：虛線框，價格顯示「—」，foot 顯示「無法取得 · 網路異常」（對應截圖 0050 狀態）。
  - `.wl-add`：代碼輸入框 `.wl-input`（focus 金色描邊）+ `.wl-addbtn`「＋ 新增」（金底）。
  - `.wl-hint`：「台股代碼輸入數字即可（自動補 .TW）；ETF 同樣適用（0050、0056…）」。
  - `.wl-sync`：左「☁ 雲端同步 · 同步碼：**yicha0426** 變更」、右 `.chip.gold.ok`「已連線」（前置綠點）。
- **行為**：
  - 分頁切換台股/美股 → 重繪 grid（`renderGrid`）。
  - 刷新鈕：`.spin` 動畫（icon 旋轉 360°）、重繪、把「更新於」時間改為當前時間（`fmtNow()`，輸出「上午/下午 HH:MM」）。
  - 新增框與「變更/Fugle API Key」目前為靜態 UI，實作時應接新增自選股、切換同步帳號、設定 API Key。

---

## Modal D：加班費統計 `#modal-overtime`（互動式計算機）
依使用者提供的兩張截圖重製，轉為暖米色調，**功能完整可互動**。
- Head：鬧鐘 SVG icon，標題「加班費統計」/「依勞基法第24條計算 · 台灣法定加班費試算」。
- **Body 由上而下：**
  1. **月薪輸入 `.ot-salary`**：`月薪（元）` label + 大號等寬數字輸入框 `#ot-salary-input` + `.ot-rate`「時薪基準：**$XXX/hr**（月薪 ÷ 30 ÷ 8）」（即時計算）。
  2. **圖例 `.ot-legend`**：平日（週一～五）slate / 休息日（週六）金 / 例假日（週日）淺紅 / 國定假日 紅，各帶 13×13 圓角色塊。
  3. **月份導覽 `.ot-monthnav`**：`←` `2026 年 6 月` `→`（`#ot-prev`/`#ot-month`/`#ot-next`）。
  4. **月曆 `.ot-cal`**：`repeat(7,1fr)`，週一起始（表頭 一二三四五六日，週末紅字）。每個日格 `.otd`：
     - 變體 class：`.sat`（金底）/`.sun`（淺紅底）/`.nat`（較深紅底，國定假日）/`.today`（金色 2px 焦點環）/`.filled`（已填工時，輸入框金底）/`.blank`（月初補位空格）。
     - 內容：`.otd-n`（日期，例假/國定為紅）+ `.otd-tag`（平日/休息日/例假日/節日名如「端午節」）+ `.otd-in`（工時數字輸入框 + 「h」單位）。
  5. **試算 `.ot-sumhead`「本月加班費試算」+ `.ot-sumgrid`（4 卡）**：平日加班 / 休息日（週六）/ 例假日（週日）/ 國定假日，各顯示 `小時` 與 `$ 金額`。
  6. **合計卡 `.ot-total`（金邊，兩欄）**：
     - 左欄 `.ot-tcol`：**本月加班費合計** + 小時 + 金額（金色 `--gold-ink` 32px）。
     - 中間 `.ot-tdiv` 細分隔線。
     - 右欄 `.ot-tcol`：**預計總薪水**（副註「月薪 ＋ 加班費」）+ 金額（主文字色 `--ink` 32px）。← 本次新增。
     - 窄螢幕（≤620px）兩欄改上下堆疊。
  7. **`.ot-notes` 說明**：
     - 「計算基準（勞基法第24條）：平日前2h × 1.33、後續 × 1.67 ｜ 休息日前2h × 1.33、3–8h × 1.67、9h以上 × 2.67 ｜ 例假日／國定假日 × 2.0」
     - 「＊ 假日資料已內建 2025－2026 年，農曆假日以行政院人事行政總處公告為準」

### 計算邏輯（務必照實作）
```
時薪基準 rate = 月薪 / 30 / 8

每日加班費 payOf(type, h, rate)：
  平日 wd  : rate × ( min(h,2)×1.33 + max(h-2,0)×1.67 )
  休息日 sat: rate × ( min(h,2)×1.33 + clamp(h-2,0,6)×1.67 + max(h-8,0)×2.67 )
  例假 sun / 國定 nat: rate × h × 2.0

日期分類 dtype(y,m,d)：
  1. 若該日在 HOLIDAYS 表 → 國定假日(nat)，tag = 節日名
  2. 否則 getDay()==0(週日) → 例假日(sun)
  3. getDay()==6(週六) → 休息日(sat)
  4. 其餘 → 平日(wd)

本月彙總 monthAgg(y,m)：逐日累加各類別 { 小時, 金額 }
本月加班費合計 = 四類別金額加總
預計總薪水 grand = 月薪 + 本月加班費合計   ← 新增
```
- `HOLIDAYS` 內建 2025–2026 台灣國定假日（元旦、和平紀念日、兒童節、清明、勞動節、端午、中秋、國慶、行憲紀念日等；key 格式 `YYYY-M-D`，月份 1-indexed）。例：`2026-6-19` → 端午節（截圖中 6/19 標為國定假日）。實作時請以行政院人事行政總處公告補齊／更新調整放假日。
- 「今天」高亮：設計稿固定 `TODAY = 2026-06-05`（示範用）；實作請改為真實當日。
- **儀表板小卡同步**：`updateMini()` 用同一份 `monthAgg` 結果回寫 `#overtime` 卡的金額、時薪基準、已記錄天數與三格時數，確保 modal 與小卡數字一致。

> 註：footer 標示倍率 1.33 / 1.67 / 2.67 / 2.0；計算即採此值（法定平日前 2 小時為 4/3≈1.34，此處依使用者截圖採 1.33，金額會差數元，屬可接受誤差。實作時可依需求改用法定精確值）。

---

## Interactions & Behavior 總表
| 互動 | 觸發 | 行為 |
|---|---|---|
| 導覽連結切換 | 點 `.navlinks a` | `preventDefault`，切 active |
| 開 AI / 財經 / 自選股 / 加班費 modal | 點對應卡片 | 開 modal、鎖背景捲動 |
| 關 modal | scrim / 關閉鈕 / Esc | 關 modal、解鎖捲動 |
| modal 日期切換（AI/財經）| 點 `.dt` | 切 on、body 捲回頂（待接資料）|
| 儀表板自選股分頁 | 點 `#stocks .tab` | `stopPropagation`，重繪前 4 檔 |
| 自選股 modal 分頁 | 點 `.wl-toolbar .tab` | 重繪 grid（台股/美股）|
| 自選股刷新 | 點 `.wl-refresh` | icon 旋轉、重繪、更新時間 |
| 月薪輸入 | 改 `#ot-salary-input` | 重算時薪、試算、合計、總薪水、小卡 |
| 工時輸入 | 改任一日格 input | 存檔、重算試算、合計、總薪水、小卡 |
| 月份切換 | 點 `←`/`→` | 重繪月曆、重算試算 |
| 字型切換 | 點 `.fontsw button` | 改 `--cjk`、存 localStorage |
| 馬拉松進度動畫 | 載入時 | `m-fill` 由 0 滑到 pct% |
| 卡片 hover | hover 可點卡 | scale + 上移 + 陰影 + 金邊 |

---

## State Management（建議）
- `dashboardDate`：當前日期（設計稿硬寫 `2026-06-03`/今天 `2026-06-05`，應動態）。
- `aiDailyReport` / `financeDailyReport`：依日期查詢的選題報告（驅動卡片清單 + modal 內容 + 日期分頁）。
- `financeSnapshot`：加權指數、漲跌、3 則重點。
- `watchlist`：自選股清單，欄位 `{ cd(代碼), nm(名稱), p(價格), chg(漲跌額), pct(漲跌幅), up(1漲/0跌), st(狀態), s(sparkline 陣列), err(取價失敗) }`；分頁狀態 `activeMarket: 'TW'|'US'`；新增/刪除自選、雲端同步帳號、Fugle API Key、最後更新時間。
- `overtime`：
  - `salary`（月薪，persist：localStorage `ot-salary`）。
  - `hours`：`{ 'YYYY-M-D': 時數 }`（persist：localStorage `ot-hours`）。
  - `HOLIDAYS`（國定假日表，可後端維護）。
  - 衍生：`rate`、各類別 `monthAgg`、`本月加班費合計`、`預計總薪水`。
- `marathon`：比賽日、訓練起始日 → remain / elapsed / pct。
- `roadmap`：功能項目與時程（可靜態）。
- `cjkFont`：UI 偏好（localStorage `cjkFont`）。

### localStorage keys（設計稿實際使用）
| key | 內容 |
|---|---|
| `ot-salary` | 月薪數字 |
| `ot-hours` | JSON：每日工時 map |
| `cjkFont` | 目前 CJK 字體 |

---

## Assets
本設計**未使用任何外部圖片資產**。所有圖示皆為 inline SVG（modal 標頭：機器人 / 折線圖 ×2 / 鬧鐘）、Unicode 字元（⚙ ♪ ▲ ▼ ✕ ← → ↻ ＋ ☁ 等）、或純 CSS 元件（圓點、長條、sparkline、進度條、月曆格）。字體來自 Google Fonts。實作時若目標 codebase 有自家 icon 系統，請以對應 icon 取代 Unicode／inline SVG。

---

## Files
- `Mac's Dashboard.html` — 完整高擬真設計稿（單檔，HTML + CSS + JS）。所有精確數值、mock 資料、計算與互動邏輯以此檔為準。
  - CSS 段落導引：`/* ---------- BENTO ---------- */`、`/* ---------- DETAIL MODAL ---------- */`、`/* ---------- WATCHLIST MODAL ---------- */`、`/* ---------- OVERTIME MODAL ---------- */`。
  - JS 段落導引：自選股資料 `TW`/`US` 與 `renderMini`/`renderGrid`、通用 `wireModal`、加班費計算機 IIFE（`HOLIDAYS`/`dtype`/`payOf`/`monthAgg`/`renderCal`/`renderSummary`/`updateMini`）、字型切換、馬拉松倒數。
