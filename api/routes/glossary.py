"""GET /glossary — metric definitions from the compiled glossary."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

GLOSSARY_PATH = Path(__file__).resolve().parent.parent.parent / "ontology" / "generated" / "glossary.json"


@router.get("/glossary")
async def get_glossary():
    if GLOSSARY_PATH.exists():
        return json.loads(GLOSSARY_PATH.read_text())
    return {"error": "glossary not found — run make compile first"}
