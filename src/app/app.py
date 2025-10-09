import os
from logging import getLogger

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.routers import api, health
from src.app.exceptions.db_error import (
    SqlExecutionException,
    dbaccess_exception_handler,
)
from src.configurations import APIConfigurations

# from src.db import initialize
# from src.db.database import engine

logger = getLogger(__name__)

app = FastAPI(
    title=APIConfigurations.title,
    description=APIConfigurations.description,
    version=APIConfigurations.version,
)

origins = [
    "*",
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health.router, prefix=f"/v{APIConfigurations.version}/health", tags=["health"]
)
app.include_router(
    api.router, prefix=f"/v{APIConfigurations.version}/api", tags=["api"]
)

app.add_exception_handler(SqlExecutionException, dbaccess_exception_handler)
