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
        user_lines = ["USER:", f"[TASK]: {task}", f"[STATE]: {td['state']}"]

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


# Category 1: Menu tasks (equivalent to "Web research then save result to a file")
# But strictly restaurant domains. Let's do: "Check menu items and update prices / mark 86" -> 10 traces
def gen_menu_tasks(count=10):
    traces = []
    items = ["Burger", "Pizza", "Pasta", "Salad", "Steak", "Fries", "Soup", "Fish", "Tacos", "Wings", "Ribs", "Sushi"]
    for i in range(count):
        item = random.choice(items) + str(i)
        price = round(random.uniform(10.0, 50.0), 2)
        task = f"Find the current menu and then update the price of {item} to ${price}."

        # We need a MEM note (10-20 words). Let's use it to remember the price.
        mem_note = f"Looked at the menu list, need to set the price of {item} to {price}."

        turns = [
            # Home -> Menu
            {"state": "Home", "reason": "I need to view the menu and update a price, so I will navigate to the Menu tools domain. This is a necessary step to ensure the task is completed correctly.", "action": DOMAIN_INDEX["Menu"]},
            # Menu -> list_menu
            {"state": "Menu", "reason": "First, I will list the current menu to find the items. This is a necessary step to ensure the task is completed correctly.", "action": get_tool_index("Menu", "list_menu")},
            # Menu -> MEM
            {"state": "Menu", "result": f"1. {item} - $10.00\n2. Coke - $2.00", "reason": "I have seen the menu. I should store a memory note to remember the exact price update required.", "action": get_mem_index("Menu"), "is_mem": True, "args": {"note": mem_note}},
            # Menu -> update_price
            {"state": "Menu", "reason": f"Now I will update the price of {item} based on my memory note.", "action": get_tool_index("Menu", "update_price"), "args": {"item": item, "price": price}},
            # Menu -> DONE
            {"state": "Menu", "result": f"Price of {item} updated to ${price}", "reason": "The price has been successfully updated according to the task. I am done.", "action": get_done_index("Menu")}
        ]
        traces.append(create_trace(task, turns))
    return traces

# Category 2: Reservations (equivalent to "Email reading and calendar scheduling") -> 8 traces
def gen_reservations(count=8):
    traces = []
    names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi"]
    for i in range(count):
        name = names[i]
        time = f"{random.randint(17,21)}:00"
        pax = random.randint(2, 6)
        cancel_id = random.randint(100, 999)
        task = f"Cancel reservation {cancel_id} and then add a new reservation for {name} at {time} for {pax} people."

        mem_note = f"Cancelled the old reservation successfully, now I will add {name} at {time} for {pax} people."

        turns = [
            {"state": "Home", "reason": "I need to manage reservations, so I will navigate to the Reservations domain. This is a necessary step to ensure the task is completed correctly.", "action": DOMAIN_INDEX["Reservations"]},
            {"state": "Reservations", "reason": f"I will cancel the existing reservation with ID {cancel_id} first.", "action": get_tool_index("Reservations", "cancel_reservation"), "args": {"id": cancel_id}},
            {"state": "Reservations", "result": f"Reservation {cancel_id} cancelled.", "reason": "The cancellation was successful. I'll store a memory note before proceeding with the new booking.", "action": get_mem_index("Reservations"), "is_mem": True, "args": {"note": mem_note}},
            {"state": "Reservations", "reason": "Now I will add the new reservation for the requested time and party size. This is a necessary step to ensure the task is completed correctly.", "action": get_tool_index("Reservations", "add_reservation"), "args": {"name": name, "time": time, "pax": pax}},
            {"state": "Reservations", "result": f"Reservation created for {name}.", "reason": "Both parts of the task are complete. I will finish the task now.", "action": get_done_index("Reservations")}
        ]
        traces.append(create_trace(task, turns))
    return traces

