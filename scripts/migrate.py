"""Build data/services.json (v2 schema) from the v1 directory plus source-backed corrections.

v1 data is read-only input (data/legacy-v1.json). Nothing here changes the v1 app.
Run:  python3 scripts/migrate.py
"""
import json, re, copy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V1 = json.loads((ROOT / "data/legacy-v1.json").read_text())
TODAY = "2026-11-20"
MAINT = "Catherine Heaney, LCSW"

NEEDS = [
    {"key": "food", "label": "Food", "v1": ["Food"],
     "synonyms": ["hungry", "hunger", "food", "groceries", "grocery", "meal", "meals", "pantry", "calfresh", "food stamps", "ebt", "no food", "run out of food", "can't afford food", "cook", "cooking", "meals on wheels", "food bank"]},
    {"key": "transport", "label": "Transportation", "v1": ["Transportation"],
     "synonyms": ["ride", "rides", "need a ride", "transportation", "no car", "can't drive", "cannot drive", "bus", "paratransit", "get to appointment", "get to my appointment", "ride fell through", "driver", "dial-a-ride", "taxi"]},
    {"key": "utilities", "label": "Utilities", "v1": ["Utilities"],
     "synonyms": ["shutoff", "shut off", "shut-off", "shutoff notice", "disconnect", "disconnection", "electric", "electricity", "power bill", "pg&e", "pge", "smud", "gas bill", "utility", "utilities", "heating", "cooling", "air conditioning", "energy bill", "water bill"]},
    {"key": "medication", "label": "Medication costs", "v1": ["Medication affordability"],
     "synonyms": ["refill", "can't afford my refill", "afford my medication", "medication cost", "medicine cost", "copay", "co-pay", "prescription", "pharmacy", "drug cost", "pills cost", "extra help", "too expensive"]},
    {"key": "housing", "label": "Housing & legal", "v1": ["Housing & legal", "Legal / housing", "Housing / all needs"],
     "synonyms": ["eviction", "evicted", "rent", "housing", "homeless", "landlord", "legal", "lawyer", "lease", "unsafe housing", "move out"]},
    {"key": "behavioral", "label": "Behavioral health", "v1": ["Behavioral health"],
     "synonyms": ["counseling", "counselor", "therapy", "therapist", "mental health", "anxiety", "anxious", "stress", "grief", "substance", "alcohol", "drinking"]},
    {"key": "isolation", "label": "Loneliness & isolation", "v1": ["Isolation / mood"],
     "synonyms": ["lonely", "loneliness", "isolated", "isolation", "no one to talk to", "alone"]},
    {"key": "caregiver", "label": "Caregiver support", "v1": ["Caregiver (strain, lack of support)"],
     "synonyms": ["caregiver", "caregiving", "burnout", "burned out", "help at home", "ihss", "in-home", "respite", "dementia", "memory"]},
    {"key": "aging", "label": "Aging & senior services", "v1": ["Aging & caregiver info (AAA)", "Aging info"],
     "synonyms": ["senior services", "older adult", "aging", "senior center", "area agency on aging"]},
    {"key": "insurance", "label": "Insurance & benefits", "v1": ["Insurance & benefits", "Insurance / benefits", "Plan benefits"],
     "synonyms": ["medicare premium", "premium", "insurance", "benefits", "medi-cal", "medical", "apply for medi-cal", "medicare savings", "plan benefits", "hicap"]},
    {"key": "phone", "label": "Phone access", "v1": ["Phone & digital access", "Phone access"],
     "synonyms": ["phone", "no phone", "cell phone", "minutes", "lifeline", "internet", "no internet", "wifi"]},
    {"key": "safety", "label": "Safety / crisis", "v1": ["Safety / crisis"],
     "synonyms": ["unsafe", "abuse", "abused", "neglect", "suicidal", "suicide", "hurt myself", "kill myself", "danger", "threatened", "scam", "exploited"]},
]
V1NEED = {v: n["key"] for n in NEEDS for v in n["v1"]}

