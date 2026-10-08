import json
import re
from pathlib import Path
data=json.loads(Path('research/tables.json').read_text(encoding='utf-8'))
models=[]
titles={7:'Ozon · сентябрь 2025',25:'WB · декабрь 2025',34:'Ozon до 300 ₽ · февраль 2026',35:'Ozon от 301 ₽ · февраль 2026'}
for wb in data:
    ident=wb['post_id'];c=wb['sheets'][0]['cells']; modern=ident in (34,35)
    def value(k):
        cell=c.get(k,{});v=cell.get('cached') if str(cell.get('value','')).startswith('=') else cell.get('value')
        return v
    d={'model':str(ident),'price':value('B2'),'cost':value('C2'),'extra':value('D2'),
       'length':value('F2'),'width':value('G2'),'height':value('H2'),'commission':value('J2')*100,
       'acquiring':1 if ident==35 else 1.253,'drr':value('V2' if modern else ('T2' if ident==7 else 'S2'))*100,
       'tax':value('Y2' if modern else ('W2' if ident==7 else 'V2'))*100,
       'buyout':value('T2' if modern else ('R2' if ident==7 else 'Q2')),
       'factor':value('S2' if modern else ('Q2' if ident==7 else 'N2')),
       'territory':value('O2') if ident==25 else 1,'base':value('O2') if modern else (63 if ident==7 else 46),
       'step':0 if modern else (10 if ident==7 else 14),'delivery':25 if modern else 0,
       'lastMile':5.5 if ident==7 else 0,'reverseExtra':15,'surcharge':0}
    lookups=[]
    if modern:
        s=wb['sheets'][1]['cells']
        for k,v in s.items():
            if re.fullmatch(r'G\d+',k) and int(k[1:])>=3:
                rate=s.get('H'+k[1:],{});n=rate.get('cached') if str(rate.get('value','')).startswith('=') else rate.get('value')
                if isinstance(n,str):n=float(re.sub(r'[^\d,.]','',n).replace(',','.'))
                if n is not None:lookups.append({'label':v['value'],'rate':n})
    models.append({'id':str(ident),'title':titles[ident],'source':wb['source'],'defaults':d,'volumeRates':lookups,
                   'cachedProfit':value('AA2' if modern else ('Y2' if ident==7 else 'X2'))})
Path('research/calculator-models.json').write_text(json.dumps(models,ensure_ascii=False,indent=2),encoding='utf-8')
Path('site/models.js').write_text('window.CALCULATOR_MODELS='+json.dumps(models,ensure_ascii=False)+';',encoding='utf-8')
print('Prepared',len(models),'models.')
