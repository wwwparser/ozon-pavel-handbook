const form=document.querySelector('#calculator-form');
const select=document.querySelector('#calc-model');
const fields=[['price','Расчётная цена, ₽'],['cost','Закупка, ₽'],['extra','Дополнительные расходы на единицу, ₽'],
['length','Длина упаковки, сантиметры'],['width','Ширина упаковки, сантиметры'],['height','Высота упаковки, сантиметры'],
['commission','Комиссия, %'],['acquiring','Эквайринг, %'],['tax','Налоговый резерв от цены, %'],['drr','ДРР от расчётной цены, %'],
['buyout','Выкуп, %'],['factor','Коэффициент логистики'],['territory','Территориальный коэффициент WB'],
['base','Базовая доставка / тариф диапазона, ₽'],['step','Стоимость дополнительного литра, ₽'],
['delivery','Доставка до места в новой модели, ₽'],['lastMile','Последняя миля старой модели, %'],
['reverseExtra','Доплата к обратной доставке, ₽'],['surcharge','Дополнительная нагрузка от цены, %']];
const names=Object.fromEntries(fields);
const formatter=new Intl.NumberFormat('ru-RU',{maximumFractionDigits:2});
let current;
for(const m of CALCULATOR_MODELS){const o=document.createElement('option');o.value=m.id;o.textContent=m.title;select.append(o);}
for(const [key,title]of fields){const label=document.createElement('label');label.textContent=title;
 const input=document.createElement('input');input.type='number';input.name=key;input.id='calc-'+key;input.step='any';input.min='0';input.required=true;
 label.append(input);form.append(label);}
function load(){current=CALCULATOR_MODELS.find(x=>x.id===select.value);for(const [key]of fields)form.elements.namedItem(key).value=current.defaults[key];
 const rates=document.querySelector('#volume-rate');rates.replaceChildren();
 const placeholder=document.createElement('option');placeholder.value='';placeholder.textContent='Тариф задан вручную';rates.append(placeholder);
 for(const row of current.volumeRates){const o=document.createElement('option');o.value=row.rate;o.textContent=row.label+' — '+formatter.format(row.rate)+' ₽';rates.append(o);}
 rates.parentElement.hidden=!current.volumeRates.length;
 document.querySelector('#calc-source').href=current.source;
 for(const [key]of fields){const inactive=(['34','35'].includes(current.id)&&['step','lastMile','territory'].includes(key)) || (current.id==='7'&&['delivery','territory'].includes(key)) || (current.id==='25'&&['delivery','lastMile'].includes(key));
 form.elements.namedItem(key).parentElement.hidden=inactive;}
 update();}
function update(){const box=document.querySelector('#calc-results');
 try{const x={model:select.value};for(const [key]of fields){const raw=form.elements.namedItem(key).value;if(raw==='')throw Error('Заполните поле «'+names[key]+'».');x[key]=Number(raw);}
 const r=PavelCalculator.calculate(x);box.replaceChildren();
 const summary=document.createElement('div');summary.className='calc-summary';
 summary.textContent='Результат с рекламой: '+formatter.format(r.profit)+' ₽ на единицу · маржа '+formatter.format(r.margin)+'%';box.append(summary);
 const table=document.createElement('table');const body=document.createElement('tbody');table.append(body);
 const rows=[['Объём упаковки, литры',r.volume],['Прямая доставка, ₽',r.forward],['Обратная доставка, ₽',r.reverse],['Логистика с учётом невыкупов, ₽',r.logistics],['Комиссия, ₽',r.fee],['Эквайринг, ₽',r.acquiring],['Реклама, ₽',r.advertising],['Налоговый резерв, ₽',r.tax],['Дополнительная нагрузка, ₽',r.surcharge],['Результат по исходной Excel-формуле, ₽',r.originalProfit],['Результат с рекламой и доп. нагрузкой, ₽',r.profit],['ROI к закупке, %',r.roi],['ДРР до нулевого результата, %',r.breakEvenDrr]];
 for(const [label,value]of rows){const row=document.createElement('tr');for(const text of [label,formatter.format(value)]){const cell=document.createElement('td');cell.textContent=text;row.append(cell);}body.append(row);}box.append(table);
 const note=document.createElement('p');note.textContent=['34','35'].includes(x.model)?'В исходной таблице реклама не вычитается из прибыли. Верхний результат учитывает её. Тариф диапазона выбран вручную: сверяйте его с рассчитанным объёмом.':'Историческая формула сохранена. Тарифы и коэффициенты можно заменить своими.';box.append(note);
 document.querySelector('#calc-error').textContent='';
 }catch(e){box.replaceChildren();document.querySelector('#calc-error').textContent=e.message;}}
select.addEventListener('change',load);form.addEventListener('input',update);form.addEventListener('submit',e=>e.preventDefault());
document.querySelector('#volume-rate').addEventListener('change',e=>{if(e.target.value){form.elements.base.value=e.target.value;update();}});
document.querySelector('#reset-calc').addEventListener('click',load);
document.querySelector('#export-calc').addEventListener('click',()=>{try{const x={model:select.value};for(const [k]of fields){if(form.elements.namedItem(k).value==='')throw Error('Заполните поле «'+names[k]+'».');x[k]=Number(form.elements.namedItem(k).value);}const r=PavelCalculator.calculate(x);
 const csv='\ufeffПоказатель;Значение\n'+[...fields.map(([k,n])=>[n,x[k]]),...Object.entries(r)].map(row=>row.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(';')).join('\n');
 const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='unit-economics.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 }catch(e){document.querySelector('#calc-error').textContent=e.message;}});
select.value='35';load();
