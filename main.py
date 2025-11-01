# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
from datetime import datetime
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# Create the FastAPI app
app = FastAPI()

# Mount the 'static' directory (for CSS and images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Point to the 'templates' folder
templates = Jinja2Templates(directory="templates")

# Define the homepage route
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# --- Simple prototype endpoints ---

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
VENDOR_NDJSON = DATA_DIR / "vendors.ndjson"
FACULTY_NDJSON = DATA_DIR / "faculty.ndjson"


@app.post("/vendor", response_class=HTMLResponse)
async def submit_vendor(
    request: Request,
    company_name: str = Form(...),
    product_name: str = Form(...),
    website: str = Form(...),
    category: str = Form(...),
    features: str = Form(""),
    integrations: str = Form(""),
    pricing_model: str = Form(""),
    contact_email: str = Form(...),
):
    submission = {
        "submitted_at": datetime.utcnow().isoformat() + "Z",
        "company_name": company_name.strip(),
        "product_name": product_name.strip(),
        "website": website.strip(),
        "category": category.strip(),
        "features": [f.strip() for f in features.split(",") if f.strip()],
        "integrations": [i.strip() for i in integrations.split(",") if i.strip()],
        "pricing_model": pricing_model.strip(),
        "contact_email": contact_email.strip(),
    }

    with VENDOR_NDJSON.open("a", encoding="utf-8") as f:
        f.write(json.dumps(submission) + "\n")

    html = f"""
    <html><head><title>Thanks</title><link rel=\"stylesheet\" href=\"/static/style.css\"></head>
    <body>
    <main class=\"narrow\">
      <h1>Thanks for your submission</h1>
      <p>We recorded <strong>{product_name}</strong> by <strong>{company_name}</strong>. We'll review and surface it to faculty.</p>
      <p><a class=\"btn\" href=\"/\">Back to homepage</a></p>
    </main>
    </body></html>
    """
    return HTMLResponse(content=html)


@app.get("/search", response_class=HTMLResponse)
async def search(
    request: Request,
    keyword: str = "",
    category: str = "",
    integrates_with: str = "",
    price_tier: str = "",
):
    results = []
    if VENDOR_NDJSON.exists():
        with VENDOR_NDJSON.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if keyword and keyword.lower() not in (
                    json.dumps(item).lower()
                ):
                    continue
                if category and category.lower() not in item.get("category", "").lower():
                    continue
                if integrates_with:
                    if not any(
                        integrates_with.lower() in integ.lower()
                        for integ in item.get("integrations", [])
                    ):
                        continue
                if price_tier and price_tier.lower() != item.get("pricing_model", "").lower():
                    continue
                results.append(item)

    # Soft gate: show up to 3 results to anonymous users, then prompt signup
    visible_results = results[:3]
    items_html = "".join(
        f"<li><strong>{r['product_name']}</strong> by {r['company_name']} — "
        f"<a href='{r['website']}' target='_blank' rel='noopener'>site</a> | "
        f"Category: {r.get('category','')} | Pricing: {r.get('pricing_model','')}" \
        f"<br><small>Integrations: {', '.join(r.get('integrations', []))}</small>" \
        f"</li>" for r in visible_results
    )

    if not items_html:
        items_html = "<li>No matches yet. Vendors: submit your product so it can be found.</li>"
    elif len(results) > 3:
        items_html += (
            f"<li class='card'>Showing 3 of {len(results)} results. "
            f"<a class='btn' href='/signup'>Create a free faculty account to see full details</a>"
            f"</li>"
        )

    html = f"""
    <html><head><title>Search results</title><link rel=\"stylesheet\" href=\"/static/style.css\"></head>
    <body>
    <main class=\"narrow\">
      <h1>Search results</h1>
      <ul class=\"results\">{items_html}</ul>
      <p><a class=\"btn\" href=\"/\">Back to homepage</a></p>
    </main>
    </body></html>
    """
    return HTMLResponse(content=html)


@app.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


# --- Import (URL → draft) prototype ---
@app.get("/vendor/import", response_class=HTMLResponse)
async def vendor_import(request: Request):
    # Simple page with a single URL field; scraping implemented in next step
    return templates.TemplateResponse("vendor_import.html", {"request": request})


@app.get("/faculty/import", response_class=HTMLResponse)
async def faculty_import(request: Request):
    # Mirror page for faculty profile import
    return templates.TemplateResponse("faculty_import.html", {"request": request})


@app.get("/import", response_class=HTMLResponse)
async def combined_import(request: Request):
    # Combined page with faculty (left) and vendor (right) import forms
    return templates.TemplateResponse("import.html", {"request": request})


