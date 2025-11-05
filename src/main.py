from fastapi import FastAPI
from routes import base
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()
app.include_router(base.base_router)