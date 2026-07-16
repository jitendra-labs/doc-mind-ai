from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.config import init_db
from .core.logging_config import setup_logging, logger

from app.api import document
from app.api import chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown lifecycles."""
    try:
        await init_db()
    except Exception as e:
        logger.critical("Database initialization failed! Exiting server process.", exc_info=e)
        raise e
    yield  # 🟢 Server is running and listening
    
    logger.info("Shutting down DocMind AI: Cleaning connection pools...")


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(
        title="DocMind AI API",
        description="Backend API for DockMind AI.",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.include_router(document.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app

app = create_app()

# root endpoint to check if API is live
@app.get('/')
def root_app():
    return {"success": True, "service": "DocMind AI Engine"}

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8100, reload=True)