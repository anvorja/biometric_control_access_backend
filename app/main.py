from fastapi import FastAPI, Response
from starlette.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.v1.api import api_router
import httpx
from fastapi.responses import Response
from async_lru import alru_cache

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@alru_cache(maxsize=1)
async def get_favicon():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://res.cloudinary.com/dv2xu8dwr/image/upload/v1733373523/fingerprint_zn7t8z.png"
        )
        return response.content if response.status_code == 200 else None


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_content = await get_favicon()
    if favicon_content:
        return Response(content=favicon_content, media_type="image/x-icon")
    return Response(status_code=404)


@app.get("/", include_in_schema=False)
async def root():
    return {"Mensaje": "Backend Biometric running"}
