from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.on_event("startup")
async def startup_db():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    app.state.mongo_client = AsyncIOMotorClient(database_url)
    app.state.db = app.state.mongo_client.get_default_database()

@app.on_event("shutdown")
async def shutdown_db():
    app.state.mongo_client.close()

@app.get("/")
async def health_check():
    return {"status": "ok"}

@app.get("/todos")
async def get_todos():
    todos = await app.state.db.todos.find().to_list(None)
    return todos

@app.post("/todos")
async def create_todo(todo: dict):
    result = await app.state.db.todos.insert_one(todo)
    return {"id": str(result.inserted_id)}
