import json
import random
import uuid

# Helper to check memory word count
def check_mem(note):
    words = note.split()
    if not (10 <= len(words) <= 20):
        raise ValueError(f"Memory note must be 10-20 words. Got {len(words)}: {note}")
    return note

def get_menu(state):
    menus = {
        "Home": "  1. Transactions — navigate to Transactions tools\n  2. Accounts — navigate to Accounts tools\n  3. Budgets — navigate to Budgets tools\n  4. Investments — navigate to Investments tools\n  5. Goals — navigate to Goals tools\n  6. Reports — navigate to Reports tools\n  7. Bills — navigate to Bills tools\n  8. MEM [note: `string`] — store a memory note (10–20 words exactly)\n  9. BACK — go to previous state\n  10. DONE — task is complete",
        "Transactions": "  1. add_expense [amount: `float`, category: `string`]\n  2. add_income [amount: `float`, source: `string`]\n  3. list_recent_transactions\n  4. MEM [note: `string`]\n  5. BACK\n  6. DONE",
        "Accounts": "  1. add_bank_account [name: `string`, balance: `float`]\n  2. transfer_funds [from_acct: `int`, to_acct: `int`, amt: `float`]\n  3. MEM [note: `string`]\n  4. BACK\n  5. DONE",
        "Budgets": "  1. set_budget [category: `string`, limit: `float`]\n  2. check_budget_status [category: `string`]\n  3. MEM [note: `string`]\n  4. BACK\n  5. DONE",
        "Investments": "  1. buy_stock [ticker: `string`, shares: `int`]\n  2. sell_stock [ticker: `string`, shares: `int`]\n  3. get_portfolio_value\n  4. MEM [note: `string`]\n  5. BACK\n  6. DONE",
        "Goals": "  1. create_savings_goal [name: `string`, target: `float`]\n  2. add_to_goal [goal_id: `int`, amount: `float`]\n  3. MEM [note: `string`]\n  4. BACK\n  5. DONE",
        "Reports": "  1. generate_monthly_summary [month: `string`]\n  2. get_top_expenses\n  3. MEM [note: `string`]\n  4. BACK\n  5. DONE",
        "Bills": "  1. add_bill_reminder [name: `string`, due: `date`, amount: `float`]\n  2. mark_bill_paid [id: `int`]\n  3. MEM [note: `string`]\n  4. BACK\n  5. DONE"
    }
    return menus[state]

def format_turn(task, state, memory, result, reason, action, args=None):
    lines = [f"[TASK]: {task}", f"[STATE]: {state}"]
    if memory:
        lines.append(f"[MEMORY]: {memory}")
    if result:
        lines.append(f"[RESULT]: {result}")
    lines.append("[MENU]:\n" + get_menu(state))

    user_str = "\n".join(lines)

    ast_dict = {"reason": reason, "action": action}
    if args is not None:
        ast_dict["args"] = args

    return {"user": user_str, "assistant": json.dumps(ast_dict)}

class TraceBuilder:
    def __init__(self, task):
        self.task = task
        self.turns = []
        self.state = "Home"
        self.memory = None
        self.result = None
        self.state_stack = []
        self.used_mem = False
        self.used_back = False
        self.domains = set()

    def step(self, reason, action, args=None, result=None, new_state=None, memory_note=None):
        turn = format_turn(self.task, self.state, self.memory, self.result, reason, action, args)
        self.turns.append(turn)

        # update state for next turn
        self.result = result
        if memory_note:
            self.memory = check_mem(memory_note)
            self.used_mem = True

        if new_state:
            if new_state == "BACK":
                self.state = self.state_stack.pop() if self.state_stack else "Home"
                self.used_back = True
            else:
                self.state_stack.append(self.state)
                self.state = new_state
                self.domains.add(new_state)

    def build(self):
        return {
            "trace": {"task": self.task, "turns": self.turns},
            "used_mem": self.used_mem,
            "used_back": self.used_back,
            "domains": self.domains
        }

traces = []

# Group 1: 10 traces - "Investigation then saving" (Mimicking Web research -> save)
# Reports -> get_top_expenses -> Budgets -> set_budget
for i in range(10):
    task = f"Find out my highest expenses for {random.choice(['January', 'February', 'March', 'April'])} and set a strict budget limit based on them to prevent overspending. Task ID: {uuid.uuid4().hex[:6]}"
    tb = TraceBuilder(task)
    tb.step("I need to look at the top expenses first, so I will navigate to the Reports domain.", 6, new_state="Reports")
    tb.step("Now in Reports, I will check the top expenses to see where the user is spending the most money.", 2, result="Top expenses:\n1. Dining Out: $850\n2. Groceries: $400\n3. Entertainment: $300")
    mem_note = "Checked top expenses, dining out is highest at $850, will set strict budget for it." # 15 words
    tb.step("I should save these findings to memory so I remember them when setting the budget in the Budgets domain.", 3, args={"note": mem_note}, memory_note=mem_note)
    tb.step("I have the expense data in memory, so I will navigate back to the Home menu to switch domains.", 4, new_state="BACK")
    tb.step("From the Home menu, I need to navigate to the Budgets domain to set the new strict limit.", 3, new_state="Budgets")
    tb.step("Now in Budgets, I will set a new budget limit for Dining Out based on the previous high expense report.", 1, args={"category": "Dining Out", "limit": 500.0}, result="Success: Budget for 'Dining Out' set to $500.0")
    tb.step("The budget limit has been successfully set as requested, so the task is fully complete.", 5)
    traces.append(tb.build())

