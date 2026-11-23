"""Run every County x Identified need x Medi-Cal combination in a real browser.

Identified need is multi-select, so needs are tested as: none (All), each single need,
every pair of needs, and all needs together (68 selections). With 23 counties plus
statewide-only and 3 Medi-Cal answers that is 4,896 combinations. Checks:
  - every card on screen matches what the filter logic returned
  - county results belong to the chosen county and selected needs, and none are missing
  - Medi-Cal "No" hides every Medi-Cal-only resource
  - 911 is listed with no need picked or for safety / behavioral health needs, and not otherwise; statewide Medi-Cal rides are hidden once a county is chosen
And for every resource on its own:
  - the patient message has no placeholders, undefined values or non-https links
  - the phone number appears in the patient text

Requires:  pip install playwright && python -m playwright install chromium
Usage:     python3 scripts/build.py && python3 tests/test_all_scenarios.py
"""
import asyncio
import os
import pathlib
import sys

from playwright.async_api import async_playwright

PAGE = (pathlib.Path(__file__).resolve().parent.parent / "index.html").as_uri()

CHECKS = r"""
async () => {
  const S = window.__sync, D = S.data, $ = s => document.querySelector(s);
  const counties = [...new Set(D.county.map(r => r.county))].sort();
  const isMc = r => /yes|medi-cal/i.test(r.medi || '') && !/crisis: no/i.test(r.medi || '');
  const errs = [], gaps = []; let n = 0;
  const combos = [[]];
  S.needs.forEach(a => combos.push([a]));
  S.needs.forEach((a, i) => S.needs.slice(i + 1).forEach(b => combos.push([a, b])));
  combos.push(S.needs.slice());
  for (const c of ['', ...counties]) for (const nd of combos) for (const m of ['yes', 'no', 'unsure']) {
    $('#county').value = c;
    document.querySelector(`input[name=mc][value=${m}]`).checked = true;
    S.setNeeds(nd); n++;
    const q = S.query();
    const shown = document.querySelectorAll('#results .card').length;
    if (shown !== q.cr.length + q.st.length + q.it.length) errs.push(`card count ${c}|${nd}|${m}`);
    for (const r of q.cr) {
      if (r.county !== c) errs.push(`wrong county ${r.id} in ${c}`);
      if (nd.length && !nd.includes(r.need)) errs.push(`wrong need ${r.id} for ${nd}`);
      if (m === 'no' && isMc(r)) errs.push(`Medi-Cal-only shown with No: ${r.id}`);
    }
    if (c && nd.length) for (const want of nd) {
      const expect = D.county.filter(r => r.county === c && r.need === want && !(m === 'no' && isMc(r))).length;
      const got = q.cr.filter(r => r.need === want).length;
      if (expect !== got) errs.push(`missing results ${c}|${want}|${m}: ${got} of ${expect}`);
    }
    for (const r of q.st) {
      if (m === 'no' && isMc(r)) errs.push(`Medi-Cal-only statewide shown with No: ${r.id}`);
      if (c && r.ql === 'NOCOUNTY') errs.push(`statewide Medi-Cal rides shown with county ${c}`);
    }
    const ns = nd;
    const want911 = !ns.length || ns.includes('Safety / crisis') || ns.includes('Behavioral health');
    const has911 = q.st.some(r => r.label === '911');
    if (want911 && !has911) errs.push(`911 missing ${c}|${nd}|${m}`);
    if (!want911 && has911) errs.push(`911 shown for unrelated need ${c}|${nd}|${m}`);
    if (c && nd.length === 1 && m === 'unsure' && !q.cr.length) gaps.push(`${c}: ${nd[0]}`);
  }
  for (const r of [...D.county, ...D.state]) {
    const html = S.compose([r]);
    if (/undefined|null|\{phone\}|@FNAME@|NaN/.test(html)) errs.push(`bad text in message ${r.id}`);
    (r.links || []).forEach(l => { if (!/https:\/\/\S+/.test(l)) errs.push(`bad link ${r.id}`); });
    const ph = (r.phone || '').match(/\d{3}-\d{3}-\d{4}|2-1-1|\b988\b|\b911\b/);
    if (ph && !(r.summary || '').includes(ph[0])) errs.push(`phone missing from patient text ${r.id}`);
  }
  return {n, errs, gaps, resources: D.county.length + D.state.length};
}
"""


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=os.environ.get("CHROME_PATH") or None)
        page = await browser.new_page(viewport={"width": 1440, "height": 1000})
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        await page.goto(PAGE)
        await page.wait_for_timeout(500)
        res = await page.evaluate(CHECKS)
        await browser.close()
    print(f"Combinations run: {res['n']}  Resources checked: {res['resources']}")
    print(f"Errors: {len(res['errs'])}  Page errors: {len(page_errors)}")
    print(f"County/need pairs with no county listing (statewide only): {len(res['gaps'])}")
    for e in res["errs"] + page_errors:
        print("  FAIL", e)
    sys.exit(1 if res["errs"] or page_errors else 0)


asyncio.run(main())
