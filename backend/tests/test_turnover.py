from datetime import date
from unittest.mock import MagicMock

from app.services.inventory_engine import DailyResult
from app.services.turnover_service import calculate_turnover


def make_unit(id, ship_date, arrival_date, region, quantity):
    """Create a mock ShipmentUnit."""
    unit = MagicMock()
    unit.id = id
    unit.ship_date = ship_date
    unit.arrival_date = arrival_date
    unit.region = region
    unit.quantity = quantity
    return unit


def make_daily_result(d, actual_sales):
    return DailyResult(
        date=d,
        opening_stock=0,
        arrivals=0,
        available_stock=0,
        planned_sales=actual_sales,
        actual_sales=actual_sales,
        closing_stock=0,
        is_stockout=False,
        has_override=False,
        arrival_details=[],
    )


class TestTurnoverCalculation:

    def test_fifo_consumption_order(self):
        """FIFO: first arrived unit consumed first."""
        unit1 = make_unit(1, date(2026, 4, 18), date(2026, 5, 3), "west", 100)
        unit2 = make_unit(2, date(2026, 4, 18), date(2026, 5, 5), "central", 100)

        daily = [
            make_daily_result(date(2026, 5, 3), 50),
            make_daily_result(date(2026, 5, 4), 50),
            make_daily_result(date(2026, 5, 5), 50),
            make_daily_result(date(2026, 5, 6), 50),
        ]

        results = calculate_turnover([unit1, unit2], daily, initial_inventory=0)

        assert results[0].unit_id == 1
        assert results[0].fully_sold is True
        assert results[0].sold_quantity == 100
        assert results[1].unit_id == 2
        assert results[1].sold_quantity == 100
        assert results[1].fully_sold is True

    def test_initial_stock_consumed_first(self):
        """Initial inventory is consumed before any shipment unit."""
        unit1 = make_unit(1, date(2026, 4, 18), date(2026, 5, 1), "west", 100)

        daily = [
            make_daily_result(date(2026, 5, 1), 60),
            make_daily_result(date(2026, 5, 2), 60),
            make_daily_result(date(2026, 5, 3), 30),
        ]

        results = calculate_turnover([unit1], daily, initial_inventory=50)

        # 50 initial consumed first on day 1 (50 units), then 10 from unit1
        # Day 2: 60 from unit1, Day 3: 30 from unit1
        # Total from unit1: 10 + 60 + 30 = 100
        assert results[0].unit_id == 1
        assert results[0].fully_sold is True
        assert results[0].sold_quantity == 100

    def test_average_turnover_calculation(self):
        """400 items sold over 8 days, verify average turnover."""
        unit = make_unit(1, date(2026, 4, 18), date(2026, 5, 3), "west", 400)

        # Sell 50/day for 8 days starting 5/3
        daily = [make_daily_result(date(2026, 5, 3 + i), 50) for i in range(8)]

        results = calculate_turnover([unit], daily, initial_inventory=0)

        assert results[0].fully_sold is True
        assert results[0].sold_quantity == 400
        # Days from ship_date (4/18): 5/3=15d, 5/4=16d, ..., 5/10=22d
        # Each day sells 50 units. Avg = (15*50 + 16*50 + ... + 22*50) / 400
        # = 50*(15+16+17+18+19+20+21+22)/400 = 50*148/400 = 18.5
        assert results[0].avg_turnover_days == 18.5

    def test_partially_sold_unit(self):
        """Unit not fully sold: marked as not fully_sold."""
        unit = make_unit(1, date(2026, 4, 18), date(2026, 5, 3), "west", 400)

        daily = [make_daily_result(date(2026, 5, 3 + i), 50) for i in range(3)]

        results = calculate_turnover([unit], daily, initial_inventory=0)

        assert results[0].fully_sold is False
        assert results[0].sold_quantity == 150
        assert results[0].quantity == 400

    def test_multiple_batches_interleaved(self):
        """Multiple units with interleaved arrival dates - FIFO correctness."""
        unit1 = make_unit(1, date(2026, 4, 18), date(2026, 5, 3), "west", 100)
        unit2 = make_unit(2, date(2026, 4, 25), date(2026, 5, 4), "west", 100)
        unit3 = make_unit(3, date(2026, 4, 18), date(2026, 5, 5), "east", 100)

        daily = [make_daily_result(date(2026, 5, 3 + i), 50) for i in range(6)]

        results = calculate_turnover([unit1, unit2, unit3], daily, initial_inventory=0)

        # Day 3: sell 50 from unit1 (remaining 50)
        # Day 4: sell 50 from unit1 (remaining 0), unit2 arrives
        # Day 5: sell 50 from unit2 (remaining 50), unit3 arrives
        # Day 6: sell 50 from unit2 (remaining 0)
        # Day 7: sell 50 from unit3 (remaining 50)
        # Day 8: sell 50 from unit3 (remaining 0)
        assert results[0].unit_id == 1
        assert results[0].fully_sold is True
        assert results[0].sold_quantity == 100
        assert results[1].unit_id == 2
        assert results[1].fully_sold is True
        assert results[2].unit_id == 3
        assert results[2].fully_sold is True
