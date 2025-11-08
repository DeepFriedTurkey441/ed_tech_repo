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

## Roadmap: Pre-Seeded Graph of Vendor and Professor Nodes

**Description**
- Implement a system modeled after Facebook’s early network-building strategy. Before users sign up, automatically create vendor and professor nodes from public data (department listings, course catalogs, vendor websites). Store them as graph entities with inferred relationships such as "teaches", "offers", and "may align with". When professors or vendors join, pre-generated profiles will be presented as editable and used to suggest immediate matches.

**Goals**
- Increase early network density and engagement at launch.
- Ensure professors and vendors find immediate, relevant connections.
- Use only publicly available professional data.
- Maintain transparency by labeling pre-generated profiles as editable upon joining.

**Tech Notes**
- Use a graph database (Neo4j or ArangoDB) for nodes/edges.
- Optional semantic layer: vector embeddings for similarity (requirements ↔ offerings), e.g., pgvector/Neo4j GDS.
- API: endpoint to surface recommended connections dynamically (e.g., `GET /graph/recommendations?actor=professor&id=<id>` and `actor=vendor`).
- Inferred edges: department → course → professor (teaches); vendor → product (offers); product ↔ course/department (may align with) via taxonomy/embedding matches.
- Label any pre-generated profile as "Pre-seeded — claim and edit" on first login.

## Faculty-Governed Vendor Funding Architecture (Planned)

### Overview
- Vendors finance the peer-review process through a central Evidence Fund.
- Funds are distributed to reviewers and platform operations, never tied to specific outcomes.

### Entities
- Vendor
- Review
- ReviewPanel
- EvidenceFund (ledger)
- Transaction (links Vendor → EvidenceFund → Reviewer payout)

### Logic Flow
1. Vendor submits payment (Stripe API integration → EvidenceFund ledger entry).
2. Platform assigns reviewers via randomization algorithm (avoiding conflicts).
3. Upon review completion:
   - Score + narrative published automatically.
   - Reviewer honorarium triggered from EvidenceFund ledger.
4. Platform margin automatically deducted (configurable percentage).

### API Endpoints (planned)
- POST /funds/deposit
- GET /funds/ledger
- POST /reviews/assign
- POST /reviews/complete
- POST /payments/release

### Governance Constraints
- Equal fee regardless of review outcome.
- Mandatory publication of all reviews.
- Public record of EvidenceFund activity (aggregated).

### Future Extensions
- PilotTrack schema integration.
- Institution subscription analytics.
- Audit dashboard for transparency reports.