PHONE_RE = re.compile(r"(?:\(?\d{3}\)?[\s.-]?)?\d{3}-\d{4}(?:\s*(?:ext\.?|x)\s*\d+)?|\b(?:2-1-1|211|911|988)\b")

def parse_links(lines):
    out = []
    for l in lines or []:
        m = re.match(r"^(.*?):\s*(https?://\S+)$", l)
        if m:
            out.append({"label": m.group(1).strip(), "url": m.group(2).strip(), "kind": "info"})
        else:
            url = l.strip()
            if not url.startswith("http"):
                url = "https://" + url
            out.append({"label": "Website", "url": url, "kind": "info"})
    for L in out:
        lab = L["label"].lower()
        if "apply" in lab:
            L["kind"] = "apply"
        if "pdf" in lab:
            L["kind"] = "info"
    return out

def parse_phones(raw, need):
    """Split a v1 phone string into role-labelled entries. Multi-number strings get explicit roles."""
    if not raw:
        return []
    raw = raw.strip()
    segs = [s.strip() for s in raw.split(";")] if ";" in raw else [raw]
    out = []
    for s in segs:
        m = PHONE_RE.search(s)
        num = m.group(0) if m else None
        label = s[: m.start()].strip() if m else s
        role = "main"
        low = s.lower()
        if len(segs) > 1 or need == "transport" and "rides" in low:
            if "rides" in low or "ride" in low:
                role = "ride scheduling"
            elif "member services" in low:
                role = "member services"
            else:
                # v1 listed plan general lines as "ride lines"; they are member services numbers.
                role = "member services"
        e = {"display": s[m.start():].strip() if (m and label) else s, "number": num, "label": label or None, "role": role}
        more = [x.group(0) for x in PHONE_RE.finditer(s)][1:]
        if more:
            e["alsoNumbers"] = more
        if "24/7" in s:
            e["hours"] = "24/7"
        out.append(e)
    return out

def medi_of(m):
    m = (m or "").strip()
    if m in ("Yes", "Medi-Cal"):
        return {"req": "required", "text": "Medi-Cal required"}
    if m.startswith("Ongoing specialty MH"):
        return {"req": "partial", "text": "Ongoing county specialty mental health: Medi-Cal. Crisis response: open to all."}
    if m == "Varies":
        return {"req": "varies", "text": "Varies by program"}
    return {"req": "none", "text": "Any insurance"}

def review_of(r):
    flag = r.get("flag")
    src = r.get("source")
    if not src:
        L = parse_links(r.get("links"))
        src = ("v1 statewide review; primary page " + L[0]["url"]) if L else "v1 statewide review (source page not recorded)"
    return {
        "status": "partly verified" if flag else "verified",
        "date": r.get("verified") or "2026-11-19",
        "source": src,
        "flag": flag,
        "maintainer": MAINT,
        "claims": [],
        "note": "Carried over from v1 directory review. A page load alone never marks a claim verified.",
    }

services = {}
order = []

def base_from(r, need):
    return {
        "id": r["id"],
        "legacyIds": [r["id"]],
        "name": r["name"],
        "label": r.get("label"),
        "need": need,
        "needs": [need],
        "serves": {"type": "counties", "counties": []},
        "basedIn": r.get("county"),
        "phones": parse_phones(r.get("phone"), need),
        "links": parse_links(r.get("links")),
        "web": r.get("web"),
        "who": r.get("who"),
        "how": r.get("how"),
        "notes": r.get("notes"),
        "medi": medi_of(r.get("medi")),
        "summary": r.get("summary"),
        "intake": {"status": "unknown", "note": None, "checked": None, "how": None},
        "review": review_of(r),
        "history": [{"date": TODAY, "by": MAINT, "change": "Imported from v1 directory"}],
        "overrides": {},
    }

