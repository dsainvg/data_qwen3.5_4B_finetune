
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
            {"state": "Home", "reason": "I need to handle payments, so I will navigate to the Payments domain.", "action": DOMAIN_INDEX["Payments"]},
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
            {"state": "Home", "reason": "I need to clock in an employee first, so I will navigate to the Staff domain.", "action": DOMAIN_INDEX["Staff"]},
            {"state": "Staff", "reason": f"I will clock in employee {emp_id}.", "action": get_tool_index("Staff", "clock_in"), "args": {"emp_id": emp_id}},
            {"state": "Staff", "result": f"Employee {emp_id} clocked in.", "reason": "The employee is clocked in. I will store a memory note before switching domains.", "action": get_mem_index("Staff"), "is_mem": True, "args": {"note": mem_note}},
            {"state": "Staff", "reason": "I need to check kitchen tickets, so I must go back to the Home menu first.", "action": get_back_index("Staff")},
            {"state": "Home", "reason": "Now I will navigate to the Kitchen domain.", "action": DOMAIN_INDEX["Kitchen"]},
            {"state": "Kitchen", "reason": "I will view the current kitchen tickets.", "action": get_tool_index("Kitchen", "view_kitchen_tickets")},
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
            {"state": "Home", "reason": "I need to manage kitchen tickets, so I will navigate to the Kitchen domain.", "action": DOMAIN_INDEX["Kitchen"]},
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
