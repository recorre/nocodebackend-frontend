# Nikola Comments Integration

This guide shows how to integrate NoCode Comments with Nikola static site generator, leveraging Nikola's Python foundation and powerful content processing capabilities.

## Why Nikola?

Nikola is a powerful static site generator written in Python that excels at:

- **Python Integration**: Native Python scripting for advanced customization
- **Content Processing**: Support for Markdown, reStructuredText, Jupyter notebooks
- **Plugin System**: Extensive plugin ecosystem for added functionality
- **Performance**: Fast rebuilds using doit for dependency tracking
- **Flexibility**: Multiple template engines (Mako, Jinja2) and themes

## Setup

### 1. Install Nikola

```bash
pip install Nikola[extras]
```

### 2. Create Nikola Site

```bash
nikola init mysite
cd mysite
```

### 3. Configure Comments Plugin

Create a custom plugin for comments integration:

```python
# plugins/comments.py
import json
import os
from nikola.plugin_categories import Task
from nikola import utils

class Comments(Task):
    """Plugin to fetch and integrate comments from NoCode Backend"""

    name = "comments"

    def set_site(self, site):
        self.site = site
        return super().set_site(site)

    def gen_tasks(self):
        """Generate tasks to fetch comments"""
        self.site.scan_posts()

        # Configuration
        api_key = os.environ.get('NOCODE_API_KEY')
        api_url = os.environ.get('NOCODE_API_URL', 'https://your-app.vercel.app')

        if not api_key:
            utils.LOGGER.warning("NOCODE_API_KEY not set, skipping comments")
            return

        def fetch_comments():
            """Fetch comments for all posts"""
            import requests

            comments_dir = os.path.join(self.site.config['OUTPUT_FOLDER'], 'comments')
            os.makedirs(comments_dir, exist_ok=True)

            for post in self.site.timeline:
                if post.meta('status') != 'published':
                    continue

                # Generate thread ID from post
                thread_id = f"post-{post.meta('slug')}"

                try:
                    # Fetch comments
                    response = requests.get(
                        f"{api_url}/api/export/threads/{thread_id}",
                        params={
                            'format': 'json',
                            'api_key': api_key
                        },
                        timeout=10
                    )

                    if response.status_code == 200:
                        comments_data = response.json()

                        # Save as JSON for templates
                        json_path = os.path.join(comments_dir, f"{thread_id}.json")
                        with open(json_path, 'w', encoding='utf-8') as f:
                            json.dump(comments_data, f, indent=2, ensure_ascii=False)

                        utils.LOGGER.info(f"Fetched comments for {thread_id}")

                except Exception as e:
                    utils.LOGGER.warning(f"Failed to fetch comments for {thread_id}: {e}")

        yield {
            'basename': 'comments',
            'name': 'fetch_comments',
            'actions': [fetch_comments],
            'targets': [],  # Dynamic targets
            'uptodate': [utils.config_changed(self.site.config, 'nikola_comments')],
        }
```

### 4. Update Configuration

Add to `conf.py`:

```python
# Comments configuration
COMMENT_SYSTEM = "nocode"
NOCODE_API_URL = "https://your-app.vercel.app"
NOCODE_API_KEY = os.environ.get('NOCODE_API_KEY')

# Add comments plugin
PLUGINS = [
    # ... existing plugins
    'comments',
]
```

## Usage

### Template Integration

Update your post template (`themes/your-theme/templates/post.tmpl`):

```mako
<%inherit file="base.tmpl"/>

<%block name="content">
<article class="post">
  <header>
    <h1>${post.title()}</h1>
    <div class="post-meta">
      <time datetime="${post.date.isoformat()}">${post.formatted_date('long')}</time>
    </div>
  </header>

  <div class="post-content">
    ${post.text()}
  </div>

  <% comments_file = f"comments/post-{post.meta('slug')}.json" %>
  % if os.path.exists(os.path.join(conf.OUTPUT_FOLDER, comments_file)):
  <%
    import json
    with open(os.path.join(conf.OUTPUT_FOLDER, comments_file)) as f:
      comments_data = json.load(f)
  %>
  <div class="comments-section">
    <h2>Comments (${len(comments_data.get('comments', []))})</h2>

    <div class="commentlist">
      % for comment in comments_data.get('comments', []):
      <li class="comment">
        <div class="comment" id="comment-${comment['id']}">
          <div class="comment-author vcard">
            <cite class="fn">${comment['author_name']}</cite>
            <span class="comment-date">
              <a href="#comment-${comment['id']}" title="Permalink to this comment">
                ${comment['created_at'][:10]}
              </a>
            </span>
          </div>
          <div class="comment-content">
            <p>${comment['content']}</p>
          </div>
          % if comment.get('replies'):
          <ul class="children">
            % for reply in comment['replies']:
            <li class="comment">
              <div class="comment" id="comment-${reply['id']}">
                <div class="comment-author vcard">
                  <cite class="fn">${reply['author_name']}</cite>
                  <span class="comment-date">
                    <a href="#comment-${reply['id']}" title="Permalink to this comment">
                      ${reply['created_at'][:10]}
                    </a>
                  </span>
                </div>
                <div class="comment-content">
                  <p>${reply['content']}</p>
                </div>
              </div>
            </li>
            % endfor
          </ul>
          % endif
        </div>
      </li>
      % endfor
    </div>

    <div class="comment-form">
      <h3>Add a comment</h3>
      <p>Comments are powered by <a href="https://nocodebackend.vercel.app" target="_blank">NoCode Comments</a></p>
      <p><a href="${post.permalink()}#comments">Add your comment</a></p>
    </div>
  </div>
  % endif
</article>
<%endblock>
```