DIFF_FIELDS = ["phones", "links", "who", "how", "notes", "summary", "medi", "label", "web", "review"]

# ---- county records: merge same service across counties, keep county-specific overrides
for r in V1["county"]:
    need = V1NEED[r["need"]]
    key = (r["name"], need) if r["name"] != "Medi-Cal rides to medical appointments" else (r["name"], need)
    cand = base_from(r, need)
    if key not in services:
        services[key] = cand
        order.append(key)
        services[key]["serves"]["counties"].append(r["county"])
    else:
        s = services[key]
        s["legacyIds"].append(r["id"])
        s["serves"]["counties"].append(r["county"])
        s["basedIn"] = None  # merged across counties: no single home county recorded in v1
        ov = {f: cand[f] for f in DIFF_FIELDS if cand[f] != s[f]}
        if ov:
            s["overrides"][r["county"]] = ov

# ---- statewide records
for r in V1["state"]:
    need = V1NEED[r["need"]] if r["need"] in V1NEED else ("medication" if r["need"] == "Medication affordability" else None)
    s = base_from(r, need)
    s["basedIn"] = None
    s["serves"] = {"type": "statewide"}
    ql = r.get("ql") or ""
    if ql == "Always":
        s["always"] = True
        s["needs"] = ["safety"]
    elif ql == "NOCOUNTY":
        s["needs"] = [need]
        s["onlyWithoutCounty"] = True
    else:
        extra = [V1NEED.get(x.strip()) for x in ql.split(";") if x.strip()]
        s["needs"] = sorted(set([need] + [e for e in extra if e]))
    key = (r["id"],)
    services[key] = s
    order.append(key)

S = {services[k]["id"]: services[k] for k in order}

def claim(sid, text, url, date=TODAY):
    S[sid]["review"]["claims"].append({"claim": text, "url": url, "checked": date})

def hist(sid, text):
    S[sid]["history"].append({"date": TODAY, "by": MAINT, "change": text})

# =====================================================================
# Source-backed corrections (Step 1 of the brief)
# =====================================================================
RETIRED = [
    {"pattern": "ConsumerFlier_7_OlderAdults_English.pdf",
     "reason": "Retired shared material (older-adult CalFresh flier). Replaced by CDSS SSI & CalFresh page and BenefitsCal for applications.",
     "retired": TODAY},
]
BENEFITSCAL = {"label": "Apply for CalFresh online at BenefitsCal, the state benefits website", "url": "https://benefitscal.com", "kind": "apply"}
GCF_INFO = {"label": "CalFresh information and help applying (GetCalFresh)", "url": "https://www.getcalfresh.org", "kind": "help"}
SSI_INFO = {"label": "CalFresh for people on SSI (CDSS)", "url": "https://cdss.ca.gov/food/home/ssi-and-calfresh", "kind": "info"}

def fix_food_links(links):
    out = []
    for L in links:
        if "ConsumerFlier" in L["url"]:
            continue
        if "getcalfresh" in L["url"]:
            out.append(dict(BENEFITSCAL))
            continue
        out.append(L)
    return out

for s in S.values():
    touched = False
    for holder in [s] + list(s["overrides"].values()):
        if "links" in holder:
            new = fix_food_links(holder["links"])
            if new != holder["links"]:
                holder["links"] = new
                touched = True
    if touched:
        hist(s["id"], "Retired the older-adult CalFresh flier PDF link; CalFresh application now points to BenefitsCal")
        claim(s["id"], "CalFresh applications are made online at BenefitsCal.com (CDSS CalFresh page: 'apply online at BenefitsCal.com').", "https://www.cdss.ca.gov/CalFresh")

