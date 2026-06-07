# 逛 Guàng — 城市即兴体验引擎

赛题：基于 OpenClaw 的本地生活 Skill 开发 版本：v2.0 OpenClaw 版本：基于 openclaw/openclaw main 分支（2026-06 最新）一句话：不做攻略，直接逛，把你的 IM 变成城市的第六感。

---

## 0. 为什么推翻 v1

| v1 知否的问题 | v2 逛的修正 |
|---|---|
| 在做一个 6 层平台（L1-L6），OpenClaw 沦为其中一层 | 严格在 OpenClaw 框架内开发 Skill，不额外造轮子 |
| 自研 ProactiveSensing / ContextAggregator / QuietHoursGuard | OpenClaw 自带调度、Memory、Channel 能力，直接复用 |
| 假设控制 IM 适配层（微信/钉钉/飞书） | OpenClaw 已支持 20+ channel（WhatsApp/Telegram/WeChat/Slack），直接用 |
| Skill 只是"名义上的模块"，实际高度耦合 | 每个 Skill 是独立的 SKILL.md + 脚本，可单独安装、单独使用 |
| 技术概念 > 可 Demo 体验 | 以"评委坐在那里 3 分钟内被震撼"为设计目标 |

---

## 1. 核心洞察

### 1.1 所有人都会做的事（红海）

> "请问附近有什么好吃的？" → AI 返回 3 家餐厅列表

这是对话版美团搜索，把 App UI 换成文字，体验没有质感，90% 的参赛队会做这个。

### 1.2 我们要做的事（蓝海）

年轻人对本地生活 App 最大的吐槽不是"找不到好店"，而是：

> "做攻略太累了。"

打开美团对比价，大众点评要翻评论，小红书要着笔记一一花在"研究去哪里"的时间比"真正在玩"还长。决策疲劳是本地生活的头号体验杀手。逛的答案：不替你做更好的攻略，帮助减少决策。

### 1.3 三种交互范式的进化

| 范式 | 代表 | 用户动作 | 问题 |
|---|---|---|---|
| 搜索式 | 美团大众点评 | "搜索→浏览→比价→下单" | 决策疲劳，9+ 次点击 |
| 推送式 | v1 知否 | "零推送→确认" | 被动，容易变成垃圾通知 |
| 感知式 | v2 逛 | "出门→走→IM 自动出现灵感" | 零决策成本，把城市变成可逛的 |

---

## 2. 方案概览

### 2.1 产品定位

逛是一套运行在 OpenClaw 上的本地生活 Skill 套件。它不替你做决策，而是在你的 IM 对话中激发即兴体验——走到哪、玩到哪、吃到哪。

### 2.2 三个核心 Skill + 两个增强 Skill

| # | Skill 名 | 覆盖场景 | 核心理念 | 一句话 |
|---|---|---|---|---|
| ★1 | street-scan 街探 | 餐饮+发现 | 实时位置感知 | "前方 200 米有家开了 3 个月的拉面店，适合你的微辣偏好" |
| ★2 | pin-zhuo 拼桌 | 餐饮+社交 | 群聊约束求解 | 5 人聚餐不再投票选餐厅，AI 算出满足所有人约束的最优解 |
| ★3 | vibe-match 心流 | 娱乐 | 氛围匹配 | 不搜"酒吧"，而是说"想安静待着，有点爵士乐"，有点爵士乐 |
| +4 | bill-snap 拍账 | 消费 | 拍照结账 | 拍收据→识别→群聊 AA→消费图谱 |
| +5 | taste-log 记味 | 偏好 | 渐进学习 | "今天这家 8 分，汤底偏咸"→入你的味觉图谱 |

### 2.3 飞轮效应

```
你出门逛 ——> street-scan 推荐沿途发现 ——> 你去体验
     |                                          ↓
taste-log 积累你的偏好 ←——— 你说"这家不错/一般"
     ↓
下次 vibe-match 更懂你 ——> 群聊 pin-zhuo 用上所有人的画像
```

---

## 3. 技术架构

### 3.1 与 OpenClaw 的关系

