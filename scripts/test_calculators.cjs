const assert=require('node:assert/strict');
const fs=require('node:fs');
const {calculate}=require('../site/calculator.js');
const models=JSON.parse(fs.readFileSync('research/calculator-models.json','utf8'));
for(const model of models){const r=calculate(model.defaults);assert(Math.abs(r.originalProfit-model.cachedProfit)<1e-8,model.id+' original cached result');}
const modern=models.find(x=>x.id==='35').defaults;
const r=calculate(modern);assert(Math.abs(r.profit-114.99448979591835)<1e-8);
assert(Math.abs(r.originalProfit-r.profit-65)<1e-8);
assert.throws(()=>calculate({...modern,buyout:0}));
assert.throws(()=>calculate({...modern,buyout:101}));
assert.throws(()=>calculate({...modern,price:0}));
assert.throws(()=>calculate({...modern,commission:150}));
assert.throws(()=>calculate({...modern,cost:-1}));
const simple=calculate({...modern,base:100,delivery:0,factor:1,reverseExtra:15,buyout:80});
assert(Math.abs(simple.logistics-153.75)<1e-8);
assert(calculate({...modern,drr:20}).profit<r.profit);
assert(calculate({...modern,buyout:50}).profit<r.profit);
console.log('4 original models match Excel caches; advertising, buyout and invalid inputs verified.');