# --- CalFresh statewide (s17)
c = S["s17"]
c["phones"] = [{"display": "877-847-3663", "number": "877-847-3663", "label": "CalFresh Info Line", "role": "information line", "purpose": "to ask about CalFresh or get help applying"}]
c["links"] = [dict(BENEFITSCAL), dict(SSI_INFO), dict(GCF_INFO)]
c["who"] = "Income-eligible households. Since June 1, 2019, people who get SSI may be eligible; applying does not change SSI."
c["how"] = "Applications: BenefitsCal.com or county office. GetCalFresh is CDSS-supported information and help, not the application of record. Pair with Nutritionist."
c["summary"] = "CalFresh gives you money each month to buy groceries. Many older adults qualify, including people who get SSI, and applying does not change your SSI. Apply online at BenefitsCal, or call the CalFresh Info Line at 877-847-3663 for help."
c["script"] = "I'd like to apply for CalFresh. Can you help me get started?"
c["prepare"] = "Proof of income and expenses, such as utility bills and medical costs, can help."
c["review"].update({"status": "verified", "date": TODAY, "flag": None, "source": "CDSS CalFresh program page; CDSS SSI & CalFresh page; CDSS GetCalFresh transition notice"})
claim("s17", "Since June 1, 2019, SSI recipients may be eligible for CalFresh; CalFresh doesn't affect other benefits.", "https://cdss.ca.gov/food/home/ssi-and-calfresh")
claim("s17", "CalFresh Info Line 1-877-847-3663.", "https://www.cdss.ca.gov/CalFresh")
claim("s17", "GetCalFresh.org continues as CDSS-supported digital outreach about how to apply through BenefitsCal.", "https://cdss.ca.gov/inforesources/cdss-programs/calfresh-outreach/getcalfresh-transition")
hist("s17", "Split apply (BenefitsCal) from information/help (GetCalFresh); replaced retired flier with CDSS SSI page")

# --- Sacramento Food Bank (c90): Food Finder for groceries
f = S["c90"]
f["phones"] = [
    {"display": "916-779-0052", "number": "916-779-0052", "label": "CalFresh Outreach team", "role": "application help", "purpose": "for help applying for CalFresh"},
    {"display": "916-456-1980", "number": "916-456-1980", "label": "Main line", "role": "main", "purpose": "for general questions"},
]
f["links"] = [
    {"label": "Food Finder (a map of free food sites near you)", "url": "https://www.sacramentofoodbank.org/find-food", "kind": "finder"},
    dict(BENEFITSCAL),
]
f["primary"] = {"type": "link", "index": 0}
f["summary"] = "Use the Food Finder to see free food sites near you, with days and times. It's a good idea to call the site before you go to confirm hours. For help applying for CalFresh, call their CalFresh team at 916-779-0052."
f["how"] = "Give the Food Finder link; SFBFS supplies 112 partner pantries and does not hand out food at its Bell Ave distribution center. CalFresh help: 916-779-0052."
f["intake"] = {"status": "unknown", "note": "Food is distributed at partner sites; days and times are listed in the Food Finder. Same-day availability not checked.", "checked": TODAY, "how": "SFBFS website (Find Food page and FAQ)"}
f["review"].update({"status": "verified", "date": TODAY, "flag": None, "source": "Sacramento Food Bank & Family Services website"})
claim("c90", "Food Finder tool locates partner distribution sites; SFBFS does not distribute food directly from its Bell Avenue distribution center.", "https://sacramentofoodbank.org")
claim("c90", "CalFresh questions or application help: (916) 779-0052.", "https://www.sacramentofoodbank.org/find-food")
hist("c90", "Primary action is now the Food Finder link; CalFresh help number added with its purpose")

