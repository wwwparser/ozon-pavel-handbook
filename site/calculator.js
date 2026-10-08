/* Deterministic implementation of the four original workbook models. */
(function (root) {
  function calculate(x) {
    const values=Object.values(x).filter(v=>typeof v==='number');
    if(values.some(v=>!Number.isFinite(v)))throw Error('Заполните все числовые поля.');
    if(x.price<=0 || x.cost<=0 || x.buyout<=0 || x.buyout>100)throw Error('Цена и закупка должны быть больше нуля; выкуп — от 0 до 100%, исключая 0.');
    if(['cost','extra','length','width','height','commission','acquiring','drr','tax','base','step','delivery','lastMile','reverseExtra','surcharge'].some(k=>x[k]<0))throw Error('Расходы, размеры и ставки не могут быть отрицательными.');
    if(['commission','acquiring','drr','tax','lastMile','surcharge'].some(k=>x[k]>100))throw Error('Процент должен быть от 0 до 100.');
    if(x.factor<=0 || x.territory<=0)throw Error('Коэффициенты должны быть больше нуля.');
    const volume=x.length*x.width*x.height/1000;
    const modern=x.model==='34'||x.model==='35';
    const forward=modern?(x.base+x.delivery)*x.factor:((volume-1)*x.step+x.base)*x.factor*(x.model==='25'?x.territory:1);
    if(forward<0)throw Error('Исходная формула даёт отрицательную доставку. Проверьте объём и исторический тариф.');
    const reverse=forward+x.reverseExtra;
    const last=x.model==='7'?x.price*x.lastMile/100:0;
    const logistics=(forward+reverse)*(100-x.buyout)/x.buyout+forward+last;
    const fee=x.price*x.commission/100,acquiring=x.price*x.acquiring/100;
    const advertising=x.price*x.drr/100;
    const tax=x.price*x.tax/100;
    const originalWithholdings=fee+acquiring+logistics+(modern?0:advertising);
    const originalProfit=x.price-x.cost-x.extra-originalWithholdings-tax;
    const surcharge=x.price*x.surcharge/100;
    const profit=originalProfit-(modern?advertising:0)-surcharge;
    return {volume,forward,reverse,logistics,fee,acquiring,advertising,tax,
      originalWithholdings,originalProfit,profit,margin:profit/x.price*100,
      roi:profit/x.cost*100,breakEvenDrr:(x.price-x.cost-x.extra-fee-acquiring-logistics-tax-surcharge)/x.price*100,surcharge};
  }
  if(typeof module!=='undefined')module.exports={calculate};
  root.PavelCalculator={calculate};
})(typeof globalThis!=='undefined'?globalThis:this);