```
┌─────────────────────────────────────────────┐
│         OpenClaw Runtime（完全复用，不修改）          │
│  ┌──────────┐ ┌──────────┐ ┌──────┐ ┌────────────┐ │
│  │ LLM Router│ │  Memory  │ │Channels│ │Skill Loader│ │
│  │ （多模型） │ │ （上下文）│ │ (IM) │ │ (SKILL.md) │ │
│  └──────────┘ └──────────┘ └──────┘ └────────────┘ │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │       Skill Hub（我们开发的 5 个 Skill）          │   │
│  │  ┌──────────┐ ┌─────────┐ ┌───────────┐   │   │
│  │  │street-scan│ │ pin-zhuo│ │ vibe-match│   │   │
│  │  │ (Python) │ │ (Python)│ │  (Python) │   │   │
│  │  └──────────┘ └─────────┘ └───────────┘   │   │
│  │  ┌──────────┐ ┌─────────┐                 │   │
│  │  │ bill-snap│ │taste-log│                 │   │
│  │  │ (Python) │ │ (Python)│                 │   │
│  │  └──────────┘ └─────────┘                 │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  本地数据层（SQLite + JSON Mock，零真实用户数据）      │   │
│  │  poi_mock.db  |  user_prefs.db  |  taste_graph.json │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 3.2 每个 Skill 的交付物

严格遵循 OpenClaw 的 Skill 规范：

```
skills/
├── street-scan/
│   ├── SKILL.md            # 标准 SKILL.md（YAML frontmatter + Markdown 正文）
│   ├── scripts/
│   │   ├── streetscan      # CLI 入口（可执行）
│   │   ├── poi_engine.py   # POI 空间匹配引擎
│   │   └── novelty_ranker.py  # 新鲜度排序算法
│   └── mock_data/
│       └── pois.json       # 80 个模拟 POI
├── pin-zhuo/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── pinzhuo         # CLI 入口
│   │   ├── constraint_solver.py  # CSP 约束求解器
│   │   └── group_pref.py   # 群体偏好交集算法
│   └── mock_data/
│       └── restaurants.json
├── vibe-match/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── vibematch       # CLI 入口
│   │   └── atmosphere_vec.py  # 氛围向量化 + 余弦匹配
│   └── mock_data/
│       └── venues.json
├── bill-snap/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── billsnap        # CLI 入口
│   │   └── receipt_parser.py  # 收据解析 + AA 计算
└── taste-log/
    ├── SKILL.md
    └── scripts/
        ├── tastelog        # CLI 入口
        └── taste_graph.py  # 味觉图谱 CRUD
```

### 3.3 技术选型

| 组件 | 选型 | 原因 |
|---|---|---|
| Skill 脚本语言 | Python 3.11+ | 快速开发 + 丰富的数学/空间计算库 |
| 本地存储 | SQLite | 零依赖、零配置、单文件 |
| 空间计算 | Haversine 公式 | 计算 POI 距离，不依赖外部地图 API |
| 约束求解 | 自实现 CSP（回溯+剪枝） | 不引入重量级依赖 |
| 氛围匹配 | 余弦相似度 | 多维向量空间匹配 |
| Mock 数据 | JSON 文件 | 可读、可编辑、可版本控制 |

---

## 4. 核心 Skill #1：street-scan 街探

### 4.1 一句话

> 开启"逛街模式"，AI 根据你的位置实时推荐前方的惊喜。

### 4.2 为什么不是"推荐附近餐厅"

| 传统搜索 | street-scan |
|---|---|
| 用户主动问"附近有啥好吃的" | 用户只是在走路，AI 主动说"前方有个好地方" |
| 按评分排序 | 按新鲜度排序（你没去过 > 评分高的） |
| 一次返回一个列表 | 持续推送，每走一段路推一条 |

### 4.3 SKILL.md

```yaml
---
name: street-scan
description: "Real-time walking companion: discover nearby places as you walk. Turn on drift-mode and get one surprise recommendation for every ~300m you walk, ranked by novelty (places you haven't been)"
metadata:
  openclaw:
    emoji: "🚶🏻"
    requires:
      bins: [python3]
    install:
      - id: pip
        kind: shell
        command: "pip install -e skills/street-scan"
        label: "Install street-scan dependencies"