# --- Medi-Cal rides: role-labelled plan numbers; Sacramento (and every Anthem county) gets verified scheduling lines
PLAN_RIDES = {
    "Anthem Blue Cross": {"ride": {"display": "877-931-4755", "number": "877-931-4755", "role": "ride scheduling", "hours": "Mon–Fri 7 a.m.–7 p.m.", "purpose": "to schedule a ride",
                                    "timing": "Call at least 5 business days before the appointment (7 for first-time riders)."},
                          "member": {"display": "800-407-4627", "number": "800-407-4627", "role": "member services", "purpose": "for plan questions"},
                          "claims": [("Anthem Medi-Cal ride scheduling 1-877-931-4755 (TTY 711), Mon–Fri 7 a.m.–7 p.m.; call at least 5 business days ahead, 7 for new riders; NEMT and NMT are requested through your doctor.", "https://mss.anthem.com/california-medicaid/benefits/medi-cal-plan-benefits/transportation.html")]},
    "Health Net": {"ride": {"display": "855-253-6863", "number": "855-253-6863", "role": "ride scheduling", "hours": "Mon–Fri 7 a.m.–7 p.m.", "purpose": "to schedule a ride (ModivCare)"},
                   "member": {"display": "800-675-6110", "number": "800-675-6110", "role": "member services", "hours": "24/7", "purpose": "for plan questions or ride problems"},
                   "claims": [("Health Net Medi-Cal rides: ModivCare 1-855-253-6863 (TTY 1-866-288-3133), Mon–Fri 7 a.m.–7 p.m.; Member Services 1-800-675-6110, 24/7.", "https://www.healthnet.com/content/dam/centene/healthnet/pdfs/medi-cal/get-a-ride-for-health-care-services-modivcare.pdf")]},
    "Molina": {"ride": {"display": "844-292-2688", "number": "844-292-2688", "role": "ride scheduling", "hours": "24/7", "purpose": "to schedule a ride (American Logistics)",
                        "timing": "Call at least 3 business days before the appointment."},
               "member": {"display": "888-665-4621", "number": "888-665-4621", "role": "member services", "purpose": "for plan questions", "unverified": True},
               "claims": [("Molina Medi-Cal transportation: American Logistics (844) 292-2688, requests 24/7; recommend 3 business days ahead.", "https://molinahealthcare.com/members/ca/mem/medicaid/medical/coverd/services/transport.aspx")]},
}

def plan_of(label):
    for p in PLAN_RIDES:
        if label and label.lower().startswith(p.lower()):
            return p
    return None

def rebuild_rides(holder, county):
    phones = holder.get("phones", [])
    out, plans = [], []
    for p in phones:
        pl = plan_of(p.get("label"))
        if pl:
            pr = PLAN_RIDES[pl]
            r1 = dict(pr["ride"], label=f"{pl} rides", plan=pl)
            m1 = dict(pr["member"], label=f"{pl} member services", plan=pl)
            out += [r1, m1]
            plans.append(pl)
        else:
            lab = p.get("label") or ""
            pname = re.sub(r"\s+(rides.*|member services.*)$", "", lab).strip() or lab
            q = dict(p, plan=pname)
            if p["role"] == "member services" and "member services" not in lab.lower():
                q["purpose"] = "for plan questions; ask them how to schedule a ride"
                q["unverified"] = True
            elif p["role"] == "ride scheduling":
                q["purpose"] = "to schedule a ride"
            else:
                q["purpose"] = "for plan questions"
            out.append(q)
    holder["phones"] = out
    return plans

