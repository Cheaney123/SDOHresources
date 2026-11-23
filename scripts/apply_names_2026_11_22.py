"""Polished resource names (Title Case, no descriptive tails) and Z-code clean-up, 2026-11-22.
Descriptive parentheticals that carried useful facts are kept in the record's notes.
"""
import json, pathlib
p = pathlib.Path(__file__).resolve().parents[1] / "data" / "resources.json"
d = json.loads(p.read_text())
NAMES = {
 # statewide
 "s5": "Long-Term Care Ombudsman Crisis Line",
 "s6": "Friendship Line California",
 "s8": "HICAP Medicare Counseling",
 "s11": "Pharmacy Technician Referral",
 "s12": "PG&E CARE and FERA Bill Discounts",
 "s14": "California LifeLine",
 "s18": "Medicare Savings Programs",
 "s19": "Health Plan's Member Services",
 "s20": "Medi-Cal Rides to Medical Appointments",
 "s21": "Medicare Counseling Benefit",
 "s22": "LIHEAP Energy Bill Help",
 "s25": "National Caregiver Support Lines",
 "s30": "Medi-Cal Application and Coverage",
 # county
 "c4": "East Bay Paratransit",
 "c115": "Rebuilding Together SF Safe at Home",
 "c7": "Alameda County Behavioral Health ACCESS Line",
 "c11": "Project Open Hand",
 "c20": "Contra Costa County Aging & Adult Services",
 "c22": "County Connection LINK Paratransit",
 "c29": "Project Open Hand",
 "c48": "Clear Lake Gleaners",
 "c49": "Redwood Empire Food Bank",
 "c50": "Lake Transit Dial-A-Ride and Flex Stop",
 "c56": "Marin County Aging & Adult Services",
 "c58": "Marin Access",
 "c67": "Merced County Transit",
 "c75": "Nevada County Now Paratransit",
 "c83": "South Placer Transit Information Center",
 "c94": "Sacramento County Behavioral Health Services",
 "c98": "211 Sacramento",
 "c99": "ACC Rides",
 "c100": "SMUD Bill Discounts",
 "c101": "SF Disability & Aging Services Benefits & Resources Hub",
 "c103": "SF Paratransit",
 "c109": "SF Disability & Aging Services Meals",
 "c110": "SF Disability & Aging Services Caregiver & Dementia Support",
 "c111": "SF Disability & Aging Services Housing Support",
 "c113": "Institute on Aging",
 "c116": "Institute on Aging Temporary Respite Caregiver Support",
 "c117": "Project Open Hand Wellness Program",
 "c120": "Emergency Food Bank of Stockton",
 "c122": "Access San Joaquin and RTD Dial-A-Ride",
 "c128": "San Mateo County Aging & Disability Services TIES Line",
 "c129": "Second Harvest of Silicon Valley",
 "c130": "SamTrans Redi-Wheels and RediCoast",
 "c138": "211 San Mateo County",
 "c139": "Central Coast Commission for Senior Citizens",
 "c141": "Easy Lift Dial-A-Ride",
 "c147": "Sourcewise",
 "c148": "Second Harvest of Silicon Valley",
 "c150": "Sacred Heart Community Service",
 "c155": "Sourcewise Meals on Wheels",
 "c157": "211 Santa Clara County",
 "c159": "Seniors Council of Santa Cruz & San Benito Counties",
 "c175": "Sonoma County Area Agency on Aging",
 "c184": "Stanislaus County Department of Aging & Veterans Services",
 "c186": "MOVE Stanislaus",
 "c202": "Yolobus Special",
}
# facts that only lived in the old name
KEEP = {
 "c4": "Run by AC Transit and BART.",
 "c22": "Serves central Contra Costa County.",
 "c29": "Through Contra Costa Health Plan.",
 "c48": "Located in Finley.",
 "c49": "Senior distributions in Lake County.",
 "c58": "Paratransit, volunteer drivers and Catch-A-Ride.",
 "c75": "Formerly Gold Country Lift.",
 "c83": "PCT Dial-A-Ride and Roseville Transit.",
 "c113": "Program name: IOA Connect.",
 "c186": "Handles ADA eligibility for all county providers.",
 "c202": "ADA paratransit.",
}
ZC = {
 "s8": "Z59.71 Insufficient health insurance coverage (only if a coverage gap is documented)",
 "s18": "Z59.868 Other specified financial insecurity; Z59.71 Insufficient health insurance coverage (only if a coverage gap is documented)",
 "s19": "N/A: code the underlying need (e.g., Z59.82 for transportation, Z59.41 for food)",
 "s30": "Z59.71 Insufficient health insurance coverage (if uninsured or underinsured)",
}
recs = {r["id"]: r for r in d["county"] + d["state"]}
for i, n in NAMES.items():
    r = recs[i]; r["name"] = n; r["updated"] = "2026-11-22"
for i, t in KEEP.items():
    r = recs[i]; old = r.get("notes") or ""
    if t.rstrip(".").lower() not in old.lower():
        r["notes"] = (t + " " + old).strip()
for i, z in ZC.items():
    recs[i]["zcodes"] = z; recs[i]["updated"] = "2026-11-22"
s19 = recs["s19"]
s19["label"] = "Plan benefits, rides and coverage questions"
s19["phone"] = "Number on member ID card"
for r in d["county"]:
    if r["name"] == "Medi-Cal rides to medical appointments":
        r["name"] = "Medi-Cal Rides to Medical Appointments"
d["updated"] = "2026-11-22"
p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
print(f"renamed {len(NAMES)}, notes kept {len(KEEP)}, z-codes {len(ZC)}")
