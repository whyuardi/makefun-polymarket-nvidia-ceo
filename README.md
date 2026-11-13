# Polymarket NVIDIA CEO forecast — make.fun entry

Forecasts the Yes price of every market of Polymarket's "Next CEO of
NVIDIA?" event at every minute of the 4 hours after each checkpoint, as
five quantiles (5% / 25% / 50% / 75% / 95%).

Method: median = last price; spread = a random walk whose per-minute
volatility is estimated per market from its own recent 1-minute moves
(EWMA mean absolute return, 720-minute window, 60-minute half-life,
floored at 0.0003 and capped at 0.005), widening with sqrt(h).

Practice score (local scorer, realized Polymarket prices): mean pinball
loss **0.2717**, vs the house baseline's 0.363589.

Entry for "Forecast Polymarket's next NVIDIA CEO prices minute by minute,
4 hours ahead" (make.fun/bounty/polymarket-nvidia-ceo-forecast-01) by
@nouzeenn. Python 3.13, standard library only, no network, deterministic.
