from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import MessageResponse
from app.schemas.sales import (
    DailySalesBatchInput,
    DailySalesInput,
    DailySalesUpdate,
    OverrideCreate,
    OverrideResponse,
    SalesPlanCreate,
    SalesPlanListItem,
    SalesPlanResponse,
    SalesPlanUpdate,
)
from app.services import sales_service

router = APIRouter(prefix="/sales-plans", tags=["销售/库存规划"])


@router.post("", response_model=SalesPlanResponse)
async def create_plan(data: SalesPlanCreate, db: AsyncSession = Depends(get_db)):
    return await sales_service.create_sales_plan(db, data)


@router.get("", response_model=list[SalesPlanListItem])
async def list_plans(db: AsyncSession = Depends(get_db)):
    return await sales_service.list_sales_plans(db)


@router.get("/{plan_id}", response_model=SalesPlanResponse)
async def get_plan(plan_id: int, db: AsyncSession = Depends(get_db)):
    plan = await sales_service.get_sales_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="销售规划不存在")
    return plan


@router.put("/{plan_id}", response_model=SalesPlanResponse)
async def update_plan(
    plan_id: int, data: SalesPlanUpdate, db: AsyncSession = Depends(get_db)
):
    plan = await sales_service.update_sales_plan(db, plan_id, data)
    if not plan:
        raise HTTPException(status_code=404, detail="销售规划不存在")
    return plan


@router.delete("/{plan_id}", response_model=MessageResponse)
async def delete_plan(plan_id: int, db: AsyncSession = Depends(get_db)):
    if not await sales_service.delete_sales_plan(db, plan_id):
        raise HTTPException(status_code=404, detail="销售规划不存在")
    return MessageResponse(message="删除成功")


@router.post("/{plan_id}/entries")
async def add_entries(
    plan_id: int, entries: list[DailySalesInput], db: AsyncSession = Depends(get_db)
):
    created = await sales_service.add_daily_entries(db, plan_id, entries)
    return {"message": f"成功添加{len(created)}条销量记录"}


@router.put("/{plan_id}/entries/{entry_date}")
async def update_entry(
    plan_id: int, entry_date: date, data: DailySalesUpdate, db: AsyncSession = Depends(get_db)
):
    entry = await sales_service.update_daily_entry(db, plan_id, entry_date, data.planned_sales)
    if not entry:
        raise HTTPException(status_code=404, detail="销量条目不存在")
    return {"message": "更新成功"}


@router.post("/{plan_id}/entries/batch")
async def batch_set(
    plan_id: int, data: DailySalesBatchInput, db: AsyncSession = Depends(get_db)
):
    count = await sales_service.batch_set_sales(db, plan_id, data)
    return {"message": f"成功设置{count}天的销量数据"}


@router.post("/{plan_id}/overrides", response_model=OverrideResponse)
async def add_override(
    plan_id: int, data: OverrideCreate, db: AsyncSession = Depends(get_db)
):
    return await sales_service.add_override(db, plan_id, data)


@router.delete("/{plan_id}/overrides/{override_date}", response_model=MessageResponse)
async def delete_override(
    plan_id: int, override_date: date, db: AsyncSession = Depends(get_db)
):
    if not await sales_service.delete_override(db, plan_id, override_date):
        raise HTTPException(status_code=404, detail="校正记录不存在")
    return MessageResponse(message="删除成功")
