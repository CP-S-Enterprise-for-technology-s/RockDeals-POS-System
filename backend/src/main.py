"""
CP'S Enterprise POS - FastAPI Application
==========================================
Main FastAPI application entry point.
"""

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from src.api.v1 import auth, pos, products, reports, sales, users
from src.core.config import settings
from src.core.exceptions import AppException
from src.core.logging import setup_logging
from src.database import init_db


# Setup Sentry for error tracking
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        traces_sample_rate=1.0 if settings.is_development else 0.1,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging()
    await init_db()
    yield
    # Shutdown
    pass


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Enterprise-grade Point of Sale System",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # Add middleware
    _add_middleware(app)
    
    # Include routers
    _include_routers(app)
    
    # Add exception handlers
    _add_exception_handlers(app)
    
    return app


def _add_middleware(app: FastAPI) -> None:
    """Add middleware to the application."""
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # GZip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)


def _include_routers(app: FastAPI) -> None:
    """Include API routers."""
    
    # API v1 routes
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
    app.include_router(sales.router, prefix="/api/v1/sales", tags=["Sales"])
    app.include_router(pos.router, prefix="/api/v1/pos", tags=["POS"])
    app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])


def _add_exception_handlers(app: FastAPI) -> None:
    """Add exception handlers."""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """Handle application exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.detail,
                    **exc.extra,
                },
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        # Log the exception
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("Unhandled exception")
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal server error occurred",
                },
            },
        )


# Create application instance
app = create_application()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "docs": "/docs" if settings.is_development else None,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        workers=settings.workers if not settings.reload else 1,
    )
