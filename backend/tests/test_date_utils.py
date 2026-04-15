from datetime import date

from app.utils.date_utils import validate_saturday, next_saturday, format_unit_label


class TestValidateSaturday:
    def test_saturday_is_valid(self):
        assert validate_saturday(date(2026, 4, 18)) is True  # Saturday

    def test_non_saturday_invalid(self):
        assert validate_saturday(date(2026, 4, 15)) is False  # Tuesday
        assert validate_saturday(date(2026, 4, 19)) is False  # Sunday


class TestNextSaturday:
    def test_from_monday(self):
        assert next_saturday(date(2026, 4, 13)) == date(2026, 4, 18)

    def test_from_saturday(self):
        # If already Saturday, get next Saturday
        assert next_saturday(date(2026, 4, 18)) == date(2026, 4, 25)

    def test_from_friday(self):
        assert next_saturday(date(2026, 4, 17)) == date(2026, 4, 18)


class TestFormatUnitLabel:
    def test_west(self):
        assert format_unit_label(date(2026, 4, 18), "west") == "4月18日-美西"

    def test_central(self):
        assert format_unit_label(date(2026, 5, 2), "central") == "5月2日-美中"

    def test_east(self):
        assert format_unit_label(date(2026, 4, 18), "east") == "4月18日-美东"
