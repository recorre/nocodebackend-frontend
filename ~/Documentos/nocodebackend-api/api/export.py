"""
Export API for static site generators
Provides endpoints for users to export their data for building static sites
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

from ..auth.dependencies import get_current_user
from ..models.user import User
from ..services.comment_service import CommentService
from ..services.thread_service import ThreadService
from ..models.user import User

router = APIRouter()

# Initialize services
comment_service = CommentService()
thread_service = ThreadService()


@router.get("/export/user/data")
async def export_user_data(
    format: str = Query("json", description="Export format: json, yaml, csv"),
    include_comments: bool = Query(True, description="Include comment content"),
    include_metadata: bool = Query(True, description="Include metadata"),
    current_user: User = Depends(get_current_user)
):
    """
    Export all user data for static site generation
    """
    try:
        # Get user's threads
        threads = await thread_service.get_user_threads(current_user.id)

        # Get all comments for user's threads
        all_comments = []
        for thread in threads:
            comments = await comment_service.get_thread_comments(thread.id, approved_only=True)
            if include_comments:
                for comment in comments:
                    comment_data = {
                        "id": comment.id,
                        "thread_id": thread.id,
                        "thread_title": thread.title,
                        "author_name": comment.author_name,
                        "author_email": comment.author_email if include_metadata else None,
                        "content": comment.content,
                        "created_at": comment.created_at.isoformat(),
                        "is_approved": comment.is_approved,
                        "parent_id": comment.parent_id
                    }
                    all_comments.append(comment_data)

        # Prepare export data
        export_data = {
            "export_info": {
                "user_id": current_user.id,
                "user_name": current_user.name,
                "export_date": datetime.utcnow().isoformat(),
                "format": format,
                "total_threads": len(threads),
                "total_comments": len(all_comments)
            },
            "threads": [
                {
                    "id": thread.id,
                    "title": thread.title,
                    "url": thread.url,
                    "external_page_id": thread.external_page_id,
                    "created_at": thread.created_at.isoformat(),
                    "updated_at": thread.updated_at.isoformat() if thread.updated_at else None,
                    "comment_count": len([c for c in all_comments if c["thread_id"] == thread.id])
                } for thread in threads
            ],
            "comments": all_comments if include_comments else []
        }

        # Format response based on requested format
        if format == "yaml":
            try:
                import yaml
                from fastapi.responses import PlainTextResponse
                yaml_content = yaml.dump(export_data, default_flow_style=False, allow_unicode=True)
                return PlainTextResponse(yaml_content, media_type="application/yaml")
            except ImportError:
                raise HTTPException(status_code=400, detail="YAML format not available")

        elif format == "csv":
            from fastapi.responses import PlainTextResponse
            import csv
            import io

            output = io.StringIO()
            if all_comments:
                fieldnames = ["id", "thread_id", "thread_title", "author_name", "content", "created_at", "is_approved"]
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                for comment in all_comments:
                    writer.writerow({k: v for k, v in comment.items() if k in fieldnames})
            csv_content = output.getvalue()
            return PlainTextResponse(csv_content, media_type="text/csv")

        else:  # json (default)
            return export_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/export/threads/{thread_id}")
async def export_thread_data(
    thread_id: str,
    format: str = Query("json", description="Export format: json, html, yaml"),
    template: str = Query("default", description="HTML template: default, neocities, hugo"),
    current_user: User = Depends(get_current_user)
):
    """
    Export data for a specific thread
    """
    try:
        # Verify thread ownership
        thread = await thread_service.get_thread_by_id(thread_id)
        if not thread or thread.usuario_proprietario_id != current_user.id:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Get approved comments
        comments = await comment_service.get_thread_comments(thread.id, approved_only=True)

        # Prepare thread data
        thread_data = {
            "thread": {
                "id": thread.id,
                "title": thread.title,
                "url": thread.url,
                "external_page_id": thread.external_page_id,
                "created_at": thread.created_at.isoformat(),
                "comment_count": len(comments)
            },
            "comments": [
                {
                    "id": comment.id,
                    "author_name": comment.author_name,
                    "content": comment.content,
                    "created_at": comment.created_at.isoformat(),
                    "parent_id": comment.parent_id,
                    "replies": []  # Will be populated below
                } for comment in comments
            ]
        }

        # Organize comments into tree structure
        comment_map = {c["id"]: c for c in thread_data["comments"]}
        for comment in thread_data["comments"]:
            if comment["parent_id"]:
                parent = comment_map.get(comment["parent_id"])
                if parent:
                    parent["replies"].append(comment)

        # Remove top-level replies (they're nested now)
        thread_data["comments"] = [c for c in thread_data["comments"] if not c["parent_id"]]

        # Format response
        if format == "html":
            from fastapi.responses import HTMLResponse

            if template == "neocities":
                html_content = generate_neocities_html(thread_data)
            elif template == "hugo":
                html_content = generate_hugo_html(thread_data)
            elif template == "nikola":
                html_content = generate_nikola_html(thread_data)
            else:
                html_content = generate_default_html(thread_data)

            return HTMLResponse(html_content)

        elif format == "yaml":
            try:
                import yaml
                from fastapi.responses import PlainTextResponse
                yaml_content = yaml.dump(thread_data, default_flow_style=False, allow_unicode=True)
                return PlainTextResponse(yaml_content, media_type="application/yaml")
            except ImportError:
                raise HTTPException(status_code=400, detail="YAML format not available")

        else:  # json
            return thread_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/export/sites/{site_id}")
async def export_site_data(
    site_id: str,
    format: str = Query("json", description="Export format: json, yaml"),
    current_user: User = Depends(get_current_user)
):
    """
    Export all data for a specific site (group of threads)
    """
    try:
        # Get all threads for this site
        threads = await thread_service.get_threads_by_site(site_id, current_user.id)

        if not threads:
            raise HTTPException(status_code=404, detail="Site not found")

        # Get all comments for all threads in this site
        all_comments = []
        for thread in threads:
            comments = await comment_service.get_thread_comments(thread.id, approved_only=True)
            for comment in comments:
                comment_data = {
                    "id": comment.id,
                    "thread_id": thread.id,
                    "thread_title": thread.title,
                    "author_name": comment.author_name,
                    "content": comment.content,
                    "created_at": comment.created_at.isoformat(),
                    "parent_id": comment.parent_id
                }
                all_comments.append(comment_data)

        # Prepare site export data
        site_data = {
            "site": {
                "site_id": site_id,
                "site_name": threads[0].title.split(" - ")[0] if threads else site_id,
                "total_threads": len(threads),
                "total_comments": len(all_comments),
                "export_date": datetime.utcnow().isoformat()
            },
            "threads": [
                {
                    "id": thread.id,
                    "title": thread.title,
                    "url": thread.url,
                    "comment_count": len([c for c in all_comments if c["thread_id"] == thread.id])
                } for thread in threads
            ],
            "comments": all_comments
        }

        # Format response
        if format == "yaml":
            try:
                import yaml
                from fastapi.responses import PlainTextResponse
                yaml_content = yaml.dump(site_data, default_flow_style=False, allow_unicode=True)
                return PlainTextResponse(yaml_content, media_type="application/yaml")
            except ImportError:
                raise HTTPException(status_code=400, detail="YAML format not available")

        else:  # json
            return site_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


def generate_default_html(thread_data: Dict[str, Any]) -> str:
    """Generate default HTML for thread comments"""
    thread = thread_data["thread"]
    comments = thread_data["comments"]

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comments for {thread['title']}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 2rem; }}
        .comment {{ margin: 1rem 0; padding: 1rem; border-left: 3px solid #007cba; background: #f8f9fa; }}
        .comment-author {{ font-weight: bold; color: #007cba; }}
        .comment-date {{ color: #666; font-size: 0.9rem; }}
        .comment-content {{ margin: 0.5rem 0; }}
        .replies {{ margin-left: 2rem; }}
    </style>
</head>
<body>
    <h1>Comments for: {thread['title']}</h1>
    <p><a href="{thread['url']}">← Back to article</a></p>

    <div class="comments">
"""

    def render_comment(comment, level=0):
        replies_html = ""
        if comment.get("replies"):
            replies_html = '<div class="replies">'
            for reply in comment["replies"]:
                replies_html += render_comment(reply, level + 1)
            replies_html += '</div>'

        return f"""
        <div class="comment" style="margin-left: {level * 2}rem;">
            <div class="comment-author">{comment['author_name']}</div>
            <div class="comment-date">{comment['created_at'][:10]}</div>
            <div class="comment-content">{comment['content']}</div>
            {replies_html}
        </div>
        """

    for comment in comments:
        html += render_comment(comment)

    html += """
    </div>
</body>
</html>
"""

    return html


