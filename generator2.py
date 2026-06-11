
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
            {"state": "Home", "reason": "I need to view the menu and update a price, so I will navigate to the Menu tools domain.", "action": DOMAIN_INDEX["Menu"]},
            # Menu -> list_menu
            {"state": "Menu", "reason": "First, I will list the current menu to find the items.", "action": get_tool_index("Menu", "list_menu")},
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
            {"state": "Home", "reason": "I need to manage reservations, so I will navigate to the Reservations domain.", "action": DOMAIN_INDEX["Reservations"]},
            {"state": "Reservations", "reason": f"I will cancel the existing reservation with ID {cancel_id} first.", "action": get_tool_index("Reservations", "cancel_reservation"), "args": {"id": cancel_id}},
            {"state": "Reservations", "result": f"Reservation {cancel_id} cancelled.", "reason": "The cancellation was successful. I'll store a memory note before proceeding with the new booking.", "action": get_mem_index("Reservations"), "is_mem": True, "args": {"note": mem_note}},
            {"state": "Reservations", "reason": "Now I will add the new reservation for the requested time and party size.", "action": get_tool_index("Reservations", "add_reservation"), "args": {"name": name, "time": time, "pax": pax}},
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
            {"state": "Home", "reason": "I need to add an item to an order, so I will navigate to the Orders domain.", "action": DOMAIN_INDEX["Orders"]},
            {"state": "Orders", "reason": f"I will try to add {item} to table {table_no}.", "action": get_tool_index("Orders", "add_item_to_order"), "args": {"table_no": table_no, "item": item}},
            {"state": "Orders", "result": f"Error: Table {table_no} is not open.", "reason": "The table is not open. I need to store a memory note about this error before I fix it.", "action": get_mem_index("Orders"), "is_mem": True, "args": {"note": mem_note}},
            # Navigate to Tables to open it
            {"state": "Orders", "reason": "I need to open the table first, so I will go back to the Home menu.", "action": get_back_index("Orders")},
            {"state": "Home", "reason": "Now I will navigate to the Tables domain to open the table.", "action": DOMAIN_INDEX["Tables"]},
            {"state": "Tables", "reason": f"I will open table {table_no}.", "action": get_tool_index("Tables", "open_table"), "args": {"table_no": table_no}},
            {"state": "Tables", "result": f"Table {table_no} opened.", "reason": "The table is open. I will go back to the Home menu.", "action": get_back_index("Tables")},
            {"state": "Home", "reason": "I will navigate back to the Orders domain to add the item.", "action": DOMAIN_INDEX["Orders"]},
            {"state": "Orders", "reason": f"Now that the table is open, I will add {item} again.", "action": get_tool_index("Orders", "add_item_to_order"), "args": {"table_no": table_no, "item": item}},
            {"state": "Orders", "result": f"Added {item} to table {table_no}.", "reason": "The item was added. Now I will send the order to the kitchen.", "action": get_tool_index("Orders", "send_to_kitchen"), "args": {"table_no": table_no}},
            {"state": "Orders", "result": "Order sent to kitchen.", "reason": "The order has been successfully processed. I am done.", "action": get_done_index("Orders")}
        ]
        traces.append(create_trace(task, turns))
    return traces
