# ECSE3038 - Week 4, Lecture 1 - starter
# Monday's API with the hard-coded list emptied.
# Run:  uvicorn app:app --reload

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI")) #connection to the cluster 
db = client["edcse3038"] #database 
devices = db["devices"]  #collection

devices.create_index([("name", 1)], unique=True)


# project, cluster, database, collection
 
app = FastAPI()


class Device(BaseModel):
    name: str
    room: str
    temp: float
    online: bool


readings = []


@app.get("/devices", status_code=201)
def get_devices():
    return list(devices.find({}, {"_id": 0}))  # return all devices, excluding the _id field


@app.get("/devices/{name}")
def get_device(name: str):
    device = devices.find_one({"name": name}, {"_id": 0})
    if device:
        return device
    raise HTTPException(status_code=404, detail="No device called " + name)


@app.post("/devices", status_code=201)
def create_device(device: Device):
    new_device = device.model_dump()
    try:
        devices.insert_one(new_device)
    except DuplicateKeyError:
        print("Error: A device with this name already exists.")
        raise HTTPException(
            status_code=400, 
            detail=f"A device with this name '{device.name}' already exists."
        )
    
    new_device.pop("_id")  # remove the _id field before returning
    return new_device

@app.delete("/devices/{name}", status_code=204)
def delete_device(name: str):
    result = devices.delete_one({"name": name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No device called " + name)
    return None