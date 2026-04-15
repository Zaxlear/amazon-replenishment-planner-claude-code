def calculate_unit_quantities(
    batch_quantity: int,
    allocation: dict[str, float],
) -> dict[str, int]:
    """
    Calculate per-warehouse quantities using the largest remainder method.
    Ensures the integer allocation sums exactly to batch_quantity.
    """
    raw = {r: batch_quantity * pct / 100 for r, pct in allocation.items()}
    floored = {r: int(v) for r, v in raw.items()}
    remainder = batch_quantity - sum(floored.values())

    decimals = sorted(raw.keys(), key=lambda r: raw[r] - floored[r], reverse=True)
    for i in range(remainder):
        floored[decimals[i]] += 1

    return floored
