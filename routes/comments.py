"""
Comments proxy routes for the frontend application.
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
async def create_comment(
    request: Request,
    thread_referencia_id: int = Form(...),
    nome_autor: str = Form(...),
    email_autor: str = Form(...),
    conteudo: str = Form(...),
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Create Comment"""
    try:
        data = {
            "thread_referencia_id": thread_referencia_id,
            "nome_autor": nome_autor,
            "email_autor": email_autor,
            "conteudo": conteudo
        }

        result = await backend_request("POST", "/comments/", data)
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_comments(
    request: Request,
    thread_referencia_id: Optional[int] = None,
    is_approved: Optional[int] = None,
    limit: Optional[int] = None,
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """List Comments"""
    try:
        params = {}
        if thread_referencia_id:
            params["thread_referencia_id"] = thread_referencia_id
        if is_approved is not None:
            params["is_approved"] = is_approved
        if limit:
            params["limit"] = limit

        result = await backend_request("GET", "/comments/", params=params)
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{comment_id}")
async def get_comment(
    comment_id: int,
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Get Comment"""
    try:
        result = await backend_request("GET", f"/comments/{comment_id}")
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Delete Comment"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        result = await backend_request("DELETE", f"/comments/{comment_id}")
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{comment_id}/moderate")
async def moderate_comment(
    comment_id: int,
    request: Request,
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Moderate Comment"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        body = await request.json()
        is_approved = body.get("is_approved")

        result = await backend_request("PUT", f"/comments/{comment_id}/moderate", {
            "is_approved": is_approved
        })
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/moderate")
async def moderate_comments_bulk(
    request: Request,
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Moderate Comments Bulk"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        body = await request.json()
        comment_ids = body.get("comment_ids", [])
        is_approved = body.get("is_approved")

        results = []
        for comment_id in comment_ids:
            try:
                result = await backend_request("PUT", f"/comments/{comment_id}/moderate", {
                    "is_approved": is_approved
                })
                results.append({"comment_id": comment_id, "success": True, "result": result})
            except Exception as e:
                results.append({"comment_id": comment_id, "success": False, "error": str(e)})

        return JSONResponse(content={"results": results})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))