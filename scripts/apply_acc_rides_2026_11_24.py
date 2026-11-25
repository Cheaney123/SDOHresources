"""ACC Rides (c99): use the number ACC Senior Services lists on its own program page, 916-393-RIDE (7433).
Source: accsv.org ACC Rides Transportation Program page."""
import json, pathlib
p = pathlib.Path(__file__).resolve().parents[1] / "data" / "resources.json"
d = json.loads(p.read_text())
r = next(x for x in d["county"] if x["id"] == "c99")
T = "2026-11-24"
r.update(
    phone="916-393-7433",
    notes="Spelled 916-393-RIDE on ACC's site. Older directories list 916-393-9026 ext. 333.",
    summary="Call 916-393-7433 to sign up. They offer rides for older adults to medical appointments, shopping and errands.",
    source="ACC Senior Services – ACC Rides program page (accsv.org)",
    verified=T, updated=T,
)
p.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("updated c99")
