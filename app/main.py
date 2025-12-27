from app.api.v1.router import api_router
from app.core.config import settings
from app.core.migration_check import check_migrations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create database tables
# Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)


# Check migrations on startup
@app.on_event("startup")
async def startup_event():
    check_migrations()


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "Welcome to the Todo API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
