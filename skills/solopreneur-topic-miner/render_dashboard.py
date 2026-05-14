#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime

BASE_DIR    = "/Users/mac/projects/AutoGenAI"
SKILL_DIR   = os.path.join(BASE_DIR, "skills/solopreneur-topic-miner")
HTML_PATH   = os.path.join(BASE_DIR, "daily_topic_dashboard.html")
PROFILE_PATH= os.path.join(SKILL_DIR, "user_profile.json")
TOPICS_PATH = os.path.join(SKILL_DIR, "latest_topics.json")
ARCHIVE_PATH= os.path.join(SKILL_DIR, "topics_archive.json")

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

def update_archive():
    """Merge latest_topics.json into the archive, keep only the 7 most recent dates."""
    latest  = load_json(TOPICS_PATH, {})
    archive = load_json(ARCHIVE_PATH, [])
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
    archive = archive[:7]   # keep only the 7 most recent dates
    save_json(ARCHIVE_PATH, archive)
    return archive

# ── card / section renderers ──────────────────────────────────────────────

def render_sources(sources):
    links = []
    for s in sources:
        name = s.get('name', '')
        url  = s.get('url', '#')
        links.append(f'<a href="{url}" target="_blank" class="source-tag">{name}</a>')
    return ''.join(links)

def render_card(item, accent_class):
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
          <div class="insight-row">
            <span class="insight-label">目標受眾</span>
            <span class="insight-value">{audience}</span>
          </div>
          <div class="insight-row">
            <span class="insight-label">痛點</span>
            <span class="insight-value">{pain_point}</span>
          </div>
          <div class="insight-row title-row">
            <span class="insight-label">標題雛形</span>
            <span class="insight-value">{title_idea}</span>
          </div>
          <div class="insight-row local-row">
            <span class="insight-label">本地化切角</span>
            <span class="insight-value">{local_angle}</span>
          </div>
        </div>
      </div>
    </div>"""

def render_section(label, dot_class, label_class, count_class, accent_class, items):
    if not items:
        return ''
    cards = '\n'.join([render_card(item, accent_class) for item in items])
    count = len(items)
    return f"""<section class="report-section">
  <div class="section-header">
    <span class="section-dot {dot_class}"></span>
    <span class="section-label {label_class}">{label}</span>
    <span class="section-count {count_class}">{count} 則</span>
    <span class="section-line"></span>
  </div>
  <div class="cards-grid">
    {cards}
  </div>
</section>"""

def render_day_panel(entry, is_active):
    date_str     = entry.get('date', '')
    big_events   = entry.get('big_events', [])
    tool_updates = entry.get('tool_updates', [])
    trends       = entry.get('trends', [])
    total        = len(big_events) + len(tool_updates) + len(trends)

    be_html  = render_section('大事件',         'dot-red',   'label-red',   'count-red',   'accent-red',   big_events)
    tu_html  = render_section('工具更新',       'dot-blue',  'label-blue',  'count-blue',  'accent-blue',  tool_updates)
    tr_html  = render_section('值得追蹤的趨勢', 'dot-green', 'label-green', 'count-green', 'accent-green', trends)

    active_cls = 'active' if is_active else ''
    panel_id   = f"day-{date_str}"

    return f"""<div id="{panel_id}" class="day-panel {active_cls}" data-date="{date_str}" data-total="{total}">
  {be_html}
  {tu_html}
  {tr_html}
