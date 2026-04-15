from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.shipment import ShipmentBatch, ShipmentPlan, ShipmentUnit
from app.models.warehouse import WarehouseConfig
from app.schemas.shipment import (
    ShipmentBatchInput,
    ShipmentBatchUpdate,
    ShipmentPlanCreate,
    ShipmentPlanUpdate,
    WarehouseConfigInput,
)
from app.utils.allocation import calculate_unit_quantities

REGION_LABELS = {"west": "美西", "central": "美中", "east": "美东"}


async def create_shipment_plan(db: AsyncSession, data: ShipmentPlanCreate) -> ShipmentPlan:
    plan = ShipmentPlan(
        plan_name=data.plan_name,
        sku=data.sku,
        asin=data.asin,
        total_quantity=data.total_quantity,
        batch_count=data.batch_count,
        notes=data.notes,
    )
    db.add(plan)
    await db.flush()

    # Create warehouse configs
    await _create_warehouse_configs(db, plan.id, data.warehouse_config)

    # Create batches and units
    allocation = _config_to_allocation(data.warehouse_config)
    transit = _config_to_transit(data.warehouse_config)

    for batch_data in data.batches:
        batch = ShipmentBatch(
            plan_id=plan.id,
            batch_index=batch_data.batch_index,
            ship_date=batch_data.ship_date,
            batch_quantity=batch_data.batch_quantity,
        )
        db.add(batch)
        await db.flush()

        quantities = calculate_unit_quantities(batch_data.batch_quantity, allocation)
        for region in ["west", "central", "east"]:
            unit = ShipmentUnit(
                batch_id=batch.id,
                region=region,
                quantity=quantities[region],
                transit_days=transit[region],
                ship_date=batch_data.ship_date,
                arrival_date=batch_data.ship_date + timedelta(days=transit[region]),
            )
            db.add(unit)

    await db.commit()
    return await get_shipment_plan(db, plan.id)


async def get_shipment_plan(db: AsyncSession, plan_id: int) -> ShipmentPlan | None:
    result = await db.execute(
        select(ShipmentPlan)
        .where(ShipmentPlan.id == plan_id)
        .options(
            selectinload(ShipmentPlan.warehouse_configs),
            selectinload(ShipmentPlan.batches).selectinload(ShipmentBatch.units),
        )
    )
    return result.scalar_one_or_none()


async def list_shipment_plans(db: AsyncSession) -> list[ShipmentPlan]:
    result = await db.execute(select(ShipmentPlan).order_by(ShipmentPlan.created_at.desc()))
    return list(result.scalars().all())


async def update_shipment_plan(
    db: AsyncSession, plan_id: int, data: ShipmentPlanUpdate
) -> ShipmentPlan | None:
    plan = await get_shipment_plan(db, plan_id)
    if not plan:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    await db.commit()
    return await get_shipment_plan(db, plan_id)


async def delete_shipment_plan(db: AsyncSession, plan_id: int) -> bool:
    plan = await db.get(ShipmentPlan, plan_id)
    if not plan:
        return False
    await db.delete(plan)
    await db.commit()
    return True


async def add_batch(
    db: AsyncSession, plan_id: int, batch_data: ShipmentBatchInput
) -> ShipmentPlan | None:
    plan = await get_shipment_plan(db, plan_id)
    if not plan:
        return None

    allocation = {c.region: float(c.allocation_pct) for c in plan.warehouse_configs}
    transit = {c.region: c.transit_days for c in plan.warehouse_configs}

    batch = ShipmentBatch(
        plan_id=plan_id,
        batch_index=batch_data.batch_index,
        ship_date=batch_data.ship_date,
        batch_quantity=batch_data.batch_quantity,
    )
    db.add(batch)
    await db.flush()

    quantities = calculate_unit_quantities(batch_data.batch_quantity, allocation)
    for region in ["west", "central", "east"]:
        unit = ShipmentUnit(
            batch_id=batch.id,
            region=region,
            quantity=quantities[region],
            transit_days=transit[region],
            ship_date=batch_data.ship_date,
            arrival_date=batch_data.ship_date + timedelta(days=transit[region]),
        )
        db.add(unit)

    plan.batch_count += 1
    await db.commit()
    return await get_shipment_plan(db, plan_id)


