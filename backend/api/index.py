"""Vercel serverless function entry point for FastAPI backend."""
from app.main import app

# Vercel looks for 'app' in this file
app = app
