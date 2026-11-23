"""Clean-up of card wording, 2026-11-22.
- Paratransit summaries: drop "reply here and we'll help you find a ride" (messages are for
  patients to act on; the care team is not offering to arrange rides) and point to the plan card.
- Verification notes ("flag") rewritten in plain words; the app now shows them under Details.
"""
import json, pathlib
p = pathlib.Path(__file__).resolve().parents[1] / "data" / "resources.json"
d = json.loads(p.read_text())
OLD = " If you have an appointment before then, reply here and we'll help you find a ride."
NEW = " If you have an appointment before then, call the number on your health plan card to ask about rides."
FLAGS = {
    "Ride lines verified for Anthem, Health Net, Molina. Other plans listed as member services; Kaiser ride line not verified.":
        "Ride numbers confirmed for Anthem, Health Net and Molina. Other plans show their member services line; the Kaiser ride line is not confirmed.",
    "24/7 status not stated by DHCS":
        "The state list doesn't say whether this line is open 24/7. In a crisis, use 988 or 911.",
    "From CWDA list; not re-checked on county site":
        "Number from the statewide county welfare directors' list; not yet confirmed on the county website.",
    "Not re-checked": "Not yet re-confirmed with the agency.",
    "Secondary source": "Listed from secondary sources; confirm details with the agency.",
}
n_sum = n_flag = 0
for r in d["county"] + d["state"]:
    changed = False
    s = r.get("summary") or ""
    if OLD in s:
        r["summary"] = s.replace(OLD, NEW); n_sum += 1; changed = True
    if r.get("flag") in FLAGS:
        r["flag"] = FLAGS[r["flag"]]; n_flag += 1; changed = True
    if changed:
        r["updated"] = "2026-11-22"
d["updated"] = "2026-11-22"
p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
print(f"summaries changed: {n_sum}; notes reworded: {n_flag}")

# Medication costs: staff tasks the pharm tech; the patient message says so and gives a callback line.
for r in d["state"]:
    if r["id"] == "s11":
        r["name"] = "Pharmacy technician referral"
        r["action"] = "Task to Pharm Tech in Epic before sending this message."
        r["summary"] = ("We're going to connect you to a pharmacy technician who can help you find lower-cost "
                        "options for your medicines. In the meantime, reach out to us if you need expedited "
                        "assistance at ___-___-____.")
        r["notes"] = "Pharm tech references (staff only): HealthWell Foundation healthwellfoundation.org; Mark Cuban Cost Plus Drugs costplusdrugs.com"
        r["links"] = []
        r["updated"] = "2026-11-22"
p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
print("medication-cost referral updated")
