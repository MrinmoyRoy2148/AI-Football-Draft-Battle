from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.config import APP_NAME, VERSION
from app.engine.player_tools import load_players
from app.api.draft import router as draft_router
from app.api.analysis import router as analysis_router
from app.api.what_if import router as what_if_router

BASE_DIR = Path(__file__).resolve().parent.parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load player dataset into memory on startup
    load_players()
    yield

app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    description="Two-Player Football Team Competition with an AI Game Analyst Agent",
    lifespan=lifespan,
)

# CORS middleware for open browser interactions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static assets
static_dir = BASE_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Mount templates
templates_dir = BASE_DIR / "templates"
templates_dir.mkdir(parents=True, exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Include API Routers
app.include_router(draft_router)
app.include_router(analysis_router)
app.include_router(what_if_router)

@app.get("/", response_class=HTMLResponse, summary="Serve application interface")
async def serve_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"title": APP_NAME})

@app.get("/health", summary="Health check probe")
def health_check():
    return {"status": "ok", "app": APP_NAME, "version": VERSION}
