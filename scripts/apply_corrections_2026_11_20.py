"""One-time resource corrections (checked against official sources on 2026-11-20), applied to data/resources.json.
Keeps the original app's schema and workflow. See VERIFICATION.md for each claim and source.
Already applied; running it again is a no-op.
"""
import json, re
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "data/resources.json"
D = json.loads(P.read_text())
if D.get("corrections") == "2026-11-20":
    print("already applied"); raise SystemExit
TODAY = "2026-11-20"
R = {r["id"]: r for r in D["county"] + D["state"]}
BENEFITSCAL = "Apply for CalFresh online (BenefitsCal): https://benefitscal.com"
SSI = "CalFresh for people on SSI (CDSS): https://cdss.ca.gov/food/home/ssi-and-calfresh"
GCF = "CalFresh information and help applying (GetCalFresh): https://www.getcalfresh.org"

# 1. Retire the older-adult CalFresh flier; applications point to BenefitsCal
for r in D["county"] + D["state"]:
    out = []
    for l in r.get("links") or []:
        if "ConsumerFlier" in l:
            continue
        if "getcalfresh" in l:
            l = BENEFITSCAL
        if l not in out and not (l == "https://benefitscal.com" and BENEFITSCAL in out):
            out.append(l)
    r["links"] = out

# 2. CalFresh (statewide)
c = R["s17"]
c["links"] = [BENEFITSCAL, SSI, GCF]
c["who"] = "Income-eligible households. Since June 1, 2019, people who get SSI may be eligible; applying does not change SSI."
c["how"] = "Applications: BenefitsCal.com or the county office. GetCalFresh is information and help applying, not the application of record. Pair with Nutritionist."
c["summary"] = "CalFresh gives you money each month to buy groceries. Many older adults qualify, including people who get SSI, and applying does not change your SSI. Apply online at BenefitsCal, or call the CalFresh Info Line at 877-847-3663 for help."
c.update(flag=None, verified=TODAY, source="CDSS CalFresh and SSI & CalFresh pages")

# 3. Sacramento Food Bank: Food Finder first, CalFresh line labelled by purpose
f = R["c90"]
f["phone"] = "916-779-0052 (CalFresh help); main line 916-456-1980"
f["how"] = "Give the Food Finder link (partner pantries, days and times); SFBFS does not hand out food at its Bell Ave distribution center. CalFresh application help: 916-779-0052. Pair with Nutritionist."
f["links"] = ["Food Finder (a map of free food sites near you): https://www.sacramentofoodbank.org/find-food", BENEFITSCAL]
f["summary"] = "Use the Food Finder to see free food sites near you, with days and times. It's a good idea to call the site before you go to confirm hours. For help applying for CalFresh, call their CalFresh team at 916-779-0052."
f.update(verified=TODAY, source="Sacramento Food Bank & Family Services website (Find Food page, FAQ)")

# 4. Medi-Cal rides: ride scheduling vs member services, verified ride lines
RIDE = {"Anthem Blue Cross": ("877-931-4755", "800-407-4627"), "Health Net": ("855-253-6863", "800-675-6110"), "Molina": ("844-292-2688", "888-665-4621")}
for r in D["county"]:
    if r["name"] != "Medi-Cal rides to medical appointments":
        continue
    rides, members = [], []
    for seg in [s.strip() for s in r["phone"].split(";")]:
        m = re.search(r"(\d{3}-\d{3}-\d{4})", seg)
        label = seg[: m.start()].strip() if m else seg
        num = m.group(1) if m else ""
        plan = next((p for p in RIDE if label.startswith(p)), None)
        if plan:
            rides.append(f"{plan} {RIDE[plan][0]}")
            members.append(f"{plan} {RIDE[plan][1]}")
        elif "rides" in label.lower():
            rides.append(f"{label.replace(' rides', '')} {num}".replace("  ", " "))
        elif "member services" in label.lower():
            members.append(f"{label.replace(' member services', '')} {num}")
        else:
            members.append(f"{label} {num}")
    parts = []
    if rides:
        parts.append("Ride scheduling: " + "; ".join(rides))
    if members:
        parts.append("Member services: " + "; ".join(members))
    r["phone"] = ". ".join(parts)
    s = "If you have Medi-Cal, your health plan gives free rides to covered medical appointments, including picking up prescriptions. Call as early as you can (most plans ask for 3 to 5 business days' notice)."
    if rides:
        s += " To schedule a ride, call your plan's ride line: " + "; ".join(rides) + "."
    other = [m for m in members if not any(m.startswith(x.split(" ")[0]) for x in rides)]
    if other:
        s += " For other plans, call the member services number on your plan card and ask for a ride: " + "; ".join(other) + "."
    elif not rides:
        s += " Call the member services number on your plan card and ask for a ride."
    r["summary"] = s
    r["how"] = ("Use the plan's ride scheduling line, not member services. Anthem rides Mon–Fri 7–7, 5 business days' notice (7 for new riders); Health Net (ModivCare) Mon–Fri 7–7; "
                "Molina (American Logistics) 24/7, 3 business days. NEMT (wheelchair or litter van) needs a provider-signed PCS form. Medicare-only patients: check MA plan transportation benefit instead.")
    r["flag"] = "Ride lines verified for Anthem, Health Net, Molina. Other plans listed as member services; Kaiser ride line not verified."
    r["verified"] = TODAY
    r["source"] = "Anthem, Health Net and Molina Medi-Cal transportation pages; DHCS Transportation Services"

