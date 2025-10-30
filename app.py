"""
Frontend Dashboard - FastAPI + Jinja2
Comment Widget Management Interface
"""

from fastapi import FastAPI, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import Optional
from datetime import datetime, timedelta
import hashlib
import logging

# Import route modules
from routes import pages, auth, dashboard, export, comments, threads, widget, api, default

# Create FastAPI app
app = FastAPI(
    title="Comment Widget Dashboard",
    description="Management interface for Comment Widget system",
    version="1.0.0"
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    import logging
    logging.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Response: {response.status_code} for {request.url}")
    # Log route information for debugging
    if hasattr(request, 'scope') and 'path' in request.scope:
        logging.info(f"Route path: {request.scope.get('path')}")
    return response

# Vercel handler for serverless deployment
# This is the entry point that Vercel uses for serverless functions
# handler = app  # Commented out to avoid conflicts

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/dist", StaticFiles(directory="dist"), name="dist")

# Templates
templates = Jinja2Templates(directory="templates")

# Include route modules
app.include_router(pages.router, tags=["pages"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(dashboard.router, tags=["dashboard"])
app.include_router(export.router, prefix="/dashboard", tags=["export"])
app.include_router(comments.router, prefix="/comments", tags=["comments"])
app.include_router(threads.router, prefix="/threads", tags=["threads"])
app.include_router(widget.router, prefix="/widget", tags=["widget"])
app.include_router(api.router, prefix="/api", tags=["api"])
app.include_router(default.router, tags=["default"])

# Debug: Log all registered routes
import logging
logging.info("Registered routes:")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        logging.info(f"  {route.methods} {route.path}")
    elif hasattr(route, 'path'):
        logging.info(f"  Mount: {route.path}")
    elif hasattr(route, 'name'):
        logging.info(f"  Route: {route.name}")
    else:
        logging.info(f"  Unknown route type: {type(route)}")

# Error handlers
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    return templates.TemplateResponse("errors/404.html", {"request": request})

@app.exception_handler(500)
async def server_error_exception_handler(request: Request, exc):
    return templates.TemplateResponse("errors/500.html", {"request": request})

# Legacy routes (will be removed after full migration to route modules)
# These are kept temporarily for backward compatibility

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=3000, reload=True)