"""Project Open Hand (SF): two routes - Wellness Program (any insurance; CHF qualifies; LCSW can sign)
and Medi-Cal Community Supports. Source: openhand.org How to Apply + SF Wellness application (July 2026)."""
import json, pathlib
p = pathlib.Path(__file__).resolve().parents[1] / "data" / "resources.json"
d = json.loads(p.read_text())
r = next(x for x in d["county"] if x["id"] == "c117")
T = "2026-11-23"
r.update(
    label="Medically tailored meals & groceries – Project Open Hand",
    medi="No",
    who="San Francisco residents with heart failure (NYHA class on form), COPD, CAD, type 2 diabetes (A1C 7.0+), ESRD, HIV/AIDS or recent major surgery. Any insurance.",
    how="Not on Medi-Cal (Medicare Advantage, SutterSelect, etc.): Wellness Program. A licensed provider (MD, NP, PA, RN, LCSW, RD) completes and signs the SF Wellness application and sends it to Project Open Hand; Client Services confirms eligibility. Recertify every 6 months. Medi-Cal (SF Health Plan or Anthem Blue Cross): refer through the plan's Community Supports medically tailored meals form, naming Project Open Hand.",
    notes="Free. Senior community meals (60+): 415-447-2335. Main line 415-447-2300. Alameda and Contra Costa: heart failure qualifies through Medi-Cal only.",
    source="openhand.org – How to Apply; SF Wellness Program application (July 2026)",
    verified=T, updated=T, flag=None,
    links=["[How to apply](https://openhand.org/get-meals/how-apply)"],
)
base = " Project Open Hand delivers free healthy meals and groceries made for heart conditions."
q = " Questions? Call Project Open Hand at 415-447-2326."
r["summaryByMedi"] = {
    "no": "Your care team can refer you to Project Open Hand's Wellness Program." + base + " You'll need to renew every 6 months." + q,
    "yes": "With Medi-Cal through San Francisco Health Plan or Anthem Blue Cross, your care team can refer you through your health plan." + base + q,
    "unsure": "Your care team can refer you to Project Open Hand." + base + q,
}
r["summary"] = r["summaryByMedi"]["unsure"]
p.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("updated c117")
