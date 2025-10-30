# NoCodeBackend Frontend

Modern web interface for the Indie Comments Widget system. Built with FastAPI, Bootstrap 5, and vanilla JavaScript.

## Features

- 🎨 **Comment Widget**: Privacy-focused, themeable comment system
- 📊 **Dashboard**: Comprehensive moderation interface
- 🔄 **Real-time Updates**: Live comment notifications
- 🔍 **Advanced Search**: Filter and search comments
- 📱 **Responsive Design**: Mobile-first approach
- ♿ **Accessibility**: WCAG 2.1 AA compliance
- 🎭 **Themes**: Multiple visual themes
- ⚡ **Performance**: Optimized loading and caching

## Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/your-org/nocodebackend-frontend.git
cd nocodebackend-frontend

# Install Python dependencies
pip install -r requirements.txt

# Install widget dependencies
cd widget && npm install

# Build widget assets
npm run build

# Run the server
uvicorn app:app --reload --host 0.0.0.0 --port 3000
```

### Docker

```bash
# Build and run with Docker
docker build -t nocodebackend-frontend .
docker run -p 3000:3000 nocodebackend-frontend
```

## Project Structure

```
nocodebackend-frontend/
├── app.py                      # FastAPI application
├── routes/                     # Route handlers
├── static/                     # Static assets (CSS, JS, images)
├── templates/                  # Jinja2 templates
├── utils/                      # Utility functions
├── widget/                     # Comment widget
│   ├── src/                   # Widget source code
│   ├── dist/                  # Built widget assets
│   ├── package.json           # Node.js dependencies
│   └── rollup.config.js       # Build configuration
├── tests/                      # Test suite
└── requirements.txt           # Python dependencies
```

## Widget Integration

### Basic Usage

```html
<!-- Add to any webpage -->
<script src="https://your-domain.com/widget/dist/widget.js"></script>

<!-- Or use the embed code -->
<div id="comments-widget-container">
  <comment-widget
    thread-id="your-thread-id"
    theme="default"
    show-theme-selector>
  </comment-widget>
</div>
```

### Advanced Configuration

```html
<comment-widget
  thread-id="custom-thread"
  api-base-url="https://api.your-domain.com"
  theme="dark"
  max-depth="5"
  show-theme-selector
  enable-replies>
</comment-widget>
```

## Environment Variables

```bash
# Backend API
BACKEND_API_URL=https://comment-widget-backend.vercel.app

# Application
SECRET_KEY=your-secret-key
DEBUG=true

# Widget Configuration
WIDGET_THEMES=default,dark,neon
WIDGET_MAX_DEPTH=5
```

## Development

### Running Tests

```bash
# Python tests
pytest tests/ -v

# Widget tests
cd widget && npm test

# Build widget for production
cd widget && npm run build
```

### Building Widget

```bash
cd widget

# Development build
npm run dev

# Production build
npm run build

# Watch mode
npm run watch
```

## Deployment

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Manual Deployment

```bash
# Build widget assets
cd widget && npm run build

# Deploy static files
# Copy dist/ contents to your CDN or static hosting
```

## API Integration

The frontend communicates with the backend API:

```javascript
// Example API calls
const API_BASE = process.env.BACKEND_API_URL;

// Get comments
fetch(`${API_BASE}/api/comments?thread_id=${threadId}`)

// Create comment
fetch(`${API_BASE}/api/comments`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    content: 'Comment text',
    author: 'User name',
    thread_id: threadId
  })
})
```

## Themes

### Available Themes

- **Default**: Clean, modern design
- **Dark**: Dark mode variant
- **Neon**: Cyberpunk aesthetic
- **Matrix**: Green terminal style
- **Ocean**: Blue aquatic theme
- **Forest**: Natural green tones
- **Sunset**: Warm orange/pink
- **Geometric**: Modern geometric patterns

### Custom Themes

Create custom themes in `static/css/themes/`:

```css
.theme-custom {
  --primary-color: #your-color;
  --background-color: #your-bg;
  --text-color: #your-text;
  /* ... more variables */
}
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test thoroughly: `pytest tests/ && cd widget && npm test`
5. Commit: `git commit -am 'Add your feature'`
6. Push: `git push origin feature/your-feature`
7. Submit a pull request

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- **Lighthouse Score**: 95+ (Performance, Accessibility, SEO)
- **Bundle Size**: < 50KB gzipped
- **First Paint**: < 1.5s
- **Time to Interactive**: < 2.5s

## Security

- Content Security Policy (CSP)
- XSS protection
- Input sanitization
- Rate limiting
- Secure headers

## License

MIT License - see LICENSE file for details.

## Support

- 📧 Email: support@nocodebackend.com
- 📖 Documentation: https://docs.nocodebackend.com
- 🐛 Issues: https://github.com/your-org/nocodebackend-frontend/issues
- 💬 Discussions: https://github.com/your-org/nocodebackend-frontend/discussions