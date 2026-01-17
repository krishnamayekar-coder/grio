"""API Router - Aggregates all API endpoints"""
from fastapi import APIRouter
from app.api.v1 import chat, health

api_router = APIRouter()

# Include v1 routes
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(health.router, tags=["health"])
