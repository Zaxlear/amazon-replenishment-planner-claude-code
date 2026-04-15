from datetime import date, timedelta

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.override import InventoryOverride
from app.models.sales import DailySalesEntry, SalesPlan
from app.models.shipment import ShipmentBatch, ShipmentPlan, ShipmentUnit
from app.schemas.sales import (
    DailySalesBatchInput,
    DailySalesInput,
    OverrideCreate,
    SalesPlanCreate,
    SalesPlanUpdate,
)
from app.services.inventory_engine import build_arrivals_map, calculate_inventory


async def create_sales_plan(db: AsyncSession, data: SalesPlanCreate) -> SalesPlan:
    plan = SalesPlan(
        plan_name=data.plan_name,
        sku=data.sku,
        asin=data.asin,
        start_date=data.start_date,
        end_date=data.end_date,
        initial_inventory=data.initial_inventory,
        shipment_plan_id=data.shipment_plan_id,
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


async def get_sales_plan(db: AsyncSession, plan_id: int) -> SalesPlan | None:
    result = await db.execute(
        select(SalesPlan)
        .where(SalesPlan.id == plan_id)
        .options(
            selectinload(SalesPlan.daily_entries),
            selectinload(SalesPlan.overrides),
        )
    )
    return result.scalar_one_or_none()


async def list_sales_plans(db: AsyncSession) -> list[SalesPlan]:
    result = await db.execute(select(SalesPlan).order_by(SalesPlan.created_at.desc()))
    return list(result.scalars().all())


async def update_sales_plan(
    db: AsyncSession, plan_id: int, data: SalesPlanUpdate
) -> SalesPlan | None:
    plan = await db.get(SalesPlan, plan_id)
    if not plan:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    await db.commit()
    await db.refresh(plan)
    return plan


async def delete_sales_plan(db: AsyncSession, plan_id: int) -> bool:
    plan = await db.get(SalesPlan, plan_id)
    if not plan:
        return False
    await db.delete(plan)
    await db.commit()
    return True


async def add_daily_entries(
    db: AsyncSession, plan_id: int, entries: list[DailySalesInput]
) -> list[DailySalesEntry]:
    created = []
    for entry_data in entries:
        entry = DailySalesEntry(
            sales_plan_id=plan_id,
            entry_date=entry_data.entry_date,
            planned_sales=entry_data.planned_sales,
        )
        db.add(entry)
        created.append(entry)
    await db.commit()
    return created


async def update_daily_entry(
    db: AsyncSession, plan_id: int, entry_date: date, planned_sales: int
) -> DailySalesEntry | None:
    result = await db.execute(
        select(DailySalesEntry).where(
            DailySalesEntry.sales_plan_id == plan_id,
            DailySalesEntry.entry_date == entry_date,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        return None
    entry.planned_sales = planned_sales
    await db.commit()
    await db.refresh(entry)
    return entry


async def batch_set_sales(
    db: AsyncSession, plan_id: int, data: DailySalesBatchInput
) -> int:
    """Set uniform daily sales for a date range. Returns number of entries created/updated."""
    current = data.start_date
    count = 0
    while current <= data.end_date:
        result = await db.execute(
            select(DailySalesEntry).where(
                DailySalesEntry.sales_plan_id == plan_id,
                DailySalesEntry.entry_date == current,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.planned_sales = data.daily_sales
        else:
            db.add(DailySalesEntry(
                sales_plan_id=plan_id,
                entry_date=current,
                planned_sales=data.daily_sales,
            ))
        count += 1
        current += timedelta(days=1)
    await db.commit()
    return count


async def add_override(
    db: AsyncSession, plan_id: int, data: OverrideCreate
) -> InventoryOverride:
    override = InventoryOverride(
        sales_plan_id=plan_id,
        override_date=data.override_date,
        override_value=data.override_value,
        reason=data.reason,
    )
    db.add(override)
    await db.commit()
    await db.refresh(override)
    return override


async def delete_override(db: AsyncSession, plan_id: int, override_date: date) -> bool:
    result = await db.execute(
        select(InventoryOverride).where(
            InventoryOverride.sales_plan_id == plan_id,
            InventoryOverride.override_date == override_date,
        )
    )
    override = result.scalar_one_or_none()
    if not override:
        return False
    await db.delete(override)
    await db.commit()
    return True


async def run_calculation(db: AsyncSession, plan_id: int):
    """Run inventory calculation and return results (not persisted to entries)."""
    plan = await get_sales_plan(db, plan_id)
    if not plan:
        return None

    # Get shipment units if linked
    shipment_units: list[ShipmentUnit] = []
    if plan.shipment_plan_id:
        result = await db.execute(
            select(ShipmentUnit)
            .join(ShipmentBatch)
            .where(ShipmentBatch.plan_id == plan.shipment_plan_id)
        )
        shipment_units = list(result.scalars().all())

    # Build arrivals map
    arrivals_map, arrivals_details = build_arrivals_map(shipment_units)

    # Build overrides map
    overrides = {o.override_date: o.override_value for o in plan.overrides}

    # Build daily planned list
    daily_planned = [
        (entry.entry_date, entry.planned_sales)
        for entry in sorted(plan.daily_entries, key=lambda e: e.entry_date)
    ]

    if not daily_planned:
        return plan, [], shipment_units

    results = calculate_inventory(
        initial_inventory=plan.initial_inventory,
        daily_planned=daily_planned,
        overrides=overrides,
        arrivals_map=arrivals_map,
        arrivals_details=arrivals_details,
    )

    return plan, results, shipment_units
