from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.database import init_db
from src.routers import datasource
from src.routers import ontologies, properties, individuals, debug
from src.routers import sync, mappings, query
from src.routers import admin
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

        converted = convert_keys(content)
        return json.dumps(converted, ensure_ascii=False).encode("utf-8")


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
app.include_router(ontologies.router)
app.include_router(properties.router)
app.include_router(individuals.router)
app.include_router(debug.router)
app.include_router(sync.router)
app.include_router(mappings.router)
app.include_router(query.router)
app.include_router(admin.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "timestamp": "2024-01-01T00:00:00Z"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3001)