# Group 2: 8 traces - "Reading and scheduling" (Mimicking Email -> Calendar)
# Bills -> mark_bill_paid -> add_bill_reminder
for i in range(8):
    b_name = random.choice(["Electric", "Water", "Internet", "Phone"])
    task = f"Mark bill ID {100+i} as paid, and then schedule a new reminder for the {b_name} bill due next month for $120.50. ID: {uuid.uuid4().hex[:6]}"
    tb = TraceBuilder(task)
    tb.step("To handle bill payments and reminders, I first need to navigate to the Bills domain from the Home menu.", 7, new_state="Bills")
    tb.step(f"I will mark bill ID {100+i} as paid since that is the first part of the user's request.", 2, args={"id": 100+i}, result=f"Bill ID {100+i} marked as paid successfully.")
    mem_note = "Marked bill paid successfully, now scheduling new reminder for the utility bill next month." # 14 words
    tb.step("I need to remember that the bill was paid before I move on to adding the reminder.", 3, args={"note": mem_note}, memory_note=mem_note)
    tb.step("The previous bill is paid. Now I must add a new bill reminder for the upcoming utility bill.", 1, args={"name": f"{b_name} Bill", "due": "2024-11-01", "amount": 120.50}, result="Reminder added successfully.")
    tb.step("Both the bill payment and the new reminder scheduling have been completed successfully.", 5)
    traces.append(tb.build())

# Group 3: 8 traces - "Write code, handle error, fix rerun" (Mimicking error handling)
# Accounts -> transfer_funds (fails) -> transfer_funds (success)
for i in range(8):
    task = f"Transfer $1000 from account {10+i} to account {20+i} for rent payment. Tracking: {uuid.uuid4().hex[:6]}"
    tb = TraceBuilder(task)
    tb.step("I need to navigate to the Accounts domain to perform a fund transfer between bank accounts.", 2, new_state="Accounts")
    tb.step(f"I will attempt to transfer the requested $1000 from account {10+i} to account {20+i}.", 2, args={"from_acct": 10+i, "to_acct": 20+i, "amt": 1000.0}, result="Error: Insufficient funds in source account. Available balance is $800.")
    mem_note = f"Attempted transfer of $1000 failed due to insufficient funds, available balance is exactly $800." # 14 words
    tb.step("The transfer failed due to insufficient funds. I will save the available balance to memory to adjust the transfer.", 3, args={"note": mem_note}, memory_note=mem_note)
    tb.step(f"Since the account only has $800, I will transfer the maximum available amount of $800 instead of $1000.", 2, args={"from_acct": 10+i, "to_acct": 20+i, "amt": 800.0}, result="Success: Transferred $800.")
    tb.step("The adjusted fund transfer was successful and the maximum available funds have been moved.", 5)
    traces.append(tb.build())

# Group 4: 8 traces - "Load data, compute/act" (Mimicking Load/Compute/Plot)
# Transactions -> list_recent_transactions -> add_expense
for i in range(8):
    task = f"Review recent transactions to see if the grocery charge went through, and if not, add a $150.25 expense for groceries. Code: {uuid.uuid4().hex[:6]}"
    tb = TraceBuilder(task)
    tb.step("I must check recent transactions, so I will navigate to the Transactions domain first.", 1, new_state="Transactions")
    tb.step("I will list the recent transactions to check if the grocery charge is already recorded there.", 3, result="1. Coffee: $4.50\n2. Gas: $40.00\n3. Subscription: $15.99")
    mem_note = "Checked recent transactions and found the grocery charge is currently missing from the list completely." # 15 words
    tb.step("I should note that the grocery charge is missing so I know to add it now.", 4, args={"note": mem_note}, memory_note=mem_note)
    tb.step("The grocery charge is not in the recent transactions list, so I need to add it manually now.", 1, args={"amount": 150.25, "category": "Groceries"}, result="Success: Added expense of $150.25 for Groceries.")
    tb.step("The recent transactions were checked and the missing grocery expense was successfully added to the system.", 6)
    traces.append(tb.build())

