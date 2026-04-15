from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from app.models.shipment import ShipmentUnit
from app.utils.date_utils import format_unit_label


@dataclass
class DailyResult:
    date: date
    opening_stock: int
    arrivals: int
    available_stock: int
    planned_sales: int
    actual_sales: int
    closing_stock: int
    is_stockout: bool
    has_override: bool
    arrival_details: list[dict]  # [{"unit_label": str, "quantity": int}]


def build_arrivals_map(
    shipment_units: list[ShipmentUnit],
) -> tuple[dict[date, int], dict[date, list[dict]]]:
    """
    Build {date: total_quantity} and {date: [detail]} mappings from shipment units.
    """
    totals: dict[date, int] = defaultdict(int)
    details: dict[date, list[dict]] = defaultdict(list)

    for unit in shipment_units:
        totals[unit.arrival_date] += unit.quantity
        details[unit.arrival_date].append({
            "unit_label": format_unit_label(unit.ship_date, unit.region),
            "quantity": unit.quantity,
        })

    return dict(totals), dict(details)


def check_stockout(
    opening: int, arrivals: int, planned: int,
    is_first: bool, is_last: bool,
) -> bool:
    available = opening + arrivals

    # First day with zero stock: not stockout
    if is_first and available == 0:
        return False

    # Last day: zero stock or exactly consumed = not stockout
    if is_last:
        if available == 0:
            return False
        if planned == available and available > 0:
            return False

    # Regular stockout check
    if available == 0:
        return True
    if planned >= available:
        return True

    return False


def calculate_inventory(
    initial_inventory: int,
    daily_planned: list[tuple[date, int]],  # [(date, planned_sales), ...]
    overrides: dict[date, int],
    arrivals_map: dict[date, int],
    arrivals_details: dict[date, list[dict]],
) -> list[DailyResult]:
    """
    Core inventory calculation engine.
    Forward iteration from start_date, applying overrides and arrivals.
    """
    results: list[DailyResult] = []
    total_days = len(daily_planned)

    for i, (current_date, planned) in enumerate(daily_planned):
        is_first = i == 0
        is_last = i == total_days - 1

        # Step 1: Determine opening stock
        if current_date in overrides:
            opening = overrides[current_date]
        elif is_first:
            opening = initial_inventory
        else:
            opening = results[i - 1].closing_stock

        # Check if this date has an override (for display purposes)
        has_override = current_date in overrides

        # Step 2: Add arrivals
        arrivals = arrivals_map.get(current_date, 0)
        available = opening + arrivals

        # Step 3: Calculate actual consumption and stockout
        actual_sales = min(planned, available)
        is_stockout = check_stockout(opening, arrivals, planned, is_first, is_last)

        # Step 4: Closing stock
        closing = available - actual_sales

        results.append(DailyResult(
            date=current_date,
            opening_stock=opening,
            arrivals=arrivals,
            available_stock=available,
            planned_sales=planned,
            actual_sales=actual_sales,
            closing_stock=closing,
            is_stockout=is_stockout,
            has_override=has_override,
            arrival_details=arrivals_details.get(current_date, []),
        ))

    return results