---
# street-scan · 街探
Your walking companion for serendipitous city discovery.
## When to use
- User says "逛逛"/"走走"/"溜达"/"附近有啥"/"开启逛街模式"
- User shares a location
- User is bored and wants to explore
## Commands
```bash
# Start drift mode at a location, get rolling recommendations
streetscan drift —lat 39.9809 —lng 116.3060 —heading NE —radius 500
# One-shot: what's around me right now?
streetscan around —lat 39.9809 —lng 116.3060 —radius 300 —mood "随便逛逛"
# liked/disliked a place (updates novelty + taste profile)
streetscan feedback —poi-id r_0042 —score 8 —note "汤底很鲜，座位太挤"
# Show my exploration map (which areas I've covered)
streetscan map —user mock_user_1
```
#### Output format

JSON with fields:

- **poi** : place info (name, type, distance_m, direction, tags, signature)
- **why** : 1-2 sentence reason (novelty-first: "你还没试过这个区域的越南粉")
- **walk** : walking instruction ("前方 200 米左转，门口有蓝色招牌")
- **novelty_score** : 0-1 (1 = completely new to you)
- **vibe_tags** : atmosphere descriptors for cross-referencing with vibe-match

#### Privacy

- Location is consumed in real-time, **never persisted as raw coordinates**
- Only area-level tags (e.g. "中关村") are stored in taste-log
- User must explicitly say "记住这家" to persist any feedback

### 4.4 核心算法：新鲜度排序

传统推荐 = `score(distance, rating, price)`
街探推荐 = `score(novelty, serendipity, contextual_fit)`

```python
def rank_pois(pois, user_history, context):
    """
    新鲜度优先排序：
    - novelty:    你没去过这个区域/品类的程度（0-1）
    - serendipity: 这个地方有多"意外"（0-1）
    - contextual:  当下时间/天气/心情的匹配度（0-1）
    """
    scored = []
    for poi in pois:
        novelty = compute_novelty(poi, user_history)
        serendipity = compute_serendipity(poi, user_history)
        contextual = compute_contextual_fit(poi, context)
        # 关键：新鲜度权重最大
        total = 0.45 * novelty + 0.30 * serendipity + 0.25 * contextual
        scored.append((poi, total))
    return sorted(scored, key=lambda x: -x[1])

def compute_novelty(poi, history):
    """
    三层新鲜度计算：
    1. 这家店去过吗？ → 去过=0，没去过=0.4
    2. 这个品类最近吃过吗？ → 7天内吃过=0，30天没吃=0.3
    3. 这个区域探索过吗？ → 去过区域5次以上=0，从未到过=0.3
    """
    store_novel = 0.0 if poi.id in history.visited_pois else 0.4
    cat_novel = 0.3 * (1 - history.category_recency(poi.category))
    area_novel = 0.3 * (1 - history.area_familiarity(poi.area))
    return store_novel + cat_novel + area_novel

def compute_serendipity(poi, history):
    """
    意外度 = 这个地方有多"出乎意料"
    - 用户从没搜索过这个品类 = 高意外度
    - 这个品类在用户品味画像中评分为空 = 中意外度
    - 这家店类别在用户画像中评分为空 = 中意外外度
    - 这家店很新（开业<3个月） = 加分
    """
    never_searched = 1.0 if poi.category not in history.search_history else 0.0
    unrated_category = 0.5 if poi.category not in history.taste_profile else 0.0
    is_new_store = 0.3 if poi.opened_months < 3 else 0.0
    return min(1.0, never_searched * 0.4 + unrated_category * 0.3 + is_new_store * 0.3)
```

### 4.5 Demo 对话

