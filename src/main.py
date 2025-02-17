import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import Settings
from route.admin_route import router as admin_router
from route.auth_route import router as auth_router
from route.content_route import router as content_router

settings = Settings()


app = FastAPI(
    title="kusis.kr backend API",
    description="This is just a simple API server for kusis.kr.",
    version="0.1.0",
    contact={
        "name": "Moonsu Kang",
        "url": "https://github.com/sounmu",
        "email": "sukkang_@korea.ac.kr"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    json_encoder=json.JSONEncoder,
    json_dumps_params={"ensure_ascii": False}
)

origins = [
    "https://localhost:8000",
    "http://localhost:5173",
    "https://kusis.kr",
    "https://api.kusis.kr"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(content_router)


@app.get("/")
async def root():
    return {"message": "kusis.kr API 서버입니다."}
