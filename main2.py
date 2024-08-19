from fastapi import FastAPI, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
import uvicorn
# Pydantic models and custom type for ObjectId

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            try:
                return str(ObjectId(v))
            except Exception as e:
                raise ValueError(f"Invalid ObjectId: {v}") from e
        raise TypeError(f"ObjectId must be of type str or ObjectId, but got {type(v)}")

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
        json_encoders = {
            ObjectId: str,
        }
        arbitrary_types_allowed = True

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
        json_encoders = {
            ObjectId: str,
        }
        arbitrary_types_allowed = True

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
        json_encoders = {
            ObjectId: str,
        }
        arbitrary_types_allowed = True

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
        json_encoders = {
            ObjectId: str,
        }
        arbitrary_types_allowed = True

# FastAPI app setup

app = FastAPI()

# MongoDB setup
MONGO_DETAILS = "mongodb+srv://jeffbarlowspady:f5nlDfzrROpHOcAg@longtrees.j3weklg.mongodb.net/retryWrites=true&w=majority"
client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.LongTrees

seed_sources_collection = database.get_collection("SeedSources")
growers_collection = database.get_collection("Growers")
sub_successions_collection = database.get_collection("SubSuccessions")
tree_list_collection = database.get_collection("TreeList")

# CRUD operations for SeedSource

@app.post("/seed_sources/", response_model=SeedSource)
async def create_seed_source(seed_source: SeedSource):
    seed_source = jsonable_encoder(seed_source)
    new_seed_source = await seed_sources_collection.insert_one(seed_source)
    created_seed_source = await seed_sources_collection.find_one({"_id": new_seed_source.inserted_id})
    return SeedSource(**created_seed_source)

@app.get("/seed_sources/", response_model=List[SeedSource])
async def list_seed_sources():
    seed_sources = await seed_sources_collection.find().to_list(length=100)
    return [SeedSource(**source) for source in seed_sources]

@app.get("/seed_sources/{id}", response_model=SeedSource)
async def get_seed_source(id: str):
    seed_source = await seed_sources_collection.find_one({"_id": ObjectId(id)})
    if seed_source is None:
        raise HTTPException(status_code=404, detail="SeedSource not found")
    return SeedSource(**seed_source)

@app.put("/seed_sources/{id}", response_model=SeedSource)
async def update_seed_source(id: str, seed_source: SeedSource):
    seed_source = {k: v for k, v in seed_source.dict().items() if v is not None}
    update_result = await seed_sources_collection.update_one({"_id": ObjectId(id)}, {"$set": seed_source})
    if update_result.modified_count == 1:
        updated_seed_source = await seed_sources_collection.find_one({"_id": ObjectId(id)})
        return SeedSource(**updated_seed_source)
    existing_seed_source = await seed_sources_collection.find_one({"_id": ObjectId(id)})
    if existing_seed_source is not None:
        return SeedSource(**existing_seed_source)
    raise HTTPException(status_code=404, detail="SeedSource not found")

@app.delete("/seed_sources/{id}")
async def delete_seed_source(id: str):
    delete_result = await seed_sources_collection.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return {"message": "SeedSource deleted successfully"}
    raise HTTPException(status_code=404, detail="SeedSource not found")

# CRUD operations for Growers

@app.post("/growers/", response_model=Grower)
async def create_grower(grower: Grower):
    grower = jsonable_encoder(grower)
    new_grower = await growers_collection.insert_one(grower)
    created_grower = await growers_collection.find_one({"_id": new_grower.inserted_id})
    return Grower(**created_grower)

@app.get("/growers/", response_model=List[Grower])
async def list_growers():
    growers = await growers_collection.find().to_list(length=100)
    return [Grower(**grower) for grower in growers]

@app.get("/growers/{id}", response_model=Grower)
async def get_grower(id: str):
    grower = await growers_collection.find_one({"_id": ObjectId(id)})
    if grower is None:
        raise HTTPException(status_code=404, detail="Grower not found")
    return Grower(**grower)

