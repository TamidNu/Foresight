from fastapi import FastAPI, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.repositories.database import get_db
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.controllers.user_controller import router as user_router  

# Initialize FastAPI app
app = FastAPI(
    title="FastAPI Backend",
    description="A simple FastAPI backend",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create new APIRouter with prefix /api
api = APIRouter(prefix="/api")

# Simple hello endpoint
@app.get("/hello")
async def hello():
    return {"message": "Hello, World!", "status": "success"}

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    # Your database queries here
    return {"message": "Connected to Neon!"}

@api.get("/db-info")
def get_db_info(db: Session = Depends(get_db)):
    try:
        # Get database name
        result = db.execute(text("SELECT current_database();"))
        db_name = result.fetchone()[0]
        
        return {
            "status": "connected",
            "database": db_name,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

api.include_router(user_router)
app.include_router(api)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)