# EdTech Repo – Product Requirements Notes

## Onboarding Strategy (Tease-first)
- Allow anonymous users to search and preview limited results.
- Require account creation to unlock full details, save/search alerts, or contact vendors.
- Vendors may start filling the submission form; require account to finalize/publish.

### Rationale
- Progressive reveal improves top-of-funnel and conversion (users see value before sign-up).
- Comparable patterns: Zillow, Glassdoor, Crunchbase.

### Initial UX (MVP)
- Faculty: show up to 3 visible results; display CTA: "Create a free faculty account to see full profiles and save searches."
- Vendors: allow draft submission; prompt to create an account to publish.

### Metrics to Track
- Preview → signup conversion rate.
- Vendor draft started → account created → listing published.
- Engagement after signup (saved searches created, vendor profile completeness).

### Future Enhancements
- Personalization: "faculty like you adopted X" after onboarding.
- Vendor dashboard metrics: impressions, clicks, contact requests.

## URL → Draft Profile Utility
- Goal: Reduce friction for vendors (and later faculty) by auto-drafting entries from a URL.
- Flow: User enters URL → scrape page → extract title/meta/OG tags → map to fields → present editable draft → save.
- MVP Tech: `requests` + `beautifulsoup4` (no headless browser). Optional LLM prompt for field mapping later.
- Data targets: company name, product name, website, category, features, integrations, contact email if present.

## Faculty Eligibility
- Faculty accounts require a `.edu` email address.
- UI copy should state: "Use .edu only — contact support if you can't comply."
- Backend must validate `.edu` and return a friendly error if not satisfied.
