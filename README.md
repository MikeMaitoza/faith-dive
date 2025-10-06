# Faith Dive - Bible Journaling Progressive Web App

A Progressive Web App (PWA) for searching Bible verses and creating personal journal entries with your thoughts and reflections.

## Features

- 🔍 **Bible Search**: Search through multiple English Bible versions using the API.Bible service
- 📝 **Personal Journaling**: Write and save your thoughts, reflections, and insights about verses
- ⭐ **Favorite Verses**: Save verses to your favorites for quick access
- 📱 **Progressive Web App**: Install on mobile devices and desktop for offline access
- 🔄 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Lightweight database for local storage
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - Lightning-fast ASGI server

### Frontend
- **Vanilla JavaScript** - No framework dependencies for simplicity
- **Bootstrap 5** - Responsive UI components
- **Service Worker** - Offline functionality and caching
- **Web App Manifest** - PWA installation support

### External Services
- **API.Bible** - Bible text and search functionality

## Getting Started

### Prerequisites
- Python 3.12+
- Poetry (for dependency management)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/faith_dive.git
   cd faith_dive
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   ```bash
   cp .env.template .env
   # Edit .env with your API.Bible API key
   ```

4. Run the application:
   ```bash
   poetry run python backend/main.py
   ```

5. Open your browser to `http://localhost:8000`

## Project Structure

```
faith_dive/
├── backend/                 # FastAPI backend
│   ├── api/                # API route handlers
│   ├── core/               # Core configuration
│   ├── database/           # Database connection and setup
│   ├── models/             # SQLAlchemy models and Pydantic schemas
│   ├── services/           # Business logic and external API services
│   └── main.py             # FastAPI application entry point
├── frontend/               # Frontend PWA
│   ├── public/             # Static files (HTML, CSS, JS)
│   └── src/                # Source files for future React/Vue migration
├── tests/                  # Test files
├── .env                    # Environment variables (not in git)
├── .env.template           # Environment template
├── pyproject.toml          # Poetry dependencies
└── README.md               # This file
```

## API Endpoints

### Bible Search
- `GET /api/v1/bibles` - Get available English Bible versions
- `POST /api/v1/search` - Search for verses

### Journal Management
- `GET /api/v1/journal` - Get all journal entries
- `POST /api/v1/journal` - Create a new journal entry
- `PUT /api/v1/journal/{id}` - Update a journal entry
- `DELETE /api/v1/journal/{id}` - Delete a journal entry

### Favorites
- `GET /api/v1/favorites` - Get favorite verses
- `POST /api/v1/favorites` - Add verse to favorites
- `DELETE /api/v1/favorites/{id}` - Remove from favorites

## Development

### Running Tests
```bash
poetry run pytest
```

### Code Formatting
```bash
poetry run black backend/
```

## Deployment

The application is designed to be easily deployed to platforms like:
- Heroku
- Railway
- DigitalOcean App Platform
- AWS Elastic Beanstalk

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [API.Bible](https://scripture.api.bible/) for providing the Bible text and search API
- Bootstrap team for the UI framework
- FastAPI team for the excellent web framework# faith-dive
