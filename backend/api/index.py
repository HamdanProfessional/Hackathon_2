"""Vercel serverless function entry point for FastAPI backend."""
from app.main import app

# This is required for Vercel to properly route requests to FastAPI
handler = app