```
用户 → 下班了想漫游达达

逛 → 🚶🏻 逛街模式已开启！我会根据你的位置推荐沿途惊喜。
你现在在哪？发个位置给我，或者告诉我大概在哪。

用户 → 中关村

逛 → 收到，中关村出发。往哪个方向走？

用户 → 随便

逛 → 那往五道口方向溜达吧，路上有几个你没去过的地方——
    🆕 前方 300 米 · 成都巷子·老锅馆
    开了 2 个月的新店，只有 8 张桌子
    你没去过这个区域的川菜小馆
    · 现在 18:20，正好趁开门
    → 从当前位置直走，过第二个路口右转，巷子里第三家

用户 → 看点近，还有别的吗

逛 → 🆕 右手边 150 米 · 一碗越南
    越南粉粉，你的味觉图谱里没有东南亚品类
    · 新鲜度拉满：你从来没吃过越南粉
    · 这家牛肉河粉是招牌，¥38
    · 就在你右边那条街，露台门头

用户 → 去看看

逛 → 👍 到了之后觉得怎么样，随时告诉我。
我继续帮你看前面还有啥好玩的。

[30分钟后]

用户 → 阿粉不错，8分，汤头鲜但辣度不够

逛 → 记下了！
    ✍🏻 "一碗越南" → 8 分，汤头鲜，辣度不够
    已更新你的味觉图谱：新增"越南粉"品类偏好，
    下次给你推东南亚的时候我会注意辣度。
```

---

## 5. 核心 Skill #2：pin-zhuo 拼桌

### 5.1 一句话

> 群聊里"周末聚餐"→ AI 自动收集每人约束 → 算出最优方案。不投票，解方程。

### 5.2 为什么不是"群投票选餐厅"

投票的问题：

- 选项由谁定？（定选项本身就是最难的决策）
- 少数人的忌口/过敏被多数票否决
- 距离远的人总吃亏
- 投完票还是要人去订

拼桌用约束求解代替投票：每个人说自己的约束（时间/位置/忌口/预算），AI 找满足所有人约束的最优解。

### 5.3 SKILL.md

```yaml
---
name: pin-zhuo
description: "Group dining constraint solver: collects each member's constraints (time, location, budget, dietary) via private DM, then computes the Pareto-optimal restaurant that satisfies ALL hard constraints and maximizes group satisfaction."
metadata:
  openclaw:
    emoji: "🍽"
    requires:
      bins: [python3]
    install:
      - id: pip
        kind: shell
        command: "pip install -e skills/pin-zhuo"
        label: "Install pin-zhuo dependencies"
---
# pin-zhuo · 拼桌
Group dining made effortless. No voting, no arguing — constraint solving.
## When to use
- Someone says "聚餐"/"约饭"/"周末吃饭"/"几个人吃饭" in a group chat
- User asks to plan a group meal
## Commands
```bash
# Start a group plan session
pinzhuo start —group-id grp_001 —members "alice,bob,charlie" —date "2026-05-07"
# Add one member's constraints
pinzhuo constrain —group-id grp_001 —member alice \
    —location "海淀" —budget-max 150 \
    —dietary-exclude "花生,香菜" —time-windows "18:00-20:00"
# Solve: find the optimal restaurant
pinzhuo solve —group-id grp_001
# Show explanation of why this restaurant was chosen
pinzhuo explain —group-id grp_001 —solution-id sol_1
```
```

#### Algorithm

Constraint Satisfaction Problem (CSP):

1. Hard constraints (MUST satisfy all): dietary exclusions, budget ceiling, open hours
2. Soft constraints (optimize): location proximity to geographic midpoint, cuisine preference intersection, rating, novelty
3. Solver: backtracking with constraint propagation + Pareto ranking on soft objectives
4. Output: top 3 Pareto-optimal solutions with per-member satisfaction breakdown

#### Output format

```json
{
  "solutions": [
    {
      "restaurant": { "name": "...", "cuisine": "...", "price_pp": 120 },
      "satisfaction": {
        "alice": { "score": 0.92, "met": ["budget","dietary","time"], "stretched": ["distance: 2.1km"] },
        "bob":   { "score": 0.88, "met": ["budget","time"], "stretched": ["cuisine: 不是首选但可接受"] },
        "charlie": { "score": 0.95, "met": ["all"] }
      },
      "geo_midpoint_distance_m": 1200,
      "why": ["满足所有人忌口", "人均¥120在预算内", "距3人位置中点最近"]
    }
  ]
}
```