# Category 3: Order/Kitchen errors (equivalent to "Write and run Python code, handle an error, fix and rerun") -> 8 traces
def gen_order_errors(count=8):
    traces = []
    items = ["Steak", "Lobster", "Truffle", "Caviar", "Oysters", "Duck", "Venison", "Crab"]
    for i in range(count):
        item = items[i]
        table_no = random.randint(1, 20)
        task = f"Add {item} to table {table_no}'s order, verify it was added, and send it to the kitchen."

        mem_note = f"I encountered an error adding {item} to table {table_no}, I must try sending to kitchen again."

        turns = [
            {"state": "Home", "reason": "I need to add an item to an order, so I will navigate to the Orders domain. This is a necessary step to ensure the task is completed correctly.", "action": DOMAIN_INDEX["Orders"]},
            {"state": "Orders", "reason": f"I will try to add {item} to table {table_no}.", "action": get_tool_index("Orders", "add_item_to_order"), "args": {"table_no": table_no, "item": item}},
            {"state": "Orders", "result": f"Error: Table {table_no} is not open.", "reason": "The table is not open. I need to store a memory note about this error before I fix it.", "action": get_mem_index("Orders"), "is_mem": True, "args": {"note": mem_note}},
            # Navigate to Tables to open it
            {"state": "Orders", "reason": "I need to open the table first, so I will go back to the Home menu. This is a necessary step to ensure the task is completed correctly.", "action": get_back_index("Orders")},
            {"state": "Home", "reason": "Now I will navigate to the Tables domain to open the table. This is a necessary step to ensure the task is completed correctly.", "action": DOMAIN_INDEX["Tables"]},
            {"state": "Tables", "reason": f"I will open table {table_no}.", "action": get_tool_index("Tables", "open_table"), "args": {"table_no": table_no}},
            {"state": "Tables", "result": f"Table {table_no} opened.", "reason": "The table is open. I will go back to the Home menu.", "action": get_back_index("Tables")},
            {"state": "Home", "reason": "I will navigate back to the Orders domain to add the item. This is a necessary step to ensure the task is completed correctly.", "action": DOMAIN_INDEX["Orders"]},
            {"state": "Orders", "reason": f"Now that the table is open, I will add {item} again.", "action": get_tool_index("Orders", "add_item_to_order"), "args": {"table_no": table_no, "item": item}},
            {"state": "Orders", "result": f"Added {item} to table {table_no}.", "reason": "The item was added. Now I will send the order to the kitchen.", "action": get_tool_index("Orders", "send_to_kitchen"), "args": {"table_no": table_no}},
            {"state": "Orders", "result": "Order sent to kitchen.", "reason": "The order has been successfully processed. I am done.", "action": get_done_index("Orders")}
        ]
        traces.append(create_trace(task, turns))
    return traces


# Category 4: Payments (equivalent to "Load or compute data, plot or calculate a result") -> 8 traces
def gen_payments(count=8):
    traces = []
    for i in range(count):
        table_no = random.randint(21, 40)
        bill_amount = round(random.uniform(50.0, 200.0), 2)
        tendered = round(bill_amount + random.uniform(10.0, 50.0), 2)
        task = f"Print the receipt for table {table_no} and then process a cash payment of ${tendered}."

        mem_note = f"Printed receipt for table {table_no}, now I will process the cash payment of ${tendered}."

        turns = [
            {"state": "Home", "reason": "I need to handle payments, so I will navigate to the Payments domain. This is a necessary step to ensure the task is completed correctly.", "action": DOMAIN_INDEX["Payments"]},
            {"state": "Payments", "reason": f"First, I will print the receipt for table {table_no}.", "action": get_tool_index("Payments", "print_receipt"), "args": {"table_no": table_no}},
            {"state": "Payments", "result": f"Receipt printed. Total: ${bill_amount}", "reason": "The receipt has been printed. I will save a memory note about the payment amount to process.", "action": get_mem_index("Payments"), "is_mem": True, "args": {"note": mem_note}},
            {"state": "Payments", "reason": f"Now I will process the cash payment of ${tendered}.", "action": get_tool_index("Payments", "process_cash"), "args": {"table_no": table_no, "tendered": tendered}},
            {"state": "Payments", "result": f"Payment processed. Change due: ${round(tendered - bill_amount, 2)}", "reason": "The payment was successfully processed. I am done.", "action": get_done_index("Payments")}
        ]
        traces.append(create_trace(task, turns))
    return traces