# 5. Senior Legal Hotline: Sacramento County residents 60+ only (moved from statewide)
s15 = R["s15"]
D["state"] = [x for x in D["state"] if x["id"] != "s15"]
D["county"].append({
    "id": "c216", "county": "Sacramento", "need": "Housing & legal",
    "label": "Senior Legal Hotline (Legal Services of Northern CA)", "name": "Senior Legal Hotline",
    "phone": "916-551-2140 (toll-free 800-222-1753)", "medi": "No",
    "who": "Sacramento County residents age 60+, regardless of income. Landlord/tenant: advises tenants in eviction cases.",
    "how": "Free phone legal advice (housing/eviction, consumer, public benefits, estate planning). Not a statewide housing service.",
    "web": "https://lsnc.net", "notes": None,
    "source": "iCarol, Pro Bono Net and findhelp listings (LSNC page not reachable 2026-11-20)", "verified": TODAY,
    "flag": "Service area from directory listings; confirm with LSNC.",
    "links": ["https://lsnc.net"],
    "summary": "If you live in Sacramento County and are 60 or older, call 916-551-2140 for free legal advice by phone, including help if you are facing eviction.",
})

# 6. Medicare Savings Programs split from the Medi-Cal application
m = R["s18"]
m.update({
    "name": "Medicare Savings Programs (help paying Medicare costs)", "label": "Medicare Savings Programs",
    "phone": "HICAP 800-434-0222 (free help applying); Medi-Cal Helpline 800-541-5555 (county office)", "medi": "No",
    "who": "Medicare beneficiaries with limited income. No asset test since January 1, 2024. Existing Medi-Cal not required.",
    "how": "HICAP screens and helps apply; or county office / BenefitsCal. MSP-only paper application: MC 14A.",
    "links": ["Apply online (BenefitsCal): https://benefitscal.com", "About Medicare Savings Programs (DHCS): https://www.dhcs.ca.gov/individuals/Pages/Medicare-Savings-Programs-in-California.aspx"],
    "summary": "Medicare Savings Programs can help pay your Medicare premiums. You don't need to already have Medi-Cal. Call HICAP at 800-434-0222 for free help checking if you qualify, or apply online at BenefitsCal.",
    "flag": None, "verified": TODAY, "source": "DHCS Medicare Savings Programs in California",
})
D["state"].append({
    "id": "s30", "need": "Insurance / benefits", "label": "Medi-Cal application", "name": "Medi-Cal: apply or check coverage",
    "phone": "800-541-5555", "medi": "No",
    "who": "Income-eligible Californians without Medi-Cal, or unsure of coverage.",
    "how": "Apply on BenefitsCal or at the county office. Use when Medi-Cal is No/Unsure and cost or coverage is the barrier.",
    "flag": None, "ql": "Insurance & benefits",
    "links": ["Apply online (BenefitsCal): https://benefitscal.com"],
    "summary": "You can apply for Medi-Cal online at BenefitsCal or at your county office. For questions, call the Medi-Cal Helpline at 800-541-5555.",
    "verified": TODAY, "source": "DHCS Medicare Savings Programs in California",
})

# 7. County mental health lines: patient wording follows Medi-Cal status
for r in D["county"]:
    if not (r.get("medi") or "").startswith("Ongoing specialty MH"):
        continue
    num = re.search(r"\d{3}-\d{3}-\d{4}", r["phone"] or "").group(0)
    r["summaryByMedi"] = {
        "yes": f"If you have Medi-Cal, call {num} to get connected to county mental health care, like counseling.",
        "no": "For ongoing counseling, ask your doctor for a referral or call the number on your health plan card. If you are ever in crisis, you can call or text 988 anytime.",
        "unsure": f"If you have Medi-Cal, call {num} to get connected to county mental health care. If you have Medicare or other insurance, ask your doctor for a referral or call the number on your plan card.",
    }

D["updated"] = TODAY
D["corrections"] = TODAY
P.write_text(json.dumps(D, indent=1, ensure_ascii=False))
print("applied:", len(D["county"]), "county,", len(D["state"]), "statewide")
