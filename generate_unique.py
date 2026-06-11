import json
import random

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

    def step(self, reason, action, args=None, result=None, new_state=None, memory_note=None):
        turn = format_turn(self.task, self.state, self.memory, self.result, reason, action, args)
        self.turns.append(turn)
        self.result = result
        if memory_note:
            self.memory = check_mem(memory_note)
        if new_state:
            if new_state == "BACK":
                self.state = self.state_stack.pop() if self.state_stack else "Home"
            else:
                self.state_stack.append(self.state)
                self.state = new_state

    def build(self):
        return {"task": self.task, "turns": self.turns}

traces = []

# ==========================================
# Group 1 (Reports Primary): 8 traces
# ==========================================
g1_data = [
    ("January", "Dining Out", 850, 500.0, "I want to reign in my dining out spending since it was my highest expense in January. Check the top expenses and set a new strict budget for it."),
    ("February", "Groceries", 920, 600.0, "Could you identify the biggest expense category from February and cap its budget to help me save?"),
    ("March", "Entertainment", 450, 200.0, "Look up where my money went the most in March, and enforce a tighter budget limit on that category."),
    ("April", "Travel", 1200, 800.0, "Please verify my leading expense for April and establish a lower ceiling for it going forward."),
    ("May", "Shopping", 670, 300.0, "Analyze my top spending area from May and implement a new financial boundary to curb my shopping habit."),
    ("June", "Utilities", 350, 250.0, "Check my peak expense from June and set a hard budget limit on it immediately."),
    ("July", "Fuel", 400, 250.0, "Find out what drained my wallet most in July, and configure a budget constraint to fix it."),
    ("August", "Subscriptions", 210, 100.0, "Discover the primary cost I had in August and restrict its future allowance with a strict budget.")
]
for month, cat, spent, new_limit, task_desc in g1_data:
    tb = TraceBuilder(task_desc)
    tb.step(f"To begin, I will access the Reports domain to analyze the user's spending habits for {month}.", 6, new_state="Reports")
    tb.step(f"Now I need to extract the top expenses to determine which category requires the new budget cap.", 2, result=f"Top expenses:\n1. {cat}: ${spent}\n2. Other: $100")
    mem_note = f"Identified that {cat} was the highest expense at exactly ${spent}, deciding to enforce a tighter budget."
    tb.step(f"I must retain this crucial insight regarding the {cat} spending before navigating to another domain.", 3, args={"note": mem_note}, memory_note=mem_note)
    tb.step("With the key data safely stored in memory, I will return to the Home interface.", 4, new_state="BACK")
    tb.step("From the main menu, I will proceed to the Budgets area to apply the desired financial limits.", 3, new_state="Budgets")
    tb.step(f"I will establish the revised budget for the {cat} category with the updated maximum of ${new_limit}.", 1, args={"category": cat, "limit": new_limit}, result=f"Success: Budget for '{cat}' set to ${new_limit}")
    tb.step("The budget configuration is finalized as requested, successfully concluding this entire operation.", 5)
    traces.append(tb.build())

# ==========================================
# Group 2 (Bills Primary): 8 traces
# ==========================================
g2_data = [
    ("Electric", 101, "2024-11-01", 120.50, "Pay off bill ID 101, then add a reminder for the Electric bill coming up for $120.50."),
    ("Water", 205, "2024-11-15", 45.00, "Clear out the outstanding bill 205, and schedule my next Water bill reminder for the 15th."),
    ("Internet", 309, "2024-11-05", 89.99, "Mark the current bill 309 as resolved, and put the Internet bill reminder on my calendar."),
    ("Phone", 412, "2024-11-10", 65.00, "Finish paying bill 412, and then set an alert for the upcoming Phone payment."),
    ("Gas", 518, "2024-11-20", 75.25, "I need bill ID 518 marked complete, followed by creating a reminder for the next Gas charge."),
    ("Trash", 621, "2024-11-25", 30.00, "Process bill 621 as paid today, and immediately schedule the Trash collection bill reminder."),
    ("HOA", 734, "2024-12-01", 250.00, "Handle the payment for bill ID 734, then add the HOA fee reminder for next month."),
    ("Insurance", 845, "2024-11-28", 140.00, "Record bill 845 as settled, and set up a reminder for the Insurance premium coming due.")
]
for b_name, b_id, b_due, b_amt, task_desc in g2_data:
    tb = TraceBuilder(task_desc)
    tb.step("I will enter the Bills module from the dashboard to manage the requested payments and reminders.", 7, new_state="Bills")
    tb.step(f"My first action here is to register bill ID {b_id} as officially paid in the system.", 2, args={"id": b_id}, result=f"Bill ID {b_id} marked as paid successfully.")
    mem_note = f"Successfully paid off the current bill, now moving on to schedule the upcoming {b_name} reminder."
    tb.step("I should briefly document that the payment step succeeded before I create the new reminder.", 3, args={"note": mem_note}, memory_note=mem_note)
    tb.step(f"Now I will set up the subsequent reminder for the {b_name} bill so the user remembers it.", 1, args={"name": f"{b_name} Bill", "due": b_due, "amount": b_amt}, result="Reminder added successfully.")
    tb.step("Both the bill resolution and the future scheduling tasks are done, so I will conclude here.", 5)
    traces.append(tb.build())

