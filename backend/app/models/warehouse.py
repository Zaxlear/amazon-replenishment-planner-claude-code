from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WarehouseConfig(Base):
    __tablename__ = "warehouse_config"
    __table_args__ = (
        CheckConstraint("region IN ('west', 'central', 'east')", name="chk_wh_region"),
        CheckConstraint("allocation_pct >= 0 AND allocation_pct <= 100", name="chk_allocation"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("shipment_plan.id", ondelete="CASCADE"))
    region: Mapped[str] = mapped_column(String(10))
    region_label: Mapped[str] = mapped_column(String(50))
    allocation_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    transit_days: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    plan: Mapped["ShipmentPlan"] = relationship(back_populates="warehouse_configs")


from app.models.shipment import ShipmentPlan  # noqa: E402, F401
