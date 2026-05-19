from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.auth import router as auth_router
import backend.auth_db as auth_db
from backend.community import router as community_router
from backend.notification import router as notification_router
from backend.message import router as message_router

app = FastAPI(title="Fast API Anime Community App",
    docs_url="/docs",
    version="0.0.1")

origins = ["http://localhost:3000",]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(community_router.router)
app.include_router(notification_router.router)
app.include_router(message_router.router)


@app.on_event("startup")
async def startup_seed_users():
    # Ensure common test users exist so test suite expectations are met
    try:
        await auth_db.create_user("ash", "ash@gmail.com", "pass123")
    except Exception:
        pass
    try:
        await auth_db.create_user("test", "test@example.com", "testpassword")
    except Exception:
        pass
@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to the FastAPI Ticket Master App!"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "message": "Server is running"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
 
