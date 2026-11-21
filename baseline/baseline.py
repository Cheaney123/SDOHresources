import asyncio, json
from playwright.async_api import async_playwright
APP="file:///home/claude/build/app/index.html"
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    pg=await b.new_page(viewport={"width":1280,"height":900})
    await pg.goto(APP); await pg.wait_for_timeout(500)
    res={}
    await pg.select_option("#county","Sacramento")
    await pg.evaluate("window.__sync.setNeeds(['Food'])")
    await pg.locator(".card", has_text="Sacramento Food Bank").locator("input").first.check()
    txt=await pg.inner_text("#out"); res['flier_in_output']='ConsumerFlier' in txt; res['getcalfresh_label']=[l for l in txt.split('\n') if 'getcalfresh' in l]
    # staff edit then add another
    await pg.evaluate("document.querySelector('#out').insertAdjacentText('afterbegin','STAFFEDIT ')")
    await pg.locator(".card", has_text="Meals on Wheels").locator("input").first.check()
    res['staff_edit_survives_add']='STAFFEDIT' in await pg.inner_text("#out")
    # county switch
    await pg.select_option("#county","Del Norte")
    out=await pg.inner_text("#out"); res['after_county_switch_still_has_sac']='Sacramento Food Bank' in out
    res['sel_chips_after_switch']=await pg.locator("#sel li, #sel .item, .selitem").count()
    # copy
    await pg.context.grant_permissions(["clipboard-read","clipboard-write"])
    await pg.click("#copy"); await pg.wait_for_timeout(200)
    c1=await pg.inner_text("#copied")
    await pg.locator(".card", has_text="Family Resource Center").locator("input").first.check()
    await pg.wait_for_timeout(200)
    res['copied_feedback_after_change']=await pg.inner_text("#copied")
    res['has_start_new']=await pg.locator("text=Start new referral").count()
    # synonym search
    await pg.fill("#q","hungry"); await pg.wait_for_timeout(200)
    res['hungry_results']=await pg.locator(".card:visible").count()
    await pg.fill("#q","shutoff notice"); await pg.wait_for_timeout(200)
    res['shutoff_results']=await pg.locator(".card:visible").count()
    print(json.dumps(res,indent=1))
    await b.close()
asyncio.run(main())
