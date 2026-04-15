from collections import deque
from dataclasses import dataclass
from datetime import date

from app.models.shipment import ShipmentUnit
from app.services.inventory_engine import DailyResult
from app.utils.date_utils import format_unit_label


@dataclass
class ShipmentTurnover:
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


def calculate_turnover(
    shipment_units: list[ShipmentUnit],
    daily_results: list[DailyResult],
    initial_inventory: int,
) -> list[ShipmentTurnover]:
    """
    Calculate inventory turnover per shipment unit using FIFO consumption.
    Initial inventory is consumed first as a virtual unit.
    """
    # Build FIFO queue
    fifo_queue: deque[dict] = deque()

    # Virtual unit for initial inventory
    if initial_inventory > 0:
        fifo_queue.append({
            "unit_id": None,
            "unit": None,
            "remaining": initial_inventory,
            "consumption_log": [],
        })

    # Sort real units by arrival date
    units_by_arrival = sorted(shipment_units, key=lambda u: (u.arrival_date, u.id))
    arrival_index = 0

    # Track all unit data for final computation
    all_unit_data: list[dict] = []
    if initial_inventory > 0:
        all_unit_data.append(fifo_queue[0])

    for day_result in daily_results:
        current_date = day_result.date

        # Add units arriving today
        while (
            arrival_index < len(units_by_arrival)
            and units_by_arrival[arrival_index].arrival_date == current_date
        ):
            unit = units_by_arrival[arrival_index]
            entry = {
                "unit_id": unit.id,
                "unit": unit,
                "remaining": unit.quantity,
                "consumption_log": [],
            }
            fifo_queue.append(entry)
            all_unit_data.append(entry)
            arrival_index += 1

        # Consume sales FIFO
        remaining_sales = day_result.actual_sales
        while remaining_sales > 0 and fifo_queue:
            front = fifo_queue[0]
            consume = min(remaining_sales, front["remaining"])
            front["remaining"] -= consume
            front["consumption_log"].append((current_date, consume))
            remaining_sales -= consume

            if front["remaining"] == 0:
                fifo_queue.popleft()

    # Compute turnover for each real unit
    results: list[ShipmentTurnover] = []
    for entry in all_unit_data:
        if entry["unit_id"] is None:
            continue  # Skip virtual initial inventory

        unit: ShipmentUnit = entry["unit"]
        ship_date = unit.ship_date
        total_turnover_days = 0
        total_pieces = 0

        for sell_date, qty in entry["consumption_log"]:
            days = (sell_date - ship_date).days
            total_turnover_days += days * qty
            total_pieces += qty

        avg_turnover = total_turnover_days / total_pieces if total_pieces > 0 else None
        sell_through_date = entry["consumption_log"][-1][0] if entry["consumption_log"] else None

        results.append(ShipmentTurnover(
            unit_id=unit.id,
            unit_label=format_unit_label(unit.ship_date, unit.region),
            region=unit.region,
            ship_date=unit.ship_date,
            arrival_date=unit.arrival_date,
            quantity=unit.quantity,
            sold_quantity=total_pieces,
            avg_turnover_days=round(avg_turnover, 1) if avg_turnover is not None else None,
            fully_sold=(entry["remaining"] == 0),
            sell_through_date=sell_through_date,
        ))

    return results
