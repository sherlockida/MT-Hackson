# 逛 Guàng — 城市即兴体验引擎

> 不做攻略，直接逛。把你的 IM 变成城市的第六感。

「逛」是一套运行在 [OpenClaw](https://github.com/openclaw/openclaw) 框架上的本地生活 Skill 套件。它不替你做决策，而是在你的 IM 对话中激发即兴体验——走到哪、玩到哪、吃到哪。

---

## 项目背景

美团黑客松 2026「基于OpenClaw的本地生活全天候私人管家」赛道参赛项目。

**核心洞察**：年轻人对本地生活 App 最大的吐槽不是"找不到好店"，而是**"做攻略太累了"**。打开美团比价、大众点评翻评论、小红书做攻略——花在"研究去哪"的时间，比"真正在玩"还长。这就是本地生活领域的头号体验杀手：**决策疲劳**。

**我们的答案**：如果根本不需要决策呢？你只管出门走，AI 在 IM 里告诉你路上有什么好玩的。

---

## 5 个 Skill

| Skill | 一句话 | 触发方式 |
|-------|--------|---------|
| 🗺 **street-scan 街探** | 走到哪，推到哪 | 群聊说"溜达溜达" |
| 🍽 **pin-zhuo 拼桌** | 5 个人吃饭不吵架 | 群聊说"周末聚餐" |
| 🎵 **vibe-match 心流** | 说氛围，不说品类 | "想找个安静的地方，有酒" |
| 📷 **bill-snap 拍账** | 拍一下，AA 好了 | 发账单照片 / 说"AA" |
| 📝 **taste-log 记味** | 吃完说一句，AI 记住你 | "这家 8 分，好吃" |

五个 Skill 独立可用，组合使用形成**飞轮**：记味沉淀偏好 → 街探推荐更准 → 拼桌用上所有人画像 → 体验后记味 → 循环。

---

## 快速开始

### 环境要求

- Python 3.9+
- SQLite 3
- OpenClaw 2026.6+

### 初始化

```bash
# 1. 初始化数据库
bash init_db.sh

# 2. 运行 Demo（交互式 IM 模拟）
python demo.py
```

### 单个 Skill CLI 测试

```bash
# 街探：查看周围推荐
cd skills/street-scan/scripts && python streetscan drift --lat 39.9809 --lng 116.3060 --radius 500

# 拼桌：5 人聚餐求解
cd skills/pin-zhuo/scripts && python pinzhuo start --group-id grp_001 --members "小赵,小钱,小孙,张三,李四" --date 2026-06-08

# 心流：氛围搜索
cd skills/vibe-match/scripts && python vibematch query --text "想安静待着，有点爵士乐，适合一个人" --lat 39.9809 --lng 116.3060

# 拍账：解析收据
cd skills/bill-snap/scripts && python billsnap parse --receipt-id rcpt_001

# 记味：查看味觉画像
cd skills/taste-log/scripts && python tastelog profile --user mock_user_zhao
```

---

## 项目结构

```
逛/
├── demo.py                  # 交互式 Demo 脚本（5 个场景模拟）
├── PRODUCT.md               # 产品全景文档
├── proposal_v2.md           # Hackathon 提案文档
├── DIVISION_OF_LABOR.md     # 团队分工报告
├── init_db.sh               # 数据库一键初始化
├── init_db.sql              # SQL 建表脚本
├── data/
│   ├── user_profiles.json   # 3 个虚拟用户画像
│   ├── pinzhuo_sessions.db  # 拼桌会话数据库
│   └── taste_graph.db       # 味觉图谱数据库
└── skills/
    ├── common/              # 公共库（Haversine / 向量运算）
    ├── street-scan/         # 街探：SKILL.md + scripts/ + mock_data/
    ├── pin-zhuo/            # 拼桌：SKILL.md + scripts/ + mock_data/
    ├── vibe-match/          # 心流：SKILL.md + scripts/ + mock_data/
    ├── bill-snap/           # 拍账：SKILL.md + scripts/
    └── taste-log/           # 记味：SKILL.md + scripts/
```

---

## 核心创新

### 新鲜度优先排序（街探）

传统推荐按评分排，街探按「你没见过的程度」排：

```
score = 0.45 × 新鲜度 + 0.30 × 意外度 + 0.25 × 场景匹配
```

### CSP 约束求解（拼桌）

不用群投票，用数学求解。硬约束（忌口/过敏/预算）一票否决，软约束（距离/菜系）帕累托优化。公平性 = 最不满意的人有多满意。

### 8 维氛围向量匹配（心流）

不搜"酒吧"，描述感受。自然语言 → 8 维氛围向量 → 余弦相似度匹配。

---

## 数据声明

- 全部使用 Mock 数据，零真实用户信息
- 80 个虚构 POI、30 家餐厅、40 个场所、3 个虚拟用户画像
- 数据存储在本地 SQLite，一键清空

---

## 团队

- **肖珍佳**：产品策略 & 核心体验设计
- **徐梓乔**：工程规范 & 数据与集成

---

## 技术栈

Python 3.9+ · SQLite · OpenClaw SKILL.md 规范 · Haversine 空间计算 · CSP 约束求解 · 余弦相似度匹配
