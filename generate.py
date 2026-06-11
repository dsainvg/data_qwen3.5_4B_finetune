import json
import random
import uuid

# Re-use builder logic
from builder import build_trace, DOMAINS, get_menu_text, get_menu_map, validate_mem

traces = []

def word_count(s):
    return len(s.split())

def generate_mem_note(base_words, padding_words):
    # Ensure exactly 10-20 words
    res = base_words + " " + padding_words
    words = res.split()
    if len(words) < 10:
        words += ["extra", "word"] * (10 - len(words))
    elif len(words) > 20:
        words = words[:20]
    return " ".join(words)

# Data generators
first_names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy", "Mallory", "Nina", "Oscar", "Peggy", "Trent", "Victor", "Walter"]
last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]
companies = ["TechCorp", "Innova", "CloudNet", "DataSys", "AlphaBeta", "GammaInc", "OmegaLLC"]

def get_name():
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# Category 1: Web research then save -> Accounts get_account_details (research) then Activities log_call (save)
# Or Reports get_sales_forecast then Campaigns create_campaign
# We will do Accounts -> BACK -> Activities
# So these are multi-domain as well, which increases BACK count.
for i in range(10):
    name = get_name()
    company = random.choice(companies)
    task_desc = f"Look up the account details for {company} ID {i+100} and log a note about their recent web activity for lead {i+50}."
    mem_note = generate_mem_note(f"Checked account {company} details", "now I need to log the activity note for the lead user.")

    steps = [
        {"action": "Accounts", "reason": "I need to look up account details, which requires the Accounts domain."},
        {"action": "get_account_details", "args": {"id": i+100}, "reason": f"Fetching the details for {company} using their account ID.", "result": f"Account: {company}, Status: Active, Web Activity: High"},
        {"action": "MEM", "args": {"note": mem_note}, "reason": "I should store the retrieved account details so I can log them accurately in the next step."},
        {"action": "BACK", "reason": "I need to switch to the Activities domain to log the call, so I must return to the Home menu first."},
        {"action": "Activities", "reason": "Navigating to Activities to log the note for the lead."},
        {"action": "log_call", "args": {"lead_id": i+50, "notes": f"Account {company} has High web activity."}, "reason": "Logging the call with the web activity details I found."},
        {"action": "DONE", "reason": "The account details have been retrieved and logged to the lead successfully."}
    ]
    traces.append(build_trace(task_desc, steps))

# Category 2: Email reading and calendar scheduling -> Activities log_email and schedule_meeting
for i in range(8):
    lead_id = 200 + i
    date = f"2024-10-0{i+1}"
    task_desc = f"Read the latest email for lead {lead_id} and schedule a follow-up meeting with them for {date}."
    mem_note = generate_mem_note(f"Logged the email for lead {lead_id}", f"now proceeding to schedule a meeting for {date} to follow up.")

    steps = [
        {"action": "Activities", "reason": "Both logging an email and scheduling a meeting are handled in the Activities domain."},
        {"action": "log_email", "args": {"lead_id": lead_id}, "reason": "Logging the latest email to ensure we have a record before scheduling.", "result": f"Email logged for lead {lead_id}. Contents: 'Please schedule a demo.'"},
        {"action": "MEM", "args": {"note": mem_note}, "reason": "Storing a reminder that the email is logged and I must now schedule the follow-up meeting."},
        {"action": "schedule_meeting", "args": {"lead_id": lead_id, "date": date}, "reason": f"Scheduling the meeting for {date} as requested based on the logged email."},
        {"action": "DONE", "reason": "Email has been logged and the meeting is scheduled, completing the task."}
    ]
    traces.append(build_trace(task_desc, steps))

# Category 3: Write code, handle error -> Campaigns create_campaign with invalid budget, fix and rerun
for i in range(8):
    camp_name = f"Promo Q{i%4 + 1}"
    task_desc = f"Create a new campaign called '{camp_name}' with a budget of -500, and if that fails, use 5000."
    mem_note = generate_mem_note("Attempted to create campaign with negative budget", "it will likely fail so I will fix it and retry.")

    steps = [
        {"action": "Campaigns", "reason": "I need to create a campaign, which is found in the Campaigns domain."},
        {"action": "MEM", "args": {"note": mem_note}, "reason": "I am noting that the initial requested budget is negative, which might cause an error."},
        {"action": "create_campaign", "args": {"name": camp_name, "budget": -500.0}, "reason": "Attempting to create the campaign with the provided initial budget of -500.", "result": "Error: Budget cannot be negative."},
        {"action": "create_campaign", "args": {"name": camp_name, "budget": 5000.0}, "reason": "The previous attempt failed due to a negative budget error, so I am retrying with a valid budget of 5000."},
        {"action": "DONE", "reason": "The campaign was successfully created after correcting the budget error."}
    ]
    traces.append(build_trace(task_desc, steps))

