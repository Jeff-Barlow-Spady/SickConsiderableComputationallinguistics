from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# MongoDB configuration
client = AsyncIOMotorClient(
    "mongodb+srv://jeffbarlowspady:f5nlDfzrROpHOcAg@longtrees.j3weklg.mongodb.net/retryWrites=true&w=majority&appName=LongTrees"
)


# Home Page
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# CRUD for SeedSources


@app.get("/seed_sources", response_class=HTMLResponse)
async def list_seed_sources(request: Request):
    seed_sources = await db.SeedSources.find().to_list(length=None)
    return templates.TemplateResponse("list_seed_sources.html", {
        "request": request,
        "seed_sources": seed_sources
    })


@app.get("/seed_source/new", response_class=HTMLResponse)
async def add_seed_source_form(request: Request):
    return templates.TemplateResponse("add_seed_source.html",
                                      {"request": request})


@app.post("/seed_source/new", response_class=HTMLResponse)
async def add_seed_source(request: Request,
                          succession_number: str = Form(...),
                          description: str = Form(...),
                          germination_rate: float = Form(...),
                          quantity: int = Form(...),
                          scarification_instructions: str = Form(...),
                          stratification_instructions: str = Form(...),
                          date_added: str = Form(...),
                          seeds_issued: int = Form(...),
                          geographic_location: str = Form(...),
                          supplier: str = Form(...),
                          viability_duration: str = Form(...)):
    seed_source = {
        "succession_number": succession_number,
        "description": description,
        "germination_rate": germination_rate,
        "quantity": quantity,
        "scarification_instructions": scarification_instructions,
        "stratification_instructions": stratification_instructions,
        "date_added": date_added,
        "seeds_issued": seeds_issued,
        "origin": {
            "geographic_location": geographic_location,
            "supplier": supplier
        },
        "viability_duration": viability_duration,
        "distribution_log": []
    }

    try:
        await db.SeedSources.insert_one(seed_source)
        return templates.TemplateResponse("_seed_source_item.html", {
            "request": request,
            "seed_source": seed_source
        },
                                          status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/seed_source/{id}/edit", response_class=HTMLResponse)
async def edit_seed_source_form(request: Request, id: str):
    seed_source = await db.SeedSources.find_one({"_id": ObjectId(id)})
    if seed_source is None:
        raise HTTPException(status_code=404, detail="Seed source not found")
    return templates.TemplateResponse("edit_seed_source.html", {
        "request": request,
        "seed_source": seed_source
    })


@app.post("/seed_source/{id}/edit", response_class=HTMLResponse)
async def edit_seed_source(request: Request,
                           id: str,
                           succession_number: str = Form(...),
                           description: str = Form(...),
                           germination_rate: float = Form(...),
                           quantity: int = Form(...),
                           scarification_instructions: str = Form(...),
                           stratification_instructions: str = Form(...),
                           date_added: str = Form(...),
                           seeds_issued: int = Form(...),
                           geographic_location: str = Form(...),
                           supplier: str = Form(...),
                           viability_duration: str = Form(...)):
    updated_seed_source = {
        "succession_number": succession_number,
        "description": description,
        "germination_rate": germination_rate,
        "quantity": quantity,
        "scarification_instructions": scarification_instructions,
        "stratification_instructions": stratification_instructions,
        "date_added": date_added,
        "seeds_issued": seeds_issued,
        "origin": {
            "geographic_location": geographic_location,
            "supplier": supplier
        },
        "viability_duration": viability_duration
    }

    try:
        update_result = await db.SeedSources.update_one(
            {"_id": ObjectId(id)}, {"$set": updated_seed_source})
        if update_result.matched_count == 0:
            raise HTTPException(status_code=404,
                                detail="Seed source not found")
        return templates.TemplateResponse("_seed_source_item.html", {
            "request": request,
            "seed_source": updated_seed_source
        },
                                          status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/seed_source/{id}/delete", response_class=HTMLResponse)
async def delete_seed_source(request: Request, id: str):
    try:
        delete_result = await db.SeedSources.delete_one({"_id": ObjectId(id)})
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404,
                                detail="Seed source not found")
        return HTMLResponse(status_code=204)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# CRUD for Growers


@app.get("/growers", response_class=HTMLResponse)
async def list_growers(request: Request):
    growers = await db.Growers.find().to_list(length=None)
    return templates.TemplateResponse("list_growers.html", {
        "request": request,
        "growers": growers
    })


@app.get("/grower/new", response_class=HTMLResponse)
async def add_grower_form(request: Request):
    return templates.TemplateResponse("add_grower.html", {"request": request})


@app.post("/grower/new", response_class=HTMLResponse)
async def add_grower(request: Request,
                     name: str = Form(...),
                     contact_info: str = Form(...),
                     joined_at: str = Form(...),
                     address: str = Form(...),
                     latitude: float = Form(...),
                     longitude: float = Form(...),
                     group_membership: str = Form(...)):
    grower = {
        "name": name,
        "contact_info": contact_info,
        "joined_at": joined_at,
        "address": address,
        "geographic_coordinates": {
            "latitude": latitude,
            "longitude": longitude
        },
        "group_membership": group_membership,
        "assigned_sub_successions": []
    }

    try:
        await db.Growers.insert_one(grower)
        return templates.TemplateResponse("_grower_item.html", {
            "request": request,
            "grower": grower
        },
                                          status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/grower/{id}/edit", response_class=HTMLResponse)
async def edit_grower_form(request: Request, id: str):
    grower = await db.Growers.find_one({"_id": ObjectId(id)})
    if grower is None:
        raise HTTPException(status_code=404, detail="Grower not found")
    return templates.TemplateResponse("edit_grower.html", {
        "request": request,
        "grower": grower
    })


@app.post("/grower/{id}/edit", response_class=HTMLResponse)
async def edit_grower(request: Request,
                      id: str,
                      name: str = Form(...),
                      contact_info: str = Form(...),
                      joined_at: str = Form(...),
                      address: str = Form(...),
                      latitude: float = Form(...),
                      longitude: float = Form(...),
                      group_membership: str = Form(...)):
    updated_grower = {
        "name": name,
        "contact_info": contact_info,
        "joined_at": joined_at,
        "address": address,
        "geographic_coordinates": {
            "latitude": latitude,
            "longitude": longitude
        },
        "group_membership": group_membership
    }

    try:
        update_result = await db.Growers.update_one({"_id": ObjectId(id)},
                                                    {"$set": updated_grower})
        if update_result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Grower not found")
        return templates.TemplateResponse("_grower_item.html", {
            "request": request,
            "grower": updated_grower
        },
                                          status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/grower/{id}/delete", response_class=HTMLResponse)
async def delete_grower(request: Request, id: str):
    try:
        delete_result = await db.Growers.delete_one({"_id": ObjectId(id)})
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Grower not found")
        return HTMLResponse(status_code=204)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# CRUD for SubSuccessions


@app.get("/sub_successions", response_class=HTMLResponse)
async def list_sub_successions(request: Request):
    sub_successions = await db.SubSuccessions.find().to_list(length=None)
    return templates.TemplateResponse("list_sub_successions.html", {
        "request": request,
        "sub_successions": sub_successions
    })


@app.get("/sub_succession/new", response_class=HTMLResponse)
async def add_sub_succession_form(request: Request):
    return templates.TemplateResponse("add_sub_succession.html",
                                      {"request": request})


@app.post("/sub_succession/new", response_class=HTMLResponse)
async def add_sub_succession(request: Request,
                             sub_succession_number: str = Form(...),
                             seed_source_id: str = Form(...),
                             grower_id: str = Form(...),
                             created_at: str = Form(...),
                             status: str = Form(...),
                             expected_outcome: str = Form(...)):
    sub_succession = {
        "sub_succession_number": sub_succession_number,
        "seed_source_id": ObjectId(seed_source_id),
        "grower_id": ObjectId(grower_id),
        "created_at": created_at,
        "status": status,
        "merged_into": None,
        "parent_sub_succession": None,
        "expected_outcome": expected_outcome,
        "tree_list": []
    }

    try:
        await db.SubSuccessions.insert_one(sub_succession)
        return templates.TemplateResponse("_sub_succession_item.html", {
            "request": request,
            "sub_succession": sub_succession
        },
                                          status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sub_succession/{id}/edit", response_class=HTMLResponse)
async def edit_sub_succession_form(request: Request, id: str):
    sub_succession = await db.SubSuccessions.find_one({"_id": ObjectId(id)})
    if sub_succession is None:
        raise HTTPException(status_code=404, detail="Sub-succession not found")
    return templates.TemplateResponse("edit_sub_succession.html", {
        "request": request,
        "sub_succession": sub_succession
    })


@app.post("/sub_succession/{id}/edit", response_class=HTMLResponse)
async def edit_sub_succession(request: Request,
                              id: str,
                              sub_succession_number: str = Form(...),
                              seed_source_id: str = Form(...),
                              grower_id: str = Form(...),
                              created_at: str = Form(...),
                              status: str = Form(...),
                              expected_outcome: str = Form(...)):
    updated_sub_succession = {
        "sub_succession_number": sub_succession_number,
        "seed_source_id": ObjectId(seed_source_id),
        "grower_id": ObjectId(grower_id),
        "created_at": created_at,
        "status": status,
        "expected_outcome": expected_outcome
    }

    try:
        update_result = await db.SubSuccessions.update_one(
            {"_id": ObjectId(id)}, {"$set": updated_sub_succession})
        if update_result.matched_count == 0:
            raise HTTPException(status_code=404,
                                detail="Sub-succession not found")
        return templates.TemplateResponse(
            "_sub_succession_item.html", {
                "request": request,
                "sub_succession": updated_sub_succession
            },
            status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sub_succession/{id}/delete", response_class=HTMLResponse)
async def delete_sub_succession(request: Request, id: str):
    try:
        delete_result = await db.SubSuccessions.delete_one(
            {"_id": ObjectId(id)})
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404,
                                detail="Sub-succession not found")
        return HTMLResponse(status_code=204)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# CRUD for Trees


@app.get("/trees", response_class=HTMLResponse)
async def list_trees(request: Request):
    trees = await db.TreeList.find().to_list(length=None)
    return templates.TemplateResponse("list_trees.html", {
        "request": request,
        "trees": trees
    })


@app.get("/tree/new", response_class=HTMLResponse)
async def add_tree_form(request: Request):
    return templates.TemplateResponse("add_tree.html", {"request": request})


@app.post("/tree/new", response_class=HTMLResponse)
async def add_tree(request: Request,
                   sub_succession_id: str = Form(...),
                   species: str = Form(...),
                   growth_stage: str = Form(...),
                   planted_at: str = Form(...),
                   height: float = Form(...),
                   health_status: str = Form(...),
                   yield_data: str = Form(...),
                   notes: str = Form(...)):
    tree = {
        "sub_succession_id": ObjectId(sub_succession_id),
        "species": species,
        "growth_stage": growth_stage,
        "planted_at": planted_at,
        "height": height,
        "health_status": health_status,
        "yield_data": yield_data,
        "environmental_monitoring": [],
        "notes": notes
    }

    try:
        await db.TreeList.insert_one(tree)
        return templates.TemplateResponse("_tree_item.html", {
            "request": request,
            "tree": tree
        },
                                          status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tree/{id}/edit", response_class=HTMLResponse)
async def edit_tree_form(request: Request, id: str):
    tree = await db.TreeList.find_one({"_id": ObjectId(id)})
    if tree is None:
        raise HTTPException(status_code=404, detail="Tree not found")
    return templates.TemplateResponse("edit_tree.html", {
        "request": request,
        "tree": tree
    })


@app.post("/tree/{id}/edit", response_class=HTMLResponse)
async def edit_tree(request: Request,
                    id: str,
                    sub_succession_id: str = Form(...),
                    species: str = Form(...),
                    growth_stage: str = Form(...),
                    planted_at: str = Form(...),
                    height: float = Form(...),
                    health_status: str = Form(...),
                    yield_data: str = Form(...),
                    notes: str = Form(...)):
    updated_tree = {
        "sub_succession_id": ObjectId(sub_succession_id),
        "species": species,
        "growth_stage": growth_stage,
        "planted_at": planted_at,
        "height": height,
        "health_status": health_status,
        "yield_data": yield_data,
        "notes": notes
    }

    try:
        update_result = await db.TreeList.update_one({"_id": ObjectId(id)},
                                                     {"$set": updated_tree})
        if update_result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Tree not found")
        return templates.TemplateResponse("_tree_item.html", {
            "request": request,
            "tree": updated_tree
        },
                                          status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tree/{id}/delete", response_class=HTMLResponse)
async def delete_tree(request: Request, id: str):
    try:
        delete_result = await db.TreeList.delete_one({"_id": ObjectId(id)})
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Tree not found")
        return HTMLResponse(status_code=204)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
