#!/usr/bin/env python3
"""逛 Guang — 交互式 Demo 演示脚本
模拟 IM 聊天界面，底层调用真实 skill 引擎。
用法: python3 demo.py
"""
import json
import os
import sys
import time
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(BASE_DIR, "skills")

# — 终端颜色 ————————————————————————————

BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
GREEN = "\033[38;5;114m"
BLUE = "\033[38;5;111m"
CYAN = "\033[38;5;80m"
YELLOW = "\033[38;5;222m"
MAGENTA = "\033[38;5;176m"
WHITE = "\033[38;5;255m"
GRAY = "\033[38;5;245m"
RED = "\033[38;5;203m"
BG_DARK = "\033[48;5;236m"
BAR_FULL = "●"
BAR_EMPTY = "○"


# — 工具函数 ————————————————————————————

def term_width():
    return shutil.get_terminal_size((80, 24)).columns


def clear():
    os.system("clear")


def type_print(text, delay=0.025, color=""):
    """逐字打印，模拟打字效果"""
    for ch in text:
        sys.stdout.write(f"{color}{ch}{RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    print()


def type_print_fast(text, color=""):
    type_print(text, delay=0.012, color=color)


def pause(msg=""):
    """等待用户按回车继续"""
    hint = msg or f"{DIM}按 Enter 继续...{RESET}"
    input(hint)


def separator():
    w = min(term_width(), 70)
    print(f"{GRAY}{'—' * w}{RESET}")


def print_header(title):
    w = min(term_width(), 70)
    print()
    print(f"{CYAN}{BOLD}{'=' * w}{RESET}")
    padding = (w - len(title) * 2) // 2
    print(f"{CYAN}{BOLD}{' ' * max(0, padding)}{title}{RESET}")
    print(f"{CYAN}{BOLD}{'=' * w}{RESET}")
    print()


def msg_user(name, text):
    """用户消息 (右对齐风格，绿色) """
    print(f"  {GREEN}{BOLD}{name}{RESET}  {GREEN}{text}{RESET}")
    print()


def msg_ai(text, typing_delay=0.015):
    """AI 回复（蓝色，带打字效果）"""
    print(f"  {BLUE}{BOLD}逛{RESET} ", end="")
    for ch in text:
        sys.stdout.write(f"{WHITE}{ch}{RESET}")
        sys.stdout.flush()
        time.sleep(typing_delay)
    print()
    print()


def msg_ai_block(lines):
    """AI 回复多行内容（无打字效果，直接输出）"""
    print(f"  {BLUE}{BOLD}逛{RESET}")
    for line in lines:
        print(f"    {WHITE}{line}{RESET}")
    print()


def msg_system(text):
    """系统提示"""
    print(f"  {GRAY}[ {text} ]{RESET}")
    print()


def msg_private(name, text):
    """私聊消息"""
    print(f"  {MAGENTA}(私聊) {BOLD}{name}{RESET}  {MAGENTA}{text}{RESET}")
    print()


def radar_bar(label_left, label_right, value, width=20):
    """生成一个氛围维度的可视化条"""
    filled = round(value * width)
    bar = f"{CYAN}{BAR_FULL}{RESET}" * filled + f"{GRAY}{BAR_EMPTY}{RESET}" * (width - filled)
    return f"    {GRAY}{label_left:>4s}{RESET} {bar} {GRAY}{label_right}{RESET}"


# — 调用 Skill 脚本 ————————————————————————————

def run_skill(skill_name, *args):
    script = os.path.join(SKILLS_DIR, skill_name, "scripts",
                          skill_name.replace("-", ""))
    if skill_name == "street-scan":
        script = os.path.join(SKILLS_DIR, "street-scan", "scripts", "streetscan")
    elif skill_name == "vibe-match":
        script = os.path.join(SKILLS_DIR, "vibe-match", "scripts", "vibematch")
    elif skill_name == "pin-zhuo":
        script = os.path.join(SKILLS_DIR, "pin-zhuo", "scripts", "pinzhuo")
    elif skill_name == "bill-snap":
        script = os.path.join(SKILLS_DIR, "bill-snap", "scripts", "billsnap")
    elif skill_name == "taste-log":
        script = os.path.join(SKILLS_DIR, "taste-log", "scripts", "tastelog")

    cmd = [sys.executable, script] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=os.path.dirname(script))
    if result.returncode != 0:
        return {"error": result.stderr}
    return json.loads(result.stdout)