#### Privacy

- Constraints are collected via **private DM** to each member
- Individual preferences are never shown to other group members
- Only the aggregated solution is posted to the group
- All data stored locally in SQLite, clearable via `pinzhuo clear`

### 5.4 核心算法：约束求解

```python
@dataclass
class MemberConstraint:
    member_id: str
    location: GeoPoint          # 出发位置
    budget_max: int             # 人均预算上限
    dietary_exclude: list[str]  # 忌口/过敏
    cuisine_prefer: list[str]   # 菜系偏好（soft）
    time_windows: list[tuple]   # 可用时间段

def solve_group_dining(constraints: list[MemberConstraint],
                       restaurants: list[Restaurant]) -> list[Solution]:
    """
    Step 1: 硬约束过滤（不满足任一人的硬约束 → 直接排除）
    Step 2: 软约束评分（多目标优化 → 帕累托前沿）
    Step 3: 可解释性（为什么选这家，每个人的满意度）
    """
    # Step 1: 硬约束过滤
    feasible = []
    for r in restaurants:
        if all(satisfies_hard(r, c) for c in constraints):
            feasible.append(r)
    if not feasible:
        # 松弛策略：逐步放宽预算 10%，扩大半径 500m
        feasible = relax_and_retry(constraints, restaurants)
    # Step 2: 多目标评分
    midpoint = geo_midpoint([c.location for c in constraints])
    scored = []
    for r in feasible:
        per_member = {}
        for c in constraints:
            per_member[c.member_id] = score_for_member(r, c, midpoint)
        # 帕累托：最小化 max_dissatisfaction（公平性）
        min_satisfaction = min(s.score for s in per_member.values())
        avg_satisfaction = mean(s.score for s in per_member.values())
        scored.append(Solution(
            restaurant=r,
            satisfaction=per_member,
            fairness=min_satisfaction,    # 最不满意的人有多满意
            efficiency=avg_satisfaction,  # 平均满意度
        ))
    # Step 3: 帕累托前沿（公平性 vs 效率）
    pareto = pareto_front(scored, keys=['fairness', 'efficiency'])
    return pareto[:3]  # 返回 top 3

def satisfies_hard(restaurant, constraint):
    """硬约束：不可妥协"""
    # 忌口检查：菜单中必须不含过敏原的选项
    if any(allergen in restaurant.menu_tags for allergen in constraint.dietary_exclude):
        if not restaurant.has_allergen_free_options(constraint.dietary_exclude):
            return False
    # 预算检查
    if restaurant.avg_price > constraint.budget_max * 1.1:  # 给 10% 容差
        return False
    # 营业时间检查
    if not any(overlaps(restaurant.hours, tw) for tw in constraint.time_windows):
        return False
    return True
```

### 5.5 Demo 对话

```
[5人群聊]
小钱 → 周六晚上聚聚？

逛 → 🍽 收到！我来帮你们拼桌。
我会私聊每个人收集时间、位置、忌口和预算，
然后算出满足所有人的最优方案。
群里的 @小钱 @张三 @李四 @王五 @孙七
开始收集，5 分钟后出结果——

[私聊 小钱]
逛 → 周六聚餐，告诉我你的约束：
    · 你大概从哪里出发？
    · 人均预算上限？
    · 有忌口或过敏吗？
    · 几点方便？
小钱 → 徐汇，150以内，不吃香菜，6点到8点都行

[私聊 张三]
逛 → （同样的约束收集问题）
张三 → 浦东，200以内，花生过敏，7点后

[... 其他人同理，省略 ...]

[5 分钟后，群聊]
逛 → 🎉 拼桌结果出来了！5 人约束已全部满足：
    ✅ 方案 A：胡同里·新京菜，人均 ¥138
    小钱：预算内，无香菜可选 → 满意度 94%
    张三：无花生菜品充足 → 满意度 91%
    李四：距他最近 → 满意度 96%
    王五：有微辣选项 → 满意度 89%
    孙七：有健身餐 → 满意度 85%
    📍 距 5 人位置中心 1.2km（步行安全）
    🕗 19:00 有位
    为什么选这里：满足所有人忌口 + 人均最低 + 最不满意的人也有 85%
    方案 B：泰式餐内，人均 ¥155（更好但王五要走远一点）
    方案 C：日式居酒屋，人均 ¥168（孙七最爱但预算略高）
    回复 A/B/C 确认，或者说"再算一次"。

小钱 → AI

逛 → ✅ 已选方案 A · 胡同里·新京菜，周六 19:00，5 位
我会在周六 17:00 提醒大家出发。
```

