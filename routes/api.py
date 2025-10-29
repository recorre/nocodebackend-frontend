"""
API proxy routes for the frontend application.
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
from typing import Optional
import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
http_client = httpx.AsyncClient(timeout=30.0)


async def backend_request_api(method: str, endpoint: str, data: Optional[dict] = None, params: Optional[dict] = None):
    """Make request to backend API for api endpoints"""
    url = f"{BACKEND_URL}{endpoint}"

    try:
        if method == "GET":
            response = await http_client.get(url, params=params)
        elif method == "POST":
            response = await http_client.post(url, json=data, params=params)
        elif method == "PUT":
            response = await http_client.put(url, json=data, params=params)
        elif method == "DELETE":
            response = await http_client.delete(url, params=params)

        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comments")
async def api_list_comments(request: Request):
    """Api List Comments"""
    try:
        params = dict(request.query_params)
        result = await backend_request_api("GET", "/api/comments", params=params)
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comments/stats")
async def api_get_comment_stats():
    """Api Get Comment Stats"""
    try:
        result = await backend_request_api("GET", "/api/comments/stats")
        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))