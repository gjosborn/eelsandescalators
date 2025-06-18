from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from config import settings

# port 8000

app = FastAPI(
    title=settings.api_info_title,
    description=settings.api_info_description,
    version=settings.api_info_version,
    docs_url=f"{settings.root_path_prefix}/docs",
    openapi_url=f"{settings.root_path_prefix}/openapi.json",
    redoc_url=f"{settings.root_path_prefix}/redoc"
)

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.DEBUG)
httpx_logger.addHandler(logging.StreamHandler())

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_methods=["GET"]
)


@app.get(f"{settings.root_path_prefix}/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify that the service is running.
    """
    return {"status": "ok"}
