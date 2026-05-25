#!/bin/zsh
# Daily AI report runner — triggered by launchd at 6 AM

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/Users/mac"

LOG_DIR="$HOME/projects/AutoGenAI/logs"
LOG_FILE="$LOG_DIR/$(date +%Y-%m-%d).log"
mkdir -p "$LOG_DIR"

echo "=== $(date) | Starting daily AI report ===" >> "$LOG_FILE"

cd "$HOME/projects/AutoGenAI" || exit 1

# Run the topic miner via Claude Code CLI (non-interactive)
/Applications/cmux.app/Contents/Resources/bin/claude --dangerously-skip-permissions -p "
你是 solopreneur-topic-miner Agent。請立刻執行以下工作：

今天日期：$(date +%Y-%m-%d)
昨日日期：$(date -v-1d +%Y-%m-%d)

【嚴格日期規則】所有納入日報的文章，發布日期必須是「昨日（$(date -v-1d +%Y-%m-%d)）」。
- TechCrunch 文章 URL 格式為 /YYYY/MM/DD/，請逐一核對 URL 中的日期，非昨日的一律剔除。
- WebSearch 結果請確認發布時間標記（如「1 day ago」「May XX」），非昨日發布的不得納入。
- 若某來源昨日無新文章，如實記錄於「來源覆蓋狀況」，不得以舊文充數。

1. 讀取 skills/solopreneur-topic-miner/user_profile.json 取得賽道設定
2. 依照 skills/solopreneur-topic-miner/SKILL.md 的完整工作流，抓取「昨日（$(date -v-1d +%Y-%m-%d)）」發布的歐美 AI 新聞：
   - 用 WebFetch 抓取 https://techcrunch.com/category/artificial-intelligence/，只保留 URL 含 $(date -v-1d +%Y/%m/%d) 的文章
   - 用 WebFetch 抓取 https://futuretools.io/news 昨日工具更新
   - 用 WebSearch 搜尋「AI news $(date -v-1d +%Y-%m-%d)」取得昨日重要 AI 發布（OpenAI、Anthropic、Google 等）
3. 篩選、評分，挑出最符合賽道的 8–11 則情報（大事件 3–4 則、工具更新 3–4 則、趨勢 2–3 則）
4. 將結果以 SKILL.md 規定的 JSON 格式寫入 skills/solopreneur-topic-miner/latest_topics.json
5. 執行 python3 skills/solopreneur-topic-miner/render_dashboard.py 更新看板

完成後輸出「DONE」。
" >> "$LOG_FILE" 2>&1

echo "--- AI report finished at $(date) ---" >> "$LOG_FILE"

# Run the finance news miner via Claude Code CLI
echo "=== $(date) | Starting daily finance report ===" >> "$LOG_FILE"

/Applications/cmux.app/Contents/Resources/bin/claude --dangerously-skip-permissions -p "
你是財經日報 Agent。請立刻執行以下工作：

今天日期：$(date +%Y-%m-%d)
昨日日期：$(date -v-1d +%Y-%m-%d)

抓取「昨日」發布的財經新聞，來源如下：

【YouTube 財經頻道】對每個頻道先 WebFetch 頻道首頁（例如 https://www.youtube.com/@GrahamStephan），
從 HTML 找到 <link rel=\"alternate\" type=\"application/rss+xml\"> 取得 RSS URL，
再 WebFetch 該 RSS URL 抓取昨日影片標題與描述。
四個頻道：
- https://www.youtube.com/@GrahamStephan
- https://www.youtube.com/@MeetKevin
- https://www.youtube.com/@AndreiJikh
- https://www.youtube.com/@HeresyFinancial

【財經媒體】WebFetch 抓取昨日重要文章：
- https://feeds.bloomberg.com/markets/news.rss（Bloomberg RSS，取標題+摘要）
- https://www.reuters.com/finance/
- https://www.cnbc.com/markets/
- https://finance.yahoo.com/news/

【替代 Twitter 來源】WebFetch 直接抓網站內容：
- https://unusualwhales.com/news（選擇權異常單與市場爆料）
- https://www.zerohedge.com/（極端市場觀點）

【重要人物動態】WebSearch 搜尋最新消息：
- 搜尋「Michael Burry」昨日動態
- 搜尋「Elon Musk market economy」昨日動態

【台灣財經】WebFetch 抓取昨日重要報導：
- https://news.cnyes.com/news/cat/tw_stock
- https://www.businesstoday.com.tw/catalog/80392

篩選標準：優先選話題性強、有爭議性、能引發「這什麼？我要點進去看」的爆款體質內容。
同等重要性下，優先選對台灣投資人有感的角度切入。

選出 8–10 則，分類為：
- market_shocks（市場震撼彈）：3–4 則
- investment_opportunities（投資機會）：3–4 則
- macro_observations（總經觀察）：2–3 則

每則情報格式：
{
  \"title\": \"繁體中文標題（50字以內）\",
  \"sources\": [{\"name\": \"來源名稱\", \"url\": \"原文連結\"}],
  \"summary\": \"繁體中文摘要（2–3句）\",
  \"tw_stock_impact\": \"對台股或台灣投資人的直接影響\",
  \"investment_insight\": \"投資啟示（具體可操作）\",
  \"title_idea\": \"爆款標題雛形（繁體中文）\",
  \"local_angle\": \"台灣讀者的切入角度\"
}

輸出完整 JSON 格式並寫入 skills/solopreneur-topic-miner/latest_finance_topics.json：
{
  \"date\": \"昨日日期（YYYY-MM-DD）\",
  \"market_shocks\": [...],
  \"investment_opportunities\": [...],
  \"macro_observations\": [...]
}

寫入後執行 python3 skills/solopreneur-topic-miner/render_dashboard.py 更新看板。

完成後輸出「FINANCE DONE」。
" >> "$LOG_FILE" 2>&1

echo "--- Finance report finished at $(date) ---" >> "$LOG_FILE"

# Commit and push to GitHub
git add -A
git commit -m "auto: daily report $(date +%Y-%m-%d)" >> "$LOG_FILE" 2>&1
git push origin main >> "$LOG_FILE" 2>&1

# Sync gh-pages without branch checkout (force because GH Actions may have committed stocks.json there)
git push origin main:gh-pages --force >> "$LOG_FILE" 2>&1

echo "=== $(date) | All done ===" >> "$LOG_FILE"
