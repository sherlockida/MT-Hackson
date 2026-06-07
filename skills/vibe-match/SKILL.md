# vibe-match · 心流

Find places by atmosphere, not keywords.

## When to use

- User describes a mood or atmosphere they want
- User says "想找个地方..." followed by vibe description
- User is looking for something experiential, not transactional

## Commands

```
# Natural language vibe query -> matched venues
vibematch query --text "想安静待着，有点爵士乐，适合一个人" --lat 39.98 --lng 116.30

# Show a venue's atmosphere profile
vibematch profile --poi-id v_0012

# Compare two venues' atmospheres
vibematch compare --poi-a v_0012 --poi-b v_0025
```

## How it works

1. User describes desired atmosphere in natural language
2. Keyword-based parser extracts an 8-dim atmosphere vector from the description
3. Cosine similarity against all venue atmosphere vectors in radius
4. Return top matches with "vibe explanation"

## Atmosphere dimensions

| Dim       | Low (0.0)                                        | High (1.0)              |
|-----------|--------------------------------------------------|-------------------------|
| noise     | library-quiet                                    | nightclub-loud          |
| light     | candlelit                                        | floor-to-ceiling windows|
| crowd     | private-room feel                                | packed-house            |
| social    | solo-friendly                                    | group-required          |
| energy    | zen-slow                                         | electric-fast           |
| aesthetic | raw-industrial                                   | polished-instagram      |
| outdoor   | fully indoor                                     | fully outdoor           |
| time_fit  | (dynamic: how well the venue fits the current hour) |                      |