# ==========================================
# Group 3 (Accounts Primary): 8 traces
# ==========================================
g3_data = [
    (15, 25, 1000.0, 800.0, "Transfer $1000 from account 15 to account 25 to cover my rent payment this month."),
    (11, 22, 500.0, 350.0, "Move $500 out of account 11 into account 22 so I can pay for the car repairs."),
    (18, 29, 2000.0, 1500.0, "Send $2000 from my 18 account to the 29 account to finalize the vacation booking."),
    (13, 27, 750.0, 600.0, "Execute a fund transfer of $750 from account 13 over to account 27 for property taxes."),
    (16, 21, 300.0, 150.0, "I need to shift $300 from account 16 to account 21 immediately for emergency medical expenses."),
    (14, 24, 1200.0, 950.0, "Process a wire of $1200 from account 14 to account 24 to handle the contractor invoice."),
    (17, 28, 450.0, 400.0, "Initiate a transfer of $450 starting from account 17 and going to account 28 for groceries."),
    (12, 26, 850.0, 700.0, "Please move $850 from account 12 into account 26 so I have enough for the new laptop.")
]
for a_from, a_to, req_amt, act_amt, task_desc in g3_data:
    tb = TraceBuilder(task_desc)
    tb.step("I will navigate directly to the Accounts domain to execute the requested financial fund transfer.", 2, new_state="Accounts")
    tb.step(f"I will now attempt to process the transfer of ${req_amt} between the two designated accounts.", 2, args={"from_acct": a_from, "to_acct": a_to, "amt": req_amt}, result=f"Error: Insufficient funds in source account. Available balance is ${act_amt}.")
    mem_note = f"The attempted transaction failed due to insufficient funds, the actual available balance is only ${act_amt}."
    tb.step("Since the initial amount was too high, I will save the true available balance to memory.", 3, args={"note": mem_note}, memory_note=mem_note)
    tb.step(f"I will adjust the transfer to move the maximum possible funds of ${act_amt} instead of the original amount.", 2, args={"from_acct": a_from, "to_acct": a_to, "amt": act_amt}, result=f"Success: Transferred ${act_amt}.")
    tb.step("The revised fund transfer has been successfully processed, fulfilling the task with the available balance.", 5)
    traces.append(tb.build())

