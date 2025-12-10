from fastapi import FastAPI
from pydantic import BaseModel

# --- Routing Imports ---
from app.presentation.routers.login import router as login_router

# --- Pydantic Models ---
# Pydantic models define the data shape and validation for requests and responses.
class HealthCheck(BaseModel):
    """Response model for health check."""
    status: str = "OK"

class Message(BaseModel):
    """A simple message model."""
    message: str


# --- FastAPI App Initialization ---
# It's a good practice to add metadata for your API.
# This information is used in the automatically generated documentation.
app = FastAPI(
    title="DataRequest API",
    description="This is a sample FastAPI application following best practices.",
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
)


# --- API Endpoints ---
# Endpoints are defined with decorators (@app.get, @app.post, etc.).
# Using async def is recommended for I/O bound operations.

@app.get(
    "/",
    response_model=Message,
    tags=["General"],
    summary="Root endpoint",
    description="Returns a simple welcome message.",
)
async def read_root():
    """
    The root endpoint provides a welcome message to verify the API is running.
    """
    return {"message": "Welcome to the API DataRequest application! \n This service for plataform of user data requests."}



app.include_router(login_router, prefix="/auth", tags=["Authentication"])