# Category 4: Load data, plot result -> Reports generate_pipeline_report, then Deals create_deal
for i in range(8):
    deal_title = f"Data Deal {i}"
    task_desc = f"Generate the pipeline report to calculate the average deal size, then create a new deal '{deal_title}' with that computed value."
    mem_note = generate_mem_note(f"Pipeline report generated", f"the computed average deal value is fifty thousand so creating deal.")

    steps = [
        {"action": "Reports", "reason": "Generating a pipeline report to calculate data belongs in the Reports domain."},
        {"action": "generate_pipeline_report", "reason": "Running the report to compute the average deal size across the pipeline.", "result": "Pipeline Report: 15 deals, Average Size: 50000.0"},
        {"action": "MEM", "args": {"note": mem_note}, "reason": "Storing the calculated average deal size of 50000 so I can use it to create the new deal."},
        {"action": "BACK", "reason": "I need to create a deal now, so I must return to the Home menu to access the Deals domain."},
        {"action": "Deals", "reason": "Navigating to the Deals domain to create the new deal using the computed value."},
        {"action": "create_deal", "args": {"title": deal_title, "value": 50000.0}, "reason": "Creating the new deal using the calculated average value from the pipeline report."},
        {"action": "DONE", "reason": "The data was calculated from the report and the deal was successfully created."}
    ]
    traces.append(build_trace(task_desc, steps))

# Category 5: Multi-domain -> Leads add_lead, then Contacts add_contact
for i in range(10):
    name = get_name()
    task_desc = f"Add {name} as a new lead with email {name.split()[0].lower()}@test.com, then also add them as a contact with phone 555-010{i}."
    mem_note = generate_mem_note(f"Successfully added {name} as a new lead", "now I must navigate to contacts to add their phone number.")

    steps = [
        {"action": "Leads", "reason": "First, I need to add the user as a lead, which requires the Leads domain."},
        {"action": "add_lead", "args": {"name": name, "email": f"{name.split()[0].lower()}@test.com"}, "reason": f"Adding the new lead {name} with their email address.", "result": f"Lead added with ID {300+i}"},
        {"action": "MEM", "args": {"note": mem_note}, "reason": "Recording that the lead was created successfully so I can proceed to add them as a contact."},
        {"action": "BACK", "reason": "Since I need to add a contact, I must go back to the Home state before entering the Contacts domain."},
        {"action": "Contacts", "reason": "Entering the Contacts domain to fulfill the second part of the user's request."},
        {"action": "add_contact", "args": {"name": name, "phone": f"555-010{i}"}, "reason": "Adding the individual as a contact with their provided phone number."},
        {"action": "DONE", "reason": "Both the lead and the contact have been successfully created across different domains."}
    ]
    traces.append(build_trace(task_desc, steps))

# Category 6: BACK correction -> User wants Contacts but agent goes to Accounts first
for i in range(8):
    name = get_name()
    task_desc = f"Link contact {400+i} to account {500+i} to organize the new company directory structure."

    steps = [
        {"action": "Accounts", "reason": "The task mentions an account directory, so I might need to link them in the Accounts domain."},
        {"action": "BACK", "reason": "Wait, linking a contact to an account is actually a Contacts domain tool. I must back out and correct my navigation."},
        {"action": "Contacts", "reason": "Navigating to the Contacts domain, which contains the correct tool for linking contacts to accounts."},
        {"action": "link_contact_to_account", "args": {"contact_id": 400+i, "account_id": 500+i}, "reason": "Executing the tool to link the specified contact to the designated account."},
        {"action": "DONE", "reason": "The contact has been properly linked to the account as requested."}
    ]
    traces.append(build_trace(task_desc, steps))

# Category 7: Short tasks -> Deals list_deals -> DONE
for i in range(8):
    task_desc = f"Quickly check the list of all current deals for regional manager {i+1}."

    steps = [
        {"action": "Deals", "reason": "I need to view the current deals, so I will navigate to the Deals domain."},
        {"action": "list_deals", "reason": "Retrieving the list of deals for the user to review.", "result": "Deals: Deal A ($100), Deal B ($200)"},
        {"action": "DONE", "reason": "The list of deals has been retrieved and the short task is complete."}
    ]
    traces.append(build_trace(task_desc, steps))

# Validation:
print(f"Total traces generated: {len(traces)}")
assert len(traces) == 60

# Write to file
filename = "sft_qwen_" + uuid.uuid4().hex[:8] + ".jsonl"
with open(filename, "w") as f:
    for t in traces:
        f.write(json.dumps(t) + "\n")
print(f"Wrote to {filename}")
