"""Statewide caregiver resources, prioritized for Sutter Sync Heart Care (2026-11-22).
Verified 11/22/2026 on caregivercalifornia.org, aging.ca.gov (Caring for the Caregivers) and edd.ca.gov/PFLCaregivers.
`priority` orders statewide resources within a need (1 = first).
"""
import json, pathlib
p = pathlib.Path(__file__).resolve().parents[1] / "data" / "resources.json"
d = json.loads(p.read_text())
CG = "Caregiver (strain, lack of support)"
Z = "Z63.6 Dependent relative needing care at home; Z74.2 Need for assistance at home and no other household member able to render care"
new = [
 {"id": "s31", "need": CG, "priority": 1,
  "label": "Statewide network of 11 regional centers for family caregivers",
  "name": "California Caregiver Resource Centers", "phone": "Find the local center online",
  "medi": "No", "who": "Unpaid family caregivers of adults with chronic or debilitating health conditions (including heart disease) or memory loss",
  "how": "First referral for general caregiver strain. Each county's regional center is listed under that county; services and eligibility vary by center, so confirm respite and counseling locally.",
  "notes": "Services may include caregiver assessment, counseling, education, support groups, care planning and respite help. No statewide phone line.",
  "flag": None, "ql": CG,
  "links": ["[Find your local Caregiver Resource Center](https://www.caregivercalifornia.org/find-your-local-center/)"],
  "summary": "California's Caregiver Resource Centers support family members who care for someone with an ongoing health condition, including heart conditions. They can offer counseling, support groups, help planning care and help finding short breaks (respite). Use the link below to find the center for your county.",
  "source": "caregivercalifornia.org", "verified": "2026-11-22", "zcodes": Z},
 {"id": "s32", "need": CG, "priority": 2,
  "label": "California Department of Aging, through local Area Agencies on Aging",
  "name": "Family Caregiver Support Program", "phone": "800-510-2020",
  "medi": "No", "who": "Unpaid caregivers of older adults or people with disabilities",
  "how": "Add when the caregiver of an older adult needs practical help or respite. The line connects to the county's Area Agency on Aging.",
  "notes": "Information and referral, training, counseling, support groups, care planning and respite.",
  "flag": None, "ql": CG,
  "links": ["[Family Caregiver Support Program](https://www.aging.ca.gov/Aging_Resources/Caring_for_the_Caregivers/)"],
  "summary": "Call 800-510-2020 to reach your local Area Agency on Aging. Its caregiver program offers support groups, counseling, training and help finding short breaks (respite) for family caregivers.",
  "source": "aging.ca.gov – Caring for the Caregivers", "verified": "2026-11-22", "zcodes": Z},
 {"id": "s33", "need": CG, "priority": 3,
  "label": "Caregiver education and online guidance",
  "name": "Family Caregiver Alliance", "phone": None,
  "medi": "No", "who": "Family caregivers; also runs the Bay Area Caregiver Resource Center (six counties)",
  "how": "Education and practical guidance on caring for someone with a chronic illness. Bay Area counties list FCA as their local center.",
  "notes": None, "flag": None, "ql": CG,
  "links": ["[Family Caregiver Alliance](https://www.caregiver.org)"],
  "summary": "Family Caregiver Alliance has free guides and practical tips for family caregivers, including how to manage a long-term illness at home.",
  "source": "caregiver.org", "verified": "2026-11-22", "zcodes": Z},
 {"id": "s34", "need": CG, "priority": 4,
  "label": "EDD partial wage replacement for working caregivers",
  "name": "California Paid Family Leave", "phone": None,
  "medi": "No", "who": "Working family members (spouse, child, parent, sibling, grandparent and others) caring for someone with a serious health condition who have paid into State Disability Insurance",
  "how": "For working spouses or adult children. Up to 8 weeks within 12 months; requires a medical certification. Immigration status does not affect eligibility.",
  "notes": None, "flag": None, "ql": CG,
  "links": ["[Paid Family Leave for caregivers](https://edd.ca.gov/PFLCaregivers)"],
  "summary": "If a family member who works needs time off to care for you, California Paid Family Leave may pay part of their wages for up to 8 weeks. They can learn more and apply online.",
  "source": "edd.ca.gov/PFLCaregivers", "verified": "2026-11-22", "zcodes": Z},
]
for r in new:
    r["updated"] = "2026-11-22"
ids = {r["id"] for r in d["state"]}
for r in new:
    if r["id"] in ids:
        d["state"] = [x if x["id"] != r["id"] else r for x in d["state"]]
    else:
        d["state"].append(r)
for r in d["state"]:
    if r["id"] == "s6":
        r["priority"] = 5
        if "Caregiver" not in r["ql"]: r["ql"] += "; " + CG
    if r["id"] == "s24": r["priority"] = 6
    if r["id"] == "s25": r["priority"] = 7
# IHSS is Medi-Cal and need-tested: make the subtitle say so
for r in d["county"]:
    if r["label"].startswith("In-home caregiver (IHSS – paid caregiver, can be a family member)"):
        r["label"] = r["label"].replace("In-home caregiver (IHSS – paid caregiver, can be a family member)", "In-home help for Medi-Cal members (IHSS)")
        r["updated"] = "2026-11-22"
d["updated"] = "2026-11-22"
p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
print("state records:", len(d["state"]))
