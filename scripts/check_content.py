"""Content checks for data/services.json. Exit 1 on errors. Writes review-queue.json.
Checks: retired materials, phone roles, regional-as-statewide, staff/patient contradictions,
CalFresh application labelling, review metadata and overdue review.
A successful page load never marks a claim verified; only a person can set review.status.
"""
import json, re, sys, datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data/services.json"
D = json.loads(path.read_text())
TODAY = datetime.date(2026, 11, 20) if "--today" not in sys.argv else datetime.date.fromisoformat(sys.argv[sys.argv.index("--today") + 1])
OVERDUE_DAYS = 183
PH = re.compile(r"\b\d{3}-\d{3}-\d{4}\b")
errors, warns, queue = [], [], []

def holders(s):
    yield None, s
    for c, ov in (s.get("overrides") or {}).items():
        yield c, ov

def patient_text(h):
    t = [h.get("summary") or "", h.get("script") or "", h.get("prepare") or "", h.get("timing") or "", h.get("limits") or "", h.get("fallback") or ""]
    t += list((h.get("summaryByMedi") or {}).values())
    return " ".join(t)

retired = [r["pattern"] for r in D.get("retired", [])]
for s in D["services"]:
    sid = s["id"]
    for cty, h in holders(s):
        where = f"{sid}{'/' + cty if cty else ''}"
        blob = json.dumps({k: h.get(k) for k in ("summary", "summaryByMedi", "links", "phones", "script", "prepare", "fallback")})
        for r in retired:
            if r in blob:
                errors.append(f"{where}: retired material '{r}' still referenced")
        for L in h.get("links") or []:
            if "getcalfresh" in L["url"] and L.get("kind") == "apply":
                errors.append(f"{where}: GetCalFresh labelled as the application (use BenefitsCal; GetCalFresh is information/help)")
            if "getcalfresh" in L["url"] and "apply" in L["label"].lower() and "help" not in L["label"].lower():
                errors.append(f"{where}: GetCalFresh link label says 'apply'")
        phones = h.get("phones")
        if phones is not None:
            if len(phones) > 1:
                for p in phones:
                    if not p.get("role") or (p["role"] == "main" and sum(q.get("role") == "main" for q in phones) > 1):
                        errors.append(f"{where}: multiple numbers without distinct roles ({p.get('display')})")
            for p in phones:
                if ";" in (p.get("display") or ""):
                    errors.append(f"{where}: one phone entry holds several numbers: {p['display']}")
                if p.get("role") == "ride scheduling" and not p.get("unverified"):
                    dig = re.sub(r"\D", "", p.get("number") or "")
                    if not any(dig and dig in re.sub(r"\D", "", c["claim"]) for c in s["review"].get("claims", [])) and not p.get("plan", "").startswith(("Partnership", "Alameda", "CenCal")):
                        warns.append(f"{where}: ride scheduling line {p.get('number')} has no source claim")
            nums = {p.get("number") for p in phones if p.get("number")} | {n for p in phones for n in p.get("alsoNumbers", [])}
            for n in PH.findall(patient_text(h)):
                if not any(n in x for x in nums if x) and n not in ("800-510-2020", "877-847-3663", "800-434-0222") and not any(n in (q.get("number") or "") for q in s.get("phones", [])):
                    errors.append(f"{where}: patient text cites {n}, which isn't in this resource's phone list")
        pt = patient_text(h).lower()
        if "24/7" in pt and not any("24/7" in (p.get("hours") or "") for p in (h.get("phones") or s.get("phones") or [])):
            errors.append(f"{where}: patient text claims 24/7 without a sourced hours value")
        medi = (h.get("medi") or s.get("medi") or {})
        if medi.get("req") == "required" and re.search(r"\b(anyone|everyone|all ages|no matter your insurance)\b", pt):
            errors.append(f"{where}: Medi-Cal-only resource but patient text says it's open to anyone")
    # statewide claims
    if s["serves"]["type"] == "statewide":
        txt = " ".join(str(s.get(k) or "") for k in ("who", "how", "summary", "notes"))
        if re.search(r"limited to [A-Z][a-z]+ (county )?residents|only (for|in) [A-Z][a-z]+ County|residents of [A-Z][a-z]+ County", txt):
            errors.append(f"{sid}: marked statewide but text describes a regional service area")
    rv = s.get("review") or {}
    for k in ("status", "date", "maintainer", "source"):
        if not rv.get(k):
            errors.append(f"{sid}: review.{k} missing")
    if rv.get("date"):
        age = (TODAY - datetime.date.fromisoformat(rv["date"])).days
        if age > OVERDUE_DAYS:
            queue.append({"id": sid, "reason": f"review overdue ({age} days)"})
    if rv.get("flag"):
        queue.append({"id": sid, "reason": "open item: " + rv["flag"]})
    if rv.get("status") not in ("verified", "partly verified", "needs review"):
        errors.append(f"{sid}: unknown review.status {rv.get('status')}")
    if not s.get("history"):
        errors.append(f"{sid}: no change history")

(ROOT / "review-queue.json").write_text(json.dumps({"generated": str(TODAY), "items": queue}, indent=1))
for w in warns: print("WARN ", w)
for e in errors: print("ERROR", e)
print(f"{len(D['services'])} services checked: {len(errors)} errors, {len(warns)} warnings, {len(queue)} review-queue items")
sys.exit(1 if errors else 0)