# Group 5: 10 traces - "Multi-domain"
# Goals -> add_to_goal -> BACK -> Investments -> buy_stock
for i in range(10):
    task = f"Add $500 to savings goal ID {5+i}, and then buy 10 shares of AAPL stock for my portfolio. Batch: {uuid.uuid4().hex[:6]}"
    tb = TraceBuilder(task)
    tb.step("I will start by navigating to the Goals domain to add funds to the savings goal.", 5, new_state="Goals")
    tb.step(f"I will add $500 to the specified savings goal ID {5+i} as requested by the user.", 2, args={"goal_id": 5+i, "amount": 500.0}, result="Success: $500 added to goal.")
    mem_note = "Added funds to savings goal successfully, now navigating to investments for the stock purchase task." # 15 words
    tb.step("I will record that the goal contribution is complete before moving to the investments domain.", 3, args={"note": mem_note}, memory_note=mem_note)
    tb.step("The goal has been updated. Now I need to navigate back to Home to switch to the Investments domain.", 4, new_state="BACK")
    tb.step("From the Home menu, I will navigate to the Investments domain to purchase the requested stock shares.", 4, new_state="Investments")
    tb.step("I will execute the stock purchase of 10 shares of AAPL to add to the portfolio.", 1, args={"ticker": "AAPL", "shares": 10}, result="Success: Bought 10 shares of AAPL.")
    tb.step("Both the goal contribution and the stock purchase have been completed successfully across the two domains.", 6)
    traces.append(tb.build())

# Group 6: 8 traces - "BACK correction"
# Goes to Budgets -> realizes wrong -> BACK -> Investments -> get_portfolio_value
for i in range(8):
    task = f"I need to check the total value of my current investment portfolio. Session: {uuid.uuid4().hex[:6]}"
    tb = TraceBuilder(task)
    tb.step("I will navigate to the Budgets domain to check the portfolio value.", 3, new_state="Budgets")
    tb.step("Wait, I am in the Budgets domain but I need to check investment portfolio value. I must go back.", 4, new_state="BACK")
    tb.step("Now back at Home, I will correctly navigate to the Investments domain to get the portfolio value.", 4, new_state="Investments")
    tb.step(f"I will retrieve the current total value of the investment portfolio as requested.", 3, result=f"Portfolio Value: $14,250.00")
    tb.step("The portfolio value has been successfully retrieved, so the task is complete.", 6)
    traces.append(tb.build())

# Group 7: 8 traces - "Short tasks"
# Accounts -> add_bank_account -> DONE
# Let's change this to use remaining domains to ensure all domains get 5 primary instances
# Let's check what we have:
# Reports (10 from Group 1, Group 6 uses Investments)
# Bills (8 from Group 2)
# Accounts (8 from Group 3)
# Transactions (8 from Group 4)
# Goals (10 from Group 5)
# Investments (8 from Group 6, plus 10 from Group 5)
# Budgets (10 from Group 1 secondary, 8 from Group 6 mistake) -> NEEDS TO BE PRIMARY!
for i in range(8):
    task = f"Set a new budget for 'Clothing' with a limit of $200. Run ID: {uuid.uuid4().hex[:6]}"
    tb = TraceBuilder(task)
    tb.step("To set a new budget, I must navigate to the Budgets domain from the Home menu.", 3, new_state="Budgets")
    tb.step(f"I will create the new budget for 'Clothing' with the specified limit of $200.", 1, args={"category": "Clothing", "limit": 200.0}, result="Success: Budget for 'Clothing' set to $200.0")
    mem_note = "Created new clothing budget successfully with the correct specified limit of two hundred dollars." # 14 words
    tb.step("I will record a note that the budget was created properly.", 3, args={"note": mem_note}, memory_note=mem_note)
    tb.step("The new budget was successfully created, completing the task.", 5)
    traces.append(tb.build())

# Shuffle traces
random.shuffle(traces)

# Check totals
print(f"Total traces: {len(traces)}")

mem_count = sum(1 for t in traces if t["used_mem"])
back_count = sum(1 for t in traces if t["used_back"])
print(f"Traces using MEM: {mem_count} (Needs >= 40)")
print(f"Traces using BACK: {back_count} (Needs >= 20)")

domain_counts = {}
for t in traces:
    for d in t["domains"]:
        domain_counts[d] = domain_counts.get(d, 0) + 1

print(f"Domains appearing in traces: {domain_counts} (All need >= 5)")

# Create the final jsonl exactly as requested
filename = f"dataset_{uuid.uuid4().hex[:8]}.jsonl"
with open(filename, "w") as f:
    for t in traces:
        f.write(json.dumps(t["trace"]) + "\n")

print(f"Saved to {filename}")
