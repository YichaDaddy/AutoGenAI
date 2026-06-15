#!/usr/bin/env python3
"""Fetch Strava runs + 竹北當日天氣 → v3/marathon.json（馬拉松月曆 A 版資料源）。

需要環境變數（放 GitHub Secrets）：
  STRAVA_CLIENT_ID / STRAVA_CLIENT_SECRET / STRAVA_REFRESH_TOKEN
天氣用 Open-Meteo（免費、免金鑰），座標取每筆活動的 GPS 起點，無 GPS 時退回竹北。
輸出結構與 v3/index.html 內建的 RUNS_FALLBACK 一致，前端 fetch 後直接渲染。
"""
import os, sys, json, urllib.request, urllib.parse, datetime

CID = os.environ.get('STRAVA_CLIENT_ID')
CSEC = os.environ.get('STRAVA_CLIENT_SECRET')
RT = os.environ.get('STRAVA_REFRESH_TOKEN')
N_RUNS = 14          # 納入最近幾筆跑步（足夠涵蓋月曆顯示）
SAMPLES = 30         # 每筆 streams 降採樣點數
ZHUBEI = [24.83, 121.01]
OUT = os.path.join(os.path.dirname(__file__), '..', 'v3', 'marathon.json')
LABEL = {'hills': '坡度課', 'interval': '間歇', 'long': '長距離', 'aerobic': '有氧'}


def die(msg):
    print(msg)
    sys.exit(1)


def http_json(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def get_token():
    body = urllib.parse.urlencode({
        'client_id': CID, 'client_secret': CSEC,
        'grant_type': 'refresh_token', 'refresh_token': RT,
    }).encode()
    return http_json('https://www.strava.com/oauth/token', data=body)['access_token']


def sapi(tok, path, params=None):
    url = 'https://www.strava.com/api/v3' + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    return http_json(url, headers={'Authorization': 'Bearer ' + tok})


def downsample(a, n):
    if not a:
        return []
    if len(a) <= n:
        return [round(x, 2) if isinstance(x, float) else x for x in a]
    out = []
    for i in range(n):
        idx = round(i * (len(a) - 1) / (n - 1))
        x = a[idx]
        out.append(round(x, 2) if isinstance(x, (int, float)) else x)
    return out


def weather(lat, lon, dt_local):
    days_ago = (datetime.date.today() - dt_local.date()).days
    past = min(92, max(1, days_ago + 1))
    url = 'https://api.open-meteo.com/v1/forecast?' + urllib.parse.urlencode({
        'latitude': round(lat, 3), 'longitude': round(lon, 3),
        'hourly': 'temperature_2m,relative_humidity_2m,apparent_temperature',
        'past_days': past, 'forecast_days': 1, 'timezone': 'Asia/Taipei',
    })
    try:
        d = http_json(url)
        h = d['hourly']
        i = h['time'].index(dt_local.strftime('%Y-%m-%dT%H:00'))
        return {'t': round(h['temperature_2m'][i], 1),
                'rh': round(h['relative_humidity_2m'][i]),
                'feel': round(h['apparent_temperature'][i], 1)}
    except Exception as e:
        print('weather miss %s: %s' % (dt_local.date(), e))
        return None


def classify(km, elev, vel):
    moving = [v for v in vel if v and v > 0.5]
    spread = (max(moving) - min(moving)) if moving else 0
    if elev >= 150:
        return 'hills'
    if spread >= 2.2 and km < 12:
        return 'interval'
    if km >= 15:
        return 'long'
    return 'aerobic'


def make_meta(km, typ, wx, ahr, mhr, elev):
    hot = bool(wx) and wx.get('feel', 0) >= 27
    kmr = round(km, 1)
    if typ == 'long':
        badge = ['heat', '🔥 熱天長跑'] if hot else ['good', '⭐ 長距離']
    elif typ == 'interval':
        badge = ['gold', '⚡ 速度課']
    elif typ == 'hills':
        badge = ['gold', '⛰️ 坡度課 +%dm' % round(elev)]
    else:
        badge = ['heat', '🔥 熱天有氧'] if hot else ['good', '✅ 輕鬆達標']
    name = '%sK %s' % (kmr, LABEL[typ])
    if wx:
        base = '%s°C、濕%d%%（體感 %s°C）下完成 %sK' % (wx['t'], wx['rh'], wx['feel'], kmr)
    else:
        base = '完成 %sK' % kmr
    if typ == 'long':
        ev = base + '。' + ('熱天能撐完已是硬仗，換算到涼天更有料。' if hot else '心率穩定、有氧效率漂亮，是破四的本錢。')
    elif typ == 'interval':
        ev = base + '。間歇刺激保留腿部彈性與跑步經濟性，最大心率 %d。' % mhr
    elif typ == 'hills':
        ev = base + '、爬升 %dm。坡度課練的是馬拉松後段腿力，對破四很有幫助。' % round(elev)
    else:
        ev = base + '。' + ('高溫高濕下請改看「跑滿時間」、別追配速。' if hot else '輕鬆日把心率壓低，替品質日存本錢。')
    return name, badge, ev


def main():
    if not (CID and CSEC and RT):
        die('Missing STRAVA_CLIENT_ID / STRAVA_CLIENT_SECRET / STRAVA_REFRESH_TOKEN')
    tok = get_token()
    acts = sapi(tok, '/athlete/activities', {'per_page': 40})
    runs = {}
    for a in acts:
        if len(runs) >= N_RUNS:
            break
        if a.get('type') != 'Run' or a.get('distance', 0) < 1500:
            continue
        aid = a['id']
        try:
            st = sapi(tok, '/activities/%d/streams' % aid,
                      {'keys': 'distance,heartrate,velocity_smooth,altitude',
                       'key_by_type': 'true', 'resolution': 'medium'})
        except Exception as e:
            print('streams miss %d: %s' % (aid, e))
            continue
        if 'heartrate' not in st:
            continue
        hr = st['heartrate']['data']
        d = st['distance']['data']
        v = st.get('velocity_smooth', {}).get('data', []) or []
        alt = st.get('altitude', {}).get('data', []) or []
        v = [x or 0 for x in v]
        if v and v[0] == 0 and len(v) > 1:
            v[0] = v[1]
        dl = datetime.datetime.fromisoformat(a['start_date_local'].replace('Z', ''))
        key = dl.strftime('%Y-%m-%d')
        ll = a.get('start_latlng') or ZHUBEI
        wx = weather(ll[0], ll[1], dl)
        km = a['distance'] / 1000.0
        elev = a.get('total_elevation_gain', 0) or 0
        ahr = round(a.get('average_heartrate') or (sum(hr) / len(hr)))
        mhr = round(a.get('max_heartrate') or max(hr))
        typ = classify(km, elev, v)
        name, badge, ev = make_meta(km, typ, wx, ahr, mhr, elev)
        runs[key] = {
            'name': name, 'km': round(km, 1), 'mov': a['moving_time'],
            'ahr': ahr, 'mhr': mhr, 'cad': round(a.get('average_cadence') or 0),
            'elev': round(elev),
            'wx': wx or {'t': None, 'rh': None, 'feel': 0},
            'badge': badge, 'ev': ev,
            'hr': downsample(hr, SAMPLES), 'd': downsample(d, SAMPLES),
            'v': downsample(v, SAMPLES), 'alt': downsample(alt, SAMPLES),
        }
    out = {'generated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
           'runs': runs}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    print('Wrote %d runs to %s' % (len(runs), os.path.relpath(OUT)))


if __name__ == '__main__':
    main()
