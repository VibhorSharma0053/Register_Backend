import motor.motor_asyncio
from app.config import MONGO_URI, DB_NAME

try:
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    async def check_connection():
        try:
            await client.admin.command("ping")
            print("DB connected!")
        except:
            print("Connection Failed!")
    db = client[DB_NAME]
except Exception as e:
    print(f'Error in Connection.py: {e}')