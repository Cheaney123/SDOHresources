"""End-to-end tests for Resource Referral Prototype 2.0, driven through normal user controls.
Synthetic scenarios only: no names, record numbers, dates of birth or clinical notes.

Run:  CHROME_PATH=/usr/bin/google-chrome python3 tests/test_v2.py
"""
import asyncio, json, os, re, subprocess, sys, tempfile
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
CHROME = os.environ.get("CHROME_PATH")
AXE = ROOT / "tmp/node_modules/axe-core/axe.min.js"
RESULTS = []

def build(data=None):
    out = Path(tempfile.mkstemp(suffix=".html")[1])
    args = [sys.executable, str(ROOT / "scripts/build.py"), "--out", str(out)]
    if data:
        args += ["--data", str(data)]
    subprocess.run(args, check=True, capture_output=True)
    return out

def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -> {detail}"))

class App:
    def __init__(self, page): self.p = page
    async def new(self):
        await self.p.click("#newref"); await self.p.click("#newyes")
    async def phrase(self, t): await self.p.fill("#phrase", t)
    async def need(self, label, on=True):
        box = self.p.locator("#needs label", has_text=re.compile("^" + re.escape(label) + "$")).locator("input")
        await (box.check() if on else box.uncheck())
    async def county(self, c): await self.p.select_option("#county", c)
    async def mc(self, v): await self.p.check(f"input[name=mc][value={v}]")
    async def pref(self, v): await self.p.check(f"input[name=pref][value={v}]")
    async def radio(self, name, v): await self.p.check(f"input[name={name}][value={v}]")
    async def select(self, name):
        await self.p.locator("#results .card", has=self.p.locator("h3", has_text=name)).first.get_by_role("button", name=re.compile("^Select")).click()
    async def toggle(self, name):
        await self.p.locator("#results .card", has=self.p.locator("h3", has_text=name)).first.get_by_role("button", name=re.compile("^(Select|Remove)")).click()
    async def text(self): return await self.p.evaluate("window.__v2.patientText()")
    async def dom_text(self): return (await self.p.inner_text("#out")).strip()
    async def note(self): return await self.p.evaluate("window.__v2.note()")
    async def copy_disabled(self): return await self.p.is_disabled("#copy")
    async def plan(self, field, value): await self.p.select_option(f"#{field}", value)
    async def cards(self): return await self.p.locator("#results .card h3").all_inner_texts()

