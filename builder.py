import json
import random
import string
import copy

DOMAINS = {
    "Leads": {
        "id": 1,
        "tools": [
            ("add_lead", ["name: `string`", "email: `email`"], ["name", "email"]),
            ("update_lead_status", ["lead_id: `int`", "status: `string`"], ["lead_id", "status"]),
            ("list_leads", [], [])
        ]
    },
    "Contacts": {
        "id": 2,
        "tools": [
            ("add_contact", ["name: `string`", "phone: `string`"], ["name", "phone"]),
            ("link_contact_to_account", ["contact_id: `int`", "account_id: `int`"], ["contact_id", "account_id"])
        ]
    },
    "Accounts": {
        "id": 3,
        "tools": [
            ("create_account", ["company: `string`"], ["company"]),
            ("list_accounts", [], []),
            ("get_account_details", ["id: `int`"], ["id"])
        ]
    },
    "Deals": {
        "id": 4,
        "tools": [
            ("create_deal", ["title: `string`", "value: `float`"], ["title", "value"]),
            ("move_deal_stage", ["deal_id: `int`", "stage: `string`"], ["deal_id", "stage"]),
            ("list_deals", [], [])
        ]
    },
    "Activities": {
        "id": 5,
        "tools": [
            ("log_call", ["lead_id: `int`", "notes: `string`"], ["lead_id", "notes"]),
            ("schedule_meeting", ["lead_id: `int`", "date: `date`"], ["lead_id", "date"]),
            ("log_email", ["lead_id: `int`"], ["lead_id"])
        ]
    },
    "Reports": {
        "id": 6,
        "tools": [
            ("get_sales_forecast", [], []),
            ("get_win_rate", [], []),
            ("generate_pipeline_report", [], [])
        ]
    },
    "Campaigns": {
        "id": 7,
        "tools": [
            ("create_campaign", ["name: `string`", "budget: `float`"], ["name", "budget"]),
            ("add_leads_to_campaign", ["campaign_id: `int`", "leads: `list`"], ["campaign_id", "leads"]),
            ("get_campaign_roi", ["id: `int`"], ["id"])
        ]
    }
}

HOME_MENU = """  1. Leads — navigate to Leads tools
  2. Contacts — navigate to Contacts tools
  3. Accounts — navigate to Accounts tools
  4. Deals — navigate to Deals tools
  5. Activities — navigate to Activities tools
  6. Reports — navigate to Reports tools
  7. Campaigns — navigate to Campaigns tools
  8. MEM [note: `string`] — store a memory note (10–20 words exactly)
  9. BACK — go to previous state
  10. DONE — task is complete"""

def get_menu_text(state):
    if state == "Home":
        return HOME_MENU
    else:
        domain = DOMAINS[state]
        lines = []
        for i, t in enumerate(domain["tools"], start=1):
            if t[1]:
                lines.append(f"  {i}. {t[0]} [{', '.join(t[1])}]")
            else:
                lines.append(f"  {i}. {t[0]}")
        start_idx = len(domain["tools"]) + 1
        lines.append(f"  {start_idx}. MEM [note: `string`]")
        lines.append(f"  {start_idx + 1}. BACK")
        lines.append(f"  {start_idx + 2}. DONE")
        return "\n".join(lines)

def get_menu_map(state):
    if state == "Home":
        return {
            "Leads": 1, "Contacts": 2, "Accounts": 3, "Deals": 4, "Activities": 5, "Reports": 6, "Campaigns": 7,
            "MEM": 8, "BACK": 9, "DONE": 10
        }
    else:
        domain = DOMAINS[state]
        m = {}
        for i, t in enumerate(domain["tools"], start=1):
            m[t[0]] = i
        start_idx = len(domain["tools"]) + 1
        m["MEM"] = start_idx
        m["BACK"] = start_idx + 1
        m["DONE"] = start_idx + 2
        return m

def validate_mem(note):
    words = note.split()
    assert 10 <= len(words) <= 20, f"MEM note must be 10-20 words, got {len(words)}: '{note}'"


import sys

def build_trace(task, steps):
    # steps is a list of dicts:
    # {
    #   "action": string (name of action or tool or "MEM" or "BACK" or "DONE" or domain name like "Leads"),
    #   "args": dict (optional),
    #   "result": string (optional, what the tool returns),
    #   "reason": string
    # }

    state = "Home"
    memory = None

    turns = []

    for i, step in enumerate(steps):
        # build USER prompt
        user_prompt = f"USER:\n[TASK]: {task}\n[STATE]: {state}\n"
        if memory is not None:
            user_prompt += f"[MEMORY]: {memory}\n"
        if i > 0 and "result" in steps[i-1] and steps[i-1]["result"] is not None:
            user_prompt += f"[RESULT]: {steps[i-1]['result']}\n"
        user_prompt += f"[MENU]:\n{get_menu_text(state)}"

        # determine action index
        m = get_menu_map(state)
        act_str = step["action"]
        if act_str not in m:
            print(f"ERROR: Invalid action '{act_str}' in state '{state}' for task '{task}'")
            sys.exit(1)
        act_idx = m[act_str]

        # build ASSISTANT response
        assistant_dict = {
            "reason": step["reason"],
            "action": act_idx
        }
        if "args" in step and step["args"]:
            assistant_dict["args"] = step["args"]

        turns.append({
            "user": user_prompt,
            "assistant": json.dumps(assistant_dict)
        })

        # update state
        if act_str in ["Leads", "Contacts", "Accounts", "Deals", "Activities", "Reports", "Campaigns"]:
            state = act_str
        elif act_str == "MEM":
            memory = step["args"]["note"]
            validate_mem(memory)
        elif act_str == "BACK":
            state = "Home" # Since we can only go from Home to a domain, back is always Home
        elif act_str == "DONE":
            break

    return {"task": task, "turns": turns}
