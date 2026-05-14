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

1. 讀取 skills/solopreneur-topic-miner/user_profile.json 取得賽道設定
2. 確認今天日期，計算昨日日期（YYYY-MM-DD）
3. 依照 skills/solopreneur-topic-miner/SKILL.md 的完整工作流，抓取歐美昨日 AI 新聞：
   - 用 WebFetch 抓取 https://techcrunch.com/category/artificial-intelligence/ 昨日文章
   - 用 WebFetch 抓取 https://futuretools.io/news 昨日工具更新
   - 用 WebSearch 搜尋昨日重要 AI 發布（OpenAI、Anthropic、Google 等）
4. 篩選、評分，挑出最符合賽道的 8–11 則情報（大事件 3–4 則、工具更新 3–4 則、趨勢 2–3 則）
5. 將結果以 SKILL.md 規定的 JSON 格式寫入 skills/solopreneur-topic-miner/latest_topics.json
6. 執行 python3 skills/solopreneur-topic-miner/render_dashboard.py 更新看板

完成後輸出「DONE」。
" >> "$LOG_FILE" 2>&1

echo "--- Claude finished at $(date) ---" >> "$LOG_FILE"

# Commit and push to GitHub (updates both main and gh-pages)
git add -A
git commit -m "auto: daily report $(date +%Y-%m-%d)" >> "$LOG_FILE" 2>&1

git push origin main >> "$LOG_FILE" 2>&1

# Sync gh-pages branch so GitHub Pages updates too
git checkout gh-pages >> "$LOG_FILE" 2>&1
git merge main --no-edit >> "$LOG_FILE" 2>&1
git push origin gh-pages >> "$LOG_FILE" 2>&1
git checkout main >> "$LOG_FILE" 2>&1

echo "=== $(date) | All done ===" >> "$LOG_FILE"
