"""
Threads proxy routes for the frontend application.
"""
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
import httpx
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
load_dotenv()

from .auth import get_current_user, backend_request

router = APIRouter()
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
http_client = httpx.AsyncClient(timeout=30.0)


@router.post("/")
async def create_thread(
    request: Request,
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Create Thread"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        body = await request.json()
        data = {
            "usuario_proprietario_id": user["user_id"],
            **body
        }

        result = await backend_request("POST", "/threads/", data)
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_threads(
    request: Request,
    usuario_proprietario_id: Optional[int] = None,
    external_page_id: Optional[str] = None,
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """List Threads"""
    try:
        params = {}
        if usuario_proprietario_id:
            params["usuario_proprietario_id"] = usuario_proprietario_id
        if external_page_id:
            params["external_page_id"] = external_page_id

        result = await backend_request("GET", "/threads/", params=params)
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{thread_id}")
async def get_thread(
    thread_id: int,
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get Thread"""
    try:
        result = await backend_request("GET", f"/threads/{thread_id}")
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{thread_id}")
async def delete_thread(
    thread_id: int,
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Delete Thread"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        result = await backend_request("DELETE", f"/threads/{thread_id}")
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))