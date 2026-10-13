var RunReviews = (function () {
  'use strict';
  var data, status = 'loading', selected;
  function escape(value) {
    return String(value).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
  }
  function number(value, digits) { return value == null ? '資料不足' : Number(value).toFixed(digits == null ? 0 : digits); }
  function pace(value) {
    if (value == null) return '資料不足';
    var seconds = Math.round(value); return Math.floor(seconds / 60) + ':' + String(seconds % 60).padStart(2,'0');
  }
  function parse(value) {
    if (!value || value.schema_version !== 1 || typeof value.local_preview !== 'boolean' || !Array.isArray(value.runs) || !/^\d{4}-\d{2}-\d{2}$/.test(value.generated_on)) throw new Error('Invalid review document');
    value.runs.forEach(function(r) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(r.date) || !r.comparison || !r.weather || !Array.isArray(r.phases) || !Array.isArray(r.observations) || !Array.isArray(r.limitations)) throw new Error('Invalid review');
      ['distance_km','duration_seconds','pace_seconds','average_hr','maximum_hr','cadence','drift_percent','pace_cv_percent','hr_coverage','high_hr_share'].forEach(function(k) {
        if (r[k] !== null && (typeof r[k] !== 'number' || !Number.isFinite(r[k]))) throw new Error('Invalid metric');
      });
      ['verdict','next_step','drift_note'].forEach(function(k){if(typeof r[k] !== 'string')throw new Error('Invalid text');});
      r.observations.concat(r.limitations).forEach(function(t){if(typeof t !== 'string')throw new Error('Invalid observation');});
      r.phases.forEach(function(p){
        if(['前段','中段','後段'].indexOf(p.label)<0)throw new Error('Invalid phase');
        ['heart_rate','pace_seconds','cadence'].forEach(function(k){if(p[k]!==null && (typeof p[k]!=='number'||!Number.isFinite(p[k])||p[k]<0))throw new Error('Invalid phase metric');});
      });
      if(['matched','short','over','rest_day_run','unplanned'].indexOf(r.comparison.distance_status)<0 || ['above_reference','consistent','unknown'].indexOf(r.comparison.intensity_status)<0)throw new Error('Invalid comparison');
    });
    return value;
  }
  function stat(label, value, unit) {
    return '<div class="rr-stat"><span>'+escape(label)+'</span><strong>'+escape(value)+'</strong><small>'+escape(unit || '')+'</small></div>';
  }
  function chart(phases) {
    var values = phases.map(function(p){return p.heart_rate;});
    if(values.some(function(v){return v == null;})) return '<p class="rr-muted">心率分段資料不足，暫不繪圖。</p>';
    var min = Math.floor(Math.min.apply(null,values)/10)*10-10, max = Math.ceil(Math.max.apply(null,values)/10)*10+10;
    var points = values.map(function(v,i){return (60+i*120)+','+(86-(v-min)/(max-min)*60);}).join(' ');
    return '<svg class="rr-chart" viewBox="0 0 360 115" role="img" aria-label="前、中、後段平均心率：'+values.map(function(v){return number(v,1);}).join('、')+' bpm">'+
      '<title>三段平均心率，非逐秒曲線</title><path d="M40 86H330" stroke="currentColor" opacity=".15"/>'+
      '<polyline points="'+points+'" fill="none" stroke="currentColor" stroke-width="2"/>'+values.map(function(v,i){var x=60+i*120,y=86-(v-min)/(max-min)*60;return '<circle cx="'+x+'" cy="'+y+'" r="4" fill="currentColor"/><text x="'+x+'" y="'+(y-10)+'" text-anchor="middle">'+number(v,1)+'</text><text x="'+x+'" y="108" text-anchor="middle">'+escape(phases[i].label)+'</text>';}).join('')+'</svg>';
  }
  function report(r,index) {
    var c=r.comparison, distance={matched:'距離符合',short:'距離較短',over:'距離超量',rest_day_run:'休息日有跑步',unplanned:'未安排課表'}[c.distance_status] || '待確認';
    var intensity={above_reference:'超出輕鬆參考',consistent:'心率大致符合參考，待主觀確認',unknown:'強度待確認'}[c.intensity_status] || '待確認';
    var drift=r.drift_percent == null ? '暫不判讀' : number(r.drift_percent,1)+'%';
    return '<article class="rr-report"><div class="rr-heading"><span>Garmin 跑後評價'+(index ? ' · 同日第 '+(index+1)+' 筆' : '')+'</span><span class="rr-pill">'+(data.local_preview?'本機預覽':'分析摘要')+'</span></div>'+
      '<h3>'+escape(r.verdict)+'</h3><div class="rr-stats">'+stat('距離',number(r.distance_km,2),'km')+stat('移動配速',pace(r.pace_seconds),'/km')+stat('平均 / 最高心率',number(r.average_hr)+' / '+number(r.maximum_hr),'bpm')+stat('平均步頻',number(r.cadence),'spm · 雙腳')+'</div>'+
      '<div class="rr-comparison"><b>課表比對</b><p>'+escape(distance)+' · '+escape(intensity)+'</p><p>當天實跑合計 '+number(c.actual_day_km,2)+'K'+(c.planned_km == null ? ' · 未安排課表' : ' / 課表 '+number(c.planned_km,0)+'K')+'</p><small>'+escape(c.explanation)+'</small></div>'+
      '<details open><summary>心率、配速與步頻變化</summary>'+chart(r.phases)+
      '<div class="rr-table-wrap"><table><caption>依經過時間分成三段；配速排除停留樣本</caption><thead><tr><th scope="col">分段</th><th scope="col">心率 bpm</th><th scope="col">配速 /km</th><th scope="col">步頻 spm</th></tr></thead><tbody>'+r.phases.map(function(p){return '<tr><th scope="row">'+escape(p.label)+'</th><td>'+number(p.heart_rate,1)+'</td><td>'+pace(p.pace_seconds)+'</td><td>'+number(p.cadence,1)+'</td></tr>';}).join('')+'</tbody></table></div>'+
      '<p class="rr-muted">心率／速度比漂移：'+escape(drift)+' · 分段配速 CV：'+number(r.pace_cv_percent,1)+'% · 心率樣本覆蓋：'+number(r.hr_coverage*100)+'%</p>'+ (r.high_hr_share == null ? '<p class="rr-muted">可用移動心率不足，無法比對高心率時間。</p>' : '<p class="rr-muted">移動中 ≥150 bpm 的時間占 '+number(r.high_hr_share*100,1)+'%。</p>')+'</details>'+
      '<div class="rr-weather"><b>天氣背景</b><p>'+ (r.weather.temperature_celsius == null ? (r.weather.status === 'unit_unverified' ? '溫度單位待核對 · 來源數值 '+number(r.weather.source_temperature,1)+' · 濕度 '+number(r.weather.humidity_percent)+'%' : '未取得可用 Garmin 活動天氣') : number(r.weather.temperature_celsius,1)+'°C · 濕度 '+number(r.weather.humidity_percent)+'%'+(r.weather.apparent_temperature_celsius == null ? '' : ' · 體感 '+number(r.weather.apparent_temperature_celsius,1)+'°C'))+'</p><small>來源：Garmin 活動起點附近測站。連接工具未確認溫度單位，這版不判讀熱度；不是手錶感測器溫度。</small><p><a href="https://support.garmin.com/hr-HR/?faq=iSaDaYsypP3QYBVRveLXAA" target="_blank" rel="noopener">Garmin 天氣來源說明</a> · <a href="https://www.cdc.gov/heat-health/risk-factors/heat-and-athletes.html" target="_blank" rel="noopener">運動與熱環境參考</a></p></div>'+
      '<div class="rr-observations"><b>綜合觀察</b><ul>'+r.observations.map(function(t){return '<li>'+escape(t)+'</li>';}).join('')+'</ul><p>'+escape(r.next_step)+'</p></div>'+
      '<details><summary>判讀依據與資料限制</summary><ul>'+r.limitations.map(function(t){return '<li>'+escape(t)+'</li>';}).join('')+'</ul><p>確定性分析，沒有生成模型補寫資料。心率漂移只在足夠時長、覆蓋與穩定配速下顯示；未通過條件就不顯示數值。</p></details></article>';
  }
  function html() {
    if(status==='loading')return '<p>跑後評價載入中…</p>';
    if(status==='error')return '<p>跑後評價讀取失敗，請重新整理。</p>';
    if(!selected)return '';
    var runs=data.runs.filter(function(r){return r.date===selected;});
    return '<div class="mm-sec"><span class="vbar"></span>跑後綜合評價<small>Garmin · 更新 '+escape(data.generated_on)+'</small></div>'+
      '<div class="rr-picker"><b>'+escape(selected)+'</b><button type="button" id="rr-back">返回月曆</button></div>'+
      (runs.length ? runs.map(report).join('') : '<p class="rr-empty">'+escape(selected || '')+' 尚無已同步的跑步紀錄。課表安排不代表完成。</p>');
  }
  function mount(key) {
    if(key)selected=key;
    var box=document.getElementById('mm-reviews');if(!box)return;
    if(!selected)return;
    box.hidden=false;box.innerHTML=html();
    var back=document.getElementById('rr-back');
    if(back)back.onclick=function(){
      var day=selected;reset();
      var calendar=document.getElementById('mmc-grid');
      if(calendar)calendar.scrollIntoView({block:'start'});
      var cell=document.querySelector('[data-date="'+day+'"]');if(cell)cell.focus({preventScroll:true});
    };
  }
  function reset(){selected=null;var box=document.getElementById('mm-reviews');if(box){box.hidden=true;box.innerHTML='';}}
  function load() {
    var controller=new AbortController(), timer=setTimeout(function(){controller.abort();},10000);
    return fetch('run-reviews.json',{cache:'no-store',signal:controller.signal}).then(function(r){if(!r.ok)throw new Error('Unavailable');return r.json();}).then(function(v){data=parse(v);status='ready';}).catch(function(){status='error';}).finally(function(){clearTimeout(timer);mount();});
  }
  function hasDate(key){return data && data.runs.some(function(r){return r.date===key;});}
  function dayLink(key){return hasDate(key)?'<div class="rr-day-link"><b>已同步實跑</b><p>這天有 Garmin 跑步紀錄與綜合評價。</p><button type="button" data-review-date="'+key+'">查看這天的跑後評價</button></div>':'<p class="rr-muted">尚無這天的 Garmin 跑步紀錄。</p>';}
  return {load:load,html:html,mount:mount,reset:reset,hasDate:hasDate,dayLink:dayLink,parse:parse};
})();