# ==========================================
# Group 4 (Transactions Primary): 8 traces
# ==========================================
g4_data = [
    ("Groceries", 150.25, "Review my recent transactions. If my $150.25 grocery bill is missing, please add it manually."),
    ("Pharmacy", 45.10, "Check if the recent pharmacy charge went through, and add the $45.10 expense if it has not."),
    ("Hardware Store", 89.99, "Look at my recent transaction log. Add an $89.99 expense for the hardware store if absent."),
    ("Pet Supplies", 65.50, "See if pet supplies show up in recent transactions. If not, log a $65.50 expense for it."),
    ("Office Supplies", 120.00, "Inspect the latest transactions to confirm office supplies. If it is missing, add the $120.00 charge."),
    ("Coffee Shop", 12.75, "Verify if my coffee shop visit was recorded. If there is no record, add a $12.75 expense."),
    ("Bookstore", 35.20, "Check recent transactions for a bookstore purchase, and insert a $35.20 expense if it is missing."),
    ("Gym Membership", 55.00, "Review the recent charges to find my gym membership. Add the $55.00 expense manually if absent.")
]
for cat, amt, task_desc in g4_data:
    tb = TraceBuilder(task_desc)
    tb.step("I need to investigate the recent transaction history, so I will switch to the Transactions module.", 1, new_state="Transactions")
    tb.step("I will retrieve the list of recent transactions to determine if the specific charge is already present.", 3, result="1. Streaming: $15.99\n2. Fast Food: $25.50\n3. Bus Fare: $4.00")
    mem_note = f"Reviewed the recent transactions list and verified that the {cat} charge is completely missing from it."
    tb.step("I will document that the charge is absent so I remember to explicitly add it next.", 4, args={"note": mem_note}, memory_note=mem_note)
    tb.step(f"Because the charge was not found, I will now manually add the {cat} expense for ${amt}.", 1, args={"amount": amt, "category": cat}, result=f"Success: Added expense of ${amt} for {cat}.")
    tb.step("The missing transaction has been successfully verified and added to the ledger, completing the requirement.", 6)
    traces.append(tb.build())

# ==========================================
# Group 5 (Goals Primary): 8 traces
# ==========================================
g5_data = [
    (101, 500.0, "AAPL", 10, "Add $500 to my primary savings goal ID 101, and buy 10 shares of AAPL for my portfolio."),
    (102, 250.0, "MSFT", 5, "Put $250 towards goal 102, and then purchase 5 shares of MSFT stock."),
    (103, 1000.0, "GOOGL", 15, "Contribute $1000 to goal ID 103, and subsequently acquire 15 shares of GOOGL."),
    (104, 75.0, "TSLA", 2, "Deposit $75 into goal 104, and execute a buy order for 2 shares of TSLA."),
    (105, 300.0, "AMZN", 8, "Fund savings goal 105 with $300, and immediately invest in 8 shares of AMZN."),
    (106, 150.0, "META", 4, "Allocate $150 to goal ID 106, and proceed to buy 4 shares of META stock."),
    (107, 800.0, "NVDA", 20, "Add an $800 contribution to goal 107, and purchase 20 shares of NVDA for the long term."),
    (108, 450.0, "NFLX", 3, "Increase goal 108 by $450, and also secure 3 shares of NFLX for my investment account.")
]
for g_id, g_amt, tckr, shrs, task_desc in g5_data:
    tb = TraceBuilder(task_desc)
    tb.step("First, I will navigate over to the Goals section to process the requested savings contribution.", 5, new_state="Goals")
    tb.step(f"I am now going to deposit the ${g_amt} into the specified savings goal ID {g_id}.", 2, args={"goal_id": g_id, "amount": g_amt}, result=f"Success: ${g_amt} added to goal.")
    mem_note = "Successfully completed the savings goal contribution, now preparing to handle the stock market purchase phase."
    tb.step("I should note the successful goal update before I transition to the next entirely different domain.", 3, args={"note": mem_note}, memory_note=mem_note)
    tb.step("With the goal updated, I will navigate back to the Home screen to switch contexts.", 4, new_state="BACK")
    tb.step("From the central Home dashboard, I will proceed to the Investments domain to buy the stock.", 4, new_state="Investments")
    tb.step(f"I will place the order to purchase {shrs} shares of the {tckr} ticker symbol.", 1, args={"ticker": tckr, "shares": shrs}, result=f"Success: Bought {shrs} shares of {tckr}.")
    tb.step("Both the savings goal contribution and the stock acquisition have been fulfilled successfully.", 6)
    traces.append(tb.build())

