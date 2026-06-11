import json
import random
import uuid

# Helper to word count strictly
def is_valid_mem(note):
    words = note.split()
    return 10 <= len(words) <= 20

def create_trace(task, turns_data):
    # turns_data is a list of dicts:
    # {
    #   "state": str,
    #   "menu": str,
    #   "memory": str or None,
    #   "result": str or None,
    #   "reason": str,
    #   "action": int,
    #   "args": dict or None
    # }
    turns = []

    current_memory = None

    for td in turns_data:
        # Build USER string
        user_lines = [f"[TASK]: {task}", f"[STATE]: {td['state']}"]

        if current_memory:
            user_lines.append(f"[MEMORY]: {current_memory}")

        if td.get("result"):
            user_lines.append(f"[RESULT]: {td['result']}")

        user_lines.append(f"[MENU]:\n{td['menu']}")

        user_str = "\n".join(user_lines)

        # Build ASSISTANT string
        ast_dict = {
            "reason": td["reason"],
            "action": td["action"]
        }
        if td.get("args") is not None:
            ast_dict["args"] = td["args"]

        # Check if memory was set in this turn
        if td.get("action") == 8 and td["state"] == "Home": # wait, MEM is always available.
            # We need to find the action number for MEM in the current menu
            pass # handled below

        if td.get("action_name") == "MEM":
            note = td["args"]["note"]
            if not is_valid_mem(note):
                raise ValueError(f"Invalid MEM note length ({len(note.split())}): {note}")
            current_memory = note

        turns.append({
            "user": user_str,
            "assistant": json.dumps(ast_dict)
        })

    return {"task": task, "turns": turns}
