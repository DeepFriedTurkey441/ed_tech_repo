# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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