async def update_batch(
    db: AsyncSession, plan_id: int, batch_id: int, data: ShipmentBatchUpdate
) -> ShipmentPlan | None:
    batch = await db.get(ShipmentBatch, batch_id)
    if not batch or batch.plan_id != plan_id:
        return None

    plan = await get_shipment_plan(db, plan_id)
    allocation = {c.region: float(c.allocation_pct) for c in plan.warehouse_configs}
    transit = {c.region: c.transit_days for c in plan.warehouse_configs}

    if data.ship_date is not None:
        batch.ship_date = data.ship_date
    if data.batch_quantity is not None:
        batch.batch_quantity = data.batch_quantity

    # Regenerate units
    for unit in batch.units:
        await db.delete(unit)
    await db.flush()

    quantities = calculate_unit_quantities(batch.batch_quantity, allocation)
    for region in ["west", "central", "east"]:
        unit = ShipmentUnit(
            batch_id=batch.id,
            region=region,
            quantity=quantities[region],
            transit_days=transit[region],
            ship_date=batch.ship_date,
            arrival_date=batch.ship_date + timedelta(days=transit[region]),
        )
        db.add(unit)

    await db.commit()
    return await get_shipment_plan(db, plan_id)


async def delete_batch(db: AsyncSession, plan_id: int, batch_id: int) -> bool:
    batch = await db.get(ShipmentBatch, batch_id)
    if not batch or batch.plan_id != plan_id:
        return False
    plan = await db.get(ShipmentPlan, plan_id)
    plan.batch_count = max(0, plan.batch_count - 1)
    await db.delete(batch)
    await db.commit()
    return True


async def update_warehouse_config(
    db: AsyncSession, plan_id: int, config_input: WarehouseConfigInput
) -> ShipmentPlan | None:
    plan = await get_shipment_plan(db, plan_id)
    if not plan:
        return None

    # Delete old configs
    for cfg in plan.warehouse_configs:
        await db.delete(cfg)
    await db.flush()

    await _create_warehouse_configs(db, plan_id, config_input)

    # Regenerate all units with new config
    allocation = _config_to_allocation(config_input)
    transit = _config_to_transit(config_input)

    for batch in plan.batches:
        for unit in batch.units:
            await db.delete(unit)
        await db.flush()

        quantities = calculate_unit_quantities(batch.batch_quantity, allocation)
        for region in ["west", "central", "east"]:
            unit = ShipmentUnit(
                batch_id=batch.id,
                region=region,
                quantity=quantities[region],
                transit_days=transit[region],
                ship_date=batch.ship_date,
                arrival_date=batch.ship_date + timedelta(days=transit[region]),
            )
            db.add(unit)

    await db.commit()
    return await get_shipment_plan(db, plan_id)


async def _create_warehouse_configs(
    db: AsyncSession, plan_id: int, config: WarehouseConfigInput
) -> None:
    for region, item in [("west", config.west), ("central", config.central), ("east", config.east)]:
        wc = WarehouseConfig(
            plan_id=plan_id,
            region=region,
            region_label=REGION_LABELS[region],
            allocation_pct=item.allocation_pct,
            transit_days=item.transit_days,
        )
        db.add(wc)


def _config_to_allocation(config: WarehouseConfigInput) -> dict[str, float]:
    return {
        "west": float(config.west.allocation_pct),
        "central": float(config.central.allocation_pct),
        "east": float(config.east.allocation_pct),
    }


def _config_to_transit(config: WarehouseConfigInput) -> dict[str, int]:
    return {
        "west": config.west.transit_days,
        "central": config.central.transit_days,
        "east": config.east.transit_days,
    }
