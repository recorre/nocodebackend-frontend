"""
Export routes for the frontend application
Provides UI for users to export their data for static site generation
"""

from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import httpx
from typing import Optional
from datetime import datetime

from .auth import get_current_user, backend_request

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard/export", response_class=HTMLResponse)
async def export_page(request: Request, user: Optional[dict] = Depends(get_current_user)):
    """Export data page"""
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    try:
        # Get user's stats for export preview
        threads = await backend_request("GET", "/api/v1/threads/", params={"usuario_proprietario_id": user.get("user_id")})

        total_comments = 0
        if isinstance(threads, dict) and "data" in threads:
            for thread in threads["data"]:
                try:
                    comments = await backend_request("GET", "/api/v1/comments/", params={"thread_referencia_id": thread["id"]})
                    if isinstance(comments, dict) and "data" in comments:
                        total_comments += len(comments["data"])
                except:
                    pass

        return templates.TemplateResponse("dashboard/export.html", {
            "request": request,
            "user": user,
            "stats": {
                "threads": len(threads.get("data", []) if isinstance(threads, dict) else threads),
                "comments": total_comments
            }
        })

    except HTTPException:
        return templates.TemplateResponse("dashboard/export.html", {
            "request": request,
            "user": user,
            "stats": {"threads": 0, "comments": 0}
        })


@router.post("/dashboard/export/download")
async def download_export(
    export_format: str = Form("json"),
    include_comments: bool = Form(True),
    include_metadata: bool = Form(True),
    user: Optional[dict] = Depends(get_current_user)
):
    """Download user data export"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Request export from backend
        export_data = await backend_request(
            "GET",
            "/api/export/user/data",
            params={
                "format": export_format,
                "include_comments": include_comments,
                "include_metadata": include_metadata
            }
        )

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nocode-comments-export-{timestamp}"

        # Set appropriate content type and filename
        if export_format == "yaml":
            content_type = "application/yaml"
            filename += ".yaml"
        elif export_format == "csv":
            content_type = "text/csv"
            filename += ".csv"
        else:
            content_type = "application/json"
            filename += ".json"

        # Convert to bytes if needed
        if isinstance(export_data, dict):
            import json
            content = json.dumps(export_data, indent=2, ensure_ascii=False).encode('utf-8')
        else:
            content = str(export_data).encode('utf-8')

        # Return as downloadable file
        return StreamingResponse(
            iter([content]),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/dashboard/export/thread/{thread_id}")
async def export_thread_page(
    thread_id: str,
    request: Request,
    user: Optional[dict] = Depends(get_current_user)
):
    """Export specific thread page"""
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    try:
        # Get thread info
        thread = await backend_request("GET", f"/api/v1/threads/{thread_id}/status")

        # Get comment count
        comments = await backend_request("GET", "/api/v1/comments/", params={"thread_referencia_id": thread_id})
        comment_count = len(comments.get("data", []) if isinstance(comments, dict) else comments)

        return templates.TemplateResponse("dashboard/export_thread.html", {
            "request": request,
            "user": user,
            "thread": thread,
            "comment_count": comment_count
        })

    except HTTPException:
        raise HTTPException(status_code=404, detail="Thread not found")


@router.post("/dashboard/export/thread/{thread_id}/download")
async def download_thread_export(
    thread_id: str,
    export_format: str = Form("json"),
    template: str = Form("default"),
    user: Optional[dict] = Depends(get_current_user)
):
    """Download thread-specific export"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Request thread export from backend
        export_data = await backend_request(
            "GET",
            f"/api/export/threads/{thread_id}",
            params={
                "format": export_format,
                "template": template
            }
        )

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"thread-{thread_id}-export-{timestamp}"

        # Set appropriate content type and filename
        if export_format == "html":
            content_type = "text/html"
            filename += ".html"
        elif export_format == "yaml":
            content_type = "application/yaml"
            filename += ".yaml"
        else:
            content_type = "application/json"
            filename += ".json"

        # Convert to bytes if needed
        if isinstance(export_data, dict):
            import json
            content = json.dumps(export_data, indent=2, ensure_ascii=False).encode('utf-8')
        else:
            content = str(export_data).encode('utf-8')

        return StreamingResponse(
            iter([content]),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/dashboard/export/site/{site_id}")
async def export_site_page(
    site_id: str,
    request: Request,
    user: Optional[dict] = Depends(get_current_user)
):
    """Export site data page"""
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    try:
        # Get site threads
        threads = await backend_request(
            "GET",
            "/api/v1/threads/",
            params={
                "usuario_proprietario_id": user.get("user_id"),
                "external_page_id": site_id
            }
        )

        threads_list = threads.get("data", []) if isinstance(threads, dict) else threads
        total_comments = 0

        for thread in threads_list:
            try:
                comments = await backend_request("GET", "/api/v1/comments/", params={"thread_referencia_id": thread["id"]})
                if isinstance(comments, dict) and "data" in comments:
                    total_comments += len(comments["data"])
            except:
                pass

        return templates.TemplateResponse("dashboard/export_site.html", {
            "request": request,
            "user": user,
            "site_id": site_id,
            "threads": threads_list,
            "total_comments": total_comments
        })

    except HTTPException:
        raise HTTPException(status_code=404, detail="Site not found")


@router.post("/dashboard/export/site/{site_id}/download")
async def download_site_export(
    site_id: str,
    export_format: str = Form("json"),
    user: Optional[dict] = Depends(get_current_user)
):
    """Download site-wide export"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Request site export from backend
        export_data = await backend_request(
            "GET",
            f"/api/export/sites/{site_id}",
            params={"format": export_format}
        )

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"site-{site_id}-export-{timestamp}"

        # Set appropriate content type and filename
        if export_format == "yaml":
            content_type = "application/yaml"
            filename += ".yaml"
        else:
            content_type = "application/json"
            filename += ".json"

        # Convert to bytes if needed
        if isinstance(export_data, dict):
            import json
            content = json.dumps(export_data, indent=2, ensure_ascii=False).encode('utf-8')
        else:
            content = str(export_data).encode('utf-8')

        return StreamingResponse(
            iter([content]),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")