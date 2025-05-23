import uvicorn

from src.main import app

if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=8000, env_file=".env")
