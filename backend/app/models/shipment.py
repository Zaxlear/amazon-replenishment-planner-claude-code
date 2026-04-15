from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ShipmentPlan(Base):
    __tablename__ = "shipment_plan"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_name: Mapped[str] = mapped_column(String(200))
    sku: Mapped[str | None] = mapped_column(String(100))
    asin: Mapped[str | None] = mapped_column(String(20))
    total_quantity: Mapped[int] = mapped_column(Integer)
    batch_count: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    batches: Mapped[list["ShipmentBatch"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan", order_by="ShipmentBatch.batch_index"
    )
    warehouse_configs: Mapped[list["WarehouseConfig"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan"
    )
    sales_plans: Mapped[list["SalesPlan"]] = relationship(back_populates="shipment_plan")


class ShipmentBatch(Base):
    __tablename__ = "shipment_batch"
    __table_args__ = (
        UniqueConstraint("plan_id", "batch_index"),
        CheckConstraint("EXTRACT(DOW FROM ship_date) = 6", name="chk_saturday"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("shipment_plan.id", ondelete="CASCADE"))
    batch_index: Mapped[int] = mapped_column(Integer)
    ship_date: Mapped[date] = mapped_column(Date)
    batch_quantity: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    plan: Mapped["ShipmentPlan"] = relationship(back_populates="batches")
    units: Mapped[list["ShipmentUnit"]] = relationship(
        back_populates="batch", cascade="all, delete-orphan"
    )


class ShipmentUnit(Base):
    __tablename__ = "shipment_unit"
    __table_args__ = (
        CheckConstraint("region IN ('west', 'central', 'east')", name="chk_unit_region"),
        Index("idx_shipment_unit_arrival", "arrival_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("shipment_batch.id", ondelete="CASCADE"))
    region: Mapped[str] = mapped_column(String(10))
    quantity: Mapped[int] = mapped_column(Integer)
    transit_days: Mapped[int] = mapped_column(Integer)
    ship_date: Mapped[date] = mapped_column(Date)
    arrival_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    batch: Mapped["ShipmentBatch"] = relationship(back_populates="units")


# Avoid circular import - WarehouseConfig and SalesPlan imported via string refs
from app.models.warehouse import WarehouseConfig  # noqa: E402, F401
from app.models.sales import SalesPlan  # noqa: E402, F401
