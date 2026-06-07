# bill-snap · 拍账

Snap a receipt, split the bill. No more mental math.

## When to use

- User shares a receipt photo or text
- Someone says "AA" or "平账" in a group chat
- After a group meal to settle bills

## Commands

```
# Parse a receipt (mock mode: uses pre-defined receipt data)
billsnap parse --receipt-id rcpt_001

# Split equally among N people
billsnap split --receipt-id rcpt_001 --members "alice,bob,charlie" --mode equal

# Split by items (each person picks what they ordered)
billsnap split --receipt-id rcpt_001 --members "alice,bob,charlie" --mode itemized \
  --assignments '{"alice":["item1","item3"],"bob":["item2"],"charlie":["item4","item5"]}'

# Show balance summary for a group
billsnap balance --group-id grp_001
```

## Privacy

- Receipt data processed locally, never uploaded
- Balance data stored in local SQLite only
