from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def landing_page():
    return {
        "message": "This is your backend "
    }

@app.get("/health")
def health():
    return {
        "status": "OK"
    }