def generate_neocities_html(thread_data: Dict[str, Any]) -> str:
    """Generate NeoCities-style HTML"""
    thread = thread_data["thread"]
    comments = thread_data["comments"]

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Comments - {thread['title']}</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background: #000;
            color: #0f0;
            margin: 2rem;
            line-height: 1.6;
        }}
        .comment {{
            margin: 1rem 0;
            padding: 1rem;
            border: 1px solid #0f0;
            background: #001100;
        }}
        .comment-author {{
            color: #0f0;
            font-weight: bold;
        }}
        .comment-date {{
            color: #6b7280;
            font-size: 0.8rem;
        }}
        .comment-content {{
            margin: 0.5rem 0;
        }}
        .replies {{
            margin-left: 2rem;
            border-left: 2px solid #0f0;
            padding-left: 1rem;
        }}
        a {{ color: #0f0; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>> Comments for: {thread['title']}</h1>
    <p><a href="{thread['url']}">< Back to article</a></p>

    <div class="comments">
"""

    def render_comment(comment, level=0):
        replies_html = ""
        if comment.get("replies"):
            replies_html = '<div class="replies">'
            for reply in comment["replies"]:
                replies_html += render_comment(reply, level + 1)
            replies_html += '</div>'

        return f"""
        <div class="comment">
            <div class="comment-author">{comment['author_name']}</div>
            <div class="comment-date">{comment['created_at'][:10]}</div>
            <div class="comment-content">{comment['content']}</div>
            {replies_html}
        </div>
        """

    for comment in comments:
        html += render_comment(comment)

    html += """
    </div>
    <p><a href="/">Home</a></p>
</body>
</html>
"""

    return html


def generate_hugo_html(thread_data: Dict[str, Any]) -> str:
    """Generate Hugo-compatible HTML fragment"""
    comments = thread_data["comments"]

    html = '<div class="comments-section">\n'

    def render_comment(comment, level=0):
        indent = "  " * level
        replies_html = ""
        if comment.get("replies"):
            replies_html = f'{indent}  <div class="comment-replies">\n'
            for reply in comment["replies"]:
                replies_html += render_comment(reply, level + 1)
            replies_html += f'{indent}  </div>\n'

        return f"""{indent}  <div class="comment">
{indent}    <div class="comment-header">
{indent}      <strong class="comment-author">{comment['author_name']}</strong>
{indent}      <time class="comment-date">{comment['created_at'][:10]}</time>
{indent}    </div>
{indent}    <div class="comment-content">
{indent}      {comment['content']}
{indent}    </div>
{replies_html}{indent}  </div>
"""

    for comment in comments:
        html += render_comment(comment)

    html += '</div>\n'

    return html


def generate_nikola_html(thread_data: Dict[str, Any]) -> str:
    """Generate Nikola-compatible HTML fragment"""
    thread = thread_data["thread"]
    comments = thread_data["comments"]

    html = f'''<div class="comments" id="comments-{thread['id']}">
  <h2>Comments for {thread['title']}</h2>

  <div class="commentlist">
'''

    def render_comment(comment, level=0):
        indent = "    " * level
        replies_html = ""
        if comment.get("replies"):
            replies_html = f'{indent}    <ul class="children">\n'
            for reply in comment["replies"]:
                replies_html += f'{indent}      <li class="comment">\n'
                replies_html += render_comment(reply, level + 1)
                replies_html += f'{indent}      </li>\n'
            replies_html += f'{indent}    </ul>\n'

        return f"""{indent}    <div class="comment" id="comment-{comment['id']}">
{indent}      <div class="comment-author vcard">
{indent}        <cite class="fn">{comment['author_name']}</cite>
{indent}        <span class="comment-date">
{indent}          <a href="#comment-{comment['id']}" title="Permalink to this comment">
{indent}            {comment['created_at'][:10]}
{indent}          </a>
{indent}        </span>
{indent}      </div>
{indent}      <div class="comment-content">
{indent}        <p>{comment['content']}</p>
{indent}      </div>
{replies_html}{indent}    </div>
"""

    for comment in comments:
        html += f'    <li class="comment">\n'
        html += render_comment(comment)
        html += '    </li>\n'

    html += '''  </div>

  <div class="comment-form">
    <h3>Add a comment</h3>
    <p>Comments are powered by <a href="https://nocodebackend.vercel.app" target="_blank">NoCode Comments</a></p>
    <p><a href="''' + thread['url'] + '''#comments">Add your comment on the original post</a></p>
  </div>
</div>
'''

    return html