@app.put("/growers/{id}", response_model=Grower)
async def update_grower(id: str, grower: Grower):
    grower = {k: v for k, v in grower.dict().items() if v is not None}
    update_result = await growers_collection.update_one({"_id": ObjectId(id)}, {"$set": grower})
    if update_result.modified_count == 1:
        updated_grower = await growers_collection.find_one({"_id": ObjectId(id)})
        return Grower(**updated_grower)
    existing_grower = await growers_collection.find_one({"_id": ObjectId(id)})
    if existing_grower is not None:
        return Grower(**existing_grower)
    raise HTTPException(status_code=404, detail="Grower not found")

@app.delete("/growers/{id}")
async def delete_grower(id: str):
    delete_result = await growers_collection.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return {"message": "Grower deleted successfully"}
    raise HTTPException(status_code=404, detail="Grower not found")

# CRUD operations for SubSuccessions

@app.post("/sub_successions/", response_model=SubSuccession)
async def create_sub_succession(sub_succession: SubSuccession):
    sub_succession = jsonable_encoder(sub_succession)
    new_sub_succession = await sub_successions_collection.insert_one(sub_succession)
    created_sub_succession = await sub_successions_collection.find_one({"_id": new_sub_succession.inserted_id})
    return SubSuccession(**created_sub_succession)

@app.get("/sub_successions/", response_model=List[SubSuccession])
async def list_sub_successions():
    sub_successions = await sub_successions_collection.find().to_list(length=100)
    return [SubSuccession(**sub_succession) for sub_succession in sub_successions]

@app.get("/sub_successions/{id}", response_model=SubSuccession)
async def get_sub_succession(id: str):
    sub_succession = await sub_successions_collection.find_one({"_id": ObjectId(id)})
    if sub_succession is None:
        raise HTTPException(status_code=404, detail="SubSuccession not found")
    return SubSuccession(**sub_succession)

@app.put("/sub_successions/{id}", response_model=SubSuccession)
async def update_sub_succession(id: str, sub_succession: SubSuccession):
    sub_succession = {k: v for k, v in sub_succession.dict().items() if v is not None}
    update_result = await sub_successions_collection.update_one({"_id": ObjectId(id)}, {"$set": sub_succession})
    if update_result.modified_count == 1:
        updated_sub_succession = await sub_successions_collection.find_one({"_id": ObjectId(id)})
        return SubSuccession(**updated_sub_succession)
    existing_sub_succession = await sub_successions_collection.find_one({"_id": ObjectId(id)})
    if existing_sub_succession is not None:
        return SubSuccession(**existing_sub_succession)
    raise HTTPException(status_code=404, detail="SubSuccession not found")

@app.delete("/sub_successions/{id}")
async def delete_sub_succession(id: str):
    delete_result = await sub_successions_collection.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return {"message": "SubSuccession deleted successfully"}
    raise HTTPException(status_code=404, detail="SubSuccession not found")

# CRUD operations for TreeList

@app.post("/trees/", response_model=Tree)
async def create_tree(tree: Tree):
    tree = jsonable_encoder(tree)
    new_tree = await tree_list_collection.insert_one(tree)
    created_tree = await tree_list_collection.find_one({"_id": new_tree.inserted_id})
    return Tree(**created_tree)

@app.get("/trees/", response_model=List[Tree])
async def list_trees():
    trees = await tree_list_collection.find().to_list(length=100)
    return [Tree(**tree) for tree in trees]

@app.get("/trees/{id}", response_model=Tree)
async def get_tree(id: str):
    tree = await tree_list_collection.find_one({"_id": ObjectId(id)})
    if tree is None:
        raise HTTPException(status_code=404, detail="Tree not found")
    return Tree(**tree)

@app.put("/trees/{id}", response_model=Tree)
async def update_tree(id: str, tree: Tree):
    tree = {k: v for k, v in tree.dict().items() if v is not None}
    update_result = await tree_list_collection.update_one({"_id": ObjectId(id)}, {"$set": tree})
    if update_result.modified_count == 1:
        updated_tree = await tree_list_collection.find_one({"_id": ObjectId(id)})
        return Tree(**updated_tree)
    existing_tree = await tree_list_collection.find_one({"_id": ObjectId(id)})
    if existing_tree is not None:
        return Tree(**existing_tree)
    raise HTTPException(status_code=404, detail="Tree not found")

@app.delete("/trees/{id}")
async def delete_tree(id: str):
    delete_result = await tree_list_collection.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return {"message": "Tree deleted successfully"}
    raise HTTPException(status_code=404, detail="Tree not found")
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
