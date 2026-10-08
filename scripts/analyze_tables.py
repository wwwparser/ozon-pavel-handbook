"""Read only: extract cells/formulas and cached results from original workbooks."""
import json
import warnings
from pathlib import Path
import openpyxl
warnings.filterwarnings('ignore',category=UserWarning,module='openpyxl')
result=[]
for p in sorted(Path('data/tables').glob('*.xlsx')):
    wb=openpyxl.load_workbook(p,data_only=False)
    cached=openpyxl.load_workbook(p,data_only=True)
    sheets=[]
    for s in wb:
        cells={c.coordinate:{'value':c.value,'cached':cached[s.title][c.coordinate].value,
                             'format':c.number_format} for row in s for c in row if c.value is not None}
        sheets.append({'name':s.title,'cells':cells})
    result.append({'post_id':int(p.stem),'source':f'https://t.me/prodavecpavel/{p.stem}','sheets':sheets})
Path('research').mkdir(exist_ok=True)
Path('research/tables.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
for r in result:
    print(r['post_id'])
    for s in r['sheets']:
        if s['name']=='вводные':
            print(s['name'],[(k,v['value']) for k,v in s['cells'].items() if k.startswith(('A','B','C','G','H'))][:55])
        else:
            print('cached first row',{k:v['cached'] for k,v in s['cells'].items() if k in ('M2','N2','O2','P2','Q2','S2','U2','W2','X2','Y2','Z2','AA2','AB2','AC2')})
