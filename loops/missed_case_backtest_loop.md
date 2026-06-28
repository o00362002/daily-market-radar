# Missed Case Backtest Loop

Purpose: turn missed cases into future hard checks.

## Loop

1. Record missed case.
2. Identify which radar should have caught it.
3. Identify missed search terms or source types.
4. Update watchlist or retry rule if needed.
5. Check the next report for recurrence.

## Output

Backtest results go to:

```text
reports/backtests/
```
