from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator, model_validator


# --- Warehouse Config ---

class WarehouseConfigItem(BaseModel):
    allocation_pct: Decimal
    transit_days: int


class WarehouseConfigInput(BaseModel):
    west: WarehouseConfigItem
    central: WarehouseConfigItem
    east: WarehouseConfigItem

    @model_validator(mode="after")
    def check_allocation_sum(self):
        total = self.west.allocation_pct + self.central.allocation_pct + self.east.allocation_pct
        if total != 100:
            raise ValueError(f"分配比例之和必须为100%，当前为{total}%")
        return self


class WarehouseConfigResponse(BaseModel):
    id: int
    region: str
    region_label: str
    allocation_pct: Decimal
    transit_days: int

    model_config = {"from_attributes": True}


# --- Shipment Unit ---

class ShipmentUnitResponse(BaseModel):
    id: int
    batch_id: int
    region: str
    quantity: int
    transit_days: int
    ship_date: date
    arrival_date: date
    status: str

    model_config = {"from_attributes": True}


# --- Shipment Batch ---

class ShipmentBatchInput(BaseModel):
    batch_index: int
    ship_date: date
    batch_quantity: int

    @field_validator("ship_date")
    @classmethod
    def validate_saturday(cls, v: date) -> date:
        if v.weekday() != 5:
            raise ValueError(f"发货日期必须为周六，{v} 是星期{v.weekday()}")
        return v


class ShipmentBatchResponse(BaseModel):
    id: int
    batch_index: int
    ship_date: date
    batch_quantity: int
    units: list[ShipmentUnitResponse] = []

    model_config = {"from_attributes": True}


class ShipmentBatchUpdate(BaseModel):
    ship_date: date | None = None
    batch_quantity: int | None = None

    @field_validator("ship_date")
    @classmethod
    def validate_saturday(cls, v: date | None) -> date | None:
        if v is not None and v.weekday() != 5:
            raise ValueError(f"发货日期必须为周六，{v} 是星期{v.weekday()}")
        return v


# --- Shipment Plan ---

class ShipmentPlanCreate(BaseModel):
    plan_name: str
    sku: str | None = None
    asin: str | None = None
    total_quantity: int
    batch_count: int = 1
    warehouse_config: WarehouseConfigInput
    batches: list[ShipmentBatchInput]
    notes: str | None = None

    @model_validator(mode="after")
    def check_batch_count(self):
        if len(self.batches) != self.batch_count:
            raise ValueError(f"batch_count({self.batch_count})与batches数量({len(self.batches)})不一致")
        return self


class ShipmentPlanUpdate(BaseModel):
    plan_name: str | None = None
    sku: str | None = None
    asin: str | None = None
    total_quantity: int | None = None
    status: str | None = None
    notes: str | None = None


class ShipmentPlanResponse(BaseModel):
    id: int
    plan_name: str
    sku: str | None
    asin: str | None
    total_quantity: int
    batch_count: int
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
    warehouse_configs: list[WarehouseConfigResponse] = []
    batches: list[ShipmentBatchResponse] = []

    model_config = {"from_attributes": True}


class ShipmentPlanListItem(BaseModel):
    id: int
    plan_name: str
    sku: str | None
    asin: str | None
    total_quantity: int
    batch_count: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
