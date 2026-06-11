import json
import random
import uuid

HOME_MENU = """  1. Tables — navigate to Tables tools
  2. Orders — navigate to Orders tools
  3. Menu — navigate to Menu tools
  4. Payments — navigate to Payments tools
  5. Staff — navigate to Staff tools
  6. Reservations — navigate to Reservations tools
  7. Kitchen — navigate to Kitchen tools
  8. MEM [note: `string`] — store a memory note (10–20 words exactly)
  9. BACK — go to previous state
  10. DONE — task is complete"""

DOMAIN_MENUS = {
    "Tables": """  1. open_table [table_no: `int`]
  2. close_table [table_no: `int`]
  3. move_table [from_no: `int`, to_no: `int`]
  4. MEM [note: `string`]
  5. BACK
  6. DONE""",
    "Orders": """  1. add_item_to_order [table_no: `int`, item: `string`]
  2. void_item [order_id: `int`, item: `string`]
  3. send_to_kitchen [table_no: `int`]
  4. MEM [note: `string`]
  5. BACK
  6. DONE""",
    "Menu": """  1. update_price [item: `string`, price: `float`]
  2. mark_item_86 [item: `string`]
  3. list_menu
  4. MEM [note: `string`]
  5. BACK
  6. DONE""",
    "Payments": """  1. print_receipt [table_no: `int`]
  2. process_card [table_no: `int`, amount: `float`]
  3. process_cash [table_no: `int`, tendered: `float`]
  4. MEM [note: `string`]
  5. BACK
  6. DONE""",
    "Staff": """  1. clock_in [emp_id: `int`]
  2. clock_out [emp_id: `int`]
  3. print_shift_report [emp_id: `int`]
  4. MEM [note: `string`]
  5. BACK
  6. DONE""",
    "Reservations": """  1. add_reservation [name: `string`, time: `time`, pax: `int`]
  2. cancel_reservation [id: `int`]
  3. MEM [note: `string`]
  4. BACK
  5. DONE""",
    "Kitchen": """  1. view_kitchen_tickets
  2. mark_ticket_done [ticket_id: `int`]
  3. MEM [note: `string`]
  4. BACK
  5. DONE"""
}

# The domains and their index from Home menu
DOMAIN_INDEX = {
    "Tables": 1,
    "Orders": 2,
    "Menu": 3,
    "Payments": 4,
    "Staff": 5,
    "Reservations": 6,
    "Kitchen": 7
}

# Find tool index in a domain menu
def get_tool_index(domain, tool_name):
    menu_lines = DOMAIN_MENUS[domain].split('\n')
    for line in menu_lines:
        if tool_name in line:
            return int(line.strip().split('.')[0])
    raise ValueError(f"Tool {tool_name} not found in {domain}")

# We also need action indices for MEM, BACK, DONE. They are at the end.
def get_mem_index(domain):
    return get_tool_index(domain, "MEM")

def get_back_index(domain):
    return get_tool_index(domain, "BACK")

def get_done_index(domain):
    return get_tool_index(domain, "DONE")

def is_valid_mem(note):
    words = note.split()
    return 10 <= len(words) <= 20

def create_trace(task, turns_data):
    turns = []
    current_memory = None

    for td in turns_data:
        # Build USER string
        user_lines = [f"[TASK]: {task}", f"[STATE]: {td['state']}"]

        if current_memory:
            user_lines.append(f"[MEMORY]: {current_memory}")

        if td.get("result"):
            user_lines.append(f"[RESULT]: {td['result']}")

        menu_str = HOME_MENU if td['state'] == "Home" else DOMAIN_MENUS[td['state']]
        user_lines.append(f"[MENU]:\n{menu_str}")

        user_str = "\n".join(user_lines)

        # Build ASSISTANT string
        ast_dict = {
            "reason": td["reason"],
            "action": td["action"]
        }
        if td.get("args") is not None:
            ast_dict["args"] = td["args"]

        # Check MEM logic
        # For home, MEM is 8. For subdomains, it's variable. We rely on td.get("is_mem")
        if td.get("is_mem"):
            note = td["args"]["note"]
            if not is_valid_mem(note):
                raise ValueError(f"Invalid MEM note length ({len(note.split())}): {note}")
            current_memory = note

        turns.append({
            "user": user_str,
            "assistant": json.dumps(ast_dict)
        })

    return {"task": task, "turns": turns}
