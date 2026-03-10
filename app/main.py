from fastapi import FastAPI
from app.routers.meetings_router import router as meetings_router
from app.routers.notes_router import router as notes_router

app = FastAPI()

app.include_router(meetings_router)
app.include_router(notes_router)