RIDE_SUMMARY = "If you have Medi-Cal, your health plan gives free rides to doctor visits and to pick up prescriptions."
for s in S.values():
    if s["name"] != "Medi-Cal rides to medical appointments":
        continue
    plans = rebuild_rides(s, s["basedIn"])
    for cty, ov in s["overrides"].items():
        if "phones" in ov:
            plans += rebuild_rides(ov, cty)
        ov.pop("summary", None)
    s["summary"] = RIDE_SUMMARY
    s["planAware"] = True
    s["fallback"] = "If you can't get through, call the member services number on your plan card and ask for a ride."
    s["script"] = "I'm a Medi-Cal member and I need a ride to a medical appointment."
    s["prepare"] = "Your member ID card, the appointment date and time, and the doctor's name and address."
    s["limits"] = "If you need a wheelchair or stretcher van, ask your doctor's office to send the form your plan needs."
    s["adviceRoutine"] = "Ask for your ride as early as you can."
    for pl in sorted(set(plans)):
        for t, u in PLAN_RIDES[pl]["claims"]:
            claim(s["id"], t, u)
    hist(s["id"], "Plan numbers relabelled by purpose (ride scheduling vs member services); v1 listed member-services lines as ride lines")
    s["review"]["flag"] = "Ride lines verified for Anthem, Health Net, Molina. Other plans show member services; ride line not individually verified. Kaiser Medi-Cal ride line not verified for Northern California."
    s["review"]["status"] = "partly verified"

# --- Senior Legal Hotline: Sacramento County service area only (not statewide)
h = S["s15"]
h["serves"] = {"type": "counties", "counties": ["Sacramento"]}
h["basedIn"] = "Sacramento"
h["needs"] = ["housing"]
h["need"] = "housing"
h["phones"] = [{"display": "916-551-2140", "number": "916-551-2140", "role": "main", "purpose": "for free legal advice"},
               {"display": "800-222-1753", "number": "800-222-1753", "role": "toll-free", "purpose": "toll-free line"}]
h["who"] = "Sacramento County residents age 60+, regardless of income. Landlord/tenant: advises tenants in eviction (unlawful detainer) cases."
h["how"] = "Patient calls for free civil legal advice (housing/eviction, consumer, public benefits, estate planning). Not a statewide housing service: outside Sacramento County use 2-1-1 or the county listing."
h["summary"] = "If you live in Sacramento County and are 60 or older, call 916-551-2140 for free legal advice by phone, including help if you are facing eviction."
h["review"].update({"status": "partly verified", "date": TODAY,
                    "flag": "LSNC's own page could not be loaded on 2026-11-20; service area taken from three directory listings (iCarol, Pro Bono Net, findhelp). Confirm with LSNC.",
                    "source": "Directory listings for LSNC Senior Legal Hotline / Senior Legal Services"})
claim("s15", "Provides free legal advice to Sacramento County residents age 60 and over; for landlord/tenant disputes, advises tenants in eviction cases.", "https://www.icarol.info/ResourceView2.aspx?org=2264&agencynum=4092912")
claim("s15", "Coverage area: Sacramento County, CA.", "https://www.findhelp.org/legal-services-of-northern-california-(lsnc)--woodland-ca-senior-legal-hotline/4828940059279360")
hist("s15", "Restricted from statewide to Sacramento County residents 60+")

# --- Medicare Savings Programs split from Medi-Cal coverage
m = S["s18"]
msp = copy.deepcopy(m)
msp.update({
    "id": "s18a", "legacyIds": ["s18"], "name": "Medicare Savings Programs (help paying Medicare costs)",
    "needs": ["insurance", "medication"], "need": "insurance",
    "medi": {"req": "none", "text": "Does not require existing Medi-Cal. Apply through the county or BenefitsCal."},
    "phones": [{"display": "800-434-0222", "number": "800-434-0222", "label": "HICAP", "role": "application help", "purpose": "for free help checking if you qualify"},
               {"display": "800-541-5555", "number": "800-541-5555", "label": "Medi-Cal Helpline", "role": "information line", "purpose": "to find your county office"}],
    "links": [{"label": "Apply online (BenefitsCal)", "url": "https://benefitscal.com", "kind": "apply"},
              {"label": "About Medicare Savings Programs (DHCS)", "url": "https://www.dhcs.ca.gov/individuals/Pages/Medicare-Savings-Programs-in-California.aspx", "kind": "info"}],
    "who": "Medicare beneficiaries with limited income. Asset test eliminated January 1, 2024 (DHCS). Existing Medi-Cal is not required.",
    "how": "HICAP screens and helps apply; or county office / BenefitsCal. MSP-only paper application: MC 14A to county.",
    "summary": "Medicare Savings Programs can help pay your Medicare premiums. You don't need to already have Medi-Cal. Call HICAP at 800-434-0222 for free help checking if you qualify, or apply online at BenefitsCal.",
    "script": "I have Medicare and I'd like to see if I qualify for a Medicare Savings Program.",
})
msp["review"] = {"status": "verified", "date": TODAY, "flag": None, "maintainer": MAINT, "source": "DHCS Medicare Savings Programs in California",
                 "claims": [{"claim": "Starting January 1, 2024, the MSP asset test was eliminated; apply online at BenefitsCal, in person at the county office, or find the county office via the Medi-Cal Helpline (800) 541-5555; MSP-only applicants may use form MC 14A.", "url": "https://www.dhcs.ca.gov/individuals/Pages/Medicare-Savings-Programs-in-California.aspx", "checked": TODAY}],
                 "note": "Income limits are not shown to patients; they change yearly."}
