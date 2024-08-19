from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from motorhead import Document, ServiceException
from motor.motor_asyncio import AsyncIOMotorClient
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
templates = Jinja2Templates(directory="~/templates")

# MongoDB setup
MONGO_DETAILS = "mongodb+srv://jeffbarlowspady:f5nlDfzrROpHOcAg@longtrees.j3weklg.mongodb.net/"
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client(['LongTrees']['SeedSource']['Sub-Succession']['Tree List'])
# Register models with the database 
#database.register(['SeedSource', 'Grower', 'Sub-Succession', 'Tree List'])

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

@app.post("/seed_sources/", response_class=HTMLResponse)
async def create_seed_source(request: Request,
                             succession_number: str = Form(...),
                             description: str = Form(None),
                             germination_rate: float = Form(...),
                             quantity: int = Form(...),
                             scarification_instructions: str = Form(None),
                             stratification_instructions: str = Form(None),
                             date_added: str = Form(...),
                             seeds_issued: int = Form(...),
                             geographic_location: str = Form(None),
                             supplier: str = Form(None),
                             viability_duration: str = Form(None)):
    try:
        seed_source = SeedSource(
            succession_number=succession_number,
            description=description,
            germination_rate=germination_rate,
            quantity=quantity,
            scarification_instructions=scarification_instructions,
            stratification_instructions=stratification_instructions,
            date_added=date.fromisoformat(date_added),
            seeds_issued=seeds_issued,
            geographic_location=geographic_location,
            supplier=supplier,
            viability_duration=viability_duration
        )
        await seed_source.insert()
        return templates.TemplateResponse("_seed_source_item.html", {"request": request, "seed_source": seed_source})
    except ServiceException as e:
        handle_service_exception(e)

@app.get("/seed_sources/{id}", response_class=HTMLResponse)
async def get_seed_source(request: Request, id: str):
    try:
        seed_source = await SeedSource.get(id)
        return templates.TemplateResponse("_seed_source_item.html", {"request": request, "seed_source": seed_source})
    except ServiceException as e:
        handle_service_exception(e)

@app.post("/seed_sources/{id}/edit", response_class=HTMLResponse)
async def update_seed_source(request: Request, id: str,
                             succession_number: str = Form(...),
                             description: str = Form(None),
                             germination_rate: float = Form(...),
                             quantity: int = Form(...),
                             scarification_instructions: str = Form(None),
                             stratification_instructions: str = Form(None),
                             date_added: str = Form(...),
                             seeds_issued: int = Form(...),
                             geographic_location: str = Form(None),
                             supplier: str = Form(None),
                             viability_duration: str = Form(None)):
    try:
        seed_source = await SeedSource.get(id)
        seed_source.succession_number = succession_number
        seed_source.description = description
        seed_source.germination_rate = germination_rate
        seed_source.quantity = quantity
        seed_source.scarification_instructions = scarification_instructions
        seed_source.stratification_instructions = stratification_instructions
        seed_source.date_added = date.fromisoformat(date_added)
        seed_source.seeds_issued = seeds_issued
        seed_source.geographic_location = geographic_location
        seed_source.supplier = supplier
        seed_source.viability_duration = viability_duration
        await seed_source.save()
        return templates.TemplateResponse("_seed_source_item.html", {"request": request, "seed_source": seed_source})
    except ServiceException as e:
        handle_service_exception(e)

@app.post("/seed_sources/{id}/delete", response_class=HTMLResponse)
async def delete_seed_source(request: Request, id: str):
    try:
        seed_source = await SeedSource.get(id)
        await seed_source.delete()
        return templates.TemplateResponse("list_seed_sources.html", {"request": request})
    except ServiceException as e:
        handle_service_exception(e)

@app.get("/growers/", response_class=HTMLResponse)
async def get_growers(request: Request):
    try:
        growers = await Grower.find_all()
        return templates.TemplateResponse("list_growers.html", {"request": request, "growers": growers})
    except ServiceException as e:
        handle_service_exception(e)

