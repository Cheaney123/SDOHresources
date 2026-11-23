"""Meals on Wheels / home-delivered meals for every county; FCA statewide -> county only;
Project Open Hand = Medi-Cal only (2026-11-22).
Phones checked 11/22/2026 on county/AAA pages where possible; see each record's source and flag.
"""
import json, pathlib
p = pathlib.Path(__file__).resolve().parents[1] / "data" / "resources.json"
d = json.loads(p.read_text())
T = "2026-11-22"
Z = "Z59.41 Food insecurity; Z59.48 Other specified lack of adequate food"
TAIL = "They deliver healthy meals to your home if shopping or cooking is hard for you."
WHO = "Homebound adults 60+ who can't shop or cook for themselves (spouse may also qualify)"
HOW = "Patient, family or SW calls to request intake; the program does a phone or home assessment. Suggested donation; no one turned away. Waitlists are common."

def mow(county, label, name, phone, summary, links, source, who=WHO, how=HOW, notes=None, flag=None, web=None):
    return {"county": county, "need": "Food", "label": "Home-delivered meals – " + label, "name": name,
            "phone": phone, "medi": "No", "who": who, "how": how,
            "web": web or (links[0].split("](")[1].rstrip(")").replace("https://", "") if links else None),
            "notes": notes, "source": source, "verified": T, "flag": flag, "links": links,
            "summary": summary + " " + TAIL, "zcodes": Z, "updated": T}

