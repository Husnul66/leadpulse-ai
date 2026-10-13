from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import health_router, leads_router, messages_router

# FastAPI Application Factory
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Personalized B2B Sales and Outreach Assistant API powered by FastAPI & PostgreSQL",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Define allowed origins for CORS (combining local Next.js dev server and settings)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Safely extend with settings if BACKEND_CORS_ORIGINS is defined
if hasattr(settings, "BACKEND_CORS_ORIGINS") and settings.BACKEND_CORS_ORIGINS:
    if isinstance(settings.BACKEND_CORS_ORIGINS, list):
        for origin in settings.BACKEND_CORS_ORIGINS:
            if str(origin) not in origins:
                origins.append(str(origin))
    elif isinstance(settings.BACKEND_CORS_ORIGINS, str):
        if settings.BACKEND_CORS_ORIGINS not in origins:
            origins.append(settings.BACKEND_CORS_ORIGINS)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
def root():
    """
    Root entrypoint giving basic metadata and API navigation links.
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "health_check": "/health",
        "api_v1_prefix": settings.API_V1_PREFIX,
    }


# Include Routers
app.include_router(health_router)
app.include_router(leads_router, prefix=settings.API_V1_PREFIX)
app.include_router(messages_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)