#!/usr/bin/env python3
"""Fetch stock prices from Yahoo Finance (server-side, no CORS issue)."""
import json, time, sys
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError

SYMBOLS = {
    '2330.TW': '台積電',
    '2454.TW': '聯發科',
    '2317.TW': '鴻海',
    '0050.TW': '元大台灣50',
    '0056.TW': '元大高股息',
    'NVDA':    '輝達',
    'AAPL':    '蘋果',
    'MSFT':    '微軟',
    'VOO':     'Vanguard S&P500',
    'QQQ':     'Invesco QQQ',
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'application/json',
}

def fetch(symbol):
    # range 必須用 1d：range=5d 時 chartPreviousClose 是「5 天前」的收盤價，
    # 算出來的漲跌幅會變成一週漲幅（曾造成聯發科顯示 +11.98%，超過台股 10% 漲停上限）
    url = (
        f'https://query2.finance.yahoo.com/v8/finance/chart/{symbol}'
        '?interval=1d&range=1d'
    )
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        r = data['chart']['result'][0]
        m = r['meta']
        price = m.get('regularMarketPrice') or m.get('previousClose', 0)
        prev  = m.get('chartPreviousClose') or m.get('previousClose', price)
        change = price - prev
        pct    = (change / prev * 100) if prev else 0
        return {
            'price':    round(float(price),  2),
            'change':   round(float(change), 2),
            'pct':      round(float(pct),    2),
            'prev':     round(float(prev),   2),
            'currency': m.get('currency', ''),
            'state':    m.get('marketState', 'CLOSED'),
        }
    except Exception as e:
        print(f'  FAIL {symbol}: {e}', file=sys.stderr)
        return None

output = {
    'updated': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    'data': {}
}

ok = 0
for sym, name in SYMBOLS.items():
    result = fetch(sym)
    if result:
        result['name'] = name
        output['data'][sym] = result
        sign = '+' if result['change'] >= 0 else ''
        print(f'  OK  {sym:12s}  {result["price"]:>10.2f}  {sign}{result["change"]:.2f} ({sign}{result["pct"]:.2f}%)')
        ok += 1
    else:
        print(f'  ERR {sym}')
    time.sleep(0.3)   # gentle rate limiting

print(f'\n{ok}/{len(SYMBOLS)} symbols fetched  ({output["updated"]})')

out_path = 'v3/stocks.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f'Written → {out_path}')
