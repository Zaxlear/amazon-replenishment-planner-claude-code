from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class InventoryOverride(Base):
    __tablename__ = "inventory_override"
    __table_args__ = (UniqueConstraint("sales_plan_id", "override_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    sales_plan_id: Mapped[int] = mapped_column(ForeignKey("sales_plan.id", ondelete="CASCADE"))
    override_date: Mapped[date] = mapped_column(Date)
    override_value: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    sales_plan: Mapped["SalesPlan"] = relationship(back_populates="overrides")


from app.models.sales import SalesPlan  # noqa: E402, F401
