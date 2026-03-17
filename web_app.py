from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from database.db import db

# Load environment variables FIRST
load_dotenv()

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db.init_db()
    yield

# Initialize FastAPI with lifespan
app = FastAPI(
    title="Fintanik API",
    description="Financial tracking API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from web.api import auth

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# Health check endpoint
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Fintanik API is running"}

# Database health check endpoint
@app.get("/health/db")
def database_health():
    """Check if database connection is working"""
    try:
        session = db.get_session()
        from database.models import User
        user_count = session.query(User).count()
        session.close()
        return {
            "status": "ok",
            "database": "connected",
            "users": user_count
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_app:app", host="0.0.0.0", port=8000, reload=True)