# ==========================================
# Group 6 (Investments Primary, Mistake -> BACK): 10 traces
# ==========================================
g6_data = [
    ("AAPL", 5, 201, "I need to check my current portfolio value, then actually sell 5 shares of AAPL."),
    ("MSFT", 2, 202, "Please retrieve the total value of my investments, then sell 2 shares of MSFT."),
    ("GOOGL", 10, 203, "Get my investment portfolio balance, and proceed to liquidate 10 shares of GOOGL."),
    ("TSLA", 1, 204, "Can you show me my portfolio value and execute a sell order for 1 TSLA share?"),
    ("AMZN", 4, 205, "I want to see my portfolio value, followed by selling off 4 shares of AMZN."),
    ("META", 3, 206, "Check the value of my portfolio, and immediately sell 3 shares of META stock."),
    ("NVDA", 15, 207, "Find out my portfolio value, and place a trade to sell 15 NVDA shares."),
    ("NFLX", 2, 208, "Report the total portfolio value, and then sell 2 shares of my NFLX holdings."),
    ("AMD", 8, 209, "Look up my overall portfolio value, and dispose of 8 shares of AMD."),
    ("INTC", 20, 210, "Get the current valuation of my portfolio, and sell 20 shares of INTC.")
]
for tckr, shrs, m_id, task_desc in g6_data:
    tb = TraceBuilder(task_desc)
    # Start in investments directly, then mistake out and back in, to make Investments the primary
    tb.step("I will enter the Investments domain to manage the portfolio queries and subsequent sell orders.", 4, new_state="Investments")
    tb.step("Wait, I misread my plan, let me step back to Home just to be absolutely certain.", 5, new_state="BACK")
    tb.step("Confirmed, I definitely need to be in Investments for portfolio queries. Re-entering Investments now.", 4, new_state="Investments")
    tb.step("I will now query the system to retrieve the real-time value of the user's investment portfolio.", 3, result="Portfolio Value: $45,250.00")
    mem_note = f"Checked portfolio value successfully, now I need to process the sell order for {tckr} shares."
    tb.step("I should save a note that the portfolio check succeeded before proceeding to the sell order.", 4, args={"note": mem_note}, memory_note=mem_note)
    tb.step(f"Next, I will execute the sell order for {shrs} shares of {tckr} as the user requested.", 2, args={"ticker": tckr, "shares": shrs}, result=f"Success: Sold {shrs} shares of {tckr}.")
    tb.step("Both the portfolio inquiry and the subsequent stock sale have been completed successfully.", 6)
    traces.append(tb.build())

# ==========================================
# Group 7 (Budgets Primary): 10 traces
# ==========================================
g7_data = [
    ("Clothing", 200.0, "Set a new budget for 'Clothing' with a limit of $200, and check if it took effect."),
    ("Fitness", 150.0, "I want to establish a 'Fitness' budget capped at $150 and verify its active status."),
    ("Dining Out", 300.0, "Create a 'Dining Out' budget strictly limited to $300, and immediately verify the status."),
    ("Education", 500.0, "Please put a $500 limit on my 'Education' budget, and check that it was applied."),
    ("Entertainment", 100.0, "Set up an 'Entertainment' budget with a $100 ceiling, and confirm the budget status afterwards."),
    ("Groceries", 600.0, "Enforce a new 'Groceries' budget limited to $600, then read back the current budget status."),
    ("Transportation", 250.0, "Add a budget for 'Transportation' not exceeding $250, and ensure it shows up in status."),
    ("Gifts", 150.0, "Configure a 'Gifts' budget at a maximum of $150, and check the status to be certain."),
    ("Hobbies", 120.0, "I need a 'Hobbies' budget implemented at $120. Verify the status once it is done."),
    ("Personal Care", 80.0, "Establish a 'Personal Care' budget boundary of $80, and immediately check the budget status.")
]
for cat, limit, task_desc in g7_data:
    tb = TraceBuilder(task_desc)
    tb.step("To manage spending limits, I will navigate to the Budgets domain from the primary Home interface.", 3, new_state="Budgets")
    tb.step(f"I will now create the new budget for '{cat}' with the specified maximum limit of ${limit}.", 1, args={"category": cat, "limit": limit}, result=f"Success: Budget for '{cat}' set to ${limit}")
    mem_note = f"Successfully set the {cat} budget to ${limit}, proceeding to verify its status in the system."
    tb.step("I will record that the budget creation step is complete before moving on to verify it.", 3, args={"note": mem_note}, memory_note=mem_note)
    tb.step(f"Now I will check the budget status for '{cat}' to ensure it is properly active.", 2, args={"category": cat}, result=f"Status: '{cat}' budget is active at ${limit}.")
    tb.step("The new budget was successfully created and its active status was confirmed, completing the requested task.", 5)
    traces.append(tb.build())

assert len(traces) == 60

random.shuffle(traces)

with open("dataset_unique.jsonl", "w") as f:
    for t in traces:
        f.write(json.dumps(t) + "\n")

print("Generated 60 highly unique traces properly distributed across primary domains.")
