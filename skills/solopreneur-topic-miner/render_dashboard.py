#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime

BASE_DIR             = "/Users/mac/projects/AutoGenAI"
SKILL_DIR            = os.path.join(BASE_DIR, "skills/solopreneur-topic-miner")
HTML_PATH            = os.path.join(BASE_DIR, "daily_topic_dashboard.html")
PROFILE_PATH         = os.path.join(SKILL_DIR, "user_profile.json")
TOPICS_PATH          = os.path.join(SKILL_DIR, "latest_topics.json")
ARCHIVE_PATH         = os.path.join(SKILL_DIR, "topics_archive.json")
FINANCE_TOPICS_PATH  = os.path.join(SKILL_DIR, "latest_finance_topics.json")
FINANCE_ARCHIVE_PATH = os.path.join(SKILL_DIR, "finance_archive.json")

# ── helpers ──────────────────────────────────────────────────────────────

def load_json(path, default_val):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                pass
    return default_val

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_archive(topics_path, archive_path):
    latest  = load_json(topics_path, {})
    archive = load_json(archive_path, [])
    if not latest or not latest.get('date'):
        return archive
    existing_dates = {entry.get('date') for entry in archive}
    if latest['date'] not in existing_dates:
        archive.insert(0, latest)
        print(f"Archive updated: added {latest['date']}")
    else:
        archive = [latest if e.get('date') == latest['date'] else e for e in archive]
        print(f"Archive updated: refreshed {latest['date']}")
    archive.sort(key=lambda x: x.get('date', ''), reverse=True)
    archive = archive[:7]
    save_json(archive_path, archive)
    return archive

# ── shared ────────────────────────────────────────────────────────────────

def render_sources(sources):
    return ''.join(
        f'<a href="{s.get("url","#")}" target="_blank" class="source-tag">{s.get("name","")}</a>'
        for s in sources
    )

def render_section(label, dot_cls, label_cls, count_cls, accent_cls, items, card_fn):
    if not items:
        return ''
    cards = '\n'.join(card_fn(item, accent_cls) for item in items)
    return f"""<section class="report-section">
  <div class="section-header">
    <span class="section-dot {dot_cls}"></span>
    <span class="section-label {label_cls}">{label}</span>
    <span class="section-count {count_cls}">{len(items)} 則</span>
    <span class="section-line"></span>
  </div>
  <div class="cards-grid">{cards}</div>
</section>"""

# ── AI channel ────────────────────────────────────────────────────────────

def render_ai_card(item, accent_class):
    title       = item.get('title', '')
    sources_html= render_sources(item.get('sources', []))
    summary     = item.get('summary', '')
    audience    = item.get('audience', '')
    pain_point  = item.get('pain_point', '')
    title_idea  = item.get('title_idea', '')
    local_angle = item.get('local_angle', '')
    return f"""<div class="news-card">
      <div class="card-accent {accent_class}"></div>
      <div class="card-body">
        <h3 class="card-title">{title}</h3>
        <div class="sources-row">{sources_html}</div>
        <p class="summary">{summary}</p>
        <div class="insight-panel">
          <div class="insight-row"><span class="insight-label">目標受眾</span><span class="insight-value">{audience}</span></div>
          <div class="insight-row"><span class="insight-label">痛點</span><span class="insight-value">{pain_point}</span></div>
          <div class="insight-row title-row"><span class="insight-label">標題雛形</span><span class="insight-value">{title_idea}</span></div>
          <div class="insight-row local-row"><span class="insight-label">本地化切角</span><span class="insight-value">{local_angle}</span></div>
        </div>
      </div>
    </div>"""

def render_ai_day_panel(entry, is_active):
    date_str     = entry.get('date', '')
    big_events   = entry.get('big_events', [])
    tool_updates = entry.get('tool_updates', [])
    trends       = entry.get('trends', [])
    total        = len(big_events) + len(tool_updates) + len(trends)
    inner = (
        render_section('大事件',         'dot-red',   'label-red',   'count-red',   'accent-red',   big_events,   render_ai_card) +
        render_section('工具更新',       'dot-blue',  'label-blue',  'count-blue',  'accent-blue',  tool_updates, render_ai_card) +
        render_section('值得追蹤的趨勢', 'dot-green', 'label-green', 'count-green', 'accent-green', trends,       render_ai_card)
    )
    return f"""<div id="ai-day-{date_str}" class="day-panel {'active' if is_active else ''}" data-date="{date_str}" data-total="{total}" data-channel="ai">
{inner}
</div>"""

