from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.database import init_db
from src.routers import datasource
from humps import camelize


class CamelCaseJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        def convert_keys(obj):
            if isinstance(obj, dict):
                return {camelize(k): convert_keys(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_keys(i) for i in obj]
            return obj

        import json

        return json.dumps(convert_keys(content), ensure_ascii=False).encode("utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="OntoAgent API",
    description="Backend API for OntoAgent Ontology Platform",
    version="0.1.0",
    lifespan=lifespan,
    default_response_class=CamelCaseJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasource.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "timestamp": "2024-01-01T00:00:00Z"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3001)