msp["history"] = [{"date": TODAY, "by": MAINT, "change": "Split from v1 's18' so MSP help is not hidden when the patient has no Medi-Cal"}]
mc = copy.deepcopy(m)
mc.update({
    "id": "s18b", "legacyIds": ["s18"], "name": "Medi-Cal: apply or check coverage",
    "needs": ["insurance"], "need": "insurance",
    "medi": {"req": "none", "text": "For people without Medi-Cal or unsure of coverage."},
    "phones": [{"display": "800-541-5555", "number": "800-541-5555", "label": "Medi-Cal Helpline", "role": "information line", "purpose": "for questions or to find your county office"}],
    "links": [{"label": "Apply online (BenefitsCal)", "url": "https://benefitscal.com", "kind": "apply"}],
    "who": "Income-eligible Californians; coverage questions.",
    "how": "Apply on BenefitsCal or at the county office. Use when Medi-Cal is No/Unsure and cost or coverage is the barrier.",
    "summary": "You can apply for Medi-Cal online at BenefitsCal or at your county office. For questions, call the Medi-Cal Helpline at 800-541-5555.",
})
mc["review"] = {"status": "verified", "date": TODAY, "flag": None, "maintainer": MAINT, "source": "DHCS Medicare Savings Programs in California",
                "claims": [{"claim": "Apply for Medi-Cal online at BenefitsCal or in person at the county office; Medi-Cal Helpline (800) 541-5555.", "url": "https://www.dhcs.ca.gov/individuals/Pages/Medicare-Savings-Programs-in-California.aspx", "checked": TODAY}]}
mc["history"] = [{"date": TODAY, "by": MAINT, "change": "Split from v1 's18' (Medi-Cal application kept separate from MSP help)"}]
del S["s18"]
S["s18a"] = msp
S["s18b"] = mc

# --- County mental health lines: staff/patient eligibility distinction (Del Norte reviewed; same pattern applied to every county line)
for s in S.values():
    if s["medi"]["req"] != "partial":
        continue
    s["summary"] = s["summary"]  # kept for Medi-Cal Yes
    num = next((p["display"] for p in s["phones"] if p.get("number")), None)
    s["summaryByMedi"] = {
        "yes": f"If you have Medi-Cal, call {num} to get connected to county mental health care, like counseling.",
        "no": "For ongoing counseling, ask your doctor for a referral or call the number on your health plan card. If you are ever in crisis, you can call or text 988 anytime.",
        "unsure": f"If you have Medi-Cal, call {num} to get connected to county mental health care. If you have Medicare or other insurance, ask your doctor for a referral or call the number on your plan card.",
    }
    s["staffNote"] = "County specialty mental health is a Medi-Cal benefit. Medicare/commercial: route ongoing care via MD or plan; county line for crisis only. Routine positive mood screens follow the team workflow (AI-CBT)."
    hist(s["id"], "Patient copy now follows Medi-Cal status (ongoing care is Medi-Cal; crisis open to all); no 24/7 claim in patient copy")
