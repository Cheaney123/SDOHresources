"""Readback and end-to-end scenarios, driven through normal controls. Synthetic only.
Writes each scenario's patient text, staff note and pre-send checks to tmp/scenarios/.
Run: CHROME_PATH=/usr/bin/google-chrome python3 tests/scenarios.py
"""
import asyncio, json, os, re, sys
from pathlib import Path
from playwright.async_api import async_playwright
sys.path.insert(0, str(Path(__file__).parent))
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tmp/scenarios"; OUT.mkdir(parents=True, exist_ok=True)
CHROME = os.environ.get("CHROME_PATH")

async def run():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path=CHROME, args=["--no-sandbox"]) if CHROME else await pw.chromium.launch()
        pg = await b.new_page(viewport={"width": 1366, "height": 900})
        await pg.goto((ROOT / "index.html").as_uri())
        async def new(): await pg.click("#newref"); await pg.click("#newyes")
        async def need(l): await pg.locator("#needs label", has_text=re.compile("^" + re.escape(l) + "$")).locator("input").check()
        async def r(n, v): await pg.check(f"input[name={n}][value={v}]")
        async def sel(name): await pg.locator("#results .card", has=pg.locator("h3", has_text=name)).first.get_by_role("button", name=re.compile("^Select")).click()
        async def f(i, v): await pg.select_option("#" + i, v)
        async def save(key, title):
            t = await pg.evaluate("window.__v2.patientText()"); n = await pg.evaluate("window.__v2.note()")
            g = (await pg.inner_text("#gate")).strip(); blocked = await pg.is_disabled("#copy")
            (OUT / f"{key}.patient.txt").write_text(t); (OUT / f"{key}.note.txt").write_text(n)
            (OUT / f"{key}.meta.json").write_text(json.dumps({"title": title, "gate": g, "copyBlocked": blocked}, indent=1))
            print(f"== {key}: {title}  copy blocked={blocked}")

        # R1 / E2-like: ride - plan agent answered, ride left pending
        await new(); await need("Transportation"); await pg.select_option("#county", "Sacramento"); await r("mc", "yes"); await f("plan", "Anthem Blue Cross")
        await r("pref", "help"); await r("timing", "soon"); await r("canCall", "yes"); await r("vm", "call-vm")
        await sel("Medi-Cal rides to medical appointments"); await sel("ACC Rides")
        await f("actor", "Me (the staff member completing this)"); await f("win", "afternoon"); await f("status", "ride-requested"); await pg.click("#statusOk")
        await f("owner", "Me (the staff member completing this)"); await f("by", "tomorrow"); await pg.click("#callback"); await f("backup", "c99")
        await save("R1-ride-pending", "Plan agent answered but left the ride pending")

        # R2 / E3: groceries tonight; pantry may not answer; staff update may be missed
        await new(); await need("Food"); await need("Housing & legal"); await pg.select_option("#county", "Sacramento"); await f("prio", "food")
        await r("pref", "help"); await r("timing", "today"); await r("delivery", "no"); await r("canCall", "yes"); await r("vm", "call-vm")
        await sel("2-1-1 Sacramento"); await sel("Sacramento Food Bank & Family Services")
        await f("actor", "Patient"); await f("status", "patient-will"); await f("win", "evening")
        await f("owner", "Me (the staff member completing this)"); await f("by", "later today"); await pg.click("#callback"); await f("retry", "later the same day"); await f("backup", "c90")
        await save("R2-food-tonight", "Groceries tonight; pantry unanswered and staff update missed")

        # R3: housing; safe callback missed, no voicemail or MHO allowed, patient can't make calls
        await new(); await need("Housing & legal"); await pg.select_option("#county", "Sacramento")
        await r("pref", "help"); await r("timing", "soon"); await r("canCall", "no"); await r("vm", "call-novm")
        await sel("Senior Legal Hotline"); await sel("2-1-1 Sacramento")
        await f("actor", "Me (the staff member completing this)"); await f("status", "attempted")
        await f("owner", "Me (the staff member completing this)"); await f("by", "end of this week"); await f("win", "morning"); await pg.click("#callback")
        await f("retry", "later the same day"); await f("backup", "c98")
        await save("R3a-housing-blocked", "Backup asks a patient who can't call to call (should be blocked)")
        await f("backup", "none"); await pg.click("#gate input[data-f=gapOk]")
        await save("R3-housing-callback", "Housing referral; safe callback window missed; no voicemail/MHO")

        # R4 / E1: refill unaffordable, due soon
        await new(); await need("Medication costs"); await pg.select_option("#county", "Sacramento")
        await r("pref", "help"); await r("timing", "soon"); await r("canCall", "yes"); await r("vm", "mho")
        await sel("Pharmacy team"); await sel("HICAP")
        await f("actor", "Me (the staff member completing this)"); await f("status", "cost-question"); await pg.click("#statusOk")
        await f("owner", "Pharmacy team"); await f("by", "tomorrow"); await pg.click("#callback"); await f("backup", "s8")
        await save("R4-refill-cost", "Refill unaffordable and due soon: cost question vs refill order")

        # R5: routine link-only control
        await new(); await need("Food"); await pg.select_option("#county", "Placer"); await r("pref", "info")
        await sel("CalFresh"); await pg.select_option("#sel select[data-act=send]", "link")
        await save("R5-link-only", "Routine: patient has food this week and only wants the CalFresh application")

        # E2: pharmacist hears tomorrow's ride fell through (plan unknown)
        await new(); await need("Transportation"); await pg.select_option("#county", "Sacramento"); await r("mc", "yes")
        await r("pref", "help"); await r("timing", "today"); await r("canCall", "yes"); await r("vm", "call-vm")
        await sel("Medi-Cal rides to medical appointments")
        await f("actor", "Patient"); await f("status", "patient-will"); await f("win", "any time"); await f("owner", "Me (the staff member completing this)"); await f("by", "later today"); await pg.click("#callback"); await f("retry", "later the same day"); await f("backup", "none"); await pg.click("#gate input[data-f=gapOk]")
        await save("E2-ride-fell-through", "Pharmacist: tomorrow's ride fell through")

        # E4: no MHO / unreliable internet; first agency couldn't help
        await new(); await need("Utilities"); await pg.select_option("#county", "Sacramento")
        await r("pref", "help"); await pg.select_option("#channel", "spoken"); await r("timing", "soon"); await r("canCall", "yes"); await r("vm", "call-novm")
        names = await pg.locator("#results .card h3").all_inner_texts()
        await sel("Community Resource Project"); await sel("2-1-1 Sacramento")
        await pg.check("#sel input[data-act=tried][data-id=c92]")
        await f("actor", "Patient"); await f("status", "patient-will"); await f("win", "afternoon"); await f("owner", "Me (the staff member completing this)"); await f("by", "next week"); await pg.click("#callback")
        opts = await pg.locator("#backup option").all_inner_texts()
        await f("backup", "none"); await pg.click("#gate input[data-f=gapOk]") if await pg.locator("#gate input[data-f=gapOk]").count() else None
        await save("E4-no-mho-spoken", "No MHO or reliable internet; first agency couldn't assist; spoken plan")

        # E5: complex / immediate safety concern leaves routine flow
        await new(); await need("Food"); await pg.select_option("#county", "Sacramento"); await pg.click("#safetyBtn")
        n = await pg.inner_text("#safetyNote"); (OUT / "E5-safety.note.txt").write_text(n)
        (OUT / "E5-safety.meta.json").write_text(json.dumps({"title": "Immediate safety concern", "mainHidden": await pg.is_hidden("#main"), "policy": await pg.inner_text("#policyTexts")}, indent=1))
        print("== E5-safety: main hidden", await pg.is_hidden("#main"))
        await b.close()

asyncio.run(run())
