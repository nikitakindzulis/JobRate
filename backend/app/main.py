from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import cv, match, profile

Base.metadata.create_all(bind=engine)

app = FastAPI(title="JobRate API")

# MVP без аутентификации: расширение работает с origin вида chrome-extension://<id>,
# который нельзя перечислить заранее, поэтому разрешаем все origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cv.router)
app.include_router(profile.router)
app.include_router(match.router)


@app.get("/health")
def health():
    return {"status": "ok"}
