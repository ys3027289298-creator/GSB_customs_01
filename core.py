"""海关核心逻辑：货物、税率、关区和查验。"""

import json

FIXED_DATE = "2026-09-29"
SAVE_FILE = "customs_save.json"

VIOLATION_PENALTY = 10
DEFAULT_CREDIT = 100
DEFAULT_ZONE_CAPACITY = 2


def new_game():
    return {
        "goods": {},
        "zone_load": 0,
        "zone_capacity": DEFAULT_ZONE_CAPACITY,
        "credit": DEFAULT_CREDIT,
        "decl_id": 0,
        "received": [],
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    state.setdefault("goods", {})
    state.setdefault("zone_load", 0)
    state.setdefault("zone_capacity", DEFAULT_ZONE_CAPACITY)
    state.setdefault("credit", DEFAULT_CREDIT)
    state.setdefault("decl_id", 0)
    state.setdefault("received", [])
    return state


def _get_goods(state, goods_id):
    return state.get("goods", {}).get(goods_id)


def declare(state, goods_id, value, banned):
    if not goods_id or goods_id in state["goods"]:
        return False
    try:
        value = int(value)
    except (TypeError, ValueError):
        return False
    if value < 0:
        return False
    state["decl_id"] += 1
    state["goods"][goods_id] = {
        "decl_no": state["decl_id"],
        "value": value,
        "banned": bool(banned),
        "cleared": False,
        "held": False,
        "defect": False,
    }
    return True


def clear(state, goods_id):
    goods = _get_goods(state, goods_id)
    if goods is None:
        return False
    if goods.get("banned"):
        return False
    goods["cleared"] = True
    return True


def tax(state, goods_id):
    goods = _get_goods(state, goods_id)
    if goods is None:
        return None
    return goods["value"]


def inspect(state, goods_id):
    goods = _get_goods(state, goods_id)
    if goods is None:
        return False
    if goods.get("defect"):
        return False
    goods["held"] = True
    return True


def cancel_inspect(state, goods_id):
    goods = _get_goods(state, goods_id)
    if goods is None:
        return False
    goods.pop("held", None)
    return True


def receive(state, goods_id):
    goods = _get_goods(state, goods_id)
    if goods is not None and goods.get("banned"):
        return False
    if goods_id in state["received"]:
        return False
    if state["zone_load"] >= state["zone_capacity"]:
        return False
    state["zone_load"] += 1
    state["received"].append(goods_id)
    return True


def violation(state):
    state["credit"] -= VIOLATION_PENALTY
    return state["credit"]


def main():
    state = new_game()
    print("海关 %s - 命令: declare/clear/tax/inspect/cancel/receive/violation/save/quit" % FIXED_DATE)
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            print("err: 空命令")
            continue
        if raw == "quit":
            break
        parts = raw.split()
        cmd = parts[0]
        args = parts[1:]
        if cmd == "declare":
            if len(args) != 3:
                print("err: 用法 declare <货物> <价值> <banned:true|false>")
                continue
            gid, val, ban = args
            ok = declare(state, gid, val, ban == "true")
            print("ok" if ok else "err: 申报失败（重复编号/非法价值）")
        elif cmd == "clear":
            if len(args) != 1:
                print("err: 用法 clear <货物>")
                continue
            print("ok" if clear(state, args[0]) else "err: 放行失败（禁运品或未申报）")
        elif cmd == "tax":
            if len(args) != 1:
                print("err: 用法 tax <货物>")
                continue
            amount = tax(state, args[0])
            print(amount if amount is not None else "err: 货物不存在")
        elif cmd == "inspect":
            if len(args) != 1:
                print("err: 用法 inspect <货物>")
                continue
            print("ok" if inspect(state, args[0]) else "err: 查验失败（缺陷/未申报），不扣税费")
        elif cmd == "cancel":
            if len(args) != 1:
                print("err: 用法 cancel <货物>")
                continue
            print("ok" if cancel_inspect(state, args[0]) else "err: 货物不存在")
        elif cmd == "receive":
            if len(args) != 1:
                print("err: 用法 receive <货物>")
                continue
            print("ok" if receive(state, args[0]) else "err: 关区已满/重复接收/禁运品")
        elif cmd == "violation":
            print(violation(state))
        elif cmd == "save":
            with open(SAVE_FILE, "w", encoding="utf-8") as fh:
                fh.write(save_state(state))
            print("ok: 已存档 %s" % SAVE_FILE)
        else:
            print("err: 非法命令")
    print("bye")


if __name__ == "__main__":
    main()