# Category 5: Multi-domain (task requires visiting exactly 2 different domains) -> 10 traces
def gen_multi_domain(count=10):
    traces = []
    for i in range(count):
        emp_id = random.randint(1000, 9999)
        task = f"Clock in employee {emp_id} and then view the current kitchen tickets."

        mem_note = f"Successfully clocked in employee {emp_id}, now I will go back and check the kitchen tickets."

        turns = [
            {"state": "Home", "reason": "I need to clock in an employee first, so I will navigate to the Staff domain. This is a necessary step to ensure the task is completed correctly.", "action": DOMAIN_INDEX["Staff"]},
            {"state": "Staff", "reason": f"I will clock in employee {emp_id}.", "action": get_tool_index("Staff", "clock_in"), "args": {"emp_id": emp_id}},
            {"state": "Staff", "result": f"Employee {emp_id} clocked in.", "reason": "The employee is clocked in. I will store a memory note before switching domains.", "action": get_mem_index("Staff"), "is_mem": True, "args": {"note": mem_note}},
            {"state": "Staff", "reason": "I need to check kitchen tickets, so I must go back to the Home menu first. This is a necessary step to ensure the task is completed correctly.", "action": get_back_index("Staff")},
            {"state": "Home", "reason": "Now I will navigate to the Kitchen domain. This is a necessary step to ensure the task is completed correctly.", "action": DOMAIN_INDEX["Kitchen"]},
            {"state": "Kitchen", "reason": "I will view the current kitchen tickets. This is a necessary step to ensure the task is completed correctly.", "action": get_tool_index("Kitchen", "view_kitchen_tickets")},
            {"state": "Kitchen", "result": "3 active tickets: Table 4, Table 9, Table 12.", "reason": "I have successfully viewed the tickets. The task is complete.", "action": get_done_index("Kitchen")}
        ]
        traces.append(create_trace(task, turns))
    return traces

# Category 6: BACK correction (agent goes to wrong domain, backs out, corrects) -> 8 traces
def gen_back_correction(count=8):
    traces = []
    for i in range(count):
        table_no = random.randint(41, 60)
        task = f"Close table {table_no}."

        turns = [
            {"state": "Home", "reason": "I need to close a table. I might find this in the Orders domain, so I will go there.", "action": DOMAIN_INDEX["Orders"]},
            {"state": "Orders", "reason": "Looking at the menu, there is no option to close a table here. I made a mistake and must go back.", "action": get_back_index("Orders")},
            {"state": "Home", "reason": "The correct domain to close a table is the Tables domain. I will navigate there.", "action": DOMAIN_INDEX["Tables"]},
            {"state": "Tables", "reason": f"Now I can close table {table_no}.", "action": get_tool_index("Tables", "close_table"), "args": {"table_no": table_no}},
            {"state": "Tables", "result": f"Table {table_no} closed successfully.", "reason": "The table has been closed. I am done.", "action": get_done_index("Tables")}
        ]
        traces.append(create_trace(task, turns))
    return traces

# Category 7: Short tasks (completed in exactly 2-3 turns) -> 8 traces
def gen_short_tasks(count=8):
    traces = []
    for i in range(count):
        ticket_id = random.randint(100, 999)
        task = f"Mark kitchen ticket {ticket_id} as done."

        turns = [
            {"state": "Home", "reason": "I need to manage kitchen tickets, so I will navigate to the Kitchen domain. This is a necessary step to ensure the task is completed correctly.", "action": DOMAIN_INDEX["Kitchen"]},
            {"state": "Kitchen", "reason": f"I will mark ticket {ticket_id} as done.", "action": get_tool_index("Kitchen", "mark_ticket_done"), "args": {"ticket_id": ticket_id}},
            {"state": "Kitchen", "result": f"Ticket {ticket_id} marked as done.", "reason": "The ticket is marked as done. The task is fully complete.", "action": get_done_index("Kitchen")}
        ]
        traces.append(create_trace(task, turns))
    return traces

def main():
    traces = []
    traces.extend(gen_menu_tasks(10))
    traces.extend(gen_reservations(8))
    traces.extend(gen_order_errors(8))
    traces.extend(gen_payments(8))
    traces.extend(gen_multi_domain(10))
    traces.extend(gen_back_correction(8))
    traces.extend(gen_short_tasks(8))

    # Shuffle for randomness
    random.shuffle(traces)

    filename = str(uuid.uuid4())[:8] + ".jsonl"
    with open(filename, "w") as f:
        for t in traces:
            f.write(json.dumps(t) + "\n")

    print(f"Generated {len(traces)} traces in {filename}")

if __name__ == "__main__":
    main()
