from datetime import date

from app.services.inventory_engine import calculate_inventory, check_stockout


class TestInventoryEngine:
    """Tests per Section 8.1 of the spec."""

    def test_basic_daily_calculation(self):
        """Basic: initial 500, daily sales 50, no arrivals, 10 days to 0."""
        daily = [(date(2026, 5, i), 50) for i in range(1, 11)]
        results = calculate_inventory(500, daily, {}, {}, {})

        assert len(results) == 10
        assert results[0].opening_stock == 500
        assert results[0].closing_stock == 450
        assert results[9].opening_stock == 50
        assert results[9].closing_stock == 0

    def test_arrivals_increase_stock(self):
        """Arrivals: initial 100, daily 50, day 3 arrives 400."""
        daily = [(date(2026, 5, i), 50) for i in range(1, 6)]
        arrivals = {date(2026, 5, 3): 400}
        results = calculate_inventory(100, daily, {}, arrivals, {})

        # Day 1: 100 - 50 = 50
        assert results[0].closing_stock == 50
        # Day 2: 50 - 50 = 0
        assert results[1].closing_stock == 0
        # Day 3: 0 + 400 = 400, 400 - 50 = 350
        assert results[2].opening_stock == 0
        assert results[2].arrivals == 400
        assert results[2].available_stock == 400
        assert results[2].closing_stock == 350

    def test_stockout_detection(self):
        """Stockout: stock exhausted, then marked as stockout."""
        daily = [(date(2026, 5, i), 50) for i in range(1, 5)]
        # 100 stock, 50/day: day2 planned==available → stockout (non-last day)
        results = calculate_inventory(100, daily, {}, {}, {})

        assert results[0].is_stockout is False
        assert results[1].is_stockout is True  # planned(50) >= available(50) on non-last day
        assert results[1].actual_sales == 50
        assert results[2].is_stockout is True  # available=0
        assert results[2].actual_sales == 0
        assert results[3].is_stockout is False  # last day with 0 → not stockout

    def test_first_day_zero_not_stockout(self):
        """First day with 0 initial inventory is NOT stockout."""
        daily = [(date(2026, 5, 1), 50)]
        results = calculate_inventory(0, daily, {}, {}, {})

        assert results[0].is_stockout is False
        assert results[0].actual_sales == 0

    def test_last_day_exact_consumption_not_stockout(self):
        """Last day: planned == available (exact consumption) is NOT stockout."""
        daily = [(date(2026, 5, i), 50) for i in range(1, 3)]
        # 100 / 50 = exactly 2 days
        results = calculate_inventory(100, daily, {}, {}, {})

        assert results[1].planned_sales == 50
        assert results[1].available_stock == 50
        assert results[1].is_stockout is False
        assert results[1].closing_stock == 0

    def test_last_day_zero_not_stockout(self):
        """Last day with 0 stock is NOT stockout."""
        daily = [(date(2026, 5, i), 50) for i in range(1, 4)]
        # 100 / 50 = 2 days, day 3 is 0
        results = calculate_inventory(100, daily, {}, {}, {})

        assert results[2].opening_stock == 0
        assert results[2].is_stockout is False

    def test_override_propagation(self):
        """Override propagates: override on day 3 affects all subsequent days."""
        daily = [(date(2026, 5, i), 50) for i in range(1, 6)]
        overrides = {date(2026, 5, 3): 3005}
        results = calculate_inventory(500, daily, overrides, {}, {})

        # Days 1-2 normal
        assert results[0].opening_stock == 500
        assert results[1].opening_stock == 450
        # Day 3 overridden
        assert results[2].opening_stock == 3005
        assert results[2].closing_stock == 2955
        # Day 4 uses day 3's closing
        assert results[3].opening_stock == 2955

    def test_multiple_overrides(self):
        """Multiple overrides are independent."""
        daily = [(date(2026, 5, i), 50) for i in range(1, 6)]
        overrides = {
            date(2026, 5, 2): 1000,
            date(2026, 5, 4): 2000,
        }
        results = calculate_inventory(500, daily, overrides, {}, {})

        assert results[1].opening_stock == 1000  # override
        assert results[2].opening_stock == 950   # 1000-50
        assert results[3].opening_stock == 2000  # override
        assert results[4].opening_stock == 1950  # 2000-50

    def test_override_with_arrivals(self):
        """Override 3005 + next day arrival 500 = available 3455 (after sales)."""
        daily = [(date(2026, 5, i), 50) for i in range(10, 13)]
        overrides = {date(2026, 5, 10): 3005}
        arrivals = {date(2026, 5, 11): 500}
        results = calculate_inventory(0, daily, overrides, arrivals, {})

        # Day 10: override 3005, sales 50, closing 2955
        assert results[0].opening_stock == 3005
        assert results[0].closing_stock == 2955
        # Day 11: opening 2955, arrivals 500, available 3455, sales 50, closing 3405
        assert results[1].opening_stock == 2955
        assert results[1].arrivals == 500
        assert results[1].available_stock == 3455
        assert results[1].closing_stock == 3405

    def test_multiple_arrivals_same_day(self):
        """Multiple shipments arriving same day are summed."""
        daily = [(date(2026, 5, 3), 50)]
        arrivals = {date(2026, 5, 3): 700}  # pre-aggregated
        results = calculate_inventory(100, daily, {}, arrivals, {})

        assert results[0].arrivals == 700
        assert results[0].available_stock == 800

    def test_sales_exceeds_stock(self):
        """Planned 100 but only 30 available: actual = 30."""
        daily = [(date(2026, 5, 1), 100), (date(2026, 5, 2), 100)]
        results = calculate_inventory(30, daily, {}, {}, {})

        assert results[0].actual_sales == 30
        assert results[0].closing_stock == 0

    def test_empty_plan(self):
        """Edge case: empty plan."""
        results = calculate_inventory(500, [], {}, {}, {})
        assert results == []

    def test_zero_initial_inventory(self):
        """Zero initial, relies entirely on arrivals."""
        daily = [(date(2026, 5, i), 50) for i in range(1, 4)]
        arrivals = {date(2026, 5, 2): 200}
        results = calculate_inventory(0, daily, {}, arrivals, {})

        # Day 1: 0 stock, first day → not stockout
        assert results[0].is_stockout is False
        assert results[0].actual_sales == 0
        # Day 2: 0 + 200 arrival = 200, sell 50 → 150
        assert results[1].available_stock == 200
        assert results[1].closing_stock == 150
        # Day 3: 150 - 50 = 100
        assert results[2].closing_stock == 100


class TestCheckStockout:
    def test_first_day_zero(self):
        assert check_stockout(0, 0, 50, is_first=True, is_last=False) is False

    def test_last_day_zero(self):
        assert check_stockout(0, 0, 50, is_first=False, is_last=True) is False

    def test_last_day_exact(self):
        assert check_stockout(50, 0, 50, is_first=False, is_last=True) is False

    def test_middle_day_zero(self):
        assert check_stockout(0, 0, 50, is_first=False, is_last=False) is True

    def test_middle_day_planned_exceeds(self):
        assert check_stockout(30, 0, 50, is_first=False, is_last=False) is True

    def test_normal_no_stockout(self):
        assert check_stockout(100, 0, 50, is_first=False, is_last=False) is False