#
#  Demo 1: 街探 — 下班溜达
#

def demo_street_scan():
    print_header("Demo 1 · 街探 — 下班溜达")

    msg_system("场景: 周五傍晚 6 点，小赵下班了，在中关村附近")
    pause()

    msg_user("小赵", "下班了，溜达溜达~")
    time.sleep(0.5)

    msg_ai("好嘞！已开启逛街模式 ↑ ")
    time.sleep(0.3)
    msg_ai("正在扫描你周围 500 米的惊喜...")

    time.sleep(0.8)
    msg_system(">>> skill: street-scan drift --lat 39.9809 --lng 116.3060 --heading 东北 --radius 500 --hour 18")
    data = run_skill("street-scan", "drift",
                     "--lat", "39.9809", "--lng", "116.3060",
                     "--heading", "东北", "--radius", "500",
                     "--hour", "18", "--user", "mock_user_zhao")

    recs = data.get("recommendations", [])
    if recs:
        r = recs[0]
        poi = r["poi"]
        lines = [
            f"",
            f"{YELLOW}{BOLD}┌──────────────────────────────────────{RESET}",
            f"{YELLOW}{BOLD}│{RESET}  {CYAN}前方 {poi['distance_m']} 米{RESET} · {BOLD}{poi['name']}{RESET} · {poi['category']}",
            f"{YELLOW}{BOLD}│{RESET} {r['why']}",
            f"{YELLOW}{BOLD}│{RESET} {DIM}人均 ¥{poi['avg_price']}{RESET}",
            f"{YELLOW}{BOLD}│{RESET} {DIM}↑ {r['walk']}{RESET}",
            f"{YELLOW}{BOLD}│{RESET} {DIM}新鲜度: {CYAN}{'★' * round(r['novelty_score'] * 5)}{'☆' * (5 - round(r['novelty_score'] * 5))}{RESET}",
            f"{YELLOW}{BOLD}└──────────────────────────────────────{RESET}",
        ]
        msg_ai_block(lines)
    pause()

    # 继续走
    msg_user("小赵", "有意思，继续走走看")
    time.sleep(0.5)

    msg_ai("继续往前走...")
    time.sleep(0.5)

    # 模拟位置变化
    msg_system(">>> skill: street-scan drift --lat 39.9835 --lng 116.3100 --radius 600 --hour 18")
    data2 = run_skill("street-scan", "drift",
                      "--lat", "39.9835", "--lng", "116.3100",
                      "--radius", "600", "--hour", "18",
                      "--user", "mock_user_zhao")

    recs2 = data2.get("recommendations", [])
    for r in recs2[:2]:
        poi = r["poi"]
        lines = [
            f"",
            f"{YELLOW}{BOLD}┌──────────────────────────────────────{RESET}",
            f"{YELLOW}{BOLD}│{RESET}  {CYAN}前方 {poi['distance_m']} 米{RESET} · {BOLD}{poi['name']}{RESET} · {poi['category']}",
            f"{YELLOW}{BOLD}│{RESET} {r['why']}",
            f"{YELLOW}{BOLD}│{RESET} {DIM}↑ {r['walk']}{RESET}",
            f"{YELLOW}{BOLD}│{RESET} {DIM}新鲜度: {CYAN}{'★' * round(r['novelty_score'] * 5)}{'☆' * (5 - round(r['novelty_score'] * 5))}{RESET}",
            f"{YELLOW}{BOLD}└──────────────────────────────────────{RESET}",
        ]
        msg_ai_block(lines)
    pause()

    # 用户反馈
    if recs:
        poi_name = recs[0]["poi"]["name"]
        poi_id = recs[0]["poi"]["id"]
        msg_user("小赵", f"刚去了{poi_name}, 8 分，味道不错！")
        time.sleep(0.5)

        msg_system(f">>> skill: taste-log log --user mock_user_zhao --poi-id {poi_id} --score 8 --note 味道不错 --category {recs[0]['poi']['category']}")
        run_skill("taste-log", "log",
                  "--user", "mock_user_zhao",
                  "--poi-id", poi_id,
                  "--score", "8",
                  "--note", "味道不错",
                  "--poi-name", poi_name,
                  "--category", recs[0]["poi"]["category"])

        msg_ai(f"已记住！你给《{poi_name}》打了 8 分 ✓")
        msg_ai("下次推荐会参考你的口味偏好~")

    pause()
    separator()