@app.post("/growers/", response_class=HTMLResponse)
async def create_grower(request: Request,
                        name: str = Form(...),
                        contact_info: str = Form(None),
                        joined_at: str = Form(...),
                        address: str = Form(None),
                        latitude: float = Form(None),
                        longitude: float = Form(None),
                        group_membership: str = Form(None)):
    try:
        grower = Grower(
            name=name,
            contact_info=contact_info,
            joined_at=date.fromisoformat(joined_at),
            address=address,
            latitude=latitude,
            longitude=longitude,
            group_membership=group_membership,
            assigned_sub_successions=[]
        )
        await grower.insert()
        return templates.TemplateResponse("_grower_item.html", {"request": request, "grower": grower})
    except ServiceException as e:
        handle_service_exception(e)

@app.get("/growers/{id}", response_class=HTMLResponse)
async def get_grower(request: Request, id: str):
    try:
        grower = await Grower.get(id)
        return templates.TemplateResponse("_grower_item.html", {"request": request, "grower": grower})
    except ServiceException as e:
        handle_service_exception(e)

@app.post("/growers/{id}/edit", response_class=HTMLResponse)
async def update_grower(request: Request, id: str,
                        name: str = Form(...),
                        contact_info: str = Form(None),
                        joined_at: str = Form(...),
                        address: str = Form(None),
                        latitude: float = Form(None),
                        longitude: float = Form(None),
                        group_membership: str = Form(None)):
    try:
        grower = await Grower.get(id)
        grower.name = name
        grower.contact_info = contact_info
        grower.joined_at = date.fromisoformat(joined_at)
        grower.address = address
        grower.latitude = latitude
        grower.longitude = longitude
        grower.group_membership = group_membership
        await grower.save()
        return templates.TemplateResponse("_grower_item.html", {"request": request, "grower": grower})
    except ServiceException as e:
        handle_service_exception(e)

@app.post("/growers/{id}/delete", response_class=HTMLResponse)
async def delete_grower(request: Request, id: str):
    try:
        grower = await Grower.get(id)
        await grower.delete()
        return templates.TemplateResponse("list_growers.html", {"request": request})
    except ServiceException as e:
        handle_service_exception(e)

@app.get("/sub_successions/", response_class=HTMLResponse)
async def get_sub_successions(request: Request):
    try:
        sub_successions = await SubSuccession.find_all()
        return templates.TemplateResponse("list_sub_successions.html", {"request": request, "sub_successions": sub_successions})
    except ServiceException as e:
        handle_service_exception(e)

@app.post("/sub_successions/", response_class=HTMLResponse)
async def create_sub_succession(request: Request,
                                sub_succession_number: str = Form(...),
                                seed_source_id: str = Form(...),
                                grower_id: str = Form(...),
                                created_at: str = Form(...),
                                status: str = Form(...),
                                expected_outcome: str = Form(None)):
    try:
        sub_succession = SubSuccession(
            sub_succession_number=sub_succession_number,
            seed_source_id=seed_source_id,
            grower_id=grower_id,
            created_at=date.fromisoformat(created_at),
            status=status,
            expected_outcome=expected_outcome,
            tree_list=[]
        )
        await sub_succession.insert()
        return templates.TemplateResponse("_sub_succession_item.html", {"request": request, "sub_succession": sub_succession})
    except ServiceException as e:
        handle_service_exception(e)

@app.get("/sub_successions/{id}", response_class=HTMLResponse)
async def get_sub_succession(request: Request, id: str):
    try:
        sub_succession = await SubSuccession.get(id)
        return templates.TemplateResponse("_sub_succession_item.html", {"request": request, "sub_succession": sub_succession})
    except ServiceException as e:
        handle_service_exception(e)

