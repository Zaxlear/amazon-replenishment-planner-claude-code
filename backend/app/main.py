from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import shipment, sales, analysis


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Amazon 补货与销售规划系统",
    description="亚马逊 FBA 多仓发货计划、销售预测与库存规划 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(shipment.router, prefix="/api/v1")
app.include_router(sales.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