#
#  Demo 2: 拼桌 — 5 人聚餐
#

def demo_pin_zhuo():
    print_header("Demo 2 · 拼桌 — 5 人聚餐")

    msg_system("场景: 周末聚餐，5 个人在群里讨论吃什么")
    pause()

    msg_user("小赵", "周末 5 个人聚餐，帮我们拼桌！")
    time.sleep(0.5)

    msg_ai("好的！我来私聊每个人收集约束，不会泄露个人偏好 🌑 ")

    # 创建会话
    msg_system(">>> skill: pin-zhuo start --group-id demo_grp --members 小赵,小钱,小孙,张三,李四 --date 2026-06-08")
    run_skill("pin-zhuo", "start",
              "--group-id", "demo_grp",
              "--members", "小赵,小钱,小孙,张三,李四",
              "--date", "2026-06-08")

    time.sleep(0.5)
    separator()

    # 私聊收集约束
    members_data = [
        ("小赵", "60 以内吧，不吃香菜，我在海淀",
         {"member": "小赵", "location": "海淀", "budget_max": "60",
          "dietary_exclude": "香菜", "cuisine_prefer": ""}),
        ("小钱", "预算 80，花生过敏！我从徐汇过来",
         {"member": "小钱", "location": "徐汇", "budget_max": "80",
          "dietary_exclude": "花生", "cuisine_prefer": ""}),
        ("小孙", "随意，200 以内都行，我在朝阳",
         {"member": "小孙", "location": "朝阳", "budget_max": "200",
          "dietary_exclude": "", "cuisine_prefer": ""}),
        ("张三", "100 以内，不吃海鲜，我在西城",
         {"member": "张三", "location": "西城", "budget_max": "100",
          "dietary_exclude": "海鲜", "cuisine_prefer": ""}),
        ("李四", "80 吧，啥都能吃，我在东城",
         {"member": "李四", "location": "东城", "budget_max": "80",
          "dietary_exclude": "", "cuisine_prefer": ""}),
    ]

    for name, reply, params in members_data:
        msg_private(f"逛 → {name}", "你好！帮大家拼桌，请告诉我: 预算? 忌口? 你在哪？")
        time.sleep(0.3)
        msg_private(name, reply)
        time.sleep(0.2)

        args_list = ["constrain", "--group-id", "demo_grp"]
        for k, v in params.items():
            args_list.extend([f"--{k.replace('_', '-')}", v])

        run_skill("pin-zhuo", *args_list)
        msg_private(f"逛 → {name}", f"收到！{name}的约束已记录 ✓")
        time.sleep(0.2)

    separator()
    pause()

    # 求解
    msg_ai("所有人的约束已收集完毕，正在计算最优方案...")
    time.sleep(0.5)

    msg_system(">>> skill: pin-zhuo solve --group-id demo_grp")
    result = run_skill("pin-zhuo", "solve", "--group-id", "demo_grp")

    solutions = result.get("solutions", [])
    if solutions:
        for i, sol in enumerate(solutions[:3]):
            r = sol["restaurant"]
            lines = [
                f"",
                f"{YELLOW}{BOLD}┌── 方案 {'ABC'[i]} ──────────────────────────{RESET}",
                f"{YELLOW}{BOLD}│{RESET} {BOLD}{r['name']}{RESET} · {r.get('cuisine', '')} · 人均 ¥{r['avg_price']}",
            ]
            for member, info in sol["satisfaction"].items():
                pct = int(info["score"] * 100)
                bar_len = pct // 5
                bar = f"{GREEN}{'█' * bar_len}{GRAY}{'░' * (20 - bar_len)}{RESET}"
                constraints = ""
                if info.get("stretched"):
                    constraints = f" {DIM}({'; '.join(info['stretched'][:1])}){RESET}"
                lines.append(
                    f"{YELLOW}{BOLD}│{RESET}  {member}: {bar} {pct}%{constraints}"
                )
            why_text = " + ".join(sol.get("why", []))
            lines.append(f"{YELLOW}{BOLD}│{RESET}  {DIM}推荐理由: {why_text}{RESET}")
            lines.append(f"{YELLOW}{BOLD}└──────────────────────────────────────{RESET}")
            msg_ai_block(lines)

        msg_ai(f"共找到 {result.get('total_feasible', 0)} 家满足所有人约束的餐厅，以上是最优的 {len(solutions[:3])} 个方案。")
        msg_ai("公平性原则：让最不满意的人也尽量满意，没有人被牺牲 ✓")

    pause()
    separator()


