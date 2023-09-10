import os
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "27017")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_URI = f"redis://{REDIS_HOST}:{REDIS_PORT}"