### Build Process

```bash
# Set environment variables
export NOCODE_API_KEY=your_api_key_here
export NOCODE_API_URL=https://your-app.vercel.app

# Build site with comments
nikola build

# Or auto-rebuild during development
nikola auto
```

## Advanced Configuration

### Custom Comment Processing

Extend the plugin for custom processing:

```python
def process_comments(comments_data):
    """Process comments data for Nikola"""
    processed = []

    for comment in comments_data.get('comments', []):
        # Add Nikola-specific metadata
        comment['url'] = f"#comment-{comment['id']}"
        comment['formatted_date'] = format_date(comment['created_at'])

        # Process content with Nikola's markdown
        from nikola.utils import apply_filters
        comment['html_content'] = apply_filters(
            comment['content'],
            filters=['markdown'],
            site=self.site
        )

        processed.append(comment)

    return processed
```

### Theme Integration

Create a Nikola theme with comments support:

```
themes/your-theme/
├── templates/
│   ├── base.tmpl
│   ├── post.tmpl
│   └── comments.tmpl  # Include this
├── assets/
│   └── css/
│       └── comments.css
└── theme.conf
```

### RSS Feed Integration

Add comments to RSS feeds:

```python
# In a custom plugin
def generate_comment_feed(post):
    """Generate RSS items for post comments"""
    # Implementation for comment RSS integration
    pass
```

## Performance Optimization

### Caching Strategy

```python
# Cache comments to avoid repeated API calls
import pickle
import hashlib

def get_cache_key(thread_id):
    return hashlib.md5(f"comments-{thread_id}".encode()).hexdigest()

def get_cached_comments(thread_id):
    cache_file = f".comment-cache/{get_cache_key(thread_id)}.pkl"
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    return None

def cache_comments(thread_id, comments):
    os.makedirs('.comment-cache', exist_ok=True)
    cache_file = f".comment-cache/{get_cache_key(thread_id)}.pkl"
    with open(cache_file, 'wb') as f:
        pickle.dump(comments, f)
```

### Incremental Builds

Leverage Nikola's dependency tracking:

```python
def gen_tasks(self):
    """Generate tasks with proper dependencies"""
    # Track which posts have changed
    changed_posts = []
    for post in self.site.timeline:
        if self.site.file_changed(post.source_path):
            changed_posts.append(post)

    # Only fetch comments for changed posts
    def fetch_changed_comments():
        for post in changed_posts:
            thread_id = f"post-{post.meta('slug')}"
            # Fetch and cache comments
            pass
```

## Troubleshooting

### Comments Not Showing

1. Check `NOCODE_API_KEY` environment variable
2. Verify API endpoint accessibility
3. Check Nikola build logs for errors
4. Ensure post slugs match thread IDs

### Template Errors

1. Verify Mako/Jinja2 syntax in templates
2. Check that comments JSON files exist
3. Validate JSON structure matches template expectations

### Performance Issues

1. Enable comment caching
2. Use incremental builds
3. Limit comment depth in API calls
4. Optimize template rendering

## Examples

### Complete Plugin

See `examples/nikola_example/plugins/comments.py` for a complete working plugin.

### Sample Site

Check `examples/nikola_example/` for a complete Nikola site with comments integration.

## Next Steps

- Set up automated comment fetching in CI/CD
- Add comment moderation in Nikola admin
- Implement real-time comment updates
- Create comment analytics dashboard

---

**Perfect for**: Python developers, data scientists, technical bloggers using Jupyter notebooks