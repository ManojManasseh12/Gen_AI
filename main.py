from fastapi import FastAPI
from app.routes import chat

app = FastAPI()

@app.get("/")
def landing_page():

    return {
        "message": "This is your backend"
    }

@app.get("/health")
def health():
    return {
        "status": "nalla iruken"
    }

app.include_router(chat.router)