"""
FastAPI entry point for the Azure VNet challenge project.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from src.config import settings
from src.auth import verify_token, create_access_token
from src.database import init_db
from src.routes import vnet_routes

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database before serving requests."""
    logger.info("Starting API")
    try:
        init_db()
        logger.info("Database ready")
    except Exception as e:
        logger.error(f"Database startup failed: {str(e)}")
        raise
    yield
    logger.info("Shutting down API")


app = FastAPI(
    title="Azure VNet Challenge API",
    description="Create Azure VNets with subnets, save them, and fetch them through an authenticated API.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


async def get_current_user(credentials=Depends(security)):
    """Validate the JWT token for protected endpoints."""
    token = credentials.credentials
    try:
        await verify_token(token)
        return {"token": token}
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


app.include_router(
    vnet_routes.router,
    prefix="/api/v1/vnets",
    tags=["VNets"],
    dependencies=[Depends(get_current_user)]
)


@app.post("/api/v1/auth/token", tags=["Auth"])
async def get_token(user_id: str, username: str):
    """Create a JWT for authenticated access to VNet endpoints."""
    try:
        token = create_access_token(user_id=user_id, username=username)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Token generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate token"
        )


@app.get("/health", tags=["Health"])
async def health_check():
    """Health route for quick checks."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/", tags=["Root"])
async def root():
    """Basic API information."""
    return {
        "message": "Azure VNet Challenge API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "auth": "/api/v1/auth/token"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Return a consistent error payload for unexpected errors."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.ENVIRONMENT != "production"
    )
