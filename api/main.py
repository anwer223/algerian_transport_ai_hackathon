#!/usr/bin/env python3

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.endpoints import router

# Create FastAPI app
app = FastAPI(
    title="🇩🇿 Algiers Transport AI",
    description="AI-powered multimodal transport recommendation system for Algiers",
    version="1.0.0"
)

# Configure CORS (for mobile app access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint with welcome message"""
    return {
        "message": "🇩🇿 مرحبا بكم في نظام الذكاء الاصطناعي للنقل في الجزائر",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": {
            "route": "/api/route (POST) - Get AI route recommendations",
            "stations": "/api/stations (GET) - Get available stations",
            "weather": "/api/weather/{city} (GET) - Get weather impact",
            "traffic": "/api/traffic/{area} (GET) - Get traffic conditions"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
