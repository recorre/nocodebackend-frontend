"""
Default proxy routes for the frontend application.
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import httpx
from typing import Optional
import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()
BACKEND_URL = os.getenv("BACKEND_API_URL", "https://nocodebackend-api.vercel.app")
http_client = httpx.AsyncClient(timeout=30.0)


async def backend_request_default(method: str, endpoint: str, data: Optional[dict] = None, params: Optional[dict] = None):
    """Make request to backend API for default endpoints"""
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
        # For health check, return the status
        if endpoint == "/health":
            return {"status": "error", "code": e.response.status_code}
        raise
    except Exception as e:
        if endpoint == "/health":
            return {"status": "error", "message": str(e)}
        raise


@router.get("/")
async def root():
    """Root"""
    try:
        result = await backend_request_default("GET", "/")
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"message": "NoCode Backend Frontend Proxy"})


@router.get("/health")
async def health():
    """Health Check"""
    try:
        result = await backend_request_default("GET", "/health")
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)})