#
#  Demo 3: 心流 — 氛围搜索
#

def demo_vibe_match():
    print_header("Demo 3 · 心流 — 用感觉找地方")

    msg_system("场景: 周五晚上，想找个地方安静待着")
    pause()

    msg_user("小赵", "想安静待着，有点爵士乐，适合一个人")
    time.sleep(0.5)

    msg_ai("正在按氛围向量匹配最合适的地方...")
    time.sleep(0.5)

    msg_system('>>> skill: vibe-match query --text "安静，爵士，一个人" --lat 39.9809 --lng 116.3060 --hour 21')
    data = run_skill("vibe-match", "query",
                     "--text", "安静，爵士，一个人",
                     "--lat", "39.9809", "--lng", "116.3060",
                     "--hour", "21")

    # 显示解析出的氛围向量
    parsed = data.get("parsed_vibe", {})
    dim_labels = {
        "noise_level": ("安静", "喧闹"),
        "light": ("昏暗", "明亮"),
        "crowd_density": ("清静", "拥挤"),
        "social_vibe": ("独处", "社交"),
        "energy": ("放松", "活力"),
        "aesthetic": ("粗犷", "精致"),
        "outdoor_ratio": ("室内", "户外"),
    }

    radar_lines = [
        f"",
        f"  {BOLD}你想要的氛围: {RESET}",
    ]
    for dim in ["noise_level", "light", "crowd_density", "social_vibe", "energy", "aesthetic", "outdoor_ratio"]:
        val = parsed.get(dim, 0.5)
        left, right = dim_labels.get(dim, ("低", "高"))
        radar_lines.append(radar_bar(left, right, val))
    radar_lines.append("")
    msg_ai_block(radar_lines)

    time.sleep(0.3)

    matches = data.get("matches", [])
    if matches:
        m = matches[0]
        v = m["venue"]
        lines = [
            f"",
            f"{YELLOW}{BOLD}┌──────────────────────────────────────{RESET}",
            f"{YELLOW}{BOLD}│{RESET}  {CYAN}匹配 TOP 1{RESET} · {BOLD}{v['name']}{RESET} · {v.get('type', '')}",
            f"{YELLOW}{BOLD}│{RESET} {GREEN}{BOLD}匹配度 {m['match_pct']}{RESET}",
            f"{YELLOW}{BOLD}│{RESET}",
        ]
        if v.get("signature"):
            lines.append(f"{YELLOW}{BOLD}│{RESET}  {v['signature']}")
        if v.get("music"):
            lines.append(f"{YELLOW}{BOLD}│{RESET}  {DIM}音乐: {v['music']}{RESET}")

        # 维度匹配
        dim_match = m.get("dim_match", [])
        match_str = " ".join(dim_match[:5])
        lines.append(f"{YELLOW}{BOLD}│{RESET}  {DIM}{match_str}{RESET}")

        if m.get("distance_m"):
            lines.append(f"{YELLOW}{BOLD}│{RESET}  {DIM}距你 {m['distance_m']/1000:.1f}km{RESET}")
        lines.append(f"{YELLOW}{BOLD}└──────────────────────────────────────{RESET}")
        msg_ai_block(lines)

        # 显示 TOP 2, 3
        for m2 in matches[1:3]:
            v2 = m2["venue"]
            print(f"    {DIM}#{m2['rank']} {v2['name']} · {v2.get('type', '')} · 匹配度 {m2['match_pct']}{RESET}")
        print()

        pause()

    # 调整氛围
    msg_user("小赵", "再热闹一点呢？适合朋友一起的")
    time.sleep(0.5)

    msg_ai("好的，调整氛围向量...")
    time.sleep(0.5)

    msg_system('>>> skill: vibe-match query --text "热闹，朋友，有酒，音乐" --lat 39.9809 --lng 116.3060 --hour 21')
    data2 = run_skill("vibe-match", "query",
                      "--text", "热闹，朋友，有酒，音乐",
                      "--lat", "39.9809", "--lng", "116.3060",
                      "--hour", "21")

    matches2 = data2.get("matches", [])
    if matches2:
        m = matches2[0]
        v = m["venue"]
        lines = [
            f"",
            f"{YELLOW}{BOLD}┌──────────────────────────────────────{RESET}",
            f"{YELLOW}{BOLD}│{RESET}  {CYAN}氛围调整后 TOP 1{RESET} · {BOLD}{v['name']}{RESET} · {v.get('type', '')}",
            f"{YELLOW}{BOLD}│{RESET} {GREEN}{BOLD}匹配度 {m['match_pct']}{RESET}",
            f"{YELLOW}{BOLD}│{RESET}  {v.get('signature', '')}",
            f"{YELLOW}{BOLD}│{RESET}  {DIM}距你 {m.get('distance_m', 0)/1000:.1f}km{RESET}",
            f"{YELLOW}{BOLD}└──────────────────────────────────────{RESET}",
        ]
        msg_ai_block(lines)

    msg_ai("不是在搜索—是在用感觉找到一个地方 ✓")

    pause()
    separator()


#
#  Demo 4: 拍账 — 聚餐 AA
#

def demo_bill_snap():
    print_header("Demo 4 · 拍账 — 聚餐后一键 AA")

    msg_system("场景: 聚餐结束，小赵拍了账单")
    pause()

    msg_user("小赵", "[拍照] 帮我们 AA 一下")
    time.sleep(0.5)

    msg_ai("正在解析账单...")
    time.sleep(0.5)

    msg_system(">>> skill: bill-snap parse --receipt-id rcpt_001")
    receipt = run_skill("bill-snap", "parse", "--receipt-id", "rcpt_001")

    r = receipt.get("receipt", {})
    items = r.get("items", [])
    lines = [
        f"",
        f"  {BOLD}║  {r.get('restaurant', '')}{RESET}",
        f"  {DIM}{r.get('date', '')}{RESET}",
        f"  {'─' * 36}",
    ]
    for item in items:
        lines.append(f"  {item['name']:<20s} ¥{item['price']}")
    lines.append(f"  {'─' * 36}")
    lines.append(f"  {BOLD}合计 ¥{r.get('total', 0)}{RESET}")
    lines.append("")
    msg_ai_block(lines)

    time.sleep(0.3)

    msg_system(">>> skill: bill-snap split --receipt-id rcpt_001 --members 小赵,小钱,小孙 --mode equal")
    split = run_skill("bill-snap", "split",
                      "--receipt-id", "rcpt_001",
                      "--members", "小赵,小钱,小孙",
                      "--mode", "equal")

    lines = [
        f"",
        f"{YELLOW}{BOLD}┌──────────────────────────────────────{RESET}",
        f"{YELLOW}{BOLD}│{RESET} {GREEN}{BOLD}{split.get('message', '')}{RESET}",
        f"{YELLOW}{BOLD}│{RESET}",
    ]
    for name, info in split.get("splits", {}).items():
        lines.append(f"{YELLOW}{BOLD}│{RESET}  {name}: ¥{info['amount']}")
    lines.append(f"{YELLOW}{BOLD}└──────────────────────────────────────{RESET}")
    msg_ai_block(lines)

    msg_ai("不复杂，但省掉了每次聚餐后 10 分钟的心算时间 ✓")

    pause()
    separator()


#
#  Demo 5: 飞轮效应展示
#

