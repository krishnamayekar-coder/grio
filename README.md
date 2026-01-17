# Griot Backend

A FastAPI-based AI storyteller service inspired by the West African griot tradition. This backend serves an AI companion that tells engaging stories and preserves historical knowledge through narrative.

## Features

- **FastAPI** for high-performance async API
- **OpenAI Integration** for intelligent storytelling
- **Memory Management** with short-term and long-term storage
- **Modular Architecture** for easy extension
- **Health Checks** and proper error handling
- **Comprehensive Logging** for debugging

## Project Structure

```
griot-backend/
├── app/
│   ├── main.py                 # App entrypoint
│   ├── core/                   # Core configuration & startup
│   ├── api/                    # API routes
│   ├── services/               # Business logic
│   ├── prompts/                # System & role prompts
│   ├── models/                 # Pydantic models
│   ├── db/                     # Persistence layer
│   └── utils/                  # Helper utilities
├── tests/                      # Unit & integration tests
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
├── run.sh                      # Run script
└── README.md                   # This file
```

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your configuration:
   ```
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-4
   DEBUG=False
   LOG_LEVEL=INFO
   ```

### Running the Application

Quick start with the run script:
```bash
chmod +x run.sh
./run.sh
```

Or manually:
```bash
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Endpoints

- **POST** `/api/v1/chat` - Send a message to Griot
  ```json
  {
    "user_id": "user123",
    "message": "Tell me a story about ancient civilizations"
  }
  ```

- **GET** `/api/v1/health` - Health check endpoint

### Testing

Run tests with pytest:
```bash
pytest tests/
```

## Development

### Code Style

Code style is enforced with:
- `black` - Code formatter
- `flake8` - Linter
- `mypy` - Type checker

```bash
black app/ tests/
flake8 app/ tests/
mypy app/
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - see LICENSE file for details
