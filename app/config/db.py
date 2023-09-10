from motor import motor_asyncio
import pymongo
from app.config.env import DB_HOST, DB_PORT


async def get_db():
    client = motor_asyncio.AsyncIOMotorClient(f"mongodb://{DB_HOST}:{DB_PORT}")
    db = client["rinha_db"]
    collection = db["rinha_collection"]
    collection.create_index("apelido", unique=True)
    collection.create_index([("buscar_like", pymongo.TEXT)])
    return db
