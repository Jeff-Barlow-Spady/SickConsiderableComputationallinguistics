from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from motorhead import ObjectId#Motorhead
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

# Customized ObjectId for Pydantic
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        try:
            return str(ObjectId(v))
        except Exception:
            raise ValueError(f"Invalid ObjectId: {v}")


# Pydantic models
class SeedSource(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
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

    class Config:
        json_encoders = {ObjectId: str}


class Grower(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    contact_info: Optional[str]
    joined_at: date
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    group_membership: Optional[str]
    assigned_sub_successions: List[str] = []

    class Config:
        json_encoders = {ObjectId: str}


class SubSuccession(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    sub_succession_number: str
    seed_source_id: PyObjectId
    grower_id: PyObjectId
    created_at: date
    status: str
    expected_outcome: Optional[str]
    tree_list: List[str] = []

    class Config:
        json_encoders = {ObjectId: str}


class Tree(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    species: str
    sub_succession_id: PyObjectId
    growth_stage: str
    planted_at: date
    height: float
    health_status: str
    yield_data: Optional[str]
    notes: Optional[str]

    class Config:
        json_encoders = {ObjectId: str}


# Initialize FastAPI app and Jinja2 templates
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# MongoDB setup
MONGO_DETAILS = "mongodb+srv://jeffbarlowspady:f5nlDfzrROpHOcAg@longtrees.j3weklg.mongodb.net/?retryWrites=true&w=majority"
client = AsyncIOMotorClient(MONGO_DETAILS)
database = AsyncIOMotorDatabase(client, "LongTrees")

seed_sources_collection = database.get_collection("SeedSource")
growers_collection = database.get_collection("Growers")
sub_successions_collection = database.get_collection("Sub-successuon")
trees_collection = database.get_collection("Tree List")


# Helper function to fetch a document by id
async def get_document_by_id(collection, resource_id, model):
    document = await collection.find_one({"_id": ObjectId(resource_id)})
    if document is None:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return model(**document)


# CRUD operations for SeedSources
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/seed_sources/", response_class=HTMLResponse)
async def get_seed_sources(request: Request):
    seed_sources = await seed_sources_collection.find().to_list(length=100)
    return templates.TemplateResponse(
        "list_seed_sources.html", {"request": request, "seed_sources": seed_sources}
    )


@app.post("/seed_sources/", response_class=HTMLResponse)
async def create_seed_source(
    request: Request,
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
    viability_duration: str = Form(None),
):
    seed_source_data = {
        "succession_number": succession_number,
        "description": description,
        "germination_rate": germination_rate,
        "quantity": quantity,
        "scarification_instructions": scarification_instructions,
        "stratification_instructions": stratification_instructions,
        "date_added": date.fromisoformat(date_added),
        "seeds_issued": seeds_issued,
        "geographic_location": geographic_location,
        "supplier": supplier,
        "viability_duration": viability_duration,
    }

    seed_source = SeedSource(**seed_source_data)
    seed_source = jsonable_encoder(seed_source)
    await seed_sources_collection.insert_one(seed_source)
    return templates.TemplateResponse(
        "seed_source_created.html", {"request": request, "seed_source": seed_source}
    )


@app.get("/seed_sources/form", response_class=HTMLResponse)
async def create_seed_source_form(request: Request):
    return templates.TemplateResponse(
        "create_seed_source_form.html", {"request": request}
    )


@app.get("/seed_sources/{id}", response_class=HTMLResponse)
async def get_seed_source(request: Request, id: str):
    seed_source = await get_document_by_id(seed_sources_collection, id, SeedSource)
    return templates.TemplateResponse(
        "view_seed_source.html", {"request": request, "seed_source": seed_source}
    )


@app.get("/seed_sources/{id}/edit", response_class=HTMLResponse)
async def edit_seed_source_form(request: Request, id: str):
    seed_source = await get_document_by_id(seed_sources_collection, id, SeedSource)
    return templates.TemplateResponse(
        "edit_seed_source_form.html", {"request": request, "seed_source": seed_source}
    )


@app.post("/seed_sources/{id}/edit", response_class=HTMLResponse)
async def update_seed_source(
    request: Request,
    id: str,
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
    viability_duration: str = Form(None),
):
    seed_source_data = {
        "succession_number": succession_number,
        "description": description,
        "germination_rate": germination_rate,
        "quantity": quantity,
        "scarification_instructions": scarification_instructions,
        "stratification_instructions": stratification_instructions,
        "date_added": date.fromisoformat(date_added),
        "seeds_issued": seeds_issued,
        "geographic_location": geographic_location,
        "supplier": supplier,
        "viability_duration": viability_duration,
    }

    update_result = await seed_sources_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": seed_source_data}
    )
    if update_result.modified_count == 1:
        updated_seed_source = await get_document_by_id(
            seed_sources_collection, id, SeedSource
        )
        return templates.TemplateResponse(
            "view_seed_source.html",
            {"request": request, "seed_source": updated_seed_source},
        )
    raise HTTPException(status_code=404, detail="SeedSource not found")


@app.post("/seed_sources/{id}/delete", response_class=HTMLResponse)
async def delete_seed_source(request: Request, id: str):
    delete_result = await seed_sources_collection.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return templates.TemplateResponse(
            "seed_source_deleted.html", {"request": request}
        )
    raise HTTPException(status_code=404, detail="SeedSource not found")


# CRUD operations for Growers
@app.get("/growers/", response_class=HTMLResponse)
async def get_growers(request: Request):
    growers = await growers_collection.find().to_list(length=100)
    return templates.TemplateResponse(
        "list_growers.html", {"request": request, "growers": growers}
    )


@app.post("/growers/", response_class=HTMLResponse)
async def create_grower(
    request: Request,
    name: str = Form(...),
    contact_info: str = Form(None),
    joined_at: str = Form(...),
    address: str = Form(None),
    latitude: float = Form(None),
    longitude: float = Form(None),
    group_membership: str = Form(None),
):
    grower_data = {
        "name": name,
        "contact_info": contact_info,
        "joined_at": date.fromisoformat(joined_at),
        "address": address,
        "latitude": latitude,
        "longitude": longitude,
        "group_membership": group_membership,
        "assigned_sub_successions": [],
    }

    grower = Grower(**grower_data)
    grower = jsonable_encoder(grower)
    await growers_collection.insert_one(grower)
    return templates.TemplateResponse(
        "grower_created.html", {"request": request, "grower": grower}
    )


@app.get("/growers/form", response_class=HTMLResponse)
async def create_grower_form(request: Request):
    return templates.TemplateResponse("create_grower_form.html", {"request": request})


@app.get("/growers/{id}", response_class=HTMLResponse)
async def get_grower(request: Request, id: str):
    grower = await get_document_by_id(growers_collection, id, Grower)
    return templates.TemplateResponse(
        "view_grower.html", {"request": request, "grower": grower}
    )


@app.get("/growers/{id}/edit", response_class=HTMLResponse)
async def edit_grower_form(request: Request, id: str):
    grower = await get_document_by_id(growers_collection, id, Grower)
    return templates.TemplateResponse(
        "edit_grower_form.html", {"request": request, "grower": grower}
    )


@app.post("/growers/{id}/edit", response_class=HTMLResponse)
async def update_grower(
    request: Request,
    id: str,
    name: str = Form(...),
    contact_info: str = Form(None),
    joined_at: str = Form(...),
    address: str = Form(None),
    latitude: float = Form(None),
    longitude: float = Form(None),
    group_membership: str = Form(None),
):
    grower_data = {
        "name": name,
        "contact_info": contact_info,
        "joined_at": date.fromisoformat(joined_at),
        "address": address,
        "latitude": latitude,
        "longitude": longitude,
        "group_membership": group_membership,
    }

    update_result = await growers_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": grower_data}
    )
    if update_result.modified_count == 1:
        updated_grower = await get_document_by_id(growers_collection, id, Grower)
        return templates.TemplateResponse(
            "view_grower.html", {"request": request, "grower": updated_grower}
        )
    raise HTTPException(status_code=404, detail="Grower not found")


@app.post("/growers/{id}/delete", response_class=HTMLResponse)
async def delete_grower(request: Request, id: str):
    delete_result = await growers_collection.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return templates.TemplateResponse("grower_deleted.html", {"request": request})
    raise HTTPException(status_code=404, detail="Grower not found")


# CRUD operations for SubSuccessions
@app.get("/sub_successions/", response_class=HTMLResponse)
async def get_sub_successions(request: Request):
    sub_successions = await sub_successions_collection.find().to_list(length=100)
    return templates.TemplateResponse(
        "list_sub_successions.html",
        {"request": request, "sub_successions": sub_successions},
    )


@app.post("/sub_successions/", response_class=HTMLResponse)
async def create_sub_succession(
    request: Request,
    sub_succession_number: str = Form(...),
    seed_source_id: str = Form(...),
    grower_id: str = Form(...),
    created_at: str = Form(...),
    status: str = Form(...),
    expected_outcome: str = Form(None),
):
    sub_succession_data = {
        "sub_succession_number": sub_succession_number,
        "seed_source_id": PyObjectId(seed_source_id),
        "grower_id": PyObjectId(grower_id),
        "created_at": date.fromisoformat(created_at),
        "status": status,
        "expected_outcome": expected_outcome,
        "tree_list": [],
    }

    sub_succession = SubSuccession(**sub_succession_data)
    sub_succession = jsonable_encoder(sub_succession)
    await sub_successions_collection.insert_one(sub_succession)
    return templates.TemplateResponse(
        "sub_succession_created.html",
        {"request": request, "sub_succession": sub_succession},
    )


@app.get("/sub_successions/form", response_class=HTMLResponse)
async def create_sub_succession_form(request: Request):
    return templates.TemplateResponse(
        "create_sub_succession_form.html", {"request": request}
    )


@app.get("/sub_successions/{id}", response_class=HTMLResponse)
async def get_sub_succession(request: Request, id: str):
    sub_succession = await get_document_by_id(
        sub_successions_collection, id, SubSuccession
    )
    return templates.TemplateResponse(
        "view_sub_succession.html",
        {"request": request, "sub_succession": sub_succession},
    )


@app.get("/sub_successions/{id}/edit", response_class=HTMLResponse)
async def edit_sub_succession_form(request: Request, id: str):
    sub_succession = await get_document_by_id(
        sub_successions_collection, id, SubSuccession
    )
    return templates.TemplateResponse(
        "edit_sub_succession_form.html",
        {"request": request, "sub_succession": sub_succession},
    )


@app.post("/sub_successions/{id}/edit", response_class=HTMLResponse)
async def update_sub_succession(
    request: Request,
    id: str,
    sub_succession_number: str = Form(...),
    seed_source_id: str = Form(...),
    grower_id: str = Form(...),
    created_at: str = Form(...),
    status: str = Form(...),
    expected_outcome: str = Form(None),
):
    sub_succession_data = {
        "sub_succession_number": sub_succession_number,
        "seed_source_id": PyObjectId(seed_source_id),
        "grower_id": PyObjectId(grower_id),
        "created_at": date.fromisoformat(created_at),
        "status": status,
        "expected_outcome": expected_outcome,
    }

    update_result = await sub_successions_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": sub_succession_data}
    )
    if update_result.modified_count == 1:
        updated_sub_succession = await get_document_by_id(
            sub_successions_collection, id, SubSuccession
        )
        return templates.TemplateResponse(
            "view_sub_succession.html",
            {"request": request, "sub_succession": updated_sub_succession},
        )
    raise HTTPException(status_code=404, detail="SubSuccession not found")


@app.post("/sub_successions/{id}/delete", response_class=HTMLResponse)
async def delete_sub_succession(request: Request, id: str):
    delete_result = await sub_successions_collection.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return templates.TemplateResponse(
            "sub_succession_deleted.html", {"request": request}
        )
    raise HTTPException(status_code=404, detail="SubSuccession not found")


# CRUD operations for Trees
@app.get("/trees/", response_class=HTMLResponse)
async def get_trees(request: Request):
    trees = await trees_collection.find().to_list(length=100)
    return templates.TemplateResponse(
        "list_trees.html", {"request": request, "trees": trees}
    )


@app.post("/trees/", response_class=HTMLResponse)
async def create_tree(
    request: Request,
    species: str = Form(...),
    sub_succession_id: str = Form(...),
    growth_stage: str = Form(...),
    planted_at: str = Form(...),
    height: float = Form(...),
    health_status: str = Form(...),
    yield_data: str = Form(None),
    notes: str = Form(None),
):
    tree_data = {
        "species": species,
        "sub_succession_id": PyObjectId(sub_succession_id),
        "growth_stage": growth_stage,
        "planted_at": date.fromisoformat(planted_at),
        "height": height,
        "health_status": health_status,
        "yield_data": yield_data,
        "notes": notes,
    }

    tree = Tree(**tree_data)
    tree = jsonable_encoder(tree)
    await trees_collection.insert_one(tree)
    return templates.TemplateResponse(
        "tree_created.html", {"request": request, "tree": tree}
    )


@app.get("/trees/form", response_class=HTMLResponse)
async def create_tree_form(request: Request):
    return templates.TemplateResponse("create_tree_form.html", {"request": request})


@app.get("/trees/{id}", response_class=HTMLResponse)
async def get_tree(request: Request, id: str):
    tree = await get_document_by_id(trees_collection, id, Tree)
    return templates.TemplateResponse(
        "view_tree.html", {"request": request, "tree": tree}
    )


@app.get("/trees/{id}/edit", response_class=HTMLResponse)
async def edit_tree_form(request: Request, id: str):
    tree = await get_document_by_id(trees_collection, id, Tree)
    return templates.TemplateResponse(
        "edit_tree_form.html", {"request": request, "tree": tree}
    )


@app.post("/trees/{id}/edit", response_class=HTMLResponse)
async def update_tree(
    request: Request,
    id: str,
    species: str = Form(...),
    sub_succession_id: str = Form(...),
    growth_stage: str = Form(...),
    planted_at: str = Form(...),
    height: float = Form(...),
    health_status: str = Form(...),
    yield_data: str = Form(None),
    notes: str = Form(None),
):
    tree_data = {
        "species": species,
        "sub_succession_id": PyObjectId(sub_succession_id),
        "growth_stage": growth_stage,
        "planted_at": date.fromisoformat(planted_at),
        "height": height,
        "health_status": health_status,
        "yield_data": yield_data,
        "notes": notes,
    }

    update_result = await trees_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": tree_data}
    )
    if update_result.modified_count == 1:
        updated_tree = await get_document_by_id(trees_collection, id, Tree)
        return templates.TemplateResponse(
            "view_tree.html", {"request": request, "tree": updated_tree}
        )
    raise HTTPException(status_code=404, detail="Tree not found")


@app.post("/trees/{id}/delete", response_class=HTMLResponse)
async def delete_tree(request: Request, id: str):
    delete_result = await trees_collection.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return templates.TemplateResponse("tree_deleted.html", {"request": request})
    raise HTTPException(status_code=404, detail="Tree not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