S["c35"]["review"]["claims"].append({"claim": "Del Norte County mental health plan access line 888-446-4408 (DHCS county MHP contact list). 24/7 status not stated by DHCS.", "url": "https://www.dhcs.ca.gov/individuals/Pages/MHPContactList.aspx", "checked": "2026-11-20"})

# --- Pharmacy team is internal: never patient-facing as a phone number
p = S["s11"]
p["staffOnly"] = True
p["phones"] = []
p["summary"] = "Our pharmacy team will look at ways to lower the cost of your medicine."
p["how"] = "Internal: send the cost question to the pharmacy team through the approved workflow. Do not record 'refill requested' unless a refill order was actually placed."

# Friendship Line hours were confirmed in the v1 review; record them on the phone entry
S["s6"]["phones"][0]["hours"] = "24/7"
S["s6"]["phones"][0]["purpose"] = "to talk with someone friendly, any time"

# County 2-1-1 lines also cover food and utility help (their own names say so)
for s in S.values():
    if s["name"].startswith("2-1-1"):
        s["needs"] = sorted(set(s["needs"] + ["housing", "utilities", "food"]))

# Need-level fallbacks (verified numbers only)
FALLBACK = {
    "food": {"text": "If you can't reach them, call the CalFresh Info Line at 877-847-3663 for help applying for food benefits.", "ids": ["s17"]},
    "transport": {"text": "If you can't get through, call the member services number on your health plan card and ask about rides.", "ids": []},
    "utilities": {"text": "You can also call the customer service number on your utility bill and ask about payment plans and bill discounts.", "ids": []},
    "medication": {"text": "You can also call HICAP at 800-434-0222 for free help lowering Medicare drug costs.", "ids": ["s8"]},
    "housing": {"text": "If you can't reach them, call 2-1-1 to find other local help.", "ids": ["s16"]},
    "behavioral": {"text": "If you are ever in crisis, you can call or text 988 anytime.", "ids": ["s3"]},
    "isolation": {"text": "You can also call the California Aging & Adult Information Line at 800-510-2020 to find local programs.", "ids": ["s7"]},
    "caregiver": {"text": "You can also call the California Aging & Adult Information Line at 800-510-2020 to find caregiver help near you.", "ids": ["s7"]},
    "aging": {"text": "You can also call the California Aging & Adult Information Line at 800-510-2020.", "ids": ["s7"]},
    "insurance": {"text": "You can also call HICAP at 800-434-0222 for free, unbiased Medicare help.", "ids": ["s8"]},
    "phone": {"text": "If you can't reach them, call 2-1-1 to find other local help.", "ids": ["s16"]},
    "safety": {"text": "", "ids": []},
}
for n in NEEDS:
    n["fallback"] = FALLBACK[n["key"]]
    n.pop("v1")

# primary action default: first phone with a number, else first link
for s in S.values():
    if "primary" not in s:
        s["primary"] = {"type": "phone", "index": 0} if any(p.get("number") for p in s["phones"]) else ({"type": "link", "index": 0} if s["links"] else {"type": "none"})

out = {
    "schema": 2,
    "updated": TODAY,
    "coverageCounties": sorted({c for s in S.values() for c in (s["serves"].get("counties") or [])}),
    "retired": RETIRED,
    "needs": NEEDS,
    "opening": "It was great speaking with you today, and thank you for your time! Here is what we talked about.",
    "openingInfo": "Here is the information you asked for.",
    "closing": "If your symptoms are severe or getting worse, seek medical care right away. For an emergency, call 911. For a mental health crisis, you can call or text 988 anytime.",
    "services": list(S.values()),
}
(ROOT / "data/services.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print("services", len(out["services"]), "counties", len(out["coverageCounties"]))
