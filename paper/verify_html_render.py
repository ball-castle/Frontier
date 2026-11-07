# -*- coding: utf-8 -*-
"""Open the offline reading artifacts and check navigation/search rendering."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'_qa'
checks = []
issues = []
with sync_playwright() as pw:
    browser = pw.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
    for p in sorted(ROOT.glob('0*.html')):
        errors = []
        def on_error(error): errors.append(str(error))
        page.on('pageerror', on_error)
        page.goto(p.as_uri(), wait_until='load')
        page.screenshot(path=str(OUT/(p.stem+'_desktop.png')))
        title = page.locator('h1').inner_text()
        overflow = page.evaluate('document.documentElement.scrollWidth > innerWidth + 2')
        item = {'file':p.name,'h1':title,'desktop_horizontal_overflow':overflow,'js_errors':errors}
        if overflow: issues.append(p.name+': desktop horizontal overflow')
        if errors: issues.append(p.name+': script error')
        if page.locator('#search').count():
            page.locator('#search').fill('W07')
            n = page.locator('#papers tr:visible').count()
            item['search_W07_visible_rows']=n
            if n != 1: issues.append(p.name+': W07 search failed')
            page.locator('#search').fill('')
        if page.locator('#q').count():
            page.locator('#q').fill('Graphormer')
            n = page.locator('tbody tr:visible').count()
            item['search_Graphormer_visible_rows']=n
            if n != 1: issues.append(p.name+': Graphormer search failed')
            page.locator('#q').fill('')
        page.set_viewport_size({'width':390,'height':844})
        page.screenshot(path=str(OUT/(p.stem+'_mobile.png')))
        item['mobile_horizontal_overflow'] = page.evaluate('document.documentElement.scrollWidth > innerWidth + 2')
        if item['mobile_horizontal_overflow']:issues.append(p.name+': mobile horizontal overflow')
        page.set_viewport_size({'width':1440,'height':1000})
        page.remove_listener('pageerror', on_error)
        checks.append(item)
    browser.close()
result = {'date':'2026-11-05','checks':checks,'issues':issues,'passed':not issues}
(OUT/'html_render_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
raise SystemExit(0 if not issues else 1)