@app.post("/vendor/import/preview", response_class=HTMLResponse)
async def vendor_import_preview(request: Request, source_url: str = Form(...)):
    url = source_url.strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        url = "https://" + url
        parsed = urlparse(url)
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "EdTechRepoBot/0.1"})
        resp.raise_for_status()
    except Exception:
        html = f"""
        <html><head><title>Import error</title><link rel=\"stylesheet\" href=\"/static/style.css\"></head>
        <body><main class=\"narrow\"> 
        <h1>We couldn't fetch that URL</h1>
        <p>Please check the address and try again: {url}</p>
        <p><a class=\"btn\" href=\"/import\">Back</a></p>
        </main></body></html>
        """
        return HTMLResponse(content=html, status_code=400)

    soup = BeautifulSoup(resp.text, "html.parser")
    title_meta = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "application-name"})
    title = title_meta.get("content") if title_meta else (soup.title.string if soup.title else "")
    site_meta = soup.find("meta", property="og:site_name")
    site_name = site_meta.get("content") if site_meta else None
    company_name = (site_name or parsed.netloc.replace("www.", "")).strip()
    product_name = (title or company_name).strip()

    draft = {
        "company_name": company_name,
        "product_name": product_name,
        "website": url,
        "category": "",
        "features": "",
        "integrations": "",
        "pricing_model": "",
        "contact_email": "",
    }

    return templates.TemplateResponse("vendor_preview.html", {"request": request, **draft})


@app.post("/faculty/manual", response_class=HTMLResponse)
async def faculty_manual(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    courses: str = Form(""),
    tools: str = Form(""),
):
    # Enforce .edu emails for faculty accounts
    domain = email.strip().lower().split("@")[-1]
    if not domain.endswith(".edu"):
        html = f"""
        <html><head><title>.edu required</title><link rel=\"stylesheet\" href=\"/static/style.css\"></head>
        <body>
        <main class=\"narrow\">
          <h1>.edu email required</h1>
          <p>Faculty accounts must use a <strong>.edu</strong> email address. If you can't comply, please contact support and we'll help.</p>
          <p><a class=\"btn\" href=\"/import\">Back to profile creation</a></p>
        </main>
        </body></html>
        """
        return HTMLResponse(content=html, status_code=400)

    entry = {
        "submitted_at": datetime.utcnow().isoformat() + "Z",
        "name": name.strip(),
        "email": email.strip(),
        "phone": phone.strip(),
        "courses": [c.strip() for c in courses.split(";") if c.strip()] if ";" in courses else [c.strip() for c in courses.split(",") if c.strip()],
        "tools": [t.strip() for t in tools.split(",") if t.strip()],
    }

    with FACULTY_NDJSON.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    html = f"""
    <html><head><title>Profile created</title><link rel=\"stylesheet\" href=\"/static/style.css\"></head>
    <body>
    <main class=\"narrow\">
      <h1>Thanks, {name}</h1>
      <p>Your faculty profile has been created in draft. We'll use this to match tools.</p>
      <p><a class=\"btn\" href=\"/\">Back to homepage</a> <a class=\"btn\" href=\"/import\">Back to import</a></p>
    </main>
    </body></html>
    """
    return HTMLResponse(content=html)


@app.post("/vendor/manual", response_class=HTMLResponse)
async def vendor_manual(
    request: Request,
    company_name: str = Form(...),
    product_name: str = Form(...),
    website: str = Form(...),
    contact_email: str = Form(...),
    phone: str = Form(""),
    category: str = Form(""),
    features: str = Form(""),
    integrations: str = Form(""),
):
    entry = {
        "submitted_at": datetime.utcnow().isoformat() + "Z",
        "company_name": company_name.strip(),
        "product_name": product_name.strip(),
        "website": website.strip(),
        "category": category.strip(),
        "features": [f.strip() for f in features.split(",") if f.strip()],
        "integrations": [i.strip() for i in integrations.split(",") if i.strip()],
        "contact_email": contact_email.strip(),
        "phone": phone.strip(),
        "source": "manual",
    }

    with VENDOR_NDJSON.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    html = f"""
    <html><head><title>Vendor profile created</title><link rel=\"stylesheet\" href=\"/static/style.css\"></head>
    <body>
    <main class=\"narrow\">
      <h1>Thanks, {company_name}</h1>
      <p>Your vendor profile has been created in draft. We'll make it discoverable to faculty.</p>
      <p><a class=\"btn\" href=\"/\">Back to homepage</a> <a class=\"btn\" href=\"/import\">Back to import</a></p>
    </main>
    </body></html>
    """
    return HTMLResponse(content=html)