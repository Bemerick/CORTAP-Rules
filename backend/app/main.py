"""
FastAPI Main Application
FTA Comprehensive Review - Applicability & LOE Assessment API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from app.routers import questions, sections, sub_areas, projects, assessment

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="FTA Comprehensive Review API",
    description="API for FTA Comprehensive Review Applicability Assessment and LOE Estimation",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins_str == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

print(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False if allowed_origins == ["*"] else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(questions.router)
app.include_router(sections.router)
app.include_router(sub_areas.router)
app.include_router(projects.router)
app.include_router(assessment.router)


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "FTA Comprehensive Review API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    reload = os.getenv("API_RELOAD", "True").lower() == "true"

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload
    )
