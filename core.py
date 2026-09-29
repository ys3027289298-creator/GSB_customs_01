"""海关核心逻辑：货物、税率、关区和查验。"""

import json

FIXED_DATE = "2026-09-29"
ZONE_CAPACITY = 2
TAX_RATE = 1.0
VIOLATION_PENALTY = 10


def new_game():
    return {
        "date": FIXED_DATE,
        "goods": {},
        "zone_load": 0,
        "zone_capacity": ZONE_CAPACITY,
        "received": [],
        "credit": 100,
        "decl_id": 0,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    if not text or not text.strip():
        raise ValueError("empty save data")
    state = json.loads(text)
    if not isinstance(state, dict) or not isinstance(state.get("goods"), dict):
        raise ValueError("invalid save data")
    state.setdefault("received", [])
    state.setdefault("date", FIXED_DATE)
    return state


def declare(state, goods_id, value, banned):
    if not goods_id or goods_id in state["goods"]:
        return False
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return False
    if amount < 0:
        return False
    state["decl_id"] += 1
    state["goods"][goods_id] = {
        "decl_no": state["decl_id"],
        "value": amount,
        "banned": bool(banned),
        "date": state.get("date", FIXED_DATE),
    }
    return True


def clear(state, goods_id):
    goods = state["goods"].get(goods_id)
    if goods is None or goods.get("banned") or goods.get("held"):
        return False
    goods["cleared"] = True
    return True


def tax(state, goods_id):
    goods = state["goods"].get(goods_id)
    if goods is None:
        return None
    return round(goods["value"] * TAX_RATE)


def inspect(state, goods_id):
    goods = state["goods"].get(goods_id)
    if goods is None:
        return False
    goods["held"] = True
    if goods.get("defect"):
        return False
    return True


def cancel_inspect(state, goods_id):
    goods = state["goods"].get(goods_id)
    if goods is None:
        return False
    goods.pop("held", None)
    return True


def receive(state, goods_id):
    if not goods_id or goods_id in state.get("received", []):
        return False
    if state["zone_load"] >= state["zone_capacity"]:
        return False
    state["zone_load"] += 1
    state["received"].append(goods_id)
    return True


def violation(state):
    state["credit"] -= 10
    return state["credit"]


def _parse_bool(text):
    return str(text).strip().lower() in ("true", "1", "yes", "banned")


def main():
    state = new_game()
    print(
        f"海关 {FIXED_DATE} - 命令: declare/clear/tax/inspect/"
        "cancel_inspect/receive/violation/save/load/quit"
    )
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            print("error: empty command")
            continue
        if raw == "quit":
            break
        parts = raw.split()
        cmd, args = parts[0], parts[1:]
        try:
            if cmd == "declare":
                if len(args) != 3:
                    raise ValueError("usage: declare <id> <value> <banned>")
                ok = declare(state, args[0], args[1], _parse_bool(args[2]))
                print("ok" if ok else "fail: duplicate or invalid declaration")
            elif cmd == "clear":
                ok = clear(state, args[0])
                print("ok" if ok else "fail: banned, held or unknown goods")
            elif cmd == "tax":
                amount = tax(state, args[0])
                print(f"tax={amount}" if amount is not None else "fail: unknown goods")
            elif cmd == "inspect":
                ok = inspect(state, args[0])
                print("ok" if ok else "fail: defect or unknown goods, held")
            elif cmd == "cancel_inspect":
                ok = cancel_inspect(state, args[0])
                print("ok: returned" if ok else "fail: unknown goods")
            elif cmd == "receive":
                ok = receive(state, args[0])
                print("ok" if ok else "fail: zone full, duplicate or invalid id")
            elif cmd == "violation":
                print(f"credit={violation(state)}")
            elif cmd == "save":
                print(save_state(state))
            elif cmd == "load":
                state = load_state(" ".join(args))
                print("ok")
            else:
                print(f"error: unknown command: {cmd}")
        except (IndexError, ValueError) as exc:
            print(f"error: {exc}")


if __name__ == "__main__":
    main()
