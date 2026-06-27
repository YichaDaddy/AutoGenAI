#!/usr/bin/env python3
"""Fetch Strava runs + 竹北當日天氣 → v3/marathon.json（馬拉松月曆 A 版資料源）。

需要環境變數（放 GitHub Secrets）：
  STRAVA_CLIENT_ID / STRAVA_CLIENT_SECRET / STRAVA_REFRESH_TOKEN
天氣用 Open-Meteo（免費、免金鑰），座標取每筆活動的 GPS 起點，無 GPS 時退回竹北。
輸出結構與 v3/index.html 內建的 RUNS_FALLBACK 一致，前端 fetch 後直接渲染。
"""
import os, sys, json, time, urllib.request, urllib.parse, urllib.error, datetime

CID = os.environ.get('STRAVA_CLIENT_ID')
CSEC = os.environ.get('STRAVA_CLIENT_SECRET')
RT = os.environ.get('STRAVA_REFRESH_TOKEN')
N_RUNS = 14          # 納入最近幾筆跑步（足夠涵蓋月曆顯示）
SAMPLES = 30         # 每筆 streams 降採樣點數
ZHUBEI = [24.83, 121.01]
OUT = os.path.join(os.path.dirname(__file__), '..', 'v3', 'marathon.json')
LABEL = {'hills': '坡度課', 'interval': '間歇', 'long': '長距離', 'aerobic': '有氧'}
SUB4_PACE = 341  # Sub-4 目標均配 5:41/km = 341 sec/km
ZB = [120, 149, 164, 178]  # 心率區間邊界，與前端一致
ZNM = ['Z1 恢復', 'Z2 有氧', 'Z3 節奏', 'Z4 閾值', 'Z5 最大']


def die(msg):
    print(msg)
    sys.exit(1)


def http_json(url, data=None, headers=None, retries=3):
    """GET/POST JSON，遇 Strava 瞬斷（403/429/5xx）或網路錯誤自動重試＋退避。"""
    short = url.split('?')[0]
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=headers or {})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429, 500, 502, 503, 504) and attempt < retries:
                wait = 4 * (attempt + 1)
                print('HTTP %d on %s → %ds 後重試 (%d/%d)' % (e.code, short, wait, attempt + 1, retries))
                time.sleep(wait)
                continue
            raise
        except urllib.error.URLError as e:
            if attempt < retries:
                wait = 4 * (attempt + 1)
                print('連線錯誤 %s on %s → %ds 後重試 (%d/%d)' % (e, short, wait, attempt + 1, retries))
                time.sleep(wait)
                continue
            raise


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


def pace_fmt(sec_per_km):
    m, s = divmod(round(sec_per_km), 60)
    return '%d:%02d' % (m, s)


def analyze(hr_full, d_full, v_full, alt_full, mov, km, cad_avg):
    """用完整 streams 計算分析指標。"""
    n = len(hr_full)
    # — 心率區間分布 —
    zc = [0] * 5
    for h in hr_full:
        z = 4
        for k in range(4):
            if h <= ZB[k]:
                z = k
                break
        zc[z] += 1
    zpct = [round(c / n * 100, 1) if n else 0 for c in zc]

    # — 心率脫鉤（前後半距離） —
    dc = None
    if d_full and len(d_full) == n and n > 10:
        half_d = d_full[-1] / 2
        h1, c1, h2, c2 = 0, 0, 0, 0
        for i in range(n):
            if d_full[i] <= half_d:
                h1 += hr_full[i]; c1 += 1
            else:
                h2 += hr_full[i]; c2 += 1
        if c1 and c2:
            avg1, avg2 = h1 / c1, h2 / c2
            dc = round((avg2 - avg1) / avg1 * 100, 1)

    # — 配速穩定度（速度 CV） —
    moving_v = [x for x in v_full if x and x > 0.5]
    pace_cv = None
    if moving_v and len(moving_v) > 10:
        mean_v = sum(moving_v) / len(moving_v)
        var_v = sum((x - mean_v) ** 2 for x in moving_v) / len(moving_v)
        pace_cv = round((var_v ** 0.5) / mean_v * 100, 1)

    # — GAP（坡度校正配速） —
    gap = None
    if alt_full and d_full and len(alt_full) == n and len(d_full) == n:
        eq_d = 0
        for i in range(1, n):
            dd = d_full[i] - d_full[i - 1]
            if dd <= 0:
                continue
            grade = (alt_full[i] - alt_full[i - 1]) / dd
            c = 1 + 3.6 * grade
            c = max(0.78, min(1.5, c))
            eq_d += dd * c
        if eq_d > 0:
            gap = round(mov / (eq_d / 1000), 1)

    # — 涼天換算配速 —
    pace = mov / km if km > 0 else 0
    cool_pace = None
    feel = 0  # will be set later from wx

    # — 前後半配速比較 —
    split_delta = None
    if d_full and v_full and len(d_full) == n and len(v_full) == n and n > 10:
        half_d = d_full[-1] / 2
        v1, c1, v2, c2 = 0, 0, 0, 0
        for i in range(n):
            if v_full[i] and v_full[i] > 0.5:
                if d_full[i] <= half_d:
                    v1 += v_full[i]; c1 += 1
                else:
                    v2 += v_full[i]; c2 += 1
        if c1 and c2:
            avg_v1, avg_v2 = v1 / c1, v2 / c2
            split_delta = round((avg_v2 - avg_v1) / avg_v1 * 100, 1)

    # — 步頻（Strava cadence 是半步，*2 = spm） —
    spm = round(cad_avg * 2) if cad_avg else 0

    return {
        'zpct': zpct, 'dc': dc, 'pace_cv': pace_cv, 'gap': gap,
        'split_delta': split_delta, 'spm': spm, 'pace': round(pace, 1),
    }