def demo_flywheel():
    print_header("飞轮效应 — 五个 Skill 如何协同")

    lines = [
        "",
        f"  {BOLD}每个 Skill 独立可用，组合使用形成飞轮: {RESET}",
        "",
        f"    {CYAN}记味{RESET} 沉淀偏好，",
        f"    ↓",
        f"    {CYAN}街探{RESET} 推荐更准（知道你喜欢什么、没试过什么）",
        f"    ↓",
        f"    {CYAN}拼桌{RESET} 约束求解时用上所有人画像",
        f"    ↓",
        f"    {CYAN}心流{RESET} 氛围匹配考虑历史偏好",
        f"    ↓",
        f"    {CYAN}拍账{RESET} 完成消费闭环",
        f"    ↓",
        f"    {CYAN}记味{RESET} 记录本次体验 → 循环",
        "",
    ]
    msg_ai_block(lines)

    # 展示记味积累的画像
    msg_system(">>> skill: taste-log profile --user mock_user_zhao")
    profile = run_skill("taste-log", "profile", "--user", "mock_user_zhao")

    cats = profile.get("categories", {})
    if cats:
        lines = [
            f"",
            f"  {BOLD}小赵的味觉图谱（记味积累）: {RESET}",
            "",
        ]
        for cat, info in cats.items():
            score = info.get("avg_score", 0)
            count = info.get("count", 0)
            bar_len = round(score * 2)
            bar = f"{GREEN}{'█' * bar_len}{GRAY}{'░' * (20 - bar_len)}{RESET}"
            keywords = info.get("keywords", [])
            kw_str = f" {DIM}({', '.join(keywords[:3])}){RESET}" if keywords else ""
            lines.append(f"   {cat}: {bar} {score}分 · {count}次{kw_str}")
        lines.append("")
        msg_ai_block(lines)

    msg_ai("这个图谱就是飞轮的燃料——你吃得越多，评价越多，推荐就越懂你。")

    pause()
    separator()


#
#  主流程
#

def show_intro():
    clear()
    w = min(term_width(), 70)
    print()
    print(f"{CYAN}{BOLD}{'=' * w}{RESET}")
    print()

    title = "逛 Guang"
    padding = (w - len(title) * 2) // 2
    print(f"{'  ' * max(0, padding)}{CYAN}{BOLD}{title}{RESET}")
    print()

    subtitle = "城市即兴体验引擎"
    padding2 = (w - len(subtitle) * 2) // 2
    print(f"{'  ' * max(0, padding2)}{WHITE}{subtitle}{RESET}")
    print()

    tagline = "不做攻略，直接逛。把你的 IM 变成城市的第六感。"
    padding3 = (w - len(tagline) * 2) // 2
    print(f"{'  ' * max(0, padding3)}{DIM}{tagline}{RESET}")
    print()
    print(f"{CYAN}{BOLD}{'=' * w}{RESET}")
    print()

    skills_info = [
        ("🗺 街探", "走到哪，推到哪"),
        ("🍽 拼桌", "5 个人吃饭不吵架"),
        ("🎵 心流", "说氛围，不说品类"),
        ("📷 拍账", "拍一下，AA 好了"),
        ("📝 记味", "吃完说一句，AI 记住你"),
    ]
    for emoji_name, desc in skills_info:
        print(f"   {CYAN}{emoji_name:<10s}{RESET}  {WHITE}{desc}{RESET}")
    print()

    separator()
    print()
    pause(f"  {DIM}按 Enter 开始 Demo 演示...{RESET}")


def show_outro():
    print_header("Demo 结束")
    lines = [
        "",
        f"  {BOLD}核心观点: {RESET}",
        "",
        f"    美团/点评在做「搜索引擎」— 帮你在已知需求中找最优解",
        f"    逛在做「发现引擎」— 帮你发现你不知道自己会喜欢的东西",
        "",
        "",
        f"  {BOLD}技术亮点: {RESET}",
        "",
        f"    · 新鲜度优先排序  f(新鲜度×0.45，意外度×0.30，场景×0.25)",
        f"    · CSP 约束求解 + 帕累托优化，公平性 = 最不满意的人有多满意",
        f"    · B 维氛围向量空间 + 余弦相似度匹配",
        f"    · 完全运行在 OpenClaw 框架上",
        "",
        "",
        f"  {DIM}所有数据为 Mock 数据，零真实用户信息{RESET}",
        "",
    ]
    msg_ai_block(lines)


def main():
    show_intro()

    try:
        demo_street_scan()
        demo_pin_zhuo()
        demo_vibe_match()
        demo_bill_snap()
        demo_flywheel()
        show_outro()
    except KeyboardInterrupt:
        print(f"\n\n{DIM}Demo 已中断{RESET}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
