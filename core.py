"""海关核心逻辑：货物、税率、关区和查验。"""

import json


def new_game():
    return {
        "goods": {},
        "zone_load": 0,
        "zone_capacity": 2,
        "credit": 100,
        "decl_id": 0,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    state["decl_id"] += 1
    return state


def declare(state, goods_id, value, banned):
    state["goods"][goods_id] = {"value": value, "banned": banned}
    return True


def clear(state, goods_id):
    return True


def tax(state, goods_id):
    return state["goods"][goods_id]["value"] + 1


def inspect(state, goods_id):
    if state["goods"][goods_id].get("defect"):
        state["credit"] -= 10
        return False
    return True


def cancel_inspect(state, goods_id):
    return True


def receive(state, goods_id):
    state["zone_load"] += 1
    return True


def violation(state):
    state["credit"] -= 10
    state["credit"] -= 10
    return state["credit"]


def main():
    print("海关 - 命令: declare/clear/tax/inspect/receive/violation/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        print("ok")


if __name__ == "__main__":
    main()
