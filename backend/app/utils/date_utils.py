from datetime import date, timedelta


def validate_saturday(ship_date: date) -> bool:
    """Check if a date is Saturday (weekday() == 5)."""
    return ship_date.weekday() == 5


def next_saturday(from_date: date) -> date:
    """Get the next Saturday from a given date."""
    days_ahead = 5 - from_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return from_date + timedelta(days=days_ahead)


def format_unit_label(ship_date: date, region: str) -> str:
    """Format shipment unit label: '{月}月{日}日-{仓库}'."""
    region_map = {"west": "美西", "central": "美中", "east": "美东"}
    region_label = region_map.get(region, region)
    return f"{ship_date.month}月{ship_date.day}日-{region_label}"