</div>"""

# ── main render ───────────────────────────────────────────────────────────

def render_html():
    profile = load_json(PROFILE_PATH, {"niche": "AI 效率工具", "target_audience": "職場上班族"})
    niche   = profile.get('track', profile.get('niche', 'AI 效率工具'))

    archive = update_archive()
    if not archive:
        print("No data found in archive.")
        return

    latest_date  = archive[0].get('date', '')
    latest_total = sum(len(archive[0].get(k, [])) for k in ('big_events','tool_updates','trends'))

    # Build date tabs
    tabs_html = ''
    for i, entry in enumerate(archive):
        d      = entry.get('date', '')
        label  = d[5:]  # MM-DD
        active = 'active' if i == 0 else ''
        tabs_html += f'<button class="date-tab {active}" data-target="day-{d}" data-date="{d}">{label}</button>\n'

    # Build day panels
    panels_html = '\n'.join(render_day_panel(entry, i == 0) for i, entry in enumerate(archive))

    final_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI 日報</title>
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
      background: #0D1117;
      color: #fff;
      padding: 0 2rem;
      height: var(--header-h);
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 200;
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
    }}
    .header-brand {{ font-size: 16px; font-weight: 800; letter-spacing: -0.3px; }}
    .header-sub   {{ font-size: 11px; color: #6B7280; margin-top: 1px; font-weight: 500; }}
    .header-right {{ text-align: right; }}
    .header-date  {{ font-size: 13px; font-weight: 700; color: #E5E7EB; letter-spacing: 0.2px; }}
    .header-count {{
      display: inline-block; margin-top: 2px;
      font-size: 10px; font-weight: 600; color: #374151;
      background: rgba(255,255,255,0.08);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 99px; padding: 1px 8px;
      letter-spacing: 0.3px;
    }}

    /* ─── Date Tab Bar ─── */
    .date-nav {{
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      height: var(--tabs-h);
      display: flex;
      align-items: center;
      padding: 0 2rem;
      gap: 6px;
      position: sticky;
      top: var(--header-h);
      z-index: 100;
      overflow-x: auto;
      scrollbar-width: none;
    }}
    .date-nav::-webkit-scrollbar {{ display: none; }}

    .date-nav-label {{
      font-size: 11px;
      font-weight: 700;
      color: var(--faint);
      letter-spacing: 0.5px;
      text-transform: uppercase;
      white-space: nowrap;
      margin-right: 4px;
    }}

    .date-tab {{
      flex-shrink: 0;
      padding: 5px 14px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: transparent;
      color: var(--muted);
      font-family: inherit;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
      white-space: nowrap;
    }}
    .date-tab:hover {{
      background: var(--page);
      color: var(--ink);
      border-color: #CBD5E0;
    }}
    .date-tab.active {{
      background: var(--ink);
      color: #fff;
      border-color: var(--ink);
    }}

    /* ─── Layout ─── */
    .container {{ max-width: 1020px; margin: 0 auto; padding: 2.5rem 1.5rem 5rem; }}

    /* ─── Day Panels ─── */
    .day-panel {{ display: none; }}
    .day-panel.active {{ display: block; }}

    /* ─── Section ─── */
    .report-section {{ margin-bottom: 3rem; }}
    .report-section {{
      opacity: 0;
      transform: translateY(10px);
      animation: fadeUp 0.35s ease forwards;
    }}
    .report-section:nth-child(1) {{ animation-delay: 0.04s; }}
    .report-section:nth-child(2) {{ animation-delay: 0.12s; }}
    .report-section:nth-child(3) {{ animation-delay: 0.20s; }}
    @keyframes fadeUp {{
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    .section-header {{
      display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem;
    }}
    .section-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
    .dot-red   {{ background: var(--red);   box-shadow: 0 0 0 3px #FED7D7; }}
    .dot-blue  {{ background: var(--blue);  box-shadow: 0 0 0 3px #BEE3F8; }}
    .dot-green {{ background: var(--green); box-shadow: 0 0 0 3px #C6F6D5; }}

    .section-label {{
      font-size: 13px; font-weight: 800;
      letter-spacing: 0.8px; text-transform: uppercase;
    }}
    .label-red   {{ color: var(--red); }}
    .label-blue  {{ color: var(--blue); }}
    .label-green {{ color: var(--green); }}

    .section-count {{
      font-size: 11px; font-weight: 600;
      padding: 2px 10px; border-radius: 99px; margin-left: 2px;
    }}
    .count-red   {{ background: var(--red-bg);   color: var(--red);   border: 1px solid var(--red-border); }}
    .count-blue  {{ background: var(--blue-bg);  color: var(--blue);  border: 1px solid var(--blue-border); }}
    .count-green {{ background: var(--green-bg); color: var(--green); border: 1px solid var(--green-border); }}

    .section-line {{ flex: 1; height: 1px; background: var(--border); }}

    /* ─── Cards Grid ─── */
    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(460px, 1fr));
      gap: 1.25rem;
    }}
    @media (max-width: 680px) {{ .cards-grid {{ grid-template-columns: 1fr; }} }}

    /* ─── News Card ─── */
    .news-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
      box-shadow: var(--shadow-sm);
      transition: box-shadow 0.2s, transform 0.2s;
      display: flex; flex-direction: column;
    }}
    .news-card:hover {{ box-shadow: var(--shadow-md); transform: translateY(-3px); }}

    .card-accent {{ height: 4px; width: 100%; }}
    .accent-red   {{ background: linear-gradient(90deg, #E53E3E, #FC8181); }}
    .accent-blue  {{ background: linear-gradient(90deg, #2B6CB0, #63B3ED); }}
    .accent-green {{ background: linear-gradient(90deg, #276749, #68D391); }}

    .card-body {{ padding: 1.25rem 1.25rem 1rem; flex: 1; display: flex; flex-direction: column; }}

    .card-title {{
      font-size: 15.5px; font-weight: 700; color: var(--ink);
      line-height: 1.5; margin-bottom: 12px; letter-spacing: -0.1px;
    }}

    /* ─── Source Tags ─── */
    .sources-row {{ display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 14px; }}
    .source-tag {{
      display: inline-flex; align-items: center; gap: 4px;
      padding: 3px 10px;
      background: #F1F5F9; color: #334155; border: 1px solid #E2E8F0;
      border-radius: 6px; font-size: 11px; font-weight: 600;
      text-decoration: none; transition: background 0.15s, border-color 0.15s;
    }}
    .source-tag::before {{ content: '↗'; font-size: 9px; color: var(--faint); }}
    .source-tag:hover {{ background: #E2E8F0; border-color: #CBD5E0; }}

    /* ─── Summary ─── */
    .summary {{
      font-size: 13.5px; color: #4A5568; line-height: 1.7;
      margin-bottom: 16px; padding: 12px 14px;
      background: #F8FAFC; border-radius: 8px; border: 1px solid #EDF2F7;
    }}

    /* ─── Insight Panel ─── */
    .insight-panel {{
      border: 1px solid var(--border); border-radius: 10px;
      overflow: hidden; margin-top: auto;
    }}
    .insight-row {{
      display: grid; grid-template-columns: 80px 1fr;
      border-bottom: 1px solid var(--border);
    }}
    .insight-row:last-child {{ border-bottom: none; }}

    .insight-label {{
      font-size: 10px; font-weight: 700;
      letter-spacing: 0.5px; text-transform: uppercase;
      color: var(--faint); padding: 10px 12px;
      background: #FAFBFC;
      display: flex; align-items: flex-start;
      border-right: 1px solid var(--border); line-height: 1.4;
    }}
    .insight-value {{
      font-size: 12.5px; color: var(--ink-2); line-height: 1.6; padding: 10px 12px;
    }}

    .title-row .insight-label {{ background: #FFFBEB; color: #92400E; border-right-color: #FDE68A; }}
    .title-row .insight-value {{ background: #FFFBEB; font-weight: 700; color: #78350F; }}

    .local-row .insight-label {{ background: #F0FFF4; color: #276749; border-right-color: #C6F6D5; }}
    .local-row .insight-value {{ background: #F0FFF4; color: #22543D; font-size: 12px; }}

    /* ─── Footer ─── */
    .site-footer {{
      background: var(--surface); border-top: 1px solid var(--border);
      padding: 14px 2rem; display: flex;
      justify-content: space-between; align-items: center;
      font-size: 11px; color: var(--faint); font-weight: 500;
    }}
    .footer-dot {{
      width: 4px; height: 4px; border-radius: 50%;
      background: var(--faint); display: inline-block;
      margin: 0 8px; vertical-align: middle;
    }}
  </style>
</head>
<body>

  <div id="progress"></div>

  <header class="site-header">
    <div class="header-left">
      <div class="header-logo">🤖</div>
      <div>
        <div class="header-brand">AI 日報</div>
        <div class="header-sub">{niche} · 為中文自媒體選題整理</div>
      </div>
    </div>
    <div class="header-right">
      <div class="header-date" id="hdr-date">{latest_date}</div>
      <div class="header-count" id="hdr-count">共 {latest_total} 則情報</div>
    </div>
  </header>

  <nav class="date-nav">
    <span class="date-nav-label">日期</span>
    {tabs_html}
  </nav>

  <main class="container">
    {panels_html}
  </main>

  <footer class="site-footer">
    <span>由 solopreneur-topic-miner 自動生成<span class="footer-dot"></span><span id="gen-time"></span></span>
    <span>{niche}</span>
  </footer>

  <script>
    // ── init ──
    document.getElementById('gen-time').textContent =
      '生成於 ' + new Date().toLocaleString('zh-TW', {{hour:'2-digit', minute:'2-digit'}});

    // ── scroll progress ──
    window.addEventListener('scroll', () => {{
      const el  = document.getElementById('progress');
      const pct = window.scrollY / (document.body.scrollHeight - window.innerHeight) * 100;
      el.style.width = Math.min(pct, 100) + '%';
    }});

    // ── date tab switching ──
    const tabs   = document.querySelectorAll('.date-tab');
    const panels = document.querySelectorAll('.day-panel');
    const hdrDate  = document.getElementById('hdr-date');
    const hdrCount = document.getElementById('hdr-count');

    function switchTo(tab) {{
      tabs.forEach(t => t.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      const target = document.getElementById(tab.dataset.target);
      if (target) {{
        target.classList.add('active');
        // retrigger section animations
        target.querySelectorAll('.report-section').forEach(s => {{
          s.style.animation = 'none';
          s.offsetHeight;   // reflow
          s.style.animation = '';
        }});
        hdrDate.textContent  = target.dataset.date;
        hdrCount.textContent = '共 ' + target.dataset.total + ' 則情報';
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }}
    }}

    tabs.forEach(tab => {{
      tab.addEventListener('click', () => switchTo(tab));
    }});
  </script>
</body>
</html>
"""
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(final_html)
    # also write index.html so GitHub Pages serves a clean URL
    index_path = os.path.join(BASE_DIR, "index.html")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"HTML Dashboard rendered — {len(archive)} date(s) in archive.")

if __name__ == "__main__":
    render_html()