NEW = [
 mow("Alameda", "Meals on Wheels programs by city", "Alameda County Meals on Wheels",
     "Oakland, Piedmont, San Leandro, Hayward, Castro Valley, San Lorenzo: 510-582-1263 ext. 118; Fremont, Newark, Union City: 510-582-1263 ext. 156; Dublin, Livermore, Pleasanton, Sunol: 510-881-0305; Berkeley: 510-981-5250; City of Alameda: 510-865-6131; Albany: 510-524-9124; Emeryville: 510-596-4309",
     "To sign up, call the program for your city. Oakland, Hayward, San Leandro, Castro Valley or San Lorenzo: 510-582-1263 ext. 118. Fremont, Newark or Union City: 510-582-1263 ext. 156. Dublin, Livermore or Pleasanton: 510-881-0305. Berkeley: 510-981-5250. City of Alameda: 510-865-6131.",
     ["[Alameda County home-delivered meal programs](https://socialservices.alamedacountyca.gov/our-services/Health-and-Food/Other-Support/senior-food)"],
     "Alameda County Social Services – Senior Food (AAA)",
     notes="SOS Meals on Wheels serves Oakland through Union City; Spectrum Community Services serves the Tri-Valley. J-Sei (Japanese-style meals, Berkeley/Oakland/Emeryville): 510-654-4000 ext. 105. City of Alameda program serves all ages."),
 mow("Amador", "Amador Senior Center", "Amador Senior Center Meals on Wheels", "209-223-0442",
     "Call the Amador Senior Center at 209-223-0442 to sign up.",
     ["[Amador County Home Delivered Meals](https://www.amadorseniorcenter.org/programs-services/home-delivered-meals/)"],
     "amadorseniorcenter.org – Amador County Home Delivered Meals",
     how="Call to register; an assessment is required before meals start. Suggested $5/meal; no one turned away.",
     notes="Fresh hot meals Monday–Friday to Amador County residents; weekend options available. Office hours Mon–Fri 8:30–4."),
 mow("Contra Costa", "Meals on Wheels Diablo Region", "Meals on Wheels Diablo Region", "925-937-8311",
     "Call Meals on Wheels Diablo Region at 925-937-8311 to sign up.",
     ["[Apply for meals](https://www.mowdiabloregion.org/apply-meals)"],
     "mowdiabloregion.org; John Muir Health community resources",
     who="Homebound adults 60+ in Contra Costa County who can't drive or cook",
     notes="Countywide. Also offers care management, friendly visitors and fall prevention."),
 mow("Del Norte", "Del Norte Senior Center", "Del Norte Senior Center Meals on Wheels", "707-464-3069",
     "Call the Del Norte Senior Center at 707-464-3069 to sign up.", [],
     "Partnership HealthPlan – Del Norte food resources (verified 3/2026); Lost Coast Outpost",
     notes="Crescent City area. Tribal elders in Crescent City, Smith River and Klamath: United Indian Health Services Elder Nutrition.",
     flag="Not confirmed on the center's own website; confirm delivery area by phone."),
 mow("El Dorado", "El Dorado County Senior Nutrition Program", "El Dorado County Senior Nutrition",
     "Western Slope: 530-621-6160; South Lake Tahoe: 530-573-3130",
     "Call 530-621-6160 to sign up (South Lake Tahoe: 530-573-3130).",
     ["[Senior Nutrition Services](https://www.eldoradocounty.ca.gov/Services/Assistance-Programs/Seniors/Senior-Services/Senior-Nutrition-Services)"],
     "El Dorado County HHSA – Senior Nutrition Services",
     who="Homebound adults 60+ who are medically or physically disabled",
     notes="County program (Area Agency on Aging). Hot lunch Monday–Friday."),
 mow("Lake", "Lake County senior centers", "Lake County Senior Center Meals on Wheels",
     "Lakeport, Kelseyville, Lucerne: 707-263-4218; Clearlake (Highlands): 707-994-3051; Clearlake Oaks (Live Oak): 707-998-1950; Middletown: 707-987-3113",
     "To sign up, call the senior center for your area. Lakeport, Kelseyville or Lucerne: 707-263-4218. Clearlake: 707-994-3051. Clearlake Oaks: 707-998-1950. Middletown: 707-987-3113.", [],
     "Lake County News; Lake County Chamber; Redwood Empire Food Bank Lake County flyer",
     notes="Each senior center runs its own Meals on Wheels route.",
     flag="No county page lists these numbers; confirm the right center by phone."),
 mow("Marin", "Marin County Area Agency on Aging (delivered by Vivalon)", "Marin County Meals on Wheels", "415-473-4636",
     "Call 415-473-4636 (415-473-INFO) to sign up.",
     ["[Marin meals for older adults](https://hhs.marincounty.gov/services/get-meals-home-or-community-nutrition-programs-older-adults)"],
     "Marin HHS – Nutrition programs for older adults (updated 5/2026)",
     how="Call the county line for phone screening and enrollment; have name, date of birth, address and health questions ready. Suggested donation $3.50/meal. Waitlist possible.",
     notes="Vivalon (formerly Whistlestop) delivers. Vivalon's Nourish program may serve seriously ill adults who don't qualify."),
 mow("Merced", "Merced County Area Agency on Aging", "Merced County Home-Delivered Meals", "209-385-7550",
     "Call the Merced County Area Agency on Aging at 209-385-7550 to sign up.",
     ["[Merced County nutrition programs](https://www.countyofmerced.com/1492/Nutrition)"],
     "Merced County – Nutrition (AAA)",
     how="Referral by patient, family or SW; AAA staff do an in-home assessment. Five ready-to-heat meals delivered once a week.",
     notes="Nutrition line: 209-626-7595."),
 mow("Nevada", "Gold Country Senior Services (west county) and Sierra Senior Services (Truckee)", "Nevada County Meals on Wheels",
     "Western Nevada County: 530-446-6853; Truckee: 530-550-7600",
     "Call Gold Country Senior Services at 530-446-6853 to sign up (Truckee area: 530-550-7600).",
     ["[Gold Country Meals on Wheels](https://www.goldcountryservices.org/meals-on-wheels/)", "[Sierra Senior Services (Truckee)](https://www.sierraseniors.org)"],
     "goldcountryservices.org – Meals on Wheels (Enrollment); Truckee Chamber listing",
     notes="Gold Country delivers Tuesday and Thursday; suggested $4/meal. It serves Grass Valley, Nevada City, Penn Valley, Lake Wildwood, Lake of the Pines, Alta Sierra, North San Juan and nearby. Sierra Senior Services serves Truckee and North Lake Tahoe.",
     flag="Truckee number (Sierra Senior Services) is from a chamber listing; confirm before sending."),
 mow("Placer", "Seniors First (Meals on Wheels Placer County)", "Meals on Wheels Placer County",
     "Seniors First: 530-889-9500; Tahoe and Truckee: Sierra Senior Services 530-550-7600",
     "Call Seniors First at 530-889-9500 to sign up (Tahoe area: 530-550-7600).",
     ["[Seniors First](https://www.seniorsfirst.org)"],
     "Placer County Board of Supervisors memo (2/2022); Seniors First 2025 Resource Guide",
     notes="Seniors First serves western Placer County; Sierra Senior Services serves the Tahoe and Truckee area."),
 mow("San Joaquin", "San Joaquin County Aging & Community Services", "San Joaquin County Meals on Wheels", "209-468-1104",
     "Call San Joaquin County Aging Services at 209-468-1104 to sign up.",
     ["[San Joaquin County aging services](https://aging.ca.gov/Find_Services_In_My_County/My_County/?cc=SJ)"],
     "City of Lodi – San Joaquin County food resources; Community Connections SJC; CDA county page",
     how="Call the Information & Assistance line, or complete form SJ30A and fax to 209-932-2663. Five frozen meals plus milk and fruit delivered weekly; $2 suggested donation.",
     notes="Lodi area: LOEL Senior Center Meals on Wheels (hot meals weekdays), 209-365-0572."),
 mow("Santa Barbara", "Meals on Wheels by area", "Santa Barbara County Meals on Wheels",
     "Santa Barbara and Goleta: 805-683-1565; Santa Maria Valley: 805-938-1200",
     "To sign up, call Santa Barbara Meals on Wheels at 805-683-1565, or in the Santa Maria Valley call 805-938-1200.",
     ["[Santa Barbara Meals on Wheels](https://mealsonwheelssb.org)", "[Meals on Wheels Santa Maria Valley](https://mealsonwheelssmv.org)"],
     "211 Santa Barbara County (CommUnify) listings",
     how="Patient or SW calls; a volunteer visit confirms need. Santa Barbara program charges a fee per meal with reduced rates; ask about cost.",
     notes="Lompoc and Santa Ynez Valley: call 211 for the current provider. CenCal Medi-Cal members may get medically tailored meals through Community Supports instead."),
 mow("Santa Cruz", "Community Bridges Meals on Wheels", "Community Bridges Meals on Wheels", "831-464-3180 ext. 100",
     "Call Community Bridges at 831-464-3180, extension 100, to sign up.",
     ["[Community Bridges Meals on Wheels](https://communitybridges.org/mealsonwheels/)"],
     "communitybridges.org/mealsonwheels",
     notes="Eligibility screened since 4/2025 because of funding cuts; most-in-need prioritized. Waitlisted clients are encouraged to use a dining site."),
 mow("Solano", "Meals on Wheels of Solano County", "Meals on Wheels of Solano County", "707-425-0638",
     "Call Meals on Wheels of Solano County at 707-425-0638 to sign up.",
     ["[Meals on Wheels of Solano County](https://www.mealsonwheelssolano.org)"],
     "Solano Public Health senior resources; City of Vacaville resource guide",
     notes="Serves Benicia, Dixon, Fairfield, Rio Vista, Suisun, Vacaville and Vallejo. Deliveries Monday, Wednesday and Friday.",
     flag="Provider website could not be opened to check; number matches county and city resource lists."),
 mow("Sonoma", "Council on Aging / Petaluma People Services", "Sonoma County Meals on Wheels",
     "Most of Sonoma County: Council on Aging 707-525-0143; Petaluma, Penngrove: Petaluma People Services 707-765-8488",
     "Call the Council on Aging at 707-525-0143 to sign up (Petaluma or Penngrove: 707-765-8488).",
     ["[Sonoma County meal programs](https://sonomacounty.gov/health-and-human-services/human-services/older-adults-people-with-disabilities/food/meal-programs)"],
     "County of Sonoma – Meal Programs",
     notes="Council on Aging serves Santa Rosa, Rohnert Park, Cotati, Sonoma, Sebastopol, Windsor, Healdsburg, Cloverdale and west county."),
 mow("Stanislaus", "Stanislaus County Area Agency on Aging", "Stanislaus County Meals on Wheels", "209-558-8698",
     "Call the Stanislaus County Senior Information Line at 209-558-8698 to sign up.",
     ["[Stanislaus senior meals](https://www.stancounty.com/aging/htc-senior-meals.shtm)"],
     "Stanislaus County Aging & Veterans Services – Senior Lunch Programs",
     how="Call the Senior Information Line to apply. Five frozen meals delivered once a week. Priority to frail seniors who live alone and don't drive."),
 mow("Sutter", "Meals on Wheels Yuba-Sutter (Agency on Aging Area 4)", "Meals on Wheels Yuba-Sutter", "530-670-0033; toll-free 800-211-4545",
     "Call Meals on Wheels Yuba-Sutter at 530-670-0033 to sign up.",
     ["[Meals on Wheels Yuba-Sutter](https://agencyonaging4.org/yuba-sutter-meals-on-wheels/)"],
     "agencyonaging4.org – Yuba-Sutter Meals on Wheels",
     how="Call to enroll; an assessment worker visits the home to confirm eligibility. Five meals delivered once a week. Waitlist possible.",
     notes="Also runs Dine Around Town restaurant vouchers in Sutter County."),
 mow("Yolo", "Meals on Wheels Yolo County", "Meals on Wheels Yolo County", "530-662-7035",
     "Call Meals on Wheels Yolo County at 530-662-7035 to sign up.",
     ["[Meals on Wheels Yolo County](https://www.mowyolo.org)"],
     "City of West Sacramento – Meals on Wheels Yolo County; SMUD Senior Resource Directory",
     notes="Countywide (Woodland, Davis, West Sacramento, Winters). Waitlist possible."),
 mow("Yuba", "Meals on Wheels Yuba-Sutter (Agency on Aging Area 4)", "Meals on Wheels Yuba-Sutter", "530-670-0033; toll-free 800-211-4545",
     "Call Meals on Wheels Yuba-Sutter at 530-670-0033 to sign up.",
     ["[Meals on Wheels Yuba-Sutter](https://agencyonaging4.org/yuba-sutter-meals-on-wheels/)"],
     "agencyonaging4.org – Yuba-Sutter Meals on Wheels",
     how="Call to enroll; an assessment worker visits the home to confirm eligibility. Five meals delivered once a week. Waitlist possible."),
]