@app.post("/sub_successions/{id}/edit", response_class=HTMLResponse)
async def update_sub_succession(request: Request, id: str,
                                sub_succession_number: str = Form(...),
                                seed_source_id: str = Form(...),
                                grower_id: str = Form(...),
                                created_at: str = Form(...),
                                status: str = Form(...),
                                expected_outcome: str = Form(None)):
    try:
        sub_succession = await SubSuccession.get(id)
        sub_succession.sub_succession_number = sub_succession_number
        sub_succession.seed_source_id = seed_source_id
        sub_succession.grower_id = grower_id
        sub_succession.created_at = date.fromisoformat(created_at)
        sub_succession.status = status
        sub_succession.expected_outcome = expected_outcome
        await sub_succession.save()
        return templates.TemplateResponse("_sub_succession_item.html", {"request": request, "sub_succession": sub_succession})
    except ServiceException as e:
        handle_service_exception(e)

@app.post("/sub_successions/{id}/delete", response_class=HTMLResponse)
async def delete_sub_succession(request: Request, id: str):
    try:
        sub_succession = await SubSuccession.get(id)
        await sub_succession.delete()
        return templates.TemplateResponse("list_sub_successions.html", {"request": request})
    except ServiceException as e:
        handle_service_exception(e)

@app.get("/trees/", response_class=HTMLResponse)
async def get_trees(request: Request):
    try:
        trees = await Tree.find_all()
        return templates.TemplateResponse("list_trees.html", {"request": request, "trees": trees})
    except ServiceException as e:
        handle_service_exception(e)

@app.post("/trees/", response_class=HTMLResponse)
async def create_tree(request: Request,
                      species: str = Form(...),
                      sub_succession_id: str = Form(...),
                      growth_stage: str = Form(...),
                      planted_at: str = Form(...),
                      height: float = Form(...),
                      health_status: str = Form(...),
                      yield_data: str = Form(None),
                      notes: str = Form(None)):
    try:
        tree = Tree(
            species=species,
            sub_succession_id=sub_succession_id,
            growth_stage=growth_stage,
            planted_at=date.fromisoformat(planted_at),
            height=height,
            health_status=health_status,
            yield_data=yield_data,
            notes=notes
        )
        await tree.insert()
        return templates.TemplateResponse("_tree_item.html", {"request": request, "tree": tree})
    except ServiceException as e:
        handle_service_exception(e)

@app.get("/trees/{id}", response_class=HTMLResponse)
async def get_tree(request: Request, id: str):
    try:
        tree = await Tree.get(id)
        return templates.TemplateResponse("_tree_item.html", {"request": request, "tree": tree})
    except ServiceException as e:
        handle_service_exception(e)

@app.post("/trees/{id}/edit", response_class=HTMLResponse)
async def update_tree(request: Request, id: str,
                      species: str = Form(...),
                      sub_succession_id: str = Form(...),
                      growth_stage: str = Form(...),
                      planted_at: str = Form(...),
                      height: float = Form(...),
                      health_status: str = Form(...),
                      yield_data: str = Form(None),
                      notes: str = Form(None)):
    try:
        tree = await Tree.get(id)
        tree.species = species
        tree.sub_succession_id = sub_succession_id
        tree.growth_stage = growth_stage
        tree.planted_at = date.fromisoformat(planted_at)
        tree.height = height
        tree.health_status = health_status
        tree.yield_data = yield_data
        tree.notes = notes
        await tree.save()
        return templates.TemplateResponse("_tree_item.html", {"request": request, "tree": tree})
    except ServiceException as e:
        handle_service_exception(e)

@app.post("/trees/{id}/delete", response_class=HTMLResponse)
async def delete_tree(request: Request, id: str):
    try:
        tree = await Tree.get(id)
        await tree.delete()
        return templates.TemplateResponse("list_trees.html", {"request": request})
    except ServiceException as e:
        handle_service_exception(e)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
