var GarminSummary = (function () {
  'use strict';
  var state = {status: 'loading'}, pending;
  function fields(value, allowed, required) {
    if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Invalid object');
    if (Object.keys(value).some(function (key) {return allowed.indexOf(key) < 0;})) throw new Error('Unexpected field');
    if (required.some(function (key) {return !Object.prototype.hasOwnProperty.call(value, key);})) throw new Error('Missing field');
  }
  function date(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) throw new Error('Invalid date');
    var parsed = new Date(value + 'T00:00:00Z');
    if (!isFinite(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== value) throw new Error('Invalid date');
    return value;
  }
  function number(value) {
    if (typeof value !== 'number' || !isFinite(value) || value < 0) throw new Error('Invalid number');
  }
  function choice(value, options) {
    if (options.indexOf(value) < 0) throw new Error('Invalid choice');
  }
  function parse(value) {
    fields(value, ['schema_version','race','volume','plan_compliance_ratio','readiness','trend','coach_summary','freshness'], ['schema_version','volume','readiness','trend','freshness']);
    if (value.schema_version !== 1) throw new Error('Unsupported schema');
    var v = value.volume, f = value.freshness, r = value.readiness, t = value.trend;
    fields(v, ['last_7_days_km','last_28_days_km','activity_count_7_days'], ['last_7_days_km','last_28_days_km','activity_count_7_days']);
    number(v.last_7_days_km); number(v.last_28_days_km); number(v.activity_count_7_days);
    if (!Number.isInteger(v.activity_count_7_days) || v.last_7_days_km > v.last_28_days_km) throw new Error('Invalid volume');
    fields(f, ['generated_on','data_through','is_stale'], ['generated_on','data_through','is_stale']);
    date(f.generated_on); if (f.data_through !== null) date(f.data_through);
    if (typeof f.is_stale !== 'boolean' || (f.data_through && f.data_through > f.generated_on)) throw new Error('Invalid freshness');
    fields(r, ['band','confidence'], ['band','confidence']);
    choice(r.band, ['good','fair','poor','unknown']); choice(r.confidence, ['high','medium','low','none']);
    fields(t, ['direction','sample_weeks'], ['direction','sample_weeks']);
    choice(t.direction, ['improving','steady','declining','unknown']); number(t.sample_weeks);
    if (!Number.isInteger(t.sample_weeks)) throw new Error('Invalid trend');
    if (value.race != null) {
      fields(value.race, ['name','race_date','days_remaining','distance_km'], ['name','race_date','days_remaining','distance_km']);
      date(value.race.race_date); number(value.race.distance_km);
      if (typeof value.race.name !== 'string' || !Number.isInteger(value.race.days_remaining)) throw new Error('Invalid race');
    }
    if (value.plan_compliance_ratio != null) {
      number(value.plan_compliance_ratio);
      if (value.plan_compliance_ratio > 1) throw new Error('Invalid compliance');
    }
    if (value.coach_summary !== undefined && (typeof value.coach_summary !== 'string' || value.coach_summary.length > 2000)) throw new Error('Invalid coaching summary');
    return value;
  }
  function today() {
    var out = {};
    new Intl.DateTimeFormat('en-CA', {timeZone:'Asia/Taipei',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date()).forEach(function (p) {out[p.type] = p.value;});
    return out.year + '-' + out.month + '-' + out.day;
  }
  function escape(value) {
    return String(value).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
  }
  function html(compact) {
    if (state.status === 'loading') return 'Garmin 摘要載入中…';
    if (state.status === 'error') return 'Garmin 摘要暫時無法讀取，請稍後重新整理。';
    var data = state.data, v = data.volume, f = data.freshness;
    var age = (Date.parse(today()) - Date.parse(f.generated_on)) / 86400000;
    var stale = f.is_stale || age > 1 || f.data_through === null;
    var freshness = (stale ? '資料可能過期 · ' : '') + '活動截至 ' + (f.data_through || '資料不足') + ' · 更新 ' + f.generated_on;
    var volume = '近 7 天 ' + v.last_7_days_km.toFixed(2) + 'K / ' + v.activity_count_7_days + ' 次 · 近 28 天 ' + v.last_28_days_km.toFixed(2) + 'K';
    if (compact) return '<b>Garmin</b> · ' + volume + '<br>' + escape(freshness);
    var readiness = data.readiness;
    var band = {good:'良好',fair:'普通',poor:'偏低',unknown:'資料不足'};
    var recovery = readiness.confidence === 'low' || readiness.confidence === 'none' ? '資料不足，暫不判讀' : band[readiness.band];
    return '<b>Garmin · 實際跑量</b><p>' + volume + '</p><p>' + escape(freshness) + '</p>' +
      '<details><summary>恢復狀態與教練摘要</summary><p>恢復：' + recovery + '</p><p>' + escape(data.coach_summary || '目前沒有教練摘要。') + '</p></details>';
  }
  function load() {
    if (pending) return pending;
    var controller = new AbortController(), timeout = setTimeout(function () {controller.abort();}, 10000);
    pending = fetch('public-summary.v1.json', {cache:'no-store',signal:controller.signal}).then(function (response) {
      if (!response.ok) throw new Error('Summary unavailable');
      return response.json();
    }).then(function (value) {
      var data = parse(value);
      if (data.freshness.generated_on > today()) throw new Error('Future summary');
      state = {status:'ready',data:data};
    }).catch(function () {state = {status:'error'};}).finally(function () {clearTimeout(timeout);});
    return pending;
  }
  return {parse:parse,load:load,html:html};
})();
