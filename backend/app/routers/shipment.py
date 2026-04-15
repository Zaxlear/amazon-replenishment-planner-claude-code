from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import MessageResponse
from app.schemas.shipment import (
    ShipmentBatchInput,
    ShipmentBatchUpdate,
    ShipmentPlanCreate,
    ShipmentPlanListItem,
    ShipmentPlanResponse,
    ShipmentPlanUpdate,
    WarehouseConfigInput,
)
from app.services import shipment_service

router = APIRouter(prefix="/shipment-plans", tags=["发货计划"])


@router.post("", response_model=ShipmentPlanResponse)
async def create_plan(data: ShipmentPlanCreate, db: AsyncSession = Depends(get_db)):
    return await shipment_service.create_shipment_plan(db, data)


@router.get("", response_model=list[ShipmentPlanListItem])
async def list_plans(db: AsyncSession = Depends(get_db)):
    return await shipment_service.list_shipment_plans(db)


@router.get("/{plan_id}", response_model=ShipmentPlanResponse)
async def get_plan(plan_id: int, db: AsyncSession = Depends(get_db)):
    plan = await shipment_service.get_shipment_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="发货计划不存在")
    return plan


@router.put("/{plan_id}", response_model=ShipmentPlanResponse)
async def update_plan(
    plan_id: int, data: ShipmentPlanUpdate, db: AsyncSession = Depends(get_db)
):
    plan = await shipment_service.update_shipment_plan(db, plan_id, data)
    if not plan:
        raise HTTPException(status_code=404, detail="发货计划不存在")
    return plan


@router.delete("/{plan_id}", response_model=MessageResponse)
async def delete_plan(plan_id: int, db: AsyncSession = Depends(get_db)):
    if not await shipment_service.delete_shipment_plan(db, plan_id):
        raise HTTPException(status_code=404, detail="发货计划不存在")
    return MessageResponse(message="删除成功")


@router.post("/{plan_id}/batches", response_model=ShipmentPlanResponse)
async def add_batch(
    plan_id: int, data: ShipmentBatchInput, db: AsyncSession = Depends(get_db)
):
    plan = await shipment_service.add_batch(db, plan_id, data)
    if not plan:
        raise HTTPException(status_code=404, detail="发货计划不存在")
    return plan


@router.put("/{plan_id}/batches/{batch_id}", response_model=ShipmentPlanResponse)
async def update_batch(
    plan_id: int, batch_id: int, data: ShipmentBatchUpdate, db: AsyncSession = Depends(get_db)
):
    plan = await shipment_service.update_batch(db, plan_id, batch_id, data)
    if not plan:
        raise HTTPException(status_code=404, detail="批次不存在")
    return plan


@router.delete("/{plan_id}/batches/{batch_id}", response_model=MessageResponse)
async def delete_batch(
    plan_id: int, batch_id: int, db: AsyncSession = Depends(get_db)
):
    if not await shipment_service.delete_batch(db, plan_id, batch_id):
        raise HTTPException(status_code=404, detail="批次不存在")
    return MessageResponse(message="删除成功")


@router.put("/{plan_id}/warehouse-config", response_model=ShipmentPlanResponse)
async def update_warehouse_config(
    plan_id: int, data: WarehouseConfigInput, db: AsyncSession = Depends(get_db)
):
    plan = await shipment_service.update_warehouse_config(db, plan_id, data)
    if not plan:
        raise HTTPException(status_code=404, detail="发货计划不存在")
    return plan
