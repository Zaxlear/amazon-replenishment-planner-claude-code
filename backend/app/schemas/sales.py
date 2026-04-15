from datetime import date, datetime

from pydantic import BaseModel


# --- Daily Sales Entry ---

class DailySalesInput(BaseModel):
    entry_date: date
    planned_sales: int


class DailySalesBatchInput(BaseModel):
    start_date: date
    end_date: date
    daily_sales: int


class DailySalesUpdate(BaseModel):
    planned_sales: int


# --- Inventory Override ---

class OverrideCreate(BaseModel):
    override_date: date
    override_value: int
    reason: str | None = None


class OverrideResponse(BaseModel):
    id: int
    override_date: date
    override_value: int
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Sales Plan ---

class SalesPlanCreate(BaseModel):
    plan_name: str
    sku: str | None = None
    asin: str | None = None
    start_date: date
    end_date: date
    initial_inventory: int = 0
    shipment_plan_id: int | None = None


class SalesPlanUpdate(BaseModel):
    plan_name: str | None = None
    sku: str | None = None
    asin: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    initial_inventory: int | None = None
    shipment_plan_id: int | None = None


class SalesPlanResponse(BaseModel):
    id: int
    plan_name: str
    sku: str | None
    asin: str | None
    start_date: date
    end_date: date
    initial_inventory: int
    shipment_plan_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SalesPlanListItem(BaseModel):
    id: int
    plan_name: str
    sku: str | None
    asin: str | None
    start_date: date
    end_date: date
    initial_inventory: int
    shipment_plan_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Calculation Results ---

class ArrivalDetail(BaseModel):
    unit_label: str
    quantity: int


class DailyCalculationResult(BaseModel):
    date: date
    opening_stock: int
    arrivals: int
    available_stock: int
    planned_sales: int
    actual_sales: int
    closing_stock: int
    is_stockout: bool
    has_override: bool
    arrival_details: list[ArrivalDetail] = []


class CalculationSummary(BaseModel):
    total_days: int
    total_planned_sales: int
    total_actual_sales: int
    stockout_days: int
    stockout_dates: list[date]
    ending_inventory: int


class CalculationResponse(BaseModel):
    sales_plan_id: int
    calculation_date: datetime
    summary: CalculationSummary
    daily_data: list[DailyCalculationResult]


# --- Turnover ---

class ShipmentTurnoverResult(BaseModel):
    unit_id: int
    unit_label: str
    region: str
    ship_date: date
    arrival_date: date
    quantity: int
    sold_quantity: int
    avg_turnover_days: float | None
    fully_sold: bool
    sell_through_date: date | None


class TurnoverResponse(BaseModel):
    sales_plan_id: int
    turnovers: list[ShipmentTurnoverResult]


# --- Chart Data ---

class ChartDataPoint(BaseModel):
    date: date
    opening_stock: int
    planned_sales: int
    actual_sales: int
    is_stockout: bool
    arrivals: int
    has_override: bool


class ChartDataResponse(BaseModel):
    sales_plan_id: int
    data: list[ChartDataPoint]


# --- Stockout Warning ---

class StockoutWarning(BaseModel):
    date: date
    planned_sales: int
    available_stock: int
    shortfall: int


class StockoutWarningResponse(BaseModel):
    sales_plan_id: int
    warnings: list[StockoutWarning]
