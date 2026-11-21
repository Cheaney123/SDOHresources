# Source-backed corrections (checked 2026-11-20)

Applied to `data/resources.json` by `scripts/apply_corrections_2026_11_20.py`. Each corrected record has `verified` and `source` set. Details I couldn't verify are kept out of patient copy and flagged for staff.

| Resource | Exact claim | Source |
|---|---|---|
| CalFresh (statewide) | Apply online at BenefitsCal.com. CalFresh Info Line 1-877-847-3663. | CDSS CalFresh page, cdss.ca.gov/CalFresh |
| CalFresh (statewide) | Since June 1, 2019, SSI recipients may be eligible for CalFresh. CalFresh doesn't affect other benefits. | CDSS "SSI and CalFresh", cdss.ca.gov/food/home/ssi-and-calfresh (replaces the retired older-adult flier) |
| CalFresh (statewide) | GetCalFresh.org continues as CDSS-supported outreach about applying through BenefitsCal. | CDSS GetCalFresh transition page |
| Sacramento Food Bank & Family Services | The Food Finder locates partner distribution sites. SFBFS does not distribute food from its Bell Ave distribution center. CalFresh help: (916) 779-0052. | sacramentofoodbank.org (FAQ and Find Food pages) |
| Medi-Cal rides: Anthem Blue Cross | Ride scheduling 1-877-931-4755 (TTY 711), Mon–Fri 7 a.m.–7 p.m. Call at least 5 business days ahead (7 for new riders). NEMT and NMT are requested through your doctor. 800-407-4627 is member services, not the ride line. | mss.anthem.com California Medicaid transportation page |
| Medi-Cal rides: Health Net | ModivCare 1-855-253-6863 (TTY 1-866-288-3133), Mon–Fri 7 a.m.–7 p.m. Member Services 1-800-675-6110, 24/7. | Health Net Medi-Cal "Get a ride" flier (healthnet.com) |
| Medi-Cal rides: Molina | American Logistics (844) 292-2688, taking requests 24/7. Call at least 3 business days ahead. | molinahealthcare.com CA Medi-Cal transportation page |
| Medi-Cal rides: any plan | Managed-care members ask their plan's member services for NEMT, which needs a prescription. | DHCS Transportation Services page |
| Senior Legal Hotline | Free legal advice for Sacramento County residents 60+. Advises tenants in eviction cases. | iCarol, Pro Bono Net and findhelp listings. **LSNC's own page could not be loaded; confirm with LSNC.** |
| Medicare Savings Programs | The asset test was eliminated on 1/1/2024. Apply on BenefitsCal, at the county office, or find the county office via the Medi-Cal Helpline (800) 541-5555. MSP-only applicants may use the MC 14A form. | DHCS "Medicare Savings Programs in California" |
| Del Norte mental health line | 888-446-4408 is the county mental health plan access line. DHCS doesn't state whether it is staffed 24/7, so patient copy makes no 24/7 claim. Ongoing county care is a Medi-Cal benefit. | DHCS county MHP contact list |

## Not verified (kept out of patient copy, or marked "not verified" for staff)

- Molina member services 888-665-4621 comes from a county desk aid only.
- The Kaiser Medi-Cal ride line for Northern California is unconfirmed. Patients are told to call the number on their card.
- Partnership, Alameda Alliance, CenCal, CCHP, HPSJ, SFHP, SCFHP, HPSM and CCAH ride lines were carried over from v1 without new claim-level evidence; they appear in the review queue.
- Paratransit lines (Merced, Santa Clara, Santa Cruz) were carried over from v1 without claim-level evidence (content-check warnings).
- Same-day intake or capacity for any food site is unknown. The default is "Intake: not confirmed".
