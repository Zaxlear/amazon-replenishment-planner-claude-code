from datetime import date, datetime

from sqlalchemy import Boolean, Date, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SalesPlan(Base):
    __tablename__ = "sales_plan"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_name: Mapped[str] = mapped_column(String(200))
    sku: Mapped[str | None] = mapped_column(String(100))
    asin: Mapped[str | None] = mapped_column(String(20))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    initial_inventory: Mapped[int] = mapped_column(Integer, default=0)
    shipment_plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("shipment_plan.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    shipment_plan: Mapped["ShipmentPlan | None"] = relationship(back_populates="sales_plans")
    daily_entries: Mapped[list["DailySalesEntry"]] = relationship(
        back_populates="sales_plan", cascade="all, delete-orphan", order_by="DailySalesEntry.entry_date"
    )
    overrides: Mapped[list["InventoryOverride"]] = relationship(
        back_populates="sales_plan", cascade="all, delete-orphan"
    )


class DailySalesEntry(Base):
    __tablename__ = "daily_sales_entry"
    __table_args__ = (
        UniqueConstraint("sales_plan_id", "entry_date"),
        Index("idx_daily_sales_date", "sales_plan_id", "entry_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sales_plan_id: Mapped[int] = mapped_column(ForeignKey("sales_plan.id", ondelete="CASCADE"))
    entry_date: Mapped[date] = mapped_column(Date)
    planned_sales: Mapped[int] = mapped_column(Integer, default=0)
    actual_sales: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_stockout: Mapped[bool] = mapped_column(Boolean, default=False)
    opening_stock: Mapped[int | None] = mapped_column(Integer, nullable=True)
    closing_stock: Mapped[int | None] = mapped_column(Integer, nullable=True)
    arrivals: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    sales_plan: Mapped["SalesPlan"] = relationship(back_populates="daily_entries")


from app.models.shipment import ShipmentPlan  # noqa: E402, F401
from app.models.override import InventoryOverride  # noqa: E402, F401