def make_meta(km, typ, wx, ahr, mhr, elev, stats):
    hot = bool(wx) and wx.get('feel', 0) >= 27
    kmr = round(km, 1)
    feel = wx.get('feel', 0) if wx else 0

    # — 涼天換算 —
    pace = stats['pace']
    cool_pace = round(pace / (1 + 0.005 * max(0, feel - 15)), 1) if feel > 15 else pace
    stats['cool_pace'] = cool_pace

    # — badge —
    if typ == 'long':
        badge = ['heat', '🔥 熱天長跑'] if hot else ['good', '⭐ 長距離']
    elif typ == 'interval':
        badge = ['gold', '⚡ 速度課']
    elif typ == 'hills':
        badge = ['gold', '⛰️ 坡度課 +%dm' % round(elev)]
    else:
        badge = ['heat', '🔥 熱天有氧'] if hot else ['good', '✅ 輕鬆達標']
    name = '%sK %s' % (kmr, LABEL[typ])

    # — 數據驅動評價 —
    zpct = stats['zpct']
    dc = stats['dc']
    spm = stats['spm']
    pace_cv = stats['pace_cv']
    gap = stats['gap']
    split_delta = stats['split_delta']
    z12 = zpct[0] + zpct[1]  # 有氧區間佔比
    z345 = zpct[2] + zpct[3] + zpct[4]

    parts = []

    # 開頭：天氣 + 距離 + 配速
    if wx:
        parts.append('體感 %s°C 下跑 %sK，均配 %s/km' % (feel, kmr, pace_fmt(pace)))
    else:
        parts.append('完成 %sK，均配 %s/km' % (kmr, pace_fmt(pace)))

    # 涼天換算（體感 > 25 才提）
    if hot and cool_pace < pace - 3:
        parts.append('（涼天換算約 %s/km，離 Sub-4 目標 5:41 %s）' % (
            pace_fmt(cool_pace),
            '已達標 ✓' if cool_pace <= SUB4_PACE else '差 %s' % pace_fmt(cool_pace - SUB4_PACE)))
    elif pace <= SUB4_PACE + 30:
        diff = pace - SUB4_PACE
        if diff <= 0:
            parts.append('（已快於 Sub-4 目標配速 ✓）')
        else:
            parts.append('（離 Sub-4 目標 5:41 差 %d 秒/km）' % round(diff))

    parts.append('。')

    # 心率區間分析
    if typ == 'aerobic':
        if z12 >= 75:
            parts.append('心率 %d%% 落在 Z1-2 有氧區，強度控制得宜' % round(z12))
        elif z12 >= 55:
            parts.append('心率 Z1-2 佔 %d%%、Z3+ 佔 %d%%，有氧日偏快了些' % (round(z12), round(z345)))
        else:
            parts.append('心率 Z3 以上佔 %d%%，輕鬆日不該這麼累——建議放慢 10-15 秒/km' % round(z345))
    elif typ == 'long':
        z23 = zpct[1] + zpct[2]
        z45 = zpct[3] + zpct[4]
        if z45 >= 20:
            parts.append('心率 Z4-5 佔 %d%%，長跑強度偏高——後段容易爆掉，建議壓在 Z2-3' % round(z45))
        elif z12 >= 70:
            parts.append('心率 %d%% 在 Z1-2，長跑配速很保守，有氧底子紮實' % round(z12))
        else:
            parts.append('心率 Z2-3 佔 %d%%，長跑該有的強度' % round(z23))
    elif typ == 'interval':
        z45 = zpct[3] + zpct[4]
        if z45 >= 25:
            parts.append('Z4-5 佔 %d%%，間歇強度到位' % round(z45))
        else:
            parts.append('Z4-5 僅 %d%%，可以再推高一點強度' % round(z45))
    elif typ == 'hills':
        parts.append('心率 Z3+ 佔 %d%%' % round(z345))

    # 心率脫鉤
    if dc is not None:
        if typ == 'long':
            if dc < 5:
                parts.append('；前後半心率脫鉤 %+.1f%%，長距離跑下來心率控制出色' % dc)
            elif dc < 8:
                parts.append('；脫鉤 %+.1f%%（長跑正常範圍）' % dc)
            else:
                parts.append('；脫鉤 %+.1f%% 偏高，後半段心率爬升明顯——注意補水和出發配速' % dc)
        elif typ == 'aerobic':
            if dc < 3:
                parts.append('；前後半心率脫鉤 %+.1f%%，有氧底子扎實' % dc)
            elif dc < 6:
                parts.append('；脫鉤 %+.1f%%（正常範圍）' % dc)
            else:
                parts.append('；脫鉤 %+.1f%% 偏高，後半段心率爬升明顯——可能出發太快或補水不足' % dc)
        elif typ == 'interval' and dc > 8:
            parts.append('；脫鉤 %+.1f%%，最後幾組掉速明顯' % dc)

    parts.append('。')

    # 步頻
    if spm > 0:
        if spm >= 176:
            parts.append('步頻 %d spm 很好' % spm)
        elif spm >= 168:
            parts.append('步頻 %d spm 尚可' % spm)
        else:
            parts.append('步頻 %d spm 偏低，試著縮小步幅、加快翻轉，目標 175+' % spm)

    # 配速穩定度（有氧/長跑才有意義）
    if pace_cv is not None and typ in ('aerobic', 'long'):
        if pace_cv < 8:
            parts.append('，配速穩定度佳（CV %.1f%%）' % pace_cv)
        elif pace_cv < 14:
            pass  # 普通，不特別提
        else:
            parts.append('，配速波動大（CV %.1f%%），練習維持均速對馬拉松很重要' % pace_cv)

    # 前後半配速
    if split_delta is not None:
        if typ == 'long':
            if split_delta > 2:
                parts.append('。後半加速 %+.1f%%（negative split），長跑配速掌控成熟' % split_delta)
            elif split_delta < -3:
                parts.append('。後半掉速 %.1f%%，長跑前半要再壓住' % abs(split_delta))
        elif typ == 'aerobic':
            if split_delta > 3:
                parts.append('。後半加速（negative split），控配速意識好' % ())
            elif split_delta < -5:
                parts.append('。後半掉速 %.1f%%，前半可能太躁進' % abs(split_delta))

    parts.append('。')

    ev = ''.join(parts)
    ev = ev.replace('。。', '。').replace('，。', '。')

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
        cad_avg = a.get('average_cadence') or 0
        typ = classify(km, elev, v)
        stats = analyze(hr, d, v, alt, a['moving_time'], km, cad_avg)
        name, badge, ev = make_meta(km, typ, wx, ahr, mhr, elev, stats)
        runs[key] = {
            'name': name, 'km': round(km, 1), 'mov': a['moving_time'],
            'ahr': ahr, 'mhr': mhr, 'cad': round(cad_avg),
            'elev': round(elev),
            'wx': wx or {'t': None, 'rh': None, 'feel': 0},
            'badge': badge, 'ev': ev, 'stats': stats,
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