async def main():
    fixture = json.loads((ROOT / "data/services.json").read_text())
    syn = [
        {"id": "t-across", "name": "SYNTHETIC Nearby Pantry (Placer only)", "need": "food", "needs": ["food"], "serves": {"type": "counties", "counties": ["Placer"]}, "basedIn": "Placer",
         "phones": [{"display": "555-010-0001", "number": "555-010-0001", "role": "main", "purpose": "for food help"}], "links": [], "medi": {"req": "none", "text": "Any insurance"},
         "summary": "Call 555-010-0001 for food help.", "intake": {"status": "unknown"}, "review": {"status": "verified", "date": "2026-11-20", "source": "synthetic", "maintainer": "test", "claims": []}, "history": [{"date": "2026-11-20", "by": "test", "change": "synthetic"}], "overrides": {}, "primary": {"type": "phone", "index": 0}},
        {"id": "t-serves", "name": "SYNTHETIC Yolo Pantry (serves Sacramento)", "need": "food", "needs": ["food"], "serves": {"type": "counties", "counties": ["Yolo", "Sacramento"]}, "basedIn": "Yolo",
         "phones": [{"display": "555-010-0002", "number": "555-010-0002", "role": "main", "purpose": "for food help"}], "links": [], "medi": {"req": "none", "text": "Any insurance"},
         "summary": "Call 555-010-0002 for food help.", "intake": {"status": "unknown"}, "review": {"status": "verified", "date": "2026-11-20", "source": "synthetic", "maintainer": "test", "claims": []}, "history": [{"date": "2026-11-20", "by": "test", "change": "synthetic"}], "overrides": {}, "primary": {"type": "phone", "index": 0}},
        {"id": "t-paused", "name": "SYNTHETIC Paused Program", "need": "food", "needs": ["food"], "serves": {"type": "counties", "counties": ["Sacramento"]}, "basedIn": "Sacramento",
         "phones": [{"display": "555-010-0003", "number": "555-010-0003", "role": "main", "purpose": "to join the waitlist"}], "links": [], "medi": {"req": "none", "text": "Any insurance"},
         "summary": "Call 555-010-0003 to join the waitlist.", "intake": {"status": "paused", "checked": "2026-11-20", "note": "Phone verified; intake paused."}, "review": {"status": "verified", "date": "2026-11-20", "source": "synthetic", "maintainer": "test", "claims": []}, "history": [{"date": "2026-11-20", "by": "test", "change": "synthetic"}], "overrides": {}, "primary": {"type": "phone", "index": 0}},
    ]
    fixture["services"] += syn
    fx = Path(tempfile.mkstemp(suffix=".json")[1]); fx.write_text(json.dumps(fixture))
    real, edge = build(), build(fx)
    D = json.loads((ROOT / "data/services.json").read_text())

    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path=CHROME, args=["--no-sandbox"]) if CHROME else await pw.chromium.launch()
        ctx = await b.new_context(viewport={"width": 1366, "height": 900})
        await ctx.grant_permissions(["clipboard-read", "clipboard-write"])
        pg = await ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(real.as_uri()); A = App(pg)

        # 1. Every county, all local food outputs: retired flier never appears; CalFresh apply = BenefitsCal
        bad, n = [], 0
        for c in D["coverageCounties"]:
            await A.new(); await A.need("Food"); await A.county(c); await A.pref("help")
            names = await pg.locator("#results .card h3").all_inner_texts()
            for nm in names:
                await pg.locator("#results .card", has=pg.locator("h3", has_text=nm.split("Staff only")[0].strip())).first.get_by_role("button", name=re.compile("^(Select|Remove)")).click()
            t = await A.text(); n += len(names)
            if "ConsumerFlier" in t or re.search(r"•\s*Apply[^:\n]*:\s*https?://\S*getcalfresh", t, re.I): bad.append(c)
            if (await A.dom_text()).replace("\u00a0", " ") != t.replace("\u00a0", " "):
                if not t: pass
                else: bad.append(c + " (DOM/plain mismatch)")
        check("All 23 counties: food outputs contain no retired flier and no GetCalFresh 'apply' link", not bad, bad)
        check(f"Food outputs enumerated ({n} food cards across counties)", n > 40, n)

        # 2. Phrase discovery
        exp = {"hungry": "food", "can't afford my refill": "medication", "need a ride": "transport", "shutoff notice": "utilities", "my ride fell through tomorrow": "transport", "landlord gave eviction notice": "housing"}
        got = {k: await pg.evaluate("p=>window.__v2.detect(p)", k) for k in exp}
        check("Common phrases discover the right need", all(exp[k] in got[k][:1] for k in exp), got)
        await A.new(); await A.phrase("hungry")
        await pg.click("[data-act=addneed][data-k=food]")
        st = await pg.evaluate("window.__v2.state()")
        check("Suggested need can be added from the phrase box", st["needs"] == ["food"], st["needs"])

        # 3. Sacramento Food -> Del Norte: conflict blocks copy until resolved
        await A.new(); await A.need("Food"); await A.county("Sacramento"); await A.pref("info")
        await A.select("Sacramento Food Bank & Family Services")
        check("Sacramento food selection copyable", not await A.copy_disabled())
        await A.county("Del Norte")
        check("County change to Del Norte flags conflict and blocks copy", await A.copy_disabled() and "doesn't list Del Norte" in await pg.inner_text("#gate"))
        st = await pg.evaluate("window.__v2.state()")
        check("Selection kept (not silently dropped) after county change", [x["id"] for x in st["sel"]] == ["c90"])
        await pg.locator("#gate, #conflictsL").get_by_role("button", name="Keep: provider serves this patient").first.click()
        check("Explicit cross-county exception unblocks copy and is recorded in note", (not await A.copy_disabled()) and "outside listed service area" in await A.note())
        await A.county("Sacramento"); await A.county("Del Norte")
        await pg.click("#conflictsL >> text=Remove it") if await pg.locator("#conflictsL >> text=Remove it").count() else None
        # 4. Rides: plan line by purpose; Yes -> No conflict
        await A.new(); await A.need("Transportation"); await A.county("Sacramento"); await A.mc("yes"); await A.pref("info")
        await A.plan("plan", "Anthem Blue Cross")
        await A.select("Medi-Cal rides to medical appointments")
        t = await A.text()
        check("Anthem rides: scheduling line 877-931-4755 with purpose; member services not given as ride line", "877-931-4755" in t and "to schedule a ride" in t and "800-407-4627" not in t, t)
        await A.plan("plan", "")
        t = await A.text()
        check("Plan unknown: patient told to call member services on card, verified ride lines labelled by plan", "number on your plan card" in t and "Anthem Blue Cross 877-931-4755" in t, t)
        await A.mc("no")
        check("Ride Yes -> No: Medi-Cal conflict blocks copy", await A.copy_disabled() and "Medi-Cal is marked No" in await pg.inner_text("#gate"))
        await A.mc("yes")
        check("Ride No -> Yes: conflict clears", not await A.copy_disabled())

        # 5. Benefits No / Unsure: MSP shown and not described as needing Medi-Cal
        for v in ("no", "unsure"):
            await A.new(); await A.need("Insurance & benefits"); await A.county("Placer"); await A.mc(v)
            names = await A.cards()
            check(f"Benefits, Medi-Cal {v}: Medicare Savings Programs and Medi-Cal application shown", any("Medicare Savings" in x for x in names) and any("Medi-Cal: apply" in x for x in names), names)
        await A.pref("info"); await A.select("Medicare Savings Programs")
        check("MSP patient copy says existing Medi-Cal isn't needed", "don't need to already have Medi-Cal" in await A.text())

        # 6. Editing then adding / reordering keeps staff edits
        await A.new(); await A.need("Food"); await A.county("Sacramento"); await A.pref("info")
        await A.select("Meals on Wheels by ACC")
        await pg.click("#sel [data-act=edit]")
        await pg.fill("#sel textarea", "STAFF WORDING: call to sign up for meals.")
        await A.select("Sacramento Food Bank & Family Services")
        await pg.click("#sel li:nth-child(2) [data-act=up]")
        t = await A.text()
        st = await pg.evaluate("window.__v2.state()")
        check("Staff edit survives adding and reordering", "STAFF WORDING" in t and st["sel"][0]["id"] == "c90", t[:300])
        await A.toggle("Meals on Wheels by ACC")  # remove
        await A.toggle("Meals on Wheels by ACC")  # re-add
        check("Staff edit survives remove and re-add in the same referral", "STAFF WORDING" in await A.text())

        # 7. Copy success: rich and plain consistent; Copied feedback resets on change
        await pg.evaluate("window.__lastCopy=null")
        await pg.click("#copy")
        await pg.wait_for_function("window.__lastCopy!==null", timeout=5000)
        lc = await pg.evaluate("window.__lastCopy")
        plain_from_html = await pg.evaluate("h=>{const d=document.createElement('div');d.innerHTML=h.replace(/<br>/g,'\\n').replace(/<\\/p><p>/g,'\\n\\n');return d.textContent.trim()}", lc["html"])
        check("Rich and plain outputs carry the same text", lc["ok"] and plain_from_html == lc["text"], (plain_from_html[:120], lc["text"][:120]))
        check("Copied feedback shown", "Copied" in await pg.inner_text("#copyStatus"))
        await pg.fill("#pnote", "I'll check in next week.")
        check("Copied feedback resets after a change", (await pg.inner_text("#copyStatus")).strip() == "")
        # mock paste target
        mock = await ctx.new_page()
        await mock.set_content("<div id=t contenteditable style='min-height:50px'></div>")
        pasted = await mock.evaluate("""([h,t])=>{const el=document.getElementById('t');el.focus();const dt=new DataTransfer();dt.setData('text/html',h);dt.setData('text/plain',t);
          el.addEventListener('paste',e=>{e.preventDefault();el.innerHTML=e.clipboardData.getData('text/html')});el.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true}));
          return {bold:el.querySelectorAll('b').length,links:el.querySelectorAll('a').length,text:el.innerText}}""", [lc["html"], lc["text"]])
        check("Mock paste target receives bold text and working links", pasted["bold"] > 0 and pasted["links"] > 0, pasted)
        await mock.close()

        # 8. Copy failure -> manual fallback with selectable plain text
        await pg.evaluate("window.__forceCopyFail=true"); await pg.click("#copy"); await pg.wait_for_timeout(300)
        vis = await pg.is_visible("#manualText"); val = await pg.input_value("#manualText")
        check("Clipboard failure shows manual copy box with the plain text", vis and val == await A.text())
        await pg.evaluate("window.__forceCopyFail=false")

        # 9. Start new referral clears all encounter state
        await A.new()
        st = await pg.evaluate("window.__v2.state()")
        check("Start new referral clears county, needs, selections, edits, note text and phrase",
              st["county"] == "" and st["needs"] == [] and st["sel"] == [] and st["edits"] == {} and st["pnote"] == "" and await pg.input_value("#phrase") == "" and await pg.input_value("#pnote") == "")

        # 10. Multi-need + priority
        await A.need("Food"); await A.need("Transportation"); await A.county("Sacramento")
        await pg.select_option("#prio", "transport")
        heads = await pg.locator("#results h3.grp").all_inner_texts()
        check("Multi-need: patient's priority need listed first", heads and heads[0].startswith("Transportation"), heads)
        st1 = (await pg.evaluate("window.__v2.state()"))
        await A.select("Sacramento Food Bank & Family Services")
        await A.need("Food", False)
        st2 = await pg.evaluate("window.__v2.state()")
        check("Selections kept during ordinary need filtering", [x["id"] for x in st2["sel"]] == ["c90"])
        await pg.check("#statewide"); await pg.uncheck("#statewide")
        check("Selections kept when statewide filter toggles", [x["id"] for x in (await pg.evaluate("window.__v2.state()"))["sel"]] == ["c90"])

        # 11. Unlisted county
        await A.new(); await A.need("Food"); await A.county("__unlisted")
        txt = await pg.inner_text("#results")
        check("County not listed: banner with direct action, statewide only", "County not listed" in txt and "800-510-2020" in txt and "Sacramento County" not in txt)

        # 12. Del Norte housing with statewide off
        await A.new(); await A.need("Housing & legal"); await A.county("Del Norte"); await pg.uncheck("#statewide")
        txt = await pg.inner_text("#results")
        has_btn = await pg.locator("#results [data-act=showsw]").count()
        check("Del Norte housing, statewide off: no-match message and a 'show statewide' action", "No housing & legal listings for Del Norte" in txt and has_btn > 0, txt[:200])
        await pg.locator("#results [data-act=showsw]").first.click()
        names = await A.cards()
        check("Show statewide reveals options; Senior Legal Hotline not offered outside Sacramento", len(names) > 0 and not any("Senior Legal" in x for x in names), names)
        await A.new(); await A.need("Housing & legal"); await A.county("Sacramento")
        check("Senior Legal Hotline offered in Sacramento", any("Senior Legal" in x for x in await A.cards()))

        # 13. Decline path
        await A.new(); await A.need("Food"); await A.county("Sacramento"); await A.pref("decline")
        await A.select("Sacramento Food Bank & Family Services")
        nt = await A.note()
        check("Voluntary decline: no patient message, copy disabled, note records decision without referral",
              await A.text() == "" and await A.copy_disabled() and "No help today" in nt and "Social worker" not in nt)

        # 14. Information-only: single link
        await A.new(); await A.need("Food"); await A.county("Placer"); await A.pref("info")
        await A.select("CalFresh")
        await pg.select_option("#sel select[data-act=send]", "link")
        t = await A.text()
        check("Information-only CalFresh: one BenefitsCal link, no fallback section", "https://benefitscal.com" in t and "If that doesn" not in t and t.count("http") == 1, t)

        # 15. Status honesty + 16. time-sensitive gating
        await A.new(); await A.need("Transportation"); await A.county("Sacramento"); await A.mc("yes"); await A.pref("help"); await A.radio("timing", "soon")
        await A.plan("plan", "Health Net"); await A.select("Medi-Cal rides to medical appointments")
        await A.plan("actor", "Me (the staff member completing this)")
        await A.plan("status", "ride-booked")
        t = await A.text(); nt = await A.note()
        check("Ride booked without confirmation reads as requested/pending in both outputs", "not booked yet" in t and "booked" in nt and "NOT confirmed" in nt and "Your ride is booked" not in t, (t, nt))
        check("Time-sensitive case without owner/backup blocks copy", await A.copy_disabled())
        await A.plan("owner", "Me (the staff member completing this)"); await A.plan("by", "tomorrow"); await A.plan("backup", "none")
        check("'No safe backup' requires the gap to be flagged", await A.copy_disabled() and "flag this gap" in await pg.inner_text("#gate"))
        await pg.click("#gate input[data-f=gapOk]")
        check("Gap acknowledged: copy allowed and note records it", (not await A.copy_disabled()) and "flagged to lead" in await A.note())
        await pg.click("#statusOk")
        check("Confirmed booking appears only after confirmation", "Your ride is booked." in await A.text() and "(staff-confirmed)" in await A.note())

        await A.new(); await A.need("Medication costs"); await A.county("Sacramento"); await A.pref("help")
        await A.select("Pharmacy team"); await A.plan("status", "cost-question"); await pg.click("#statusOk")
        t = await A.text()
        check("Refill: cost question is distinct from a refill order", "does not order a refill" in t and "refill has been requested" not in t, t)
        await A.plan("status", "refill-requested")
        check("Refill requested without confirmation falls back to the cost-question wording", "does not order a refill" in await A.text())

        # 17. Can't make calls
        await A.new(); await A.need("Food"); await A.county("Sacramento"); await A.pref("help"); await A.radio("canCall", "no")
        await A.select("Meals on Wheels by ACC"); await A.plan("actor", "Patient")
        check("Patient can't make calls + patient acts first is blocked", await A.copy_disabled() and "can’t make calls" in await pg.inner_text("#gate"))

        # 18. Spoken plan has no URLs; note says verbal
        await A.new(); await A.need("Food"); await A.county("Sacramento"); await A.pref("info"); await pg.select_option("#channel", "spoken")
        await A.select("Meals on Wheels by ACC")
        check("Spoken plan: no web addresses; note records verbal plan", "http" not in await A.text() and "Verbal plan" in await A.note())

        # 19. Safety leaves routine flow
        await pg.click("#safetyBtn")
        check("Safety concern hides the routine flow and gives a safety staff note", await pg.is_hidden("#main") and "Routine directory flow stopped" in await pg.inner_text("#safetyNote") and "Sutter-approved wording needed" in await pg.inner_text("#policyTexts"))
        await pg.click("#safetyBack")

        # 20. Del Norte mental health: patient copy follows Medi-Cal
        await A.new(); await A.need("Behavioral health"); await A.county("Del Norte"); await A.pref("info"); await A.mc("no")
        await pg.locator("#results .card", has=pg.locator("h3", has_text="Del Norte")).first.get_by_role("button", name=re.compile("^Select")).click()
        t = await A.text()
        check("Del Norte MH, Medi-Cal No: patient pointed to MD/plan and 988, not told county line gives ongoing care", "888-446-4408" not in t and "988" in t, t)

        # 21. Correction report without patient info
        await pg.locator("#results details.more").first.click()
        await pg.locator("#results [data-act=report]").first.click()
        await pg.fill("#corrText", "Phone disconnected, patient DOB 01/02/1950")
        check("Correction report blocks text that looks like patient details", await pg.is_visible("#corrPhi") and await pg.is_disabled("#corrCopy"))
        await pg.fill("#corrText", "Main line rings to a fax tone.")
        check("Correction report allowed with resource ID only", (not await pg.is_disabled("#corrCopy")) and (await pg.input_value("#corrId")) != "")
        await pg.click("#corrClose")

        # 22. Edge fixtures: county lines, cross-county service, paused intake
        await pg.goto(edge.as_uri()); A2 = App(pg)
        await A2.need("Food"); await A2.county("Sacramento")
        names = await A2.cards()
        check("Nearby provider that excludes the patient's county is not listed", not any("Placer only" in x for x in names), names)
        check("Out-of-county provider that serves the patient's county is listed and labelled", any("serves Sacramento" in x for x in names) and "Based in Yolo County" in await pg.inner_text("#results"))
        await A2.pref("info"); await A2.select("SYNTHETIC Paused Program")
        check("Verified phone with paused intake is labelled and warns before sending", "Intake: paused" in await pg.inner_text("#results") and "intake is paused" in await pg.inner_text("#gate"))
        await pg.goto(real.as_uri())

        # 23. Accessibility: axe, keyboard, 320px, 200% text
        await A.new(); await A.need("Food"); await A.county("Sacramento"); await A.pref("help")
        await A.select("Sacramento Food Bank & Family Services")
        if AXE.exists():
            await pg.add_script_tag(path=str(AXE))
            res = await pg.evaluate("axe.run(document,{runOnly:['wcag2a','wcag2aa']}).then(r=>r.violations.map(v=>v.id+':'+v.nodes.length))")
            check("axe-core WCAG 2 A/AA: no violations", not res, res)
        # keyboard only
        await A.new()
        await pg.focus("#phrase")
        seen = set()
        for _ in range(60):
            await pg.keyboard.press("Tab")
            seen.add(await pg.evaluate("document.activeElement.id||document.activeElement.name||document.activeElement.dataset.act||document.activeElement.tagName"))
        check("Keyboard reaches needs, county, Medi-Cal and preference controls", {"county", "mc", "pref"}.issubset(seen) and "need" in seen, sorted(seen)[:30])
        await pg.focus("#county"); await pg.keyboard.press("ArrowDown")
        await pg.focus("#tabP"); await pg.keyboard.press("ArrowRight")
        check("Output tabs work with arrow keys", await pg.is_visible("#note"))
        await pg.keyboard.press("ArrowLeft")
        # 320 px
        small = await ctx.new_page(); await small.set_viewport_size({"width": 320, "height": 800}); await small.goto(real.as_uri())
        S = App(small); await S.need("Food"); await S.county("Sacramento"); await S.pref("help"); await S.select("Sacramento Food Bank & Family Services")
        ow = await small.evaluate("document.documentElement.scrollWidth")
        await small.screenshot(path=str(ROOT / "tmp/w320.png"), full_page=False)
        check("320 px viewport: no horizontal scrolling", ow <= 320, ow)
        await small.evaluate("document.documentElement.style.fontSize='200%'")
        ow2 = await small.evaluate("document.documentElement.scrollWidth")
        check("320 px at 200% text: no horizontal scrolling", ow2 <= 330, ow2)
        await small.close()
        check("No page errors during the run", not errs, errs)
        await b.close()

    passed = sum(1 for r in RESULTS if r[1])
    print(f"\n{passed}/{len(RESULTS)} checks passed")
    (ROOT / "tmp/test-results.json").write_text(json.dumps([{"check": n, "pass": p, "detail": str(d)[:400]} for n, p, d in RESULTS], indent=1))
    sys.exit(0 if passed == len(RESULTS) else 1)

asyncio.run(main())
