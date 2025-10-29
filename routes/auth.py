"""
Authentication routes for the frontend application.
"""
from fastapi import APIRouter, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
from typing import Optional
from datetime import datetime, timedelta
import hashlib
import os
from dotenv import load_dotenv
load_dotenv()

from utils.helpers import (
    hash_password,
    generate_session_id,
    validate_email,
    validate_password
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Backend API configuration
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

# Session management (simple in-memory for demo)
sessions = {}


async def get_current_user(request: Request) -> Optional[dict]:
    """Get current user from session"""
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return None

    user_data = sessions[session_id]
    if datetime.now() - user_data["created_at"] > timedelta(hours=24):
        del sessions[session_id]
        return None

    return user_data["user"]


async def backend_request(method: str, endpoint: str, data: Optional[dict] = None, params: Optional[dict] = None):
    """Make request to backend API with context-managed HTTP client"""
    url = f"{BACKEND_URL}{endpoint}"

    try:
        print(f"DEBUG: backend_request - method={method}, url={url}, data={data}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(url, params=params)
            elif method == "POST":
                response = await client.post(url, json=data, params=params)
            elif method == "PUT":
                response = await client.put(url, json=data, params=params)
            elif method == "DELETE":
                response = await client.delete(url, params=params)

        print(f"DEBUG: backend_request - response status: {response.status_code}")
        response.raise_for_status()
        result = response.json()
        print(f"DEBUG: backend_request - response json: {result}")
        return result

    except httpx.HTTPStatusError as e:
        print(f"DEBUG: backend_request - HTTPStatusError: {e.response.status_code}, {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        print(f"DEBUG: backend_request - Exception: {type(e)}, {str(e)}")
        import traceback
        print(f"DEBUG: backend_request - Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login")
async def login(request: Request, email: str = Form(), password: str = Form()):
    """Handle login"""
    try:
        # Validate input
        if not validate_email(email) or not validate_password(password):
            raise HTTPException(status_code=400, detail="Invalid email or password format")

        # Authenticate with backend
        result = await backend_request("POST", "/auth/login", {
            "email": email,
            "password": password
        })

        # Create session
        session_id = generate_session_id(email)
        sessions[session_id] = {
            "user": result,
            "created_at": datetime.now()
        }

        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return response

    except HTTPException:
        error_message = "Invalid credentials"
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "error": error_message
        })


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Register page"""
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.post("/register")
async def register(request: Request, name: str = Form(), email: str = Form(), password: str = Form()):
    """Handle registration"""
    try:
        # Validate input
        if not name or len(name.strip()) < 2:
            raise HTTPException(status_code=400, detail="Name must be at least 2 characters")
        if not validate_email(email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        if not validate_password(password):
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

        # Log backend URL and request data
        print(f"DEBUG: BACKEND_URL = {BACKEND_URL}")
        print(f"DEBUG: Registering user: name={name.strip()}, email={email.lower()}")

        # Register with backend
        print("DEBUG: About to call backend_request")
        result = await backend_request("POST", "/auth/register", {
            "name": name.strip(),
            "email": email.lower(),
            "password": password
        })
        print("DEBUG: backend_request completed successfully")

        print(f"DEBUG: Backend response: {result}")

        # Auto-login after registration
        session_id = generate_session_id(email)
        sessions[session_id] = {
            "user": result,
            "created_at": datetime.now()
        }

        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return response

    except HTTPException as e:
        print(f"DEBUG: HTTPException in register: {e.detail}")
        error_message = str(e.detail)
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": error_message
        })
    except Exception as e:
        print(f"DEBUG: Unexpected error in register: {str(e)}")
        print(f"DEBUG: Exception type: {type(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        error_message = "Registration failed. Please try again."
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": error_message
        })


@router.get("/logout")
async def logout(request: Request):
    """Logout"""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions:
        del sessions[session_id]

    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie(key="session_id")
    return response