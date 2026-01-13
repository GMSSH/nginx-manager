import asyncio
from app.server import app

if __name__ == "__main__":
    asyncio.run(app.run())