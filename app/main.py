from fastapi import FastAPI
from dotenv import load_dotenv
from app.controllers import text_controller, media_controller
import os

# Load environment variables from the .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

app = FastAPI(title="WhatsApp Boost Tool")

# Include text_controller routes under a specific path
app.include_router(text_controller.router, prefix="/send", tags=["Send Actions"])
app.include_router(media_controller.router, prefix="/send", tags=["Send Actions"])

@app.get("/")
def read_root():
    return {"message": "WhatsApp Boost Tool API is running."}