---

## 6. 核心 Skill #3：vibe-match 心流

### 6.1 一句话

> 不搜"酒吧"，说"想安静待着，有点爵士乐"。用氛围找地方。

### 6.2 核心创新：氛围向量化

传统搜索的维度：品类 + 距离 + 评分 + 价格 心流的维度：人类感知的多维氛围空间

```
每个 POI 的氛围向量（8 维）：
    noise_level:    0.0（图书馆安静）→ 1.0（夜店嗡嗡）
    light:          0.0（昏暗烛光）  → 1.0（落地玻璃窗）
    crowd_density:  0.0（包场感）    → 1.0（人挨人）
    social_vibe:    0.0（独处友好）  → 1.0（社交必需）
    energy:         0.0（放松慢节奏）→ 1.0（热烈快节奏）
    aesthetic:      0.0（极简工业）  → 1.0（精致ins风）
    outdoor_ratio:  0.0（纯室内）    → 1.0（纯户外）
    time_fit:       按当前时段动态计算
```

用户的自然语言描述 → LLM 提取氛围向量 → 余弦相似度匹配。

### 6.3 SKILL.md

```yaml
---
name: vibe-match
description: "Atmosphere-first venue discovery: describe the vibe you want in natural language, get matched to places by 8-dimensional atmosphere vectors using cosine similarity. No keyword search, pure vibe."
metadata:
  openclaw:
    emoji: "✨"
    requires:
      bins: [python3]
    install:
      - id: pip
        kind: shell
        command: "pip install -e skills/vibe-match"
        label: "Install vibe-match dependencies"
---
# vibe-match · 心流
Find places by atmosphere, not keywords.
## When to use
- User describes a mood or atmosphere they want
- User says "帮我找个地方..." followed by vibe description
- User is looking for something experiential, not transactional
## Commands
```bash
# Natural language vibe query → matched venues
vibematch query —text "想安静待着，有点爵士乐，适合一个人" —lat 39.98 —lng 116.30
# Show a venue's atmosphere profile
vibematch profile —poi-id v_0012
# Compare two venues' atmospheres
vibematch compare —poi-a v_0012 —poi-b v_0025
```
```

#### How it works

1. User describes desired atmosphere in natural language
2. LLM extracts an 8-dim atmosphere vector from the description
3. Cosine similarity against all venue atmosphere vectors in radius
4. Return top matches with "vibe explanation"

#### Atmosphere dimensions

| Dim | Low (0.0) | High (1.0) |
|---|---|---|
| noise | library-quiet | nightclub-loud |
| light | candlelit | floor-to-ceiling windows |
| crowd | private-room feel | packed-house |
| social | solo-friendly | group-required |
| energy | zen-slow | electric-fast |
| aesthetic | raw-industrial | polished-instagram |
| outdoor | fully indoor | fully outdoor |
| time_fit | (dynamic: how well the venue fits the current hour) | |

### 6.4 Demo 对话

```
用户 ▸ 想找一个能待到很晚的地方，安静一点，最好有酒

逛 ▸ 🛰 解析你的氛围：
    安静(noise=0.2) + 夜间友好(time=late) + 有酒(类型=bar/lounge)
    搜索中...
    氛围匹配 TOP 3:
    1️⃣ 暗室 Darkroom · 威士忌吧 · 匹配度 94%
       🚫 安静（播放黑胶爵士）
       🕯 昏暗烛光 · 8 张吧台位
       ⬛ 营业到凌晨 2 点
       💰 人均 ¥120
       → 距你 800 米，步行 10 分钟
       为什么匹配：噪音 0.15 < 你要的 0.2 ✓，深夜营业 ✓，独处友好 ✓
    2️⃣ 树洞 TreeHole · 精酿啤酒 · 匹配度 87%
       略有人声但不吵 · 工业风 · 到 0 点
       → 1.2km
    3️⃣ 月台 Platform · 清酒居酒屋 · 匹配度 82%
       日式安静 · 偏贵(¥180) · 到 23:30
       → 600m

用户 ▸ 暗室听起来不错

逛 ▸ 👍 暗室 Darkroom，直走 800 米左转巷子里。
    去了之后告诉我感觉怎么样，帮你更新氛围偏好。
```

