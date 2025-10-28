# NoCode Backend Frontend

A modern, responsive web dashboard for managing the NoCode Comments Widget system. Built with FastAPI, Jinja2 templates, and enhanced with accessibility features and automated testing.

## 🚀 Features

- **User Dashboard**: Complete management interface for comments and threads
- **Comment Moderation**: Approve/reject comments with admin controls
- **Widget Preview**: Live preview of comment widgets with different themes
- **Theme Customization**: Customize widget appearance and behavior
- **Responsive Design**: Mobile-first design that works on all devices
- **Accessibility**: WCAG 2.2 compliant with ARIA labels and keyboard navigation
- **Automated Testing**: Selenium-based screenshot testing for UI validation
- **SSR Support**: Server-side rendering templates for better SEO and performance

## 📋 Pages & Features

### Authentication
- **Login**: Secure user authentication
- **Registration**: New user signup with validation
- **Session Management**: Secure cookie-based sessions

### Dashboard
- **Home**: Overview with statistics and recent activity
- **Comments**: Moderation queue with approve/reject actions
- **Threads**: Manage discussion threads
- **Sites**: Multi-site management interface

### Widget Features
- **Theme Preview**: Live widget theming (Default, Dark, Matrix, NeoCities)
- **Configuration**: Customize widget behavior and appearance
- **Embed Code**: Generate embed codes for websites

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nocodebackend-frontend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv autotester_env
   source autotester_env/bin/activate  # On Windows: autotester_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # The frontend connects to the backend API
   # Make sure nocodebackend-api is running on http://localhost:8000
   ```

5. **Start the frontend server**
   ```bash
   python app.py
   # Or with auto-reload:
   # uvicorn app:app --reload --host 0.0.0.0 --port 3000
   ```

## 🧪 Testing

### Automated Screenshot Testing
```bash
# Install test dependencies
pip install selenium webdriver-manager

# Run basic theme tests
python screenshot_autotester.py --mode basic --url http://localhost:3000

# Run interactive mode
python screenshot_autotester.py
```

### Widget Build
```bash
# Build the widget for production
./build_widget.sh

# Output files in dist/:
# - comment-widget.min.js (1.3kb minified)
# - widget.html (SSR template)
# - widget.css (styles)
# - embed.js (CDN embed script)
```

## 🎨 Widget Features

### Themes
- **Default**: Clean, professional appearance
- **Dark**: Dark mode for modern websites
- **Matrix**: Retro green terminal theme
- **NeoCities**: 90s web aesthetic

### Accessibility (WCAG 2.2)
- **ARIA Labels**: Screen reader support
- **Keyboard Navigation**: Full keyboard accessibility
- **High Contrast**: `prefers-contrast` support
- **Reduced Motion**: `prefers-reduced-motion` support
- **Focus Management**: Visible focus indicators

### SSR (Server-Side Rendering)
- **Progressive Enhancement**: Works without JavaScript
- **SEO Friendly**: Search engine compatible
- **Performance**: Faster initial page loads
- **JSON Payload**: Embedded data for hydration

## 📊 Environment Setup

### Backend API Connection
The frontend expects the backend API to be running on `http://localhost:8000`. Update `routes/auth.py` if needed:

```python
BACKEND_URL = "http://localhost:8000"  # Change if backend is on different port
```

### File Structure
```
nocodebackend-frontend/
├── app.py                    # FastAPI application
├── embed.html               # Widget demo page
├── build_widget.sh          # Build script
├── requirements.txt         # Python dependencies
├── autotester_env/          # Test environment
├── dist/                    # Built widget files
├── routes/                  # Route handlers
│   ├── auth.py             # Authentication
│   └── dashboard.py        # Dashboard pages
├── static/                  # Static assets
│   ├── css/
│   ├── js/
│   │   ├── widget.js       # Hydration script
│   │   └── widgetv01.js    # Main widget component
│   └── ...
├── templates/               # Jinja2 templates
│   ├── base.html
│   ├── auth/
│   ├── dashboard/
│   ├── components/
│   ├── widget.html         # SSR template
│   └── widget_inline.css   # Inline styles
└── screenshots/            # Test screenshots
```

## 🚀 Deployment

### Local Development
```bash
# Start both services
# Terminal 1: Backend
cd nocodebackend-api
python main.py

# Terminal 2: Frontend
cd nocodebackend-frontend
python app.py
```

### Production Deployment
```bash
# Build widget
./build_widget.sh

# Deploy frontend (similar to backend)
# The frontend can be deployed to Vercel, Heroku, or any Python hosting
```

## 🔗 API Integration

The frontend communicates with the backend API for:
- **Authentication**: Login/register via `/auth/*`
- **Comments**: CRUD operations via `/api/v1/comments/*`
- **Threads**: Management via `/api/v1/threads/*`
- **Widget Config**: Theming via `/widget/*`

## 📱 Responsive Design

- **Mobile First**: Optimized for mobile devices
- **Tablet Support**: Adaptive layouts for tablets
- **Desktop**: Full-featured desktop experience
- **Touch Friendly**: Large touch targets for mobile

## 🧪 Testing Strategy

### Automated Tests
- **Screenshot Testing**: Visual regression testing with Selenium
- **Theme Validation**: Ensure themes load correctly
- **Accessibility**: Basic a11y checks

### Manual Testing
- **Cross-browser**: Chrome, Firefox, Safari, Edge
- **Mobile**: iOS Safari, Chrome Mobile
- **Screen Readers**: NVDA, JAWS, VoiceOver

## 🤝 Integration with Backend

This frontend is designed to work seamlessly with the `nocodebackend-api` backend:

1. **API Compatibility**: All endpoints match the backend API structure
2. **Authentication**: Shared session management
3. **Data Models**: Compatible data structures
4. **Error Handling**: Consistent error responses

## 📈 Performance

- **Lazy Loading**: Components load as needed
- **Caching**: Static asset caching
- **Minification**: CSS/JS minification in production
- **CDN Ready**: Built files optimized for CDN deployment

## 🆘 Troubleshooting

### Widget Not Loading
1. Check browser console for JavaScript errors
2. Verify backend API is running on port 8000
3. Check network tab for failed API calls

### Theme Not Changing
1. Ensure Shadow DOM is disabled (for testing)
2. Check CSS is loading correctly
3. Verify theme selector has correct event listeners

### Authentication Issues
1. Clear browser cookies
2. Check backend `/auth/*` endpoints
3. Verify session cookie settings

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For support, please check:
1. Browser console for errors
2. Network tab for API failures
3. Backend API logs
4. Open an issue on GitHub