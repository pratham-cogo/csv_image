from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from src.middlewares import AuthenticationMiddleware
from src.configs.env import APP_ENV
from src.database.db import initialize_db
import logging
import os

logging.basicConfig(
    level=logging.DEBUG if APP_ENV == "development" else logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(title="CSV image reformatter", version="1.0")

if APP_ENV == "development":
    os.environ['PYTHONBREAKPOINT'] = 'IPython.terminal.debugger.set_trace'

# app.include_router(KAM_router, prefix="/KAM", tags=["Key Account Manager"])

# Add middleware
app.add_middleware(GZipMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if APP_ENV == "development" else ["https://your-production-domain.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the custom AuthenticationMiddleware
app.add_middleware(AuthenticationMiddleware)

@app.on_event("startup")
async def startup_event():
    initialize_db()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Welcome to the Image reformatter"}
