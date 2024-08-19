from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from motorhead import Document, AgnosticClient , ServiceException
from typing import List, Optional
from datetime import date

# Define models using Motorhead's Document class
class SeedSource(Document):
    succession_number: str
    description: Optional[str]
    germination_rate: float
    quantity: int
    scarification_instructions: Optional[str]
    stratification_instructions: Optional[str]
    date_added: date
    seeds_issued: int
    geographic_location: Optional[str]
    supplier: Optional[str]
    viability_duration: Optional[str]

class Grower(Document):
    name: str
    contact_info: Optional[str]
    joined_at: date
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    group_membership: Optional[str]
    assigned_sub_successions: List[str] = []

class SubSuccession(Document):
    sub_succession_number: str
    seed_source_id: str
    grower_id: str
    created_at: date
    status: str
    expected_outcome: Optional[str]
    tree_list: List[str] = []

class Tree(Document):
    species: str
    sub_succession_id: str
    growth_stage: str
    planted_at: date
    height: float
    health_status: str
    yield_data: Optional[str]
    notes: Optional[str]

# Initialize FastAPI app and Jinja2 templates
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# MongoDB setup
MONGO_DETAILS = "mongodb+srv://jeffbarlowspady:f5nlDfzrROpHOcAg@longtrees.j3weklg.mongodb.net/?retryWrites=true&w=majority"
client = AgnosticClient(MONGO_DETAILS)

# Register models with the database
client['LongTrees']

# Helper function to handle ServiceException
def handle_service_exception(e: ServiceException):
    raise HTTPException(status_code=404, detail=str(e))

# CRUD Routes

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/seed_sources/", response_class=HTMLResponse)
async def get_seed_sources(request: Request):
    try:
        seed_sources = await SeedSource.find_all()
        return templates.TemplateResponse("list_seed_sources.html", {"request": request, "seed_sources": seed_sources})
    except ServiceException as e:
        handle_service_exception(e)

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
