# taste-log · 记味

Your personal taste memory. Every meal builds your flavor profile.

## When to use

- User rates a restaurant/dish ("这家8分", "不错", "太咸了")
- User wants to see their taste preferences
- Other skills need user preference data (street-scan, pin-zhuo)

## Commands

```
# Log a taste entry
tastelog log --user mock_user_zhao --poi-id r_0042 --score 8 \
  --note "汤底很鲜，座位太挤" --tags "鲜,偏咸"

# View taste profile
tastelog profile --user mock_user_zhao

# Query taste graph for a specific category
tastelog query --user mock_user_zhao --category "越南粉"

# Export taste data for other skills
tastelog export --user mock_user_zhao --format json
```

## Privacy

- Strictly explicit input: every entry requires user to actively provide feedback
- AI never passively learns from behavior
- User can delete any entry: tastelog delete --entry-id entry_001
- Full data export and wipe: tastelog clear --user mock_user_zhao
