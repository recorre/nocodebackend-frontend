# NoCode Backend API

A comprehensive FastAPI backend for the NoCode Comments Widget system, providing RESTful APIs for comment management, user authentication, and widget configuration.

## 🚀 Features

- **Comment Management**: Full CRUD operations for comments with moderation support
- **Thread Management**: Organize comments by discussion threads
- **User Authentication**: Secure login/registration with session management
- **Widget Configuration**: Dynamic widget theming and customization
- **Moderation System**: Approve/reject comments with admin controls
- **Real-time Updates**: WebSocket support for live comment updates
- **Caching**: Redis-based caching for improved performance
- **Monitoring**: Built-in health checks and metrics

## 📋 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout

### Comments
- `GET /api/v1/comments/{thread_id}` - Get comments for a thread
- `POST /api/v1/comments/` - Create new comment
- `PUT /api/v1/comments/{comment_id}/moderate` - Moderate comment (approve/reject)
- `DELETE /api/v1/comments/{comment_id}` - Delete comment

### Threads
- `GET /api/v1/threads/{thread_id}/status` - Get thread status
- `POST /api/v1/threads/` - Create new thread
- `GET /api/v1/threads/` - List user threads
- `DELETE /api/v1/threads/{thread_id}` - Delete thread

### Widget
- `GET /widget/config` - Get widget configuration
- `POST /widget/config` - Update widget configuration
- `GET /widget/embed/{thread_id}` - Generate embed code
- `GET /widget/themes` - List available themes

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nocodebackend-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   python -c "from core.database import create_tables; create_tables()"
   ```

6. **Start the server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📊 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `SECRET_KEY` | JWT secret key | Auto-generated |
| `DEBUG` | Debug mode | `false` |
| `CORS_ORIGINS` | Allowed CORS origins | `["*"]` |

## 🗄️ Database Schema

The API uses PostgreSQL with the following main tables:
- `users` - User accounts
- `threads` - Discussion threads
- `comments` - Comments with moderation status
- `widget_configs` - Widget customization settings

## 🔒 Security Features

- **Password Hashing**: bcrypt-based password storage
- **JWT Tokens**: Secure authentication tokens
- **CORS Protection**: Configurable cross-origin policies
- **Input Validation**: Pydantic-based request validation
- **Rate Limiting**: Built-in request rate limiting
- **SQL Injection Protection**: Parameterized queries

## 📈 Monitoring & Health Checks

- **Health Endpoint**: `GET /health` - System health status
- **Metrics**: Prometheus-compatible metrics
- **Logging**: Structured logging with configurable levels

## 🚀 Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### Docker
```bash
# Build image
docker build -t nocode-backend .

# Run container
docker run -p 8000:8000 nocode-backend
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_comments.py
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For support, please open an issue on GitHub or contact the development team.