const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const {test} = require('node:test');
const script = fs.readFileSync(path.join(__dirname,'../v3/run-reviews.js'),'utf8');
function fixture() {
  return {schema_version:1,local_preview:false,generated_on:'2026-10-14',runs:[{
    date:'2026-10-13',distance_km:10.01,duration_seconds:4180,pace_seconds:418,
    average_hr:139,maximum_hr:148,cadence:157,drift_percent:null,drift_note:'insufficient',
    pace_cv_percent:11.7,hr_coverage:1,high_hr_share:0,
    phases:['前段','中段','後段'].map(label=>({label,heart_rate:139,pace_seconds:418,cadence:157})),
    weather:{temperature_celsius:null,humidity_percent:72,status:'unit_unverified',source_temperature:76},
    comparison:{planned_km:10,actual_day_km:10.01,distance_status:'matched',intensity_status:'consistent',explanation:'fixture'},
    verdict:'fixture',observations:['<img src=x onerror=alert(1)>'],next_step:'fixture',limitations:[]
  }]};
}
function setup(value=fixture(),ok=true) {
  const context={Set,Array,Number,Math,String,AbortController,setTimeout,clearTimeout,
    document:{getElementById:()=>null},fetch:async()=>({ok,json:async()=>value})};
  vm.createContext(context);vm.runInContext(script,context);return context.RunReviews;
}
test('analysis stays hidden until a date is selected and resets on return',async()=>{
  const review=setup();await review.load();assert.equal(review.html(),'');
  review.mount('2026-10-13');assert(review.html().includes('10.01'));
  review.reset();assert.equal(review.html(),'');
});
test('activity lookup distinguishes recorded and unrecorded dates',async()=>{
  const review=setup();await review.load();
  assert.equal(review.hasDate('2026-10-13'),true);assert.equal(review.hasDate('2026-10-14'),false);
});
test('analysis text is escaped before HTML rendering',async()=>{
  const review=setup();await review.load();review.mount('2026-10-13');
  assert(review.html().includes('&lt;img src=x onerror=alert(1)&gt;'));
  assert(!review.html().includes('<img src=x'));
});
test('nonfinite phase values reject the document',()=>{
  const value=fixture();value.runs[0].phases[0].heart_rate=Infinity;
  assert.throws(()=>setup().parse(value));
});
test('weather displays Celsius values and humidity without exposing raw Fahrenheit',async()=>{
  const value=fixture();
  value.runs[0].weather={temperature_celsius:24.4,apparent_temperature_celsius:26.7,
    humidity_percent:72,status:'available',source_temperature:76,source_temperature_unit:'F'};
  const review=setup(value);await review.load();review.mount('2026-10-13');
  const output=review.html();
  assert(output.includes('<strong>24.4</strong>'));
  assert(output.includes('<strong>26.7</strong>'));
  assert(output.includes('<strong>72</strong>'));
  assert(!output.includes('<strong>76</strong>'));
});
test('missing review file produces a visible error when a date is selected',async()=>{
  const review=setup(fixture(),false);await review.load();review.mount('2026-10-13');
  assert(!review.html().includes('10.01'));assert(review.html().includes('讀取失敗'));
});
