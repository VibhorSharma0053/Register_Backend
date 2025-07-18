from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import employee
from app.database import check_connection, db

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await check_connection()

# Routes
app.include_router(employee.router)
