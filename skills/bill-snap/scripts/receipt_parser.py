"""Receipt parser + AA calculator for bill-snap."""
from __future__ import annotations
import json
import math
from pathlib import Path

MOCK_RECEIPTS = {
    "rcpt_001": {
        "id": "rcpt_001",
        "restaurant": "胡同里·新京菜",
        "date": "2026-06-07",
        "items": [
            {"id": "item_1", "name": "宫保鸡丁", "price": 58, "qty": 1},
            {"id": "item_2", "name": "京酱肉丝", "price": 48, "qty": 1},
            {"id": "item_3", "name": "糊塌里脊", "price": 52, "qty": 1},
            {"id": "item_4", "name": "干炸丸子", "price": 38, "qty": 1},
            {"id": "item_5", "name": "拍黄瓜", "price": 18, "qty": 1},
            {"id": "item_6", "name": "米饭 x5", "price": 15, "qty": 1},
            {"id": "item_7", "name": "燕京啤酒 x3", "price": 30, "qty": 1},
            {"id": "item_8", "name": "橙汁 x2", "price": 24, "qty": 1},
        ],
        "subtotal": 283,
        "service_charge": 0,
        "discount": 0,
        "total": 283,
    },
    "rcpt_002": {
        "id": "rcpt_002",
        "restaurant": "泰式船面",
        "date": "2026-06-06",
        "items": [
            {"id": "item_1", "name": "冬阴功汤", "price": 68, "qty": 1},
            {"id": "item_2", "name": "绿咖喱鸡", "price": 55, "qty": 1},
            {"id": "item_3", "name": "芒果糯米饭", "price": 32, "qty": 2},
            {"id": "item_4", "name": "泰式奶茶", "price": 22, "qty": 3},
            {"id": "item_5", "name": "菠萝炒饭", "price": 45, "qty": 1},
        ],
        "subtotal": 298,
        "service_charge": 30,
        "discount": 28,
        "total": 300,
    },
    "rcpt_003": {
        "id": "rcpt_003",
        "restaurant": "暗室 Darkroom",
        "date": "2026-06-07",
        "items": [
            {"id": "item_1", "name": "山崎12年", "price": 128, "qty": 1},
            {"id": "item_2", "name": "Old Fashioned", "price": 88, "qty": 2},
            {"id": "item_3", "name": "Mojito", "price": 68, "qty": 1},
            {"id": "item_4", "name": "薯条拼盘", "price": 48, "qty": 1},
            {"id": "item_5", "name": "芝士拼盘", "price": 88, "qty": 1},
        ],
        "subtotal": 508,
        "service_charge": 51,
        "discount": 0,
        "total": 559,
    },
}


def parse_receipt(receipt_id: str) -> dict:
    if receipt_id in MOCK_RECEIPTS:
        receipt = MOCK_RECEIPTS[receipt_id]
        return {
            "status": "parsed",
            "receipt": receipt,
            "item_count": len(receipt["items"]),
            "message": f"已解析「{receipt['restaurant']}」账单，共 {len(receipt['items'])} 项，合计 ¥{receipt['total']}",
        }
    return {"status": "not_found", "message": f"未找到账单 {receipt_id}"}


def split_equal(receipt_id: str, members: list[str]) -> dict:
    if receipt_id not in MOCK_RECEIPTS:
        return {"status": "not_found"}
    receipt = MOCK_RECEIPTS[receipt_id]
    total = receipt["total"]
    n = len(members)
    per_person = math.ceil(total / n)
    remainder = per_person * n - total

    splits = {}
    for i, m in enumerate(members):
        amount = per_person if i > 0 else per_person - remainder
        splits[m] = {"amount": amount, "items": "均摊"}

    return {
        "status": "split",
        "mode": "equal",
        "receipt_id": receipt_id,
        "restaurant": receipt["restaurant"],
        "total": total,
        "member_count": n,
        "per_person": per_person,
        "splits": splits,
        "message": f"「{receipt['restaurant']}」¥{total} 均分 {n} 人，每人 ¥{per_person}",
    }


def split_itemized(receipt_id: str, members: list[str],
                   assignments: dict[str, list[str]]) -> dict:
    if receipt_id not in MOCK_RECEIPTS:
        return {"status": "not_found"}
    receipt = MOCK_RECEIPTS[receipt_id]
    item_map = {item["id"]: item for item in receipt["items"]}

    splits = {m: {"amount": 0, "items": []} for m in members}
    assigned_total = 0

    for member, item_ids in assignments.items():
        if member not in splits:
            splits[member] = {"amount": 0, "items": []}
        for iid in item_ids:
            if iid in item_map:
                item = item_map[iid]
                splits[member]["amount"] += item["price"]
                splits[member]["items"].append(item["name"])
                assigned_total += item["price"]

    shared = receipt["total"] - assigned_total
    if shared > 0:
        per_person_shared = math.ceil(shared / len(members))
        for m in splits:
            splits[m]["amount"] += per_person_shared
            splits[m]["items"].append(f"公共费用均摊 ¥{per_person_shared}")

    return {
        "status": "split",
        "mode": "itemized",
        "receipt_id": receipt_id,
        "restaurant": receipt["restaurant"],
        "total": receipt["total"],
        "splits": splits,
        "shared_cost": shared,
    }


def get_balance(group_id: str) -> dict:
    return {
        "group_id": group_id,
        "total_receipts": 2,
        "balances": {
            "alice": {"paid": 283, "should_pay": 200, "balance": 83},
            "bob": {"paid": 0, "should_pay": 150, "balance": -150},
            "charlie": {"paid": 300, "should_pay": 233, "balance": 67},
        },
        "settlements": [
            {"from": "bob", "to": "alice", "amount": 83},
            {"from": "bob", "to": "charlie", "amount": 67},
        ],
        "message": "bob 需转 ¥83 给 alice，¥67 给 charlie",
    }
