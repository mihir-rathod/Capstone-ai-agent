from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import mock

# Initialize FastAPI app
app = FastAPI(
    title="Mock API",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include mock router
app.include_router(mock.router, prefix="/api/v1", tags=["Mock"])

# Root endpoint
@app.get("/")
def root():
    return {"message": "Mock API running successfully"}

@app.get("/health")
def health():
    return {"status": "healthy"}