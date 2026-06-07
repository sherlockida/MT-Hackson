# street-scan · 街探

Your walking companion for serendipitous city discovery.

## When to use

- User says "逛逛"/"走走"/"遛达"/"附近有啥"/"开启逛街模式"
- User shares a location
- User is bored and wants to explore

## Commands

```
# Start drift mode at a location, get rolling recommendations
streetscan drift --lat 39.9809 --lng 116.3060 --heading NE --radius 500

# One-shot: what's around me right now?
streetscan around --lat 39.9809 --lng 116.3060 --radius 300 --mood "随便逛逛"

# I liked/disliked a place (updates novelty + taste profile)
streetscan feedback --poi-id r_0042 --score 8 --note "汤底很鲜，座位太挤"

# Show my exploration map (which areas I've covered)
streetscan map --user mock_user_zhao
```

## Output format

JSON with fields:

- poi : place info (name, type, distance_m, direction, tags, signature)
- why : 1-2 sentence reason (novelty-first: "你还没试过这个区域的越南粉")
- walk : walking instruction ("前方 200 米左转，门口有蓝色招牌")
- novelty_score : 0-1 (1 = completely new to you)
- vibe_tags : atmosphere descriptors for cross-referencing with vibe-match

## Privacy

- Location is consumed in real-time, never persisted as raw coordinates · Only area-level tags (e.g. "中关村") are stored in taste-log · User must explicitly say "记住这家" to persist any feedback
