"""Exercise the generated reader and financial calculators in a real browser."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'data/qa';out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,channel='chrome')
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((ROOT/'docs/index.html').as_uri())
    page.screenshot(path=str(out/'desktop.png'))
    for ident,expected in [('7','1\u00a0798,8'),('25','2\u00a0021,45'),('34','50,25'),('35','114,99')]:
        page.select_option('#calc-model',ident)
        assert expected in page.locator('.calc-summary').inner_text(),page.locator('.calc-summary').inner_text()
    page.locator('#calc-drr').fill('0')
    assert '179,99' in page.locator('.calc-summary').inner_text()
    page.locator('#calc-buyout').fill('0')
    assert page.locator('#calc-error').inner_text()
    page.click('#reset-calc')
    page.locator('#calc-cost').fill('')
    page.click('#export-calc')
    assert 'Заполните' in page.locator('#calc-error').inner_text()
    page.click('#reset-calc')
    with page.expect_download() as d:page.click('#export-calc')
    d.value.save_as(str(out/'calculation.csv'))
    assert '114.994' in (out/'calculation.csv').read_text(encoding='utf-8-sig')
    assert '345' in page.locator('#china-calculator .result').inner_text()
    page.locator('#china-calculator input[name="qty"]').fill('0')
    assert 'больше нуля' in page.locator('#china-calculator .result').inner_text()
    assert '37\u00a0000' in page.locator('#actual-calculator .result').inner_text()
    page.locator('#actual-calculator input[name="net"]').fill('-1000')
    assert '-64\u00a0000' in page.locator('#actual-calculator .result').inner_text().replace('−','-')
    page.locator('#search').fill('кросс-докинг')
    assert page.locator('.chapter[hidden]').count()>0
    page.locator('nav a[href="#02-ekonomika"]').click()
    assert page.locator('.chapter[hidden]').count()==0
    page.select_option('#calc-model','35')
    page.locator('#calculators').scroll_into_view_if_needed()
    page.screenshot(path=str(out/'calculators-desktop.png'))
    for width in (390,768):
        mobile=browser.new_page(viewport={'width':width,'height':844})
        mobile.goto((ROOT/'docs/index.html').as_uri())
        assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'Page overflow at {width}'
        if width<700:
            assert not mobile.locator('#toc').evaluate('(e)=>e.open')
            mobile.locator('#toc summary').click()
            mobile.locator('nav a[href="#calculators"]').click()
            assert not mobile.locator('#toc').evaluate('(e)=>e.open')
        mobile.locator('#calculators').scroll_into_view_if_needed()
        mobile.screenshot(path=str(out/f'calculators-{width}.png'))
        mobile.close()
    assert not errors,errors
    browser.close()
print('Browser QA passed: four Excel models, advertising, invalid input, CSV, two extra calculators, search and mobile layout.')
