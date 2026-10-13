const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const {test} = require('node:test');
const html = fs.readFileSync(path.join(__dirname,'../v3/index.html'),'utf8');
const source = html.match(/var MarathonTraining=\(function\(\)\{[\s\S]*?\}\)\(\);/)[0];
const context = {Date,Intl};vm.createContext(context);vm.runInContext(source,context);
const training = context.MarathonTraining;
for(const start of ['2026-10-12','2026-10-19']) {
  test('Monday and Thursday rest preserve 50 km over five runs: '+start,()=>{
    const keys=Array.from({length:7},(_,i)=>new Date(Date.parse(start)+i*86400000).toISOString().slice(0,10));
    const distances=keys.map(key=>training.plan[key].km);
    assert.deepEqual(distances,[0,10,10,0,8,8,14]);
    assert.equal(distances.reduce((a,b)=>a+b,0),50);
    assert.equal(distances.filter(km=>km>0).length,5);
    assert.equal(training.plan[keys[3]].c,'rest');
    assert.equal(training.plan[keys[6]].c,'long');
  });
}
test('Wednesday is a planned run and Thursday is a rest day',()=>{
  assert.equal(training.summary('2026-10-14').today,'輕鬆 10K');
  assert.equal(training.summary('2026-10-15').today,'休息');
  assert.equal(training.summary('2026-10-14').km,50);
});
