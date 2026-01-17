"""Griot Backend Application Entry Point"""
from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.startup import init_app
from app.api.router import api_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
    )
    
    # Setup logging
    setup_logging()
    
    # Initialize app
    init_app(app)
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
