"""2026-11-21 updates to data/resources.json:
- link check results (broken links replaced, moved links updated, unconfirmable links flagged)
- suggested ICD-10-CM Z-codes per need (FY2027 code set, effective Oct 1, 2026; source: CMS MS-DRG v44.0 Definitions Manual)
- "updated" date on every resource
Running it again is a no-op.
"""
import json, re
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "data/resources.json"
D = json.loads(P.read_text())
if D.get("updates") == "2026-11-21":
    print("already applied"); raise SystemExit
TODAY = "2026-11-21"
recs = D["county"] + D["state"]

# ---- 1. Links: replaced (broken), moved (redirected), verified 2026-11-21 in a browser
REPLACE = {
    "https://dhs.saccounty.gov/BHS": "https://dhs.saccounty.gov/us/en/behavioral-health.html",
    "https://mysourcewise.com/meals-wheels": "https://mysourcewise.com/programs-services/meals/",
    "https://smchealth.org/aas": "https://smchealth.org/division/divisions/aging-and-disability-services/",
    "https://static1.squarespace.com/static/605b5dc033224821d80ad63a/t/656fc85a8eaea146c20a77f8/1701824603159/Ceres+Medical+Referral+Form+%28Fillable%29.pdf": "https://www.ceresproject.org/s/Ceres-Medical-Referral-Form-Fillable.pdf",
    "https://www.chhs.ca.gov/wp-content/uploads/2020/01/Handout_CRC-Statewide-Brochure_KK_Accessible.pdf": "https://www.caregivercalifornia.org",
    "https://co.amador.ca.us/services/social-services/in-home-supportive-services": "https://www.amadorcounty.gov/services/social-services/in-home-supportive-services",
    "https://edcgov.us": "https://www.eldoradocounty.ca.gov",
    "https://marinhhs.org/home-supportive-services-ihss": "https://hhs.marincounty.gov/services/get-home-supportive-services",
    "https://www.ssa.gov/extrahelp": "https://www.ssa.gov/medicare/part-d-extra-help",
    "https://www.dhcs.ca.gov/services/medi-cal/Pages/Transportation.aspx": "https://www.dhcs.ca.gov/services/medi-cal-resources/transportation-services/",
    "https://dhcs.ca.gov/services/medi-cal/Pages/Transportation.aspx": "https://www.dhcs.ca.gov/services/medi-cal-resources/transportation-services/",
    "https://www.dhcs.ca.gov/individuals/Pages/Medicare-Savings-Programs-in-California.aspx": "https://www.dhcs.ca.gov/individuals/medicare-savings-programs-in-california/",
    "https://alamedacountysocialservices.org/our-services/Seniors-and-Disabled/IHSS": "https://socialservices.alamedacountyca.gov/our-services/Seniors-and-Disabled/IHSS/In-Home-Supportive-Services",
    "https://marinaccess.org": "https://marintransit.gov/marin-access",
    "https://mercedcaa.com": "https://www.mercedcaa.org",
    "https://mynevadacounty.com/1311/Apply-for-In-Home-Supportive-Service": "https://nevadacountyca.gov/1311/Apply-for-In-Home-Supportive-Service",
    "https://sjaging.org": "https://www.sjchsa.org/Aging-Services",
    "https://cresource.org": "https://www.communityresourceproject.org",
    "https://211sacramento.org": "https://www.211sacramento.org/211/",
    "https://delnorteseniorcenter.org": "http://delnorteseniorcenter.org",
}
WEBMAP = {re.sub(r"^https?://", "", k).rstrip("/"): re.sub(r"^https?://", "", v).rstrip("/") for k, v in REPLACE.items()}
WEBMAP["delnorteseniorcenter.org"] = "http://delnorteseniorcenter.org"
changed = set()
for r in recs:
    new = []
    for l in r.get("links") or []:
        l2 = l
        for old, nu in REPLACE.items():
            if l2.endswith(old) or (old + " ") in l2 or l2 == old:
                l2 = l2.replace(old, nu)
        if l2 != l:
            changed.add(r["id"])
        new.append(l2)
    r["links"] = new
    w = (r.get("web") or "").rstrip("/")
    if w in WEBMAP:
        r["web"] = WEBMAP[w]; changed.add(r["id"])

