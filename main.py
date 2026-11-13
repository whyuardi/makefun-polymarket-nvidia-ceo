"""Forecast Polymarket's "Next CEO of NVIDIA?" Yes prices, 4 hours ahead.

Method: for each market, the median forecast is its last price (prediction
market prices are close to a martingale: recent trends and post-jump
reversals carry no usable signal in the practice data), and the spread
around it is a random walk whose per-minute volatility is estimated from
that market's own recent 1-minute moves. The estimator is the mean
absolute 1-minute return over the last 720 minutes, exponentially
weighted with a 60-minute half-life (recent minutes matter most) and
scaled to a normal sigma; it is floored at 0.0003 and capped at 0.005
price units per square-root minute. Quantiles are the standard normal's
at 0.05 / 0.25 / 0.5 / 0.75 / 0.95, widening with sqrt(h) over the
240-minute horizon, clamped to [0, 1] and rounded to 6 decimals.

On the kit's six practice cases this scores a mean pinball loss of
0.2717 against the house baseline's 0.363589 (median error and coverage
are computed by the local scorer, not needed here).

Standard library only, no network, deterministic: the same case always
writes the same bytes.
"""

import json
import math
import os

QUANTILES = [0.05, 0.25, 0.5, 0.75, 0.95]
Z = [-1.644854, -0.67449, 0.0, 0.67449, 1.644854]
WINDOW = 720
HALFLIFE = 60.0
SIGMA_FLOOR = 0.0003
SIGMA_CAP = 0.005

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def price6(x):
    """Clamp to [0, 1] and round to 6 decimals (0, never -0)."""
    return round(min(1.0, max(0.0, x)), 6) + 0.0


def market_sigma(prices):
    """EWMA mean-absolute 1-minute return, scaled to a normal sigma."""
    window = prices[-WINDOW - 1:] if len(prices) > WINDOW else prices
    if len(window) < 3:
        return SIGMA_FLOOR
    weighted = 0.0
    weight_sum = 0.0
    for i in range(len(window) - 2, -1, -1):
        age = len(window) - 2 - i
        w = 0.5 ** (age / HALFLIFE)
        weighted += w * abs(window[i + 1] - window[i])
        weight_sum += w
    sigma = (weighted / weight_sum) * 1.2533 if weight_sum else 0.0
    return min(SIGMA_CAP, max(SIGMA_FLOOR, sigma))


def forecast_market(prices, horizon):
    """240 rows of five quantiles for one market."""
    if not prices:
        return [[0.5, 0.5, 0.5, 0.5, 0.5] for _ in range(horizon)]
    x = prices[-1]
    sigma = market_sigma(prices)
    rows = []
    for h in range(1, horizon + 1):
        spread = sigma * math.sqrt(h)
        rows.append([price6(x + z * spread) for z in Z])
    return rows


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    inputs = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith(".in"))
    for name in inputs:
        case_id = name[:-3]
        with open(os.path.join(INPUT_DIR, name), "r", encoding="utf-8") as f:
            case = json.load(f)
        horizon = int(case["horizon_minutes"])
        forecasts = []
        for market in case["markets"]:
            forecasts.append({
                "id": market["id"],
                "q": forecast_market(market["prices"], horizon),
            })
        payload = json.dumps({"forecasts": forecasts}) + "\n"
        with open(os.path.join(OUTPUT_DIR, case_id + ".out"), "w", encoding="utf-8") as f:
            f.write(payload)


if __name__ == "__main__":
    main()
