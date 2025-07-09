from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

import app.models
from app.config.settings import Settings
from app.routes import auth
from app.routes import city as city_router
from app.routes import flight as flight_router
from app.routes import post as post_router

settings = Settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for managing city and flight information for a travel app.",
    version="1.0.0",
    contact={
        "name": "Admin",
        "email": "admin@example.com",
    },
    openapi_url=None if settings.APP_STATUS == "production" else "/openapi.json",
    docs_url=None if settings.APP_STATUS == "production" else "/docs",
    redoc_url=None if settings.APP_STATUS == "production" else "/redoc",
)


if settings.APP_STATUS == "production":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth.router)
app.include_router(city_router.router)
app.include_router(flight_router.router)
app.include_router(post_router.router)


@app.get("/", tags=["Root"])
def read_root():
    """
    Welcome endpoint.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "status": settings.APP_STATUS,
    }
