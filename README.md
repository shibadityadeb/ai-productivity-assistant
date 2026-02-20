# AI Productivity Assistant

A production-ready FastAPI backend service that integrates Gmail, Slack, Toggl, and AI APIs (Claude/Gemini) to enhance productivity through intelligent automation and insights.

## Features

- **Gmail Integration**: Read, send, and analyze emails
- **Slack Integration**: Send messages, read channels, and summarize conversations
- **Toggl Time Tracking**: Manage time entries and analyze productivity
- **AI-Powered Insights**: 
  - Claude API for email analysis and Slack summarization
  - Gemini API for productivity analysis and smart replies
- **RESTful API**: Clean, documented endpoints with FastAPI
- **Production-Ready**: Structured logging, error handling, and configuration management

## Project Structure

```
ai-productivity-assistant/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py     # Shared dependencies
│   │   └── routes/             # API endpoints
│   │       ├── __init__.py
│   │       ├── gmail.py
│   │       ├── slack.py
│   │       ├── toggl.py
│   │       └── ai.py
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── gmail_service.py
│   │   ├── slack_service.py
│   │   ├── toggl_service.py
│   │   ├── claude_service.py
│   │   └── gemini_service.py
│   ├── models/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   └── schemas.py
│   └── utils/                  # Utilities
│       ├── __init__.py
│       └── logger.py
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── .env.example                # Environment variables template
├── .gitignore
├── requirements.txt            # Python dependencies
├── README.md
└── run.py                      # Application entry point
```

## Prerequisites

- Python 3.10+
- Gmail API credentials (OAuth 2.0)
- Slack Bot Token and App Token
- Toggl API Token
- Claude API Key (Anthropic)
- Gemini API Key (Google)

## Setup Instructions

### 1. Clone and Setup Environment

```bash
# Navigate to project directory
cd ai-productivity-assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Required environment variables:
- `SECRET_KEY`: Your application secret key
- `GMAIL_CLIENT_ID` & `GMAIL_CLIENT_SECRET`: Gmail OAuth credentials
- `SLACK_BOT_TOKEN`: Slack bot token (starts with `xoxb-`)
- `TOGGL_API_TOKEN`: Your Toggl API token
- `TOGGL_WORKSPACE_ID`: Your Toggl workspace ID
- `CLAUDE_API_KEY`: Anthropic Claude API key
- `GEMINI_API_KEY`: Google Gemini API key

### 4. Setup API Credentials

#### Gmail API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download credentials and update `.env`

#### Slack API Setup
1. Go to [Slack API](https://api.slack.com/apps)
2. Create a new app
3. Add Bot Token Scopes: `channels:read`, `chat:write`, `users:read`
4. Install app to workspace
5. Copy Bot Token to `.env`

#### Toggl API Setup
1. Go to [Toggl Profile](https://track.toggl.com/profile)
2. Copy your API token
3. Find your workspace ID from workspace settings

#### AI API Keys
- **Claude**: Get API key from [Anthropic Console](https://console.anthropic.com/)
- **Gemini**: Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### 5. Run the Application

```bash
# Using the run script
python run.py

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Gmail
- `GET /api/gmail/messages` - List recent emails
- `GET /api/gmail/messages/{id}` - Get specific email
- `POST /api/gmail/send` - Send email
- `GET /api/gmail/auth/status` - Check authentication status

### Slack
- `GET /api/slack/channels` - List channels
- `POST /api/slack/messages` - Send message
- `GET /api/slack/channels/{id}/history` - Get channel history
- `GET /api/slack/users/{id}` - Get user info

### Toggl
- `GET /api/toggl/current` - Get current time entry
- `GET /api/toggl/entries` - List time entries
- `POST /api/toggl/start` - Start time tracking
- `POST /api/toggl/stop/{id}` - Stop time entry
- `GET /api/toggl/projects` - List projects

### AI
- `POST /api/ai/claude/generate` - Generate text with Claude
- `POST /api/ai/claude/analyze-emails` - Analyze emails
- `POST /api/ai/claude/summarize-slack` - Summarize Slack conversations
- `POST /api/ai/gemini/generate` - Generate text with Gemini
- `POST /api/ai/gemini/analyze-productivity` - Analyze productivity
- `POST /api/ai/gemini/daily-summary` - Generate daily summary
- `POST /api/ai/gemini/smart-reply` - Get smart reply suggestions

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## Development

```bash
# Install dev dependencies
pip install pytest pytest-cov black flake8 mypy

# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

## Production Deployment

### Using Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t ai-productivity-assistant .
docker run -p 8000:8000 --env-file .env ai-productivity-assistant
```

### Environment-Specific Configuration

Modify `.env` for different environments:
- Set `ENVIRONMENT=production`
- Set `DEBUG=False`
- Use proper CORS origins
- Use strong `SECRET_KEY`
- Configure proper logging

## Security Considerations

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Use environment variables** for all secrets
3. **Rotate API keys** regularly
4. **Enable HTTPS** in production
5. **Implement rate limiting** for API endpoints
6. **Use OAuth 2.0** for Gmail authentication
7. **Validate and sanitize** all user inputs

## Troubleshooting

### Gmail Authentication Issues
- Ensure OAuth credentials are correctly configured
- Check redirect URI matches your setup
- Verify Gmail API is enabled in Google Cloud Console

### Slack Connection Issues
- Verify bot token is correct
- Check bot has required scopes
- Ensure bot is installed in workspace

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## License

MIT License - feel free to use this project for your needs.

## Support

For issues and questions, please create an issue in the repository.
