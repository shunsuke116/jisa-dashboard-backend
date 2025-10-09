import uuid
from logging import getLogger
from typing import Any, Dict, List

from fastapi import APIRouter

logger = getLogger(__name__)
router = APIRouter()


@router.get("/health")
def health() -> Dict[str, str]:
    return {"health": "ok"}
