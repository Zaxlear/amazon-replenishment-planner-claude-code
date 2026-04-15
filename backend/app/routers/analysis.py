from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.sales import (
    ArrivalDetail,
    CalculationResponse,
    CalculationSummary,
    ChartDataPoint,
    ChartDataResponse,
    DailyCalculationResult,
    ShipmentTurnoverResult,
    StockoutWarning,
    StockoutWarningResponse,
    TurnoverResponse,
)
from app.services.sales_service import run_calculation
from app.services.turnover_service import calculate_turnover

router = APIRouter(prefix="/sales-plans", tags=["图表与分析"])


@router.get("/{plan_id}/calculate", response_model=CalculationResponse)
async def calculate(plan_id: int, db: AsyncSession = Depends(get_db)):
    result = await run_calculation(db, plan_id)
    if result is None:
        raise HTTPException(status_code=404, detail="销售规划不存在")

    plan, daily_results, shipment_units = result

    if not daily_results:
        return CalculationResponse(
            sales_plan_id=plan_id,
            calculation_date=datetime.now(),
            summary=CalculationSummary(
                total_days=0, total_planned_sales=0, total_actual_sales=0,
                stockout_days=0, stockout_dates=[], ending_inventory=plan.initial_inventory,
            ),
            daily_data=[],
        )

    stockout_dates = [r.date for r in daily_results if r.is_stockout]

    return CalculationResponse(
        sales_plan_id=plan_id,
        calculation_date=datetime.now(),
        summary=CalculationSummary(
            total_days=len(daily_results),
            total_planned_sales=sum(r.planned_sales for r in daily_results),
            total_actual_sales=sum(r.actual_sales for r in daily_results),
            stockout_days=len(stockout_dates),
            stockout_dates=stockout_dates,
            ending_inventory=daily_results[-1].closing_stock,
        ),
        daily_data=[
            DailyCalculationResult(
                date=r.date,
                opening_stock=r.opening_stock,
                arrivals=r.arrivals,
                available_stock=r.available_stock,
                planned_sales=r.planned_sales,
                actual_sales=r.actual_sales,
                closing_stock=r.closing_stock,
                is_stockout=r.is_stockout,
                has_override=r.has_override,
                arrival_details=[ArrivalDetail(**d) for d in r.arrival_details],
            )
            for r in daily_results
        ],
    )


@router.get("/{plan_id}/chart-data", response_model=ChartDataResponse)
async def chart_data(plan_id: int, db: AsyncSession = Depends(get_db)):
    result = await run_calculation(db, plan_id)
    if result is None:
        raise HTTPException(status_code=404, detail="销售规划不存在")

    plan, daily_results, _ = result

    return ChartDataResponse(
        sales_plan_id=plan_id,
        data=[
            ChartDataPoint(
                date=r.date,
                opening_stock=r.opening_stock,
                planned_sales=r.planned_sales,
                actual_sales=r.actual_sales,
                is_stockout=r.is_stockout,
                arrivals=r.arrivals,
                has_override=r.has_override,
            )
            for r in daily_results
        ],
    )


@router.get("/{plan_id}/turnover", response_model=TurnoverResponse)
async def turnover(plan_id: int, db: AsyncSession = Depends(get_db)):
    result = await run_calculation(db, plan_id)
    if result is None:
        raise HTTPException(status_code=404, detail="销售规划不存在")

    plan, daily_results, shipment_units = result

    turnovers = calculate_turnover(shipment_units, daily_results, plan.initial_inventory)

    return TurnoverResponse(
        sales_plan_id=plan_id,
        turnovers=[
            ShipmentTurnoverResult(
                unit_id=t.unit_id,
                unit_label=t.unit_label,
                region=t.region,
                ship_date=t.ship_date,
                arrival_date=t.arrival_date,
                quantity=t.quantity,
                sold_quantity=t.sold_quantity,
                avg_turnover_days=t.avg_turnover_days,
                fully_sold=t.fully_sold,
                sell_through_date=t.sell_through_date,
            )
            for t in turnovers
        ],
    )


@router.get("/{plan_id}/stockout-warnings", response_model=StockoutWarningResponse)
async def stockout_warnings(plan_id: int, db: AsyncSession = Depends(get_db)):
    result = await run_calculation(db, plan_id)
    if result is None:
        raise HTTPException(status_code=404, detail="销售规划不存在")

    _, daily_results, _ = result

    warnings = [
        StockoutWarning(
            date=r.date,
            planned_sales=r.planned_sales,
            available_stock=r.available_stock,
            shortfall=r.planned_sales - r.available_stock,
        )
        for r in daily_results
        if r.is_stockout
    ]

    return StockoutWarningResponse(sales_plan_id=plan_id, warnings=warnings)
