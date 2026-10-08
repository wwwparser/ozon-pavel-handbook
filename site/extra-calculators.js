function setupExtra(id,fields,calculate){const box=document.querySelector('#'+id),form=box.querySelector('form'),result=box.querySelector('.result');
 for(const [name,label,value]of fields){const l=document.createElement('label');l.textContent=label;const input=document.createElement('input');input.type='number';input.name=name;input.step='any';input.value=value;input.required=true;l.append(input);form.append(l);}
 function update(){try{const x={};for(const [name]of fields){if(form.elements.namedItem(name).value==='')throw Error('Заполните все поля.');x[name]=Number(form.elements.namedItem(name).value);if(!Number.isFinite(x[name]))throw Error('Проверьте числовые значения.');}result.textContent=calculate(x);}catch(e){result.textContent=e.message;}}
 form.addEventListener('input',update);form.addEventListener('submit',e=>e.preventDefault());update();}
const money=new Intl.NumberFormat('ru-RU',{maximumFractionDigits:2});
setupExtra('china-calculator',[
 ['price','Закупочная цена, юани',7.5],['yuan','Рублей за юань',12],['weight','Вес упаковки, килограммы',.5],['rate','Доставка, долларов за килограмм',3],['usd','Рублей за доллар',90],['pack','Упаковка на единицу, ₽',20],['docs','Документы на партию, ₽',30000],['qty','Единиц в партии',300],['other','Прочие расходы на партию, ₽',0]],x=>{
 if(x.qty<=0||!Number.isInteger(x.qty))throw Error('Количество должно быть целым и больше нуля.');if(Object.values(x).some(v=>v<0))throw Error('Расходы не могут быть отрицательными.');
 const per=x.price*x.yuan+x.weight*x.rate*x.usd+x.pack+(x.docs+x.other)/x.qty;
 return 'Стоимость получения: '+money.format(per)+' ₽ на единицу; партия — '+money.format(per*x.qty)+' ₽. По весу, без отдельной поправки на объёмный вес.';});
setupExtra('actual-calculator',[
 ['net','Начисления после удержанных услуг и возвратов, ₽',100000],['units','Реализованные единицы после возвратов',100],['cost','Закупка реализованной единицы, ₽',350],['ads','Реклама, ещё не учтённая в начислениях, ₽',18000],['tax','Налоговый резерв за период, ₽',6000],['other','Другие ещё не учтённые расходы, ₽',4000]],x=>{
 if(x.units<0||!Number.isInteger(x.units)||x.cost<0||x.ads<0||x.tax<0||x.other<0)throw Error('Количество должно быть целым; расходы — неотрицательными.');
 return 'Расчётный результат за период: '+money.format(x.net-x.units*x.cost-x.ads-x.tax-x.other)+' ₽. Сверьте полноту расходов и определения исходного отчёта.';});
