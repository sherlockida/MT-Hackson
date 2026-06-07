# 逛 Guàng — 团队分工报告

> 项目：美团黑客松 2026「基建狂魔」赛道 — 基于 OpenClaw 的本地生活 Skill 开发
> 团队：肖珍佳、徐梓乔

---

## 分工总览

| 维度 | 肖珍佳 | 徐梓乔 |
|------|--------|--------|
| **角色** | 产品策略 & 核心体验设计 | 工程规范 & 数据与集成 |
| **主要产出** | 产品定位 + 3 核心 Skill 流程设计 + Demo 脚本 + 演示视频 | 5 个 Skill 规范对齐 + 2 增强 Skill 实现 + 数据库 + 飞书部署 |
| **核心贡献** | 产品从 0 到 1 的定义与验证 | 工程从设计到交付的落地与集成 |

---

## 肖珍佳：产品策略 & 核心体验设计

负责团队任务统筹与产品方向把控，带领团队完成从概念到验证的全流程。

### 1. 产品战略与定位

- 带领团队讨论并确立产品方向：从本地生活「决策疲劳」痛点出发，提出「感知式交互」范式，区别于传统的搜索式和推送式
- 设计产品核心主张——「不做攻略，直接逛」，确立了 3 核心（街探/拼桌/心流）+ 2 增强（拍账/记味）的 Skill 组合策略
- 撰写 PRODUCT.md：产品全景定位、Skill 能力矩阵、隐私设计原则、赛题合规论证

### 2. Skill 流程与功能设计

- 设计 **street-scan 街探**的交互流程：「用户开启逛街模式 → 位置感知 → 新鲜度优先推荐 → 反馈闭环」，定义三层新鲜度计算逻辑（店铺级/品类级/区域级）
- 设计 **pin-zhuo 拼桌**的多轮私聊流程：「群聊发起 → 逐一私聊收集约束 → CSP 求解 → 群内公布方案」，确立「公平性 > 效率」的帕累托优化原则
- 设计 **vibe-match 心流**的感知匹配流程：「自然语言描述氛围 → 8 维向量解析 → 余弦相似度匹配 → 维度级解释」，定义 8 维氛围空间（noise/light/crowd/social/energy/aesthetic/outdoor/time_fit）
- 设计 bill-snap 拍账与 taste-log 记味的功能边界与数据接口

### 3. 核心流程验证与演示

- 编写 demo.py（约 649 行）：实现 5 个 Demo 场景的交互式 IM 模拟，包括街探 drift（新鲜度推荐）、拼桌约束求解（满意度逐人展示）、心流氛围匹配（8 维雷达图可视化）、拍账 AA 分账、飞轮效应展示
- 设计并实现终端 UI 效果：逐字打印效果、多色终端格式化、氛围雷达可视化条
- 录制项目演示视频，展示完整用户体验闭环

### 4. 飞书 IM 集成测试

- 在飞书群聊中验证 5 个 Skill 的 @mention 触发与回复流程
- 验证拼桌私聊收集约束 → 群聊公布方案的多轮交互
- 验证街探位置感知、心流氛围搜索、拍账 AA 分账等场景的端到端可用性

---

## 徐梓乔：工程规范 & 数据与集成

负责将产品设计落地为符合 OpenClaw 规范的工程交付，并承担数据层与部署集成工作。

### 1. Skill 规范对齐与工程优化

- 对 5 个 Skill 的 SKILL.md 进行 OpenClaw 标准规范对齐：统一 YAML frontmatter 元数据格式（name/description/metadata.openclaw），配置 emoji、依赖声明、触发条件
- 完成跨 Skill 的接口一致性校验：确保所有 CLI 入口输出 JSON 格式统一，供 demo.py 和飞书 Agent 无缝调用
- 修复 Windows 环境下 Python 编码兼容性问题（GBK → UTF-8），将所有 SKILL.md 命令标准化为 `PYTHONIOENCODING=utf-8` 跨平台可执行格式
- 将 5 个 Skill 部署至 OpenClaw 全局 Skill 目录及 Workspace，配置符号链接，确保 Agent 正确发现并加载

### 2. 增强 Skill 实现

- 实现 **bill-snap 拍账**引擎（约 209 行 Python）：
  - receipt_parser.py：收据解析引擎，支持均摊分账（split_equal）与按明细分账（split_itemized）两种模式，含余额汇总查询
  - billsnap CLI：支持 parse / split / balance 三个子命令
- 实现 **taste-log 记味**引擎（约 304 行 Python）：
  - taste_graph.py：味觉图谱 CRUD 引擎，支持结构化记录（log_entry）、品类聚合画像（get_profile）、单品类深度查询（query_category）、逐条删除与一键清空（delete / clear）
  - tastelog CLI：支持 log / profile / query / export / delete / clear 六个子命令

### 3. 数据库设计与实现

- 设计并实现 SQLite 数据持久化方案：
  - pinzhuo_sessions.db：sessions 表 + constraints 表（含位置/预算/忌口/菜系偏好/时间段）
  - taste_graph.db：taste_entries 表 + taste_profile 表（含评分/标签/关键词聚合）
- 编写 init_db.sh（一键初始化脚本，65 行）与 init_db.sql（独立建表脚本，54 行）

### 4. OpenClaw 飞书通道部署

- 完成飞书 Bot 通道配置：AppID/AppSecret 配置、开放平台权限申请（im:message / im:chat）、WebSocket 事件订阅
- 完成 openclaw.json 通道参数配置（dmPolicy / groupPolicy / requireMention）
- 在飞书 IM 环境中完成 5 个 Skill 的端到端集成测试与调试

---

## 协作交叉点

| 协作事项 | 肖珍佳 | 徐梓乔 |
|---------|--------|--------|
| **飞轮效应数据流** | 定义 taste-log → street-scan / pin-zhuo 的消费接口 | 实现 taste_graph 数据层，保证输出格式匹配 |
| **SKILL.md 编写** | 编写 Skill 功能描述、触发条件、输出格式 | 对齐 OpenClaw YAML frontmatter 规范与元数据 |
| **飞书群聊测试** | 设计测试场景与验证标准 | 配置通道环境，联调排查 |
| **Demo 联调** | 编写 demo.py 交互脚本 | 确保 CLI 接口输出一致 |
| **赛题合规** | 确保产品层面满足赛题要求 | 确保工程层面符合 SKILL.md 规范 |

---

## 产出对比

| 产出类型 | 肖珍佳 | 徐梓乔 |
|---------|--------|--------|
| 产品文档 | PRODUCT.md | proposal_v2_compact.md |
| 核心代码 | demo.py（649行）+ 5 个 SKILL.md | bill-snap 引擎（209行）+ taste-log 引擎（304行） |
| 数据库 | — | init_db.sh + init_db.sql + SQLite schema |
| 部署集成 | — | OpenClaw 全局部署 + Feishu 通道配置 |
| 算法/流程设计 | street-scan / pin-zhuo / vibe-match 全流程 | 收据解析 + 味觉图谱 CRUD |
| 测试验证 | 核心流程验证 + 演示视频录制 | 跨平台编码兼容 + 飞书端到端测试 |

---

> 两人分工互补：肖珍佳负责产品从 0 到 1 的战略定义与体验验证，徐梓乔负责工程从设计到交付的规范落地与系统集成。双方在飞轮数据接口、SKILL.md 规范、飞书测试三个关键环节紧密协作，共同完成项目交付。