have = {r["county"] for r in d["county"] if r["label"].startswith("Home-delivered meals") and r["id"] in ("c97", "c118", "c136", "c155")}
n = max(int(r["id"][1:]) for r in d["county"])
for r in NEW:
    assert r["county"] not in have
    if not any(x["county"] == r["county"] and x["name"] == r["name"] for x in d["county"]):
        n += 1
        d["county"].append({"id": f"c{n}", **r})

by = {r["id"]: r for r in d["county"] + d["state"]}
# Sacramento: current name
s = by["c97"]
s.update(name="Meals on Wheels Sacramento County", label="Home-delivered meals – Meals on Wheels Sacramento County (ACC Senior Services)",
         notes="Formerly Meals on Wheels by ACC (renamed 2024).", links=["[Meals on Wheels Sacramento County](https://mowsac.org)"],
         summary="Call Meals on Wheels Sacramento County at 916-444-9533 to sign up. " + TAIL, verified=T, updated=T)

# Family Caregiver Alliance is the Bay Area CRC, not statewide: county records already exist (Alameda, Contra Costa, Marin, SF, San Mateo, Santa Clara)
d["state"] = [r for r in d["state"] if r["id"] != "s33"]

# Project Open Hand: Medi-Cal only (Community Supports through the member's plan)
for i, plan in (("c11", "Alameda Alliance for Health"), ("c117", "San Francisco Health Plan or Anthem Blue Cross")):
    r = by[i]
    r.update(name="Project Open Hand", medi="Yes",
             label=f"Medically tailored meals & groceries – Project Open Hand (Medi-Cal: {plan})",
             who=f"Medi-Cal members with {plan} and a qualifying chronic condition (e.g., heart failure, diabetes)",
             how=f"Referral through {plan} Community Supports (medically tailored meals). Medicare-only and commercial patients: use Meals on Wheels instead.",
             summary=f"If you have Medi-Cal through {plan}, you may qualify for healthy meals and groceries made for heart conditions, delivered by Project Open Hand. Your care team can send the referral through your health plan. Questions? Call Project Open Hand at {r['phone']}.",
             updated=T)
by["c29"].update(name="Project Open Hand", updated=T)

d["updated"] = T
p.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("county records:", len(d["county"]), "statewide:", len(d["state"]))