---

## 7. 增强 Skill #4 & #5（简述）

### 7.1 bill-snap 拍账

```yaml
---
name: bill-snap
description: "Receipt parser + group AA calculator. Snap a receipt photo, parse items, split the bill in group chat."
metadata:
  openclaw:
    emoji: "🧾"
    requires:
      bins: [python3]
---
```

核心能力：

- 拍收据 → OCR 解析（Mock 阶段用预置 JSON 模拟 OCR 结果）
- 群聊里说"AA"→ 自动按人数平摊或按明细拆分
- 追账提醒（仅 1 次，不骚扰）

### 7.2 taste-log 记味

```yaml
---
name: taste-log
description: "Incremental taste profile builder. After each dining experience, say how you liked it — the AI builds your taste graph over time. Explicit-input only, no passive learning."
metadata:
  openclaw:
    emoji: "🍴"
    requires:
      bins: [python3]
---
```

核心能力：

- 用户说"今天这家 8 分，辣度刚好但太咸了"→ 解析为结构化评价
- 渐进式构建味觉图谱（品类偏好、辣度、价位、关键词）
- 严格显式输入：每条评价必须用户主动说，AI 不偷偷学
- 输出供 street-scan 和 pin-zhuo 消费

---

## 8. Mock 数据规范

### 8.1 零真实用户数据声明

- 所有 POI 数据为虚构（名称/地址/菜单均为模拟）
- 用户画像为 3 个预设虚拟角色
- 位置数据使用 Mock GPS 流（可回放）
- 所有偏好仅通过 Demo 中的显式对话输入
- 数据存储在本地 SQLite，Demo 结束后一键清空

### 8.2 Mock POI 数据（80 个）

| 品类 | 数量 | 范围覆盖 |
|---|---|---|
| 中餐 | 15 | 从苍蝇馆到高端中餐 |
| 西餐 | 8 | 从快餐到西餐厅 |
| 日韩 | 10 | 拉面/居酒屋/韩式烤肉 |
| 东南亚 | 6 | 越南粉/泰菜/加坡 |
| 咖啡茶 | 10 | 从连锁到独立精品 |
| 酒吧 | 8 | 从安静威士忌到热闹夜店 |
| 活动 | 12 | 展览/Live/桌游/SPA/电影 |
| 户外 | 6 | 公园/市集/夜跑路线 |
| 甜品 | 5 | 面包店/冰淇淋/甜品站 |

### 8.3 虚拟用户画像

|  | 小赵（程序员） | 小钱（设计师） | 小孙（销售） |
|---|---|---|---|
| 城市 | 北京·海淀 | 上海·徐汇 | 北京·朝阳 |
| 辣度 | 高 | 无辣 | 中 |
| 预算 | ¥60 | ¥80 | ¥200 |
| 忌口 | 香菜 | 花生 | 无 |
| 氛围偏好 | 安静+独处 | 美感+打卡 | 社交+热闹 |
| 探索倾向 | 中（愿意试新但不主动找） | 高（爱探店） | 低（固定几家轮转） |

---

## 9. 三个 Demo 高光时刻

### 9.1 Demo #1：「下班溜达」— street-scan 的即兴魔力

评委看到的：用户说"逛逛溜达"，AI 像一个在你耳边的本地朋友，走一段路推荐一个惊喜，全是你没去过的地方。不是列表，是伴随式发现。对比冲击：打开美团 App 搜索"附近美食"=一个评分排序列表，千篇一律。street-scan = 每走一步都有新发现，像逛一个活的城市。

