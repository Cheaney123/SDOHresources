# Link check (November 21, 2026)

Every link in `data/resources.json` was opened (144 unique URLs, 512 uses), first by script and then in a real browser for any that failed. Each was checked for the right page (title and content), not only that it loads.

## Replaced: broken links (404 or bad PDF)
| Resource | Old | New |
|---|---|---|
| Sacramento County Behavioral Health | dhs.saccounty.gov/BHS | dhs.saccounty.gov/us/en/behavioral-health.html |
| Meals on Wheels (Sourcewise) | mysourcewise.com/meals-wheels | mysourcewise.com/programs-services/meals/ |
| San Mateo County Aging & Adult Services (now **Aging & Disability Services**) | smchealth.org/aas | smchealth.org/division/divisions/aging-and-disability-services/ (still mentions the TIES line) |
| Ceres Community Project referral form | old Squarespace PDF | ceresproject.org/s/Ceres-Medical-Referral-Form-Fillable.pdf |
| Caregiver Resource Centers brochure (24 resources) | chhs.ca.gov brochure PDF (removed) | caregivercalifornia.org (CA Caregiver Resource Centers) |

## Updated: moved addresses (redirects)
DHCS Medi-Cal transportation page and Medicare Savings Programs page (DHCS site redesign), Alameda IHSS, Amador IHSS, El Dorado County, Marin IHSS, Marin Access, Merced CAA, Nevada County IHSS, San Joaquin Aging Services, Community Resource Project, 211 Sacramento, SSA Extra Help. Nevada County Now now links to nevadacountyconnects.com instead of the county homepage.

## Flagged: could not be confirmed automatically
| Resource | Reason |
|---|---|
| Santa Clara County Behavioral Health Services Call Center (bhsd.santaclaracounty.gov) | Site blocks automated checks (Cloudflare). Confirm manually. |
| Santa Clara County IHSS (ssa.santaclaracounty.gov) | Same. |
| California LifeLine (californialifeline.com) | Same. |
| Del Norte Senior Center | Site works only over http (invalid security certificate). |

All other links load the expected page. Several government sites (Placer, Amador, El Dorado, Marin, SSA, CSD, cchealth.org) block scripts but load normally in a browser.