# Nevada County Now: county homepage -> Nevada County Connects transit site (lists paratransit)
for r in D["county"]:
    if r["id"] == "c75":
        r["links"] = ["https://www.nevadacountyconnects.com"]; r["web"] = "nevadacountyconnects.com"; changed.add("c75")
    if r["id"] in ("c128", "c136", "c137"):
        r["name"] = r["name"].replace("Aging & Adult Services", "Aging & Disability Services")
        r["label"] = (r.get("label") or "").replace("Aging & Adult Services", "Aging & Disability Services")
        r["summary"] = (r.get("summary") or "").replace("Aging & Adult Services", "Aging & Disability Services")
        changed.add(r["id"])
    if r["id"] == "c33":
        r["flag"] = "Website has no valid security certificate (opens as http). Phone verified separately."
# Medi-Cal rides: plain DHCS link label
FLAG_BLOCKED = "Website blocks automated checks; confirm the link manually (11/21)."
for r in recs:
    if r["id"] in ("c152", "c153", "s14"):
        r["flag"] = (r.get("flag") + " " if r.get("flag") else "") + FLAG_BLOCKED

# ---- 2. Suggested Z-codes by need (clinician assigns from documented need; suggestions only)
Z = {
    "Food": "Z59.41 Food insecurity; Z59.48 Other specified lack of adequate food",
    "Transportation": "Z59.82 Transportation insecurity",
    "Utilities": "Z59.861 Financial insecurity, difficulty paying for utilities; Z59.12 Inadequate housing utilities",
    "Housing & legal": "Z59.811 Housing instability, housed, with risk of homelessness; Z59.0- Homelessness; Z59.2 Discord with neighbors, lodgers and landlord; Z65.3 Problems related to other legal circumstances",
    "Legal / housing": "Z59.811 Housing instability, housed, with risk of homelessness; Z65.3 Problems related to other legal circumstances",
    "Housing / all needs": "Z59.811 Housing instability, housed, with risk of homelessness; Z59.41 Food insecurity; Z59.861 Financial insecurity, difficulty paying for utilities",
    "Caregiver (strain, lack of support)": "Z63.6 Dependent relative needing care at home; Z74.2 Need for assistance at home and no other household member able to render care",
    "Aging & caregiver info (AAA)": "Z74.2 Need for assistance at home and no other household member able to render care; Z60.2 Problems related to living alone",
    "Aging info": "Z74.2 Need for assistance at home and no other household member able to render care; Z60.2 Problems related to living alone",
    "Isolation / mood": "Z60.2 Problems related to living alone; Z60.4 Social exclusion and rejection",
    "Insurance & benefits": "Z59.71 Insufficient health insurance coverage; Z59.72 Insufficient welfare support",
    "Insurance / benefits": "Z59.71 Insufficient health insurance coverage; Z59.72 Insufficient welfare support",
    "Plan benefits": "Z59.71 Insufficient health insurance coverage",
    "Medication affordability": "Z59.868 Other specified financial insecurity; Z59.87 Material hardship due to limited financial resources; Z91.120 Intentional underdosing of medication due to financial hardship (only if documented)",
    "Phone & digital access": "No specific Z-code; Z59.87 Material hardship due to limited financial resources may apply",
    "Phone access": "No specific Z-code; Z59.87 Material hardship due to limited financial resources may apply",
    "Behavioral health": "N/A: not an SDOH Z-code (clinical diagnosis applies)",
    "Safety / crisis": "N/A: clinical codes (e.g., T74/T76 abuse codes) per assessment",
}
for r in recs:
    r["zcodes"] = Z.get(r["need"], "N/A")
    if r["id"] in ("c216", "s15"):
        r["zcodes"] = Z["Legal / housing"]

# ---- 3. Last updated
for r in recs:
    if r["id"] in changed:
        r["updated"] = TODAY
    else:
        r["updated"] = (r.get("verified") or "").strip("'") or "Not recorded"
D["updated"] = TODAY
D["updates"] = TODAY
D["zcodeSource"] = "ICD-10-CM FY2027 (effective Oct 1, 2026), CMS MS-DRG v44.0 Definitions Manual. Suggestions only; assign from the documented assessment."
P.write_text(json.dumps(D, indent=1, ensure_ascii=False))
print("links changed on", len(changed), "resources:", sorted(changed))