# ── Finance channel ───────────────────────────────────────────────────────

def render_finance_card(item, accent_class):
    title              = item.get('title', '')
    sources_html       = render_sources(item.get('sources', []))
    summary            = item.get('summary', '')
    tw_stock_impact    = item.get('tw_stock_impact', '')
    investment_insight = item.get('investment_insight', '')
    title_idea         = item.get('title_idea', '')
    local_angle        = item.get('local_angle', '')
    return f"""<div class="news-card">
      <div class="card-accent {accent_class}"></div>
      <div class="card-body">
        <h3 class="card-title">{title}</h3>
        <div class="sources-row">{sources_html}</div>
        <p class="summary">{summary}</p>
        <div class="insight-panel">
          <div class="insight-row stock-row"><span class="insight-label">對台股影響</span><span class="insight-value">{tw_stock_impact}</span></div>
          <div class="insight-row invest-row"><span class="insight-label">投資啟示</span><span class="insight-value">{investment_insight}</span></div>
          <div class="insight-row title-row"><span class="insight-label">標題雛形</span><span class="insight-value">{title_idea}</span></div>
          <div class="insight-row local-row"><span class="insight-label">本地化切角</span><span class="insight-value">{local_angle}</span></div>
        </div>
      </div>
    </div>"""

def render_finance_day_panel(entry, is_active):
    date_str           = entry.get('date', '')
    market_shocks      = entry.get('market_shocks', [])
    investment_opps    = entry.get('investment_opportunities', [])
    macro_observations = entry.get('macro_observations', [])
    total = len(market_shocks) + len(investment_opps) + len(macro_observations)
    empty = '' if total > 0 else '''<div class="empty-state">
  <div class="empty-icon">📊</div>
  <div class="empty-title">財經日報尚未生成</div>
  <div class="empty-desc">將於每日清晨自動抓取並更新</div>
</div>'''
    inner = empty + (
        render_section('市場震撼彈', 'dot-amber',  'label-amber',  'count-amber',  'accent-amber',  market_shocks,   render_finance_card) +
        render_section('投資機會',   'dot-purple', 'label-purple', 'count-purple', 'accent-purple', investment_opps, render_finance_card) +
        render_section('總經觀察',   'dot-teal',   'label-teal',   'count-teal',   'accent-teal',   macro_observations, render_finance_card)
    )
    return f"""<div id="finance-day-{date_str}" class="day-panel {'active' if is_active else ''}" data-date="{date_str}" data-total="{total}" data-channel="finance">
{inner}
</div>"""

# ── main render ───────────────────────────────────────────────────────────

