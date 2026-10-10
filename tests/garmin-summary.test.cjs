const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');
const source = fs.readFileSync('v3/garmin-summary.js', 'utf8');
const original = {
  schema_version:1,
  volume:{last_7_days_km:18.01,last_28_days_km:77.37,activity_count_7_days:2},
  readiness:{band:'poor',confidence:'low'},
  trend:{direction:'unknown',sample_weeks:0},
  freshness:{generated_on:'2026-10-10',data_through:'2026-10-09',is_stale:false}
};
class FixedDate extends Date {
  constructor(value) {super(value === undefined ? '2026-10-10T12:00:00Z' : value);}
}

async function render(data, ok = true) {
  const context = {Date:FixedDate,Intl,AbortController,setTimeout,clearTimeout,
    fetch:async () => ({ok,json:async () => data})};
  vm.createContext(context);
  vm.runInContext(source, context);
  await context.GarminSummary.load();
  return context.GarminSummary.html();
}

test('fresh summary shows actual volume and conservative recovery', async () => {
  const result = await render(original);
  assert.match(result, /18\.01K \/ 2 次/);
  assert.match(result, /77\.37K/);
  assert.match(result, /資料不足，暫不判讀/);
});
test('old generation is visibly stale even if producer flag is false', async () => {
  const data = structuredClone(original);
  data.freshness.generated_on = '2026-10-08';
  data.freshness.data_through = '2026-10-08';
  data.freshness.is_stale = false;
  assert.match(await render(data), /資料可能過期/);
});
test('missing, malformed and private data never become zero mileage', async () => {
  for (const data of [null, {}, {...original,schema_version:2}, {...original,gps:[24,121]}]) {
    assert.match(await render(data), /暫時無法讀取/);
  }
  assert.match(await render(original, false), /暫時無法讀取/);
});
test('date and nested fields are validated', async () => {
  const data = structuredClone(original);
  data.freshness.generated_on = '2026-02-30';
  assert.match(await render(data), /暫時無法讀取/);
  data.freshness.generated_on = '2026-10-10';
  data.volume.heart_rate = 150;
  assert.match(await render(data), /暫時無法讀取/);
});
test('coach prose is escaped instead of executed', async () => {
  const data = {...original,coach_summary:'<img src=x onerror=alert(1)>'};
  const result = await render(data);
  assert.match(result, /&lt;img/);
  assert.doesNotMatch(result, /<img/);
});