### 9.2 Demo #2：「5 人拼桌」— pin-zhuo 的约束求解

评委看到的：5 个人各有各的忌口/位置/预算，AI 私聊收集后一键算出最优方案。不是投票（投票总有人不满意），而是数学上满足所有人约束的最优解，并且每个人能看到自己的满意度打分。对比冲击：微信群里"吃哈哈哈吃啥讨论 30 分钟 → 拼桌 5 分钟搞定"。

### 9.3 Demo #3：「氛围搜索」— vibe-match 的感知匹配

评委看到的：用户不说"找酒吧"，而是说"想安静待着，有点爵士乐，适合一个人"。AI 返回的不是"酒吧列表"，而是"氛围最匹配的 3 个地方"，带着 8 维氛围雷达图。对比冲击：大众点评搜"酒吧" = 按评分排序，你不知道进去之后是安静还是吵闹。vibe-match = 你描述感觉，AI 帮你找感受匹配的地方。

---

## 10. 与 v1 知否的关键差异

| 维度 | v1 知否 | v2 逛 |
|---|---|---|
| 身份 | 平台（6 层架构） | 5 个 OpenClaw Skill |
| 与 OpenClaw 关系 | OpenClaw 是其中一层 | 完全运行在 OpenClaw 内 |
| 核心创新 | 主动推送（ProactiveSensing） | 新鲜度排序 + 约束求解 + 氛围匹配 |
| 交互范式 | 推送式（服务器人） | 感知式（环境即接口） |
| 技术深度 | 概念多实现少 | 3 个可运行的算法引擎（有伪代码） |
| Demo 效果 | 需要 6 层架构图解释 | 3 分钟内体验即明白 |
| 赛题合规 | 形式合规，实质跑偏 | 严格按 SKILL.md 规范，每个 Skill 独立可装 |
| 可行性 | 12 周，5 人团队 | 2-3 天黑客松可 Demo |

---

## 11. 赛题合规自检

| 赛题要求 | 达成 | 证据 |
|---|---|---|
| 基于 OpenClaw 框架 + 版本说明 | ✅ | 基于 openclaw/openclaw main 分支（2026-06），§3.1 |
| Skill 含 SKILL.md + 实现代码 | ✅ | 5 个 Skill 各有 SKILL.md + scripts/ + mock_data/，§3.2 |
| ≥3 个本地生活核心 Skill | ✅ | street-scan（餐饮+发现）+ pin-zhuo（社交+餐饮）+ vibe-match（娱乐），§4-6 |
| 无真实用户信息 | ✅ | 全部 Mock POI + 3 个虚拟画像 + 显式输入，§8 |
| 展示 NL 对话如何改变 App 交互 | ✅ | 三个 Demo 分别展示：伴随发现/约束求解/氛围搜索，§9 |

---

## 12. 评委 QA 预案

| 问题 | 回答 |
|---|---|
| 这和美团搜索有什么区别？ | 美团搜索是"你告诉它你要什么"，逛是"你只管走，它告诉你路上有什么好玩的"。本质区别：搜索 vs 发现。 |
| 新鲜度排序会不会推坏店？ | 新鲜度是 45% 权重，还有 25% 的上下文匹配度。而且用户可以说"这家不好"，taste-log 会记住。 |
| 约束求解和投票有什么区别？ | 投票是多数暴力——3 个人想吃辣，2 个人讨厌就被否决了。约束求解是找满足所有人的解，没有人被牺牲。 |
| 氛围向量怎么标注？ | Mock 阶段人工标注 80 个 POI，生产阶段可以从大众点评中用 LLM 自动提取。 |
| 为什么不做主动推送？ | v1 试过了，发现主动推送的工程复杂度巨大（静默时段/频次控制/反打扰），且容易变成垃圾通知，选择的是"用户主动开启，AI 被动响应"的模式，体验更可控。 |
| 这些 Skill 能独立使用吗？ | 可以，每个 Skill 有自己的 SKILL.md + CLI + 数据，哪一个都能单独一用，组合使用效果更好（飞轮效应），但不强制。 |