def render_html():
    profile = load_json(PROFILE_PATH, {"niche": "AI 效率工具"})
    niche   = profile.get('track', profile.get('niche', 'AI 效率工具'))

    ai_archive      = update_archive(TOPICS_PATH, ARCHIVE_PATH)
    finance_archive = update_archive(FINANCE_TOPICS_PATH, FINANCE_ARCHIVE_PATH)

    if not ai_archive:
        print("No AI data found in archive.")
        return

    if not finance_archive:
        today = datetime.now().strftime('%Y-%m-%d')
        finance_archive = [{"date": today, "market_shocks": [], "investment_opportunities": [], "macro_observations": []}]

    latest_ai_date  = ai_archive[0].get('date', '')
    latest_ai_total = sum(len(ai_archive[0].get(k, [])) for k in ('big_events', 'tool_updates', 'trends'))

    ai_tabs = ''.join(
        f'<button class="date-tab {"active" if i == 0 else ""}" data-target="ai-day-{e["date"]}" data-date="{e["date"]}" data-channel="ai">{e["date"][5:]}</button>\n'
        for i, e in enumerate(ai_archive)
    )
    fin_tabs = ''.join(
        f'<button class="date-tab {"active" if i == 0 else ""}" data-target="finance-day-{e["date"]}" data-date="{e["date"]}" data-channel="finance">{e["date"][5:]}</button>\n'
        for i, e in enumerate(finance_archive)
    )

    ai_panels  = '\n'.join(render_ai_day_panel(e, i == 0)      for i, e in enumerate(ai_archive))
    fin_panels = '\n'.join(render_finance_day_panel(e, i == 0) for i, e in enumerate(finance_archive))

    final_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI 日報 & 財經新聞</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --red:          #E53E3E;
      --red-bg:       #FFF5F5;
      --red-border:   #FED7D7;
      --blue:         #2B6CB0;
      --blue-bg:      #EBF8FF;
      --blue-border:  #BEE3F8;
      --green:        #276749;
      --green-bg:     #F0FFF4;
      --green-border: #C6F6D5;
      --amber:        #B7791F;
      --amber-bg:     #FEFCE8;
      --amber-border: #FEF08A;
      --purple:       #6B46C1;
      --purple-bg:    #FAF5FF;
      --purple-border:#D6BCFA;
      --teal:         #2C7A7B;
      --teal-bg:      #E6FFFA;
      --teal-border:  #B2F5EA;
      --ink:          #1A202C;
      --ink-2:        #2D3748;
      --muted:        #718096;
      --faint:        #A0AEC0;
      --surface:      #FFFFFF;
      --page:         #F7F8FA;
      --border:       #E8ECF0;
      --shadow-sm:    0 1px 3px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
      --shadow-md:    0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.04);
      --radius:       14px;
      --header-h:     64px;
      --channel-h:    44px;
      --tabs-h:       52px;
    }}

    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--page);
      color: var(--ink);
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }}

    /* ─── Progress bar ─── */
    #progress {{
      position: fixed; top: 0; left: 0; height: 3px;
      background: linear-gradient(90deg, #6366F1, #10B981);
      width: 0%; z-index: 300;
      transition: width 0.1s linear;
    }}

    /* ─── Header ─── */
    .site-header {{
      background: #0D1117; color: #fff;
      padding: 0 2rem; height: var(--header-h);
      display: flex; align-items: center; justify-content: space-between;
      position: sticky; top: 0; z-index: 200;
      border-bottom: 1px solid rgba(255,255,255,0.06);
    }}
    .header-left {{ display: flex; align-items: center; gap: 12px; }}
    .header-logo {{
      width: 36px; height: 36px;
      background: linear-gradient(135deg, #6366F1 0%, #10B981 100%);
      border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      font-size: 18px; flex-shrink: 0;
      box-shadow: 0 0 0 1px rgba(255,255,255,0.1);
      transition: background 0.3s;
    }}
    .header-brand {{ font-size: 16px; font-weight: 800; letter-spacing: -0.3px; transition: all 0.2s; }}
    .header-sub   {{ font-size: 11px; color: #6B7280; margin-top: 1px; font-weight: 500; }}
    .header-right {{ text-align: right; }}
    .header-date  {{ font-size: 13px; font-weight: 700; color: #E5E7EB; letter-spacing: 0.2px; }}
    .header-count {{
      display: inline-block; margin-top: 2px;
      font-size: 10px; font-weight: 600; color: #374151;
      background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.1);
      border-radius: 99px; padding: 1px 8px; letter-spacing: 0.3px;
    }}

    /* ─── Channel Nav ─── */
    .channel-nav {{
      background: #161B22;
      border-bottom: 1px solid rgba(255,255,255,0.07);
      height: var(--channel-h);
      display: flex; align-items: center;
      padding: 0 2rem; gap: 4px;
      position: sticky; top: var(--header-h); z-index: 150;
    }}
    .channel-tab {{
      display: flex; align-items: center; gap: 6px;
      padding: 5px 14px; border-radius: 8px;
      border: 1px solid transparent; background: transparent;
      color: rgba(255,255,255,0.45);
      font-family: inherit; font-size: 13px; font-weight: 600;
      cursor: pointer; transition: all 0.15s;
    }}
    .channel-tab:hover {{ background: rgba(255,255,255,0.07); color: rgba(255,255,255,0.75); }}
    .channel-tab.active {{ background: rgba(255,255,255,0.1); color: #fff; border-color: rgba(255,255,255,0.15); }}

    /* ─── Date Tab Bar ─── */
    .date-nav {{
      background: var(--surface); border-bottom: 1px solid var(--border);
      height: var(--tabs-h);
      display: flex; align-items: center;
      padding: 0 2rem; gap: 6px;
      position: sticky; top: calc(var(--header-h) + var(--channel-h)); z-index: 100;
      overflow-x: auto; scrollbar-width: none;
    }}
    .date-nav::-webkit-scrollbar {{ display: none; }}
    .date-nav-label {{
      font-size: 11px; font-weight: 700; color: var(--faint);
      letter-spacing: 0.5px; text-transform: uppercase;
      white-space: nowrap; margin-right: 4px; flex-shrink: 0;
    }}
    .date-tabs-group {{ display: flex; gap: 6px; }}
    .date-tab {{
      flex-shrink: 0; padding: 5px 14px;
      border-radius: 8px; border: 1px solid var(--border);
      background: transparent; color: var(--muted);
      font-family: inherit; font-size: 12px; font-weight: 600;
      cursor: pointer; transition: all 0.15s; white-space: nowrap;
    }}
    .date-tab:hover {{ background: var(--page); color: var(--ink); border-color: #CBD5E0; }}
    .date-tab.active {{ background: var(--ink); color: #fff; border-color: var(--ink); }}

    /* ─── Layout ─── */
    .container {{ max-width: 1020px; margin: 0 auto; padding: 2.5rem 1.5rem 5rem; }}

    /* ─── Day Panels ─── */
    .day-panel {{ display: none; }}
    .day-panel.active {{ display: block; }}

    /* ─── Section ─── */
    .report-section {{
      margin-bottom: 3rem; opacity: 0; transform: translateY(10px);
      animation: fadeUp 0.35s ease forwards;
    }}
    .report-section:nth-child(1) {{ animation-delay: 0.04s; }}
    .report-section:nth-child(2) {{ animation-delay: 0.12s; }}
    .report-section:nth-child(3) {{ animation-delay: 0.20s; }}
    @keyframes fadeUp {{ to {{ opacity: 1; transform: translateY(0); }} }}

    .section-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem; }}
    .section-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
    .dot-red    {{ background: var(--red);    box-shadow: 0 0 0 3px #FED7D7; }}
    .dot-blue   {{ background: var(--blue);   box-shadow: 0 0 0 3px #BEE3F8; }}
    .dot-green  {{ background: var(--green);  box-shadow: 0 0 0 3px #C6F6D5; }}
    .dot-amber  {{ background: #D69E2E;       box-shadow: 0 0 0 3px #FEF08A; }}
    .dot-purple {{ background: var(--purple); box-shadow: 0 0 0 3px #D6BCFA; }}
    .dot-teal   {{ background: var(--teal);   box-shadow: 0 0 0 3px #B2F5EA; }}

    .section-label {{ font-size: 13px; font-weight: 800; letter-spacing: 0.8px; text-transform: uppercase; }}
    .label-red    {{ color: var(--red); }}
    .label-blue   {{ color: var(--blue); }}
    .label-green  {{ color: var(--green); }}
    .label-amber  {{ color: var(--amber); }}
    .label-purple {{ color: var(--purple); }}
    .label-teal   {{ color: var(--teal); }}

    .section-count {{ font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 99px; margin-left: 2px; }}
    .count-red    {{ background: var(--red-bg);    color: var(--red);    border: 1px solid var(--red-border); }}
    .count-blue   {{ background: var(--blue-bg);   color: var(--blue);   border: 1px solid var(--blue-border); }}
    .count-green  {{ background: var(--green-bg);  color: var(--green);  border: 1px solid var(--green-border); }}
    .count-amber  {{ background: var(--amber-bg);  color: var(--amber);  border: 1px solid var(--amber-border); }}
    .count-purple {{ background: var(--purple-bg); color: var(--purple); border: 1px solid var(--purple-border); }}
    .count-teal   {{ background: var(--teal-bg);   color: var(--teal);   border: 1px solid var(--teal-border); }}

    .section-line {{ flex: 1; height: 1px; background: var(--border); }}

    /* ─── Cards Grid ─── */
    .cards-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(460px, 1fr)); gap: 1.25rem; }}
    @media (max-width: 680px) {{ .cards-grid {{ grid-template-columns: 1fr; }} }}

    /* ─── News Card ─── */
    .news-card {{
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--radius); overflow: hidden;
      box-shadow: var(--shadow-sm);
      transition: box-shadow 0.2s, transform 0.2s;
      display: flex; flex-direction: column;
    }}
    .news-card:hover {{ box-shadow: var(--shadow-md); transform: translateY(-3px); }}

    .card-accent {{ height: 4px; width: 100%; }}
    .accent-red    {{ background: linear-gradient(90deg, #E53E3E, #FC8181); }}
    .accent-blue   {{ background: linear-gradient(90deg, #2B6CB0, #63B3ED); }}
    .accent-green  {{ background: linear-gradient(90deg, #276749, #68D391); }}
    .accent-amber  {{ background: linear-gradient(90deg, #D69E2E, #F6AD55); }}
    .accent-purple {{ background: linear-gradient(90deg, #6B46C1, #9F7AEA); }}
    .accent-teal   {{ background: linear-gradient(90deg, #2C7A7B, #4FD1C5); }}

    .card-body {{ padding: 1.25rem 1.25rem 1rem; flex: 1; display: flex; flex-direction: column; }}
    .card-title {{ font-size: 15.5px; font-weight: 700; color: var(--ink); line-height: 1.5; margin-bottom: 12px; letter-spacing: -0.1px; }}

    .sources-row {{ display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 14px; }}
    .source-tag {{
      display: inline-flex; align-items: center; gap: 4px;
      padding: 3px 10px; background: #F1F5F9; color: #334155;
      border: 1px solid #E2E8F0; border-radius: 6px;
      font-size: 11px; font-weight: 600; text-decoration: none;
      transition: background 0.15s, border-color 0.15s;
    }}
    .source-tag::before {{ content: '↗'; font-size: 9px; color: var(--faint); }}
    .source-tag:hover {{ background: #E2E8F0; border-color: #CBD5E0; }}

    .summary {{
      font-size: 13.5px; color: #4A5568; line-height: 1.7;
      margin-bottom: 16px; padding: 12px 14px;
      background: #F8FAFC; border-radius: 8px; border: 1px solid #EDF2F7;
    }}

    /* ─── Insight Panel ─── */
    .insight-panel {{ border: 1px solid var(--border); border-radius: 10px; overflow: hidden; margin-top: auto; }}
    .insight-row {{ display: grid; grid-template-columns: 80px 1fr; border-bottom: 1px solid var(--border); }}
    .insight-row:last-child {{ border-bottom: none; }}
    .insight-label {{
      font-size: 10px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;
      color: var(--faint); padding: 10px 12px; background: #FAFBFC;
      display: flex; align-items: flex-start;
      border-right: 1px solid var(--border); line-height: 1.4;
    }}
    .insight-value {{ font-size: 12.5px; color: var(--ink-2); line-height: 1.6; padding: 10px 12px; }}

    .title-row .insight-label {{ background: #FFFBEB; color: #92400E; border-right-color: #FDE68A; }}
    .title-row .insight-value {{ background: #FFFBEB; font-weight: 700; color: #78350F; }}
    .local-row .insight-label {{ background: #F0FFF4; color: #276749; border-right-color: #C6F6D5; }}
    .local-row .insight-value {{ background: #F0FFF4; color: #22543D; font-size: 12px; }}
    .stock-row .insight-label {{ background: #EBF8FF; color: #2B6CB0; border-right-color: #BEE3F8; }}
    .stock-row .insight-value {{ background: #EBF8FF; color: #1A365D; }}
    .invest-row .insight-label {{ background: #FAF5FF; color: #6B46C1; border-right-color: #D6BCFA; }}
    .invest-row .insight-value {{ background: #FAF5FF; color: #44337A; }}

    /* ─── Empty State ─── */
    .empty-state {{ text-align: center; padding: 5rem 2rem; color: var(--muted); }}
    .empty-icon  {{ font-size: 3rem; margin-bottom: 1rem; }}
    .empty-title {{ font-size: 1.1rem; font-weight: 700; color: var(--ink-2); margin-bottom: 0.5rem; }}
    .empty-desc  {{ font-size: 0.875rem; }}

    /* ─── Footer ─── */
    .site-footer {{
      background: var(--surface); border-top: 1px solid var(--border);
      padding: 14px 2rem; display: flex;
      justify-content: space-between; align-items: center;
      font-size: 11px; color: var(--faint); font-weight: 500;
    }}
    .footer-dot {{ width: 4px; height: 4px; border-radius: 50%; background: var(--faint); display: inline-block; margin: 0 8px; vertical-align: middle; }}
  </style>
</head>
<body>

  <div id="progress"></div>

  <header class="site-header">
    <div class="header-left">
      <div class="header-logo" id="hdr-logo">🤖</div>
      <div>
        <div class="header-brand" id="hdr-brand">AI 日報</div>
        <div class="header-sub" id="hdr-sub">{niche} · 為中文自媒體選題整理</div>
      </div>
    </div>
    <div class="header-right">
      <div class="header-date" id="hdr-date">{latest_ai_date}</div>
      <div class="header-count" id="hdr-count">共 {latest_ai_total} 則情報</div>
    </div>
  </header>

  <nav class="channel-nav">
    <button class="channel-tab active" data-channel="ai"
            data-logo="🤖" data-brand="AI 日報"
            data-sub="{niche} · 為中文自媒體選題整理">🤖 AI 日報</button>
    <button class="channel-tab" data-channel="finance"
            data-logo="💹" data-brand="財經新聞"
            data-sub="市場動態 · 台灣投資人視角">💹 財經新聞</button>
  </nav>

  <nav class="date-nav">
    <span class="date-nav-label">日期</span>
    <div class="date-tabs-group" id="ai-date-tabs">
      {ai_tabs}
    </div>
    <div class="date-tabs-group" id="finance-date-tabs" style="display:none">
      {fin_tabs}
    </div>
  </nav>

  <main class="container">
    <div id="ai-content">
      {ai_panels}
    </div>
    <div id="finance-content" style="display:none">
      {fin_panels}
    </div>
  </main>

  <footer class="site-footer">
    <span>由 AutoGenAI 自動生成<span class="footer-dot"></span><span id="gen-time"></span></span>
    <span id="footer-label">{niche}</span>
  </footer>

  <script>
    document.getElementById('gen-time').textContent =
      '生成於 ' + new Date().toLocaleString('zh-TW', {{hour:'2-digit', minute:'2-digit'}});

    window.addEventListener('scroll', () => {{
      const pct = window.scrollY / (document.body.scrollHeight - window.innerHeight) * 100;
      document.getElementById('progress').style.width = Math.min(pct, 100) + '%';
    }});

    const hdrLogo  = document.getElementById('hdr-logo');
    const hdrBrand = document.getElementById('hdr-brand');
    const hdrSub   = document.getElementById('hdr-sub');
    const hdrDate  = document.getElementById('hdr-date');
    const hdrCount = document.getElementById('hdr-count');
    const footerLabel = document.getElementById('footer-label');

    function retriggerAnim(container) {{
      container.querySelectorAll('.report-section').forEach(s => {{
        s.style.animation = 'none'; s.offsetHeight; s.style.animation = '';
      }});
    }}

    function updateHeaderFromPanel(panel) {{
      if (!panel) return;
      hdrDate.textContent  = panel.dataset.date;
      hdrCount.textContent = '共 ' + panel.dataset.total + ' 則情報';
    }}

    // ── channel switching ──
    document.querySelectorAll('.channel-tab').forEach(tab => {{
      tab.addEventListener('click', () => {{
        const ch = tab.dataset.channel;
        document.querySelectorAll('.channel-tab').forEach(t => t.classList.toggle('active', t.dataset.channel === ch));

        document.getElementById('ai-date-tabs').style.display      = ch === 'ai'      ? '' : 'none';
        document.getElementById('finance-date-tabs').style.display = ch === 'finance' ? '' : 'none';
        document.getElementById('ai-content').style.display        = ch === 'ai'      ? '' : 'none';
        document.getElementById('finance-content').style.display   = ch === 'finance' ? '' : 'none';

        hdrLogo.textContent  = tab.dataset.logo;
        hdrBrand.textContent = tab.dataset.brand;
        hdrSub.textContent   = tab.dataset.sub;
        footerLabel.textContent = tab.dataset.sub.split(' · ')[0];

        const activePanel = document.querySelector(`#${{ch}}-content .day-panel.active`);
        if (activePanel) retriggerAnim(activePanel);
        updateHeaderFromPanel(activePanel);
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }});
    }});

    // ── date tab switching ──
    document.querySelectorAll('.date-tab').forEach(tab => {{
      tab.addEventListener('click', () => {{
        const ch       = tab.dataset.channel;
        const targetId = tab.dataset.target;

        document.querySelectorAll(`#${{ch}}-date-tabs .date-tab`).forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        document.querySelectorAll(`#${{ch}}-content .day-panel`).forEach(p => p.classList.remove('active'));
        const target = document.getElementById(targetId);
        if (target) {{
          target.classList.add('active');
          retriggerAnim(target);
          updateHeaderFromPanel(target);
        }}
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }});
    }});
  </script>
</body>
</html>
"""

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(final_html)
    index_path = os.path.join(BASE_DIR, "index.html")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"HTML rendered — AI: {len(ai_archive)} date(s), Finance: {len(finance_archive)} date(s).")

if __name__ == "__main__":
    render_html()
