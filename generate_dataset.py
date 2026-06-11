import json
import random
import string

def get_menu_text(state):
    menus = {
        'Home': '''  1. Properties — navigate to Properties tools
  2. Tenants — navigate to Tenants tools
  3. Leases — navigate to Leases tools
  4. Maintenance — navigate to Maintenance tools
  5. Finances — navigate to Finances tools
  6. Viewings — navigate to Viewings tools
  7. Documents — navigate to Documents tools
  8. MEM [note: `string`] — store a memory note (10–20 words exactly)
  9. BACK — go to previous state
  10. DONE — task is complete''',
        'Properties': '''  1. add_property [address: `string`, type: `string`]
  2. update_rent [id: `int`, rent: `float`]
  3. list_properties
  4. MEM [note: `string`]
  5. BACK
  6. DONE''',
        'Tenants': '''  1. add_tenant [name: `string`, email: `email`]
  2. assign_tenant_to_property [tenant_id: `int`, prop_id: `int`]
  3. evict_tenant [id: `int`]
  4. MEM [note: `string`]
  5. BACK
  6. DONE''',
        'Leases': '''  1. create_lease [prop_id: `int`, start: `date`, end: `date`]
  2. renew_lease [lease_id: `int`, months: `int`]
  3. MEM [note: `string`]
  4. BACK
  5. DONE''',
        'Maintenance': '''  1. create_ticket [prop_id: `int`, issue: `string`]
  2. assign_contractor [ticket_id: `int`, contractor: `string`]
  3. close_ticket [id: `int`]
  4. MEM [note: `string`]
  5. BACK
  6. DONE''',
        'Finances': '''  1. log_rent_payment [tenant_id: `int`, amount: `float`]
  2. log_expense [prop_id: `int`, amount: `float`]
  3. generate_pnl_report
  4. MEM [note: `string`]
  5. BACK
  6. DONE''',
        'Viewings': '''  1. schedule_viewing [prop_id: `int`, time: `time`]
  2. list_viewings
  3. MEM [note: `string`]
  4. BACK
  5. DONE''',
        'Documents': '''  1. upload_contract [prop_id: `int`, path: `path`]
  2. send_document_for_signature [tenant_id: `int`, doc_id: `int`]
  3. MEM [note: `string`]
  4. BACK
  5. DONE'''
    }
    return menus[state]

def format_turn(task, state, memory, result, assistant_dict):
    user_parts = [f"USER:\n[TASK]: {task}", f"[STATE]: {state}"]
    if memory:
        user_parts.append(f"[MEMORY]: {memory}")
    if result:
        user_parts.append(f"[RESULT]: {result}")
    user_parts.append(f"[MENU]:\n{get_menu_text(state)}")

    return {
        "user": "\n".join(user_parts),
        "assistant": json.dumps(assistant_dict)
    }

def count_words(s):
    return len(s.split())

def validate_trace(trace):
    turns = trace["turns"]
    if not (3 <= len(turns) - 1 <= 8):
        print("Trace length invalid:", len(turns) - 1)
        return False
    # Validate reason length in sentences
    for turn in turns:
        assist = json.loads(turn["assistant"])
        sentences = [s for s in assist["reason"].replace('!', '.').replace('?', '.').split('.') if s.strip()]
        if not (2 <= len(sentences) <= 4):
            print(f"Reason sentence count invalid: {len(sentences)} in '{assist['reason']}'")
            return False
    return True

def t_web_research_viewings(idx):
    task = f"Research available viewings online and save the contract for property {idx} to /docs/viewing.pdf."
    turns = []
    memory = None

    turns.append(format_turn(
        task, "Home", memory, None,
        {"reason": "I need to research viewings first to find the right property details. Navigating to the Viewings domain will allow me to check the schedule.", "action": 6}
    ))

    turns.append(format_turn(
        task, "Viewings", memory, None,
        {"reason": "I must list the existing viewings to simulate checking online slots. This will help me locate the correct property information.", "action": 2}
    ))

    note_words = f"Researched viewings online successfully, now proceeding to upload the contract for property {idx} as requested."
    turns.append(format_turn(
        task, "Viewings", memory, f"1. Viewing for property {idx} at 10:00\n2. Viewing for property {idx+1} at 11:00",
        {"reason": "I have found the viewing times needed for my research. I will save a memory note before navigating to the Documents section.", "action": 3, "args": {"note": note_words}}
    ))
    memory = note_words

    turns.append(format_turn(
        task, "Viewings", memory, None,
        {"reason": "My online research phase is complete for now. I need to go back to the Home menu to reach the Documents domain.", "action": 4}
    ))

    turns.append(format_turn(
        task, "Home", memory, None,
        {"reason": "I am back at the Home menu. Now I will enter the Documents domain to handle the contract file upload.", "action": 7}
    ))

    turns.append(format_turn(
        task, "Documents", memory, None,
        {"reason": "I am ready to upload the contract file to the designated path. I will use the upload tool with the details from my research.", "action": 1, "args": {"prop_id": idx, "path": "/docs/viewing.pdf"}}
    ))

    turns.append(format_turn(
        task, "Documents", memory, f"Contract uploaded to /docs/viewing.pdf.",
        {"reason": "The file upload was successful according to the tool output. This fulfills the task requirements, so I am completely done.", "action": 5}
    ))

    return {"task": task, "turns": turns}

def t_web_research_docs(idx):
    task = f"Research property contracts online and then schedule a viewing for property {idx} at 12:00."
    turns = []
    memory = None

    turns.append(format_turn(
        task, "Home", memory, None,
        {"reason": "The task asks me to look into contracts first. I will open the Documents domain to review the necessary paperwork.", "action": 7}
    ))

    note_words = f"Completed contract research online for property {idx}, now need to schedule a viewing at 12:00."
    turns.append(format_turn(
        task, "Documents", memory, None,
        {"reason": "I have gathered the required contract information from my research. Storing this in memory will ensure I remember to schedule the viewing next.", "action": 3, "args": {"note": note_words}}
    ))
    memory = note_words

    turns.append(format_turn(
        task, "Documents", memory, None,
        {"reason": "I must leave the Documents area to continue with the task. Returning to the Home menu is the only way to switch domains.", "action": 4}
    ))

    turns.append(format_turn(
        task, "Home", memory, None,
        {"reason": "From the main menu, I can now proceed to handle the calendar. I will navigate into Viewings to set up the appointment.", "action": 6}
    ))

    turns.append(format_turn(
        task, "Viewings", memory, None,
        {"reason": "I need to schedule the appointment as specified in the instructions. I will input the correct property ID and the 12:00 time slot.", "action": 1, "args": {"prop_id": idx, "time": "12:00"}}
    ))

    turns.append(format_turn(
        task, "Viewings", memory, f"Viewing for property {idx} scheduled at 12:00.",
        {"reason": "The system confirms the viewing has been successfully booked. All parts of the user request are finished, so I will mark this as done.", "action": 5}
    ))

    return {"task": task, "turns": turns}

def t_email_calendar(idx):
    task = f"Read the email requesting a calendar appointment and schedule a viewing for property {idx} at 15:00."
    turns = []
    memory = None

    turns.append(format_turn(
        task, "Home", memory, None,
        {"reason": "I have received an email request that involves scheduling. I need to open the Viewings menu to manage the calendar events.", "action": 6}
    ))

    turns.append(format_turn(
        task, "Viewings", memory, None,
        {"reason": "Before adding a new appointment, I should see what is already booked. Listing the viewings will let me check for conflicts.", "action": 2}
    ))

    note_words = f"Checked calendar and read email request for property {idx}, proceeding to schedule the viewing at 15:00."
    turns.append(format_turn(
        task, "Viewings", memory, "No conflicting viewings found at 15:00.",
        {"reason": "The schedule is clear for the requested time slot. I will make a quick note to confirm I processed the email request.", "action": 3, "args": {"note": note_words}}
    ))
    memory = note_words

    turns.append(format_turn(
        task, "Viewings", memory, None,
        {"reason": "Now it is safe to add the new appointment to the calendar. I will schedule the viewing at 15:00 for the specified property.", "action": 1, "args": {"prop_id": idx, "time": "15:00"}}
    ))

    turns.append(format_turn(
        task, "Viewings", memory, f"Viewing scheduled for property {idx} at 15:00.",
        {"reason": "The appointment has been successfully recorded in the calendar. My scheduling task is complete and requires no further action.", "action": 5}
    ))

    return {"task": task, "turns": turns}

def t_python_code(idx):
    task = f"Write a script to update rent for property {idx} to 1600.0, handle any execution errors."
    turns = []
    memory = None

    turns.append(format_turn(
        task, "Home", memory, None,
        {"reason": "I am asked to write and run code to adjust property details. I will enter the Properties domain where this tool resides.", "action": 1}
    ))

    note_words = f"Attempting to update rent for property {idx} to 1600.0, preparing to handle potential script execution errors."
    turns.append(format_turn(
        task, "Properties", memory, None,
        {"reason": "Executing scripts can sometimes result in errors. I will save a memory note about my objective before attempting the programmatic update.", "action": 4, "args": {"note": note_words}}
    ))
    memory = note_words

    turns.append(format_turn(
        task, "Properties", memory, None,
        {"reason": "I will run the update command now. However, I am guessing an invalid property ID of 999 to simulate an initial script failure.", "action": 2, "args": {"id": 999, "rent": 1600.0}}
    ))

    turns.append(format_turn(
        task, "Properties", memory, "Error: Property ID 999 not found during script execution.",
        {"reason": "As expected, the script execution failed because the ID was wrong. I will list all properties to find the correct valid ID.", "action": 3}
    ))

    turns.append(format_turn(
        task, "Properties", memory, f"1. Property {idx} at 123 Main St",
        {"reason": "The correct property ID is clearly shown in the output now. I will debug my input and re-run the rent update.", "action": 2, "args": {"id": idx, "rent": 1600.0}}
    ))

    turns.append(format_turn(
        task, "Properties", memory, f"Rent updated to 1600.0 for property {idx}.",
        {"reason": "The script execution error has been fully handled and resolved. The rent is updated, so my work here is finished.", "action": 6}
    ))

    return {"task": task, "turns": turns}

def t_load_data(idx):
    task = f"Load financial data by logging rent and expenses for property {idx}, then compute the PnL report."
    turns = []
    memory = None

    turns.append(format_turn(
        task, "Home", memory, None,
        {"reason": "I need to work with numbers and compute a result report. The Finances menu is the correct place to handle this data.", "action": 5}
    ))

    turns.append(format_turn(
        task, "Finances", memory, None,
        {"reason": "My first step is to load the incoming revenue data into the system. I will log the rent payment amount.", "action": 1, "args": {"tenant_id": idx, "amount": 1300.0}}
    ))

    turns.append(format_turn(
        task, "Finances", memory, f"Logged rent payment of 1300.0.",
        {"reason": "Next, I need to load the outgoing costs associated with the property. I will record the expense data point.", "action": 2, "args": {"prop_id": idx, "amount": 400.0}}
    ))

    note_words = f"Loaded financial data for property {idx}, now preparing to compute and plot the PnL report result."
    turns.append(format_turn(
        task, "Finances", memory, f"Logged expense of 400.0.",
        {"reason": "The data entry is complete, so I am ready for the calculation phase. I will store a note documenting my progress.", "action": 4, "args": {"note": note_words}}
    ))
    memory = note_words

    turns.append(format_turn(
        task, "Finances", memory, None,
        {"reason": "With all data loaded, I can compute the final result. I will generate the Profit and Loss report now.", "action": 3}
    ))

    turns.append(format_turn(
        task, "Finances", memory, "PnL Report: Revenue: 1300.0, Expenses: 400.0, Net: 900.0",
        {"reason": "The report shows the correctly calculated net result. This completes the data loading and computation task.", "action": 6}
    ))

    return {"task": task, "turns": turns}

def t_multi_leases(idx):
    task = f"Create a lease for property {idx} starting 2024-05-01 and then create a maintenance ticket."
    turns = []
    memory = None

    turns.append(format_turn(
        task, "Home", memory, None,
        {"reason": "I have a task that spans multiple domains. I will begin by navigating to Leases to set up the contract.", "action": 3}
    ))

    turns.append(format_turn(
        task, "Leases", memory, None,
        {"reason": "I need to establish a new lease using the provided dates. I am submitting the property ID and the starting timeframe.", "action": 1, "args": {"prop_id": idx, "start": "2024-05-01", "end": "2025-05-01"}}
    ))

    note_words = f"Lease created successfully for property {idx}, now I need to navigate to Maintenance to create a ticket."
    turns.append(format_turn(
        task, "Leases", memory, f"Lease {idx} created.",
        {"reason": "The lease is active. I will write a quick memory note to ensure I transition to the second domain next.", "action": 3, "args": {"note": note_words}}
    ))
    memory = note_words

    turns.append(format_turn(
        task, "Leases", memory, None,
        {"reason": "I cannot reach the maintenance area from here directly. I must go back to the Home menu first.", "action": 4}
    ))

    turns.append(format_turn(
        task, "Home", memory, None,
        {"reason": "I am back at the root level. Now I will open the Maintenance menu to address the second part of my task.", "action": 4}
    ))

    turns.append(format_turn(
        task, "Maintenance", memory, None,
        {"reason": "I need to log an issue for the property. I will create a new maintenance ticket with a placeholder issue description.", "action": 1, "args": {"prop_id": idx, "issue": "Routine checkup"}}
    ))

    turns.append(format_turn(
        task, "Maintenance", memory, f"Ticket 10{idx} created.",
        {"reason": "The ticket has been successfully registered in the system. Both domain actions are complete, so I am done.", "action": 6}
    ))

    return {"task": task, "turns": turns}

def t_multi_tenants(idx):
    task = f"Assign tenant {idx} to property {idx} and then update its rent to 2000.0."
    turns = []
    memory = None

    turns.append(format_turn(
        task, "Home", memory, None,
        {"reason": "This request involves linking a tenant before modifying property details. I will enter the Tenants domain first.", "action": 2}
    ))

    turns.append(format_turn(
        task, "Tenants", memory, None,
        {"reason": "I need to execute the assignment operation. This will link the specific tenant ID to the appropriate property ID.", "action": 2, "args": {"tenant_id": idx, "prop_id": idx}}
    ))

    note_words = f"Tenant {idx} assigned to property {idx}, now I need to update the rent in the Properties domain."
    turns.append(format_turn(
        task, "Tenants", memory, f"Tenant {idx} assigned.",
        {"reason": "The assignment was successful. I will leave a memory note to remind myself to handle the rent update next.", "action": 4, "args": {"note": note_words}}
    ))
    memory = note_words

    turns.append(format_turn(
        task, "Tenants", memory, None,
        {"reason": "The rent tool is not located here. I have to travel back to the Home screen to switch contexts.", "action": 5}
    ))

    turns.append(format_turn(
        task, "Home", memory, None,
        {"reason": "From the Home menu, I can easily reach the property settings. I will select the Properties domain now.", "action": 1}
    ))

    turns.append(format_turn(
        task, "Properties", memory, None,
        {"reason": "I will change the financial terms for the property as requested. Applying the new rent value of 2000.0 is the final step.", "action": 2, "args": {"id": idx, "rent": 2000.0}}
    ))

    turns.append(format_turn(
        task, "Properties", memory, f"Rent updated to 2000.0.",
        {"reason": "The new rent value is confirmed in the output. Since both domains were visited and updated, the task is finished.", "action": 6}
    ))

    return {"task": task, "turns": turns}

def t_back_correction(idx):
    task = f"Assign contractor 'FixIt' to maintenance ticket {idx}."
    turns = []
    memory = None

    turns.append(format_turn(
        task, "Home", memory, None,
        {"reason": "I need to assign someone to do work. I mistakenly believe this might be handled in the Leases domain.", "action": 3}
    ))

    note_words = f"I navigated to the Leases domain to assign a contractor, but realised this is the wrong menu."
    turns.append(format_turn(
        task, "Leases", memory, None,
        {"reason": "Looking at this menu, I realize my mistake. I will store a note acknowledging that I chose the wrong domain.", "action": 3, "args": {"note": note_words}}
    ))
    memory = note_words

    turns.append(format_turn(
        task, "Leases", memory, None,
        {"reason": "I cannot complete the task from this location. I must use the BACK function to correct my path.", "action": 4}
    ))

    turns.append(format_turn(
        task, "Home", memory, None,
        {"reason": "Now I am back at the start. Maintenance is clearly the correct place for contractor assignments, so I will head there.", "action": 4}
    ))

    turns.append(format_turn(
        task, "Maintenance", memory, None,
        {"reason": "I see the correct option for the assignment task. I will attach the contractor FixIt to the requested ticket.", "action": 2, "args": {"ticket_id": idx, "contractor": "FixIt"}}
    ))

    turns.append(format_turn(
        task, "Maintenance", memory, f"Contractor FixIt assigned to ticket {idx}.",
        {"reason": "The output confirms the contractor was successfully assigned. The error was corrected and the task is fully accomplished.", "action": 6}
    ))

    return {"task": task, "turns": turns}

def t_short(idx):
    task = f"Upload the contract for property {idx} to /docs/final.pdf immediately."
    turns = []
    memory = None

    turns.append(format_turn(
        task, "Home", memory, None,
        {"reason": "This is a straightforward request to handle a file. I will go directly to the Documents domain to find the upload tool.", "action": 7}
    ))

    note_words = f"Uploading the final contract document for property {idx} to the requested path /docs/final.pdf right now."
    turns.append(format_turn(
        task, "Documents", memory, None,
        {"reason": "I want to document that I am starting the upload process. A quick memory note will keep track of my action.", "action": 3, "args": {"note": note_words}}
    ))
    memory = note_words

    turns.append(format_turn(
        task, "Documents", memory, None,
        {"reason": "I am ready to transfer the file to the system. I will run the upload command with the given property ID and file path.", "action": 1, "args": {"prop_id": idx, "path": "/docs/final.pdf"}}
    ))

    turns.append(format_turn(
        task, "Documents", memory, f"Contract uploaded successfully.",
        {"reason": "The document upload process confirmed success immediately. There is nothing left to do, so I am done.", "action": 5}
    ))

    return {"task": task, "turns": turns}

def generate_all():
    traces = []

    for i in range(1, 6):
        t = t_web_research_viewings(i)
        assert validate_trace(t)
        traces.append(t)
    for i in range(6, 11):
        t = t_web_research_docs(i)
        assert validate_trace(t)
        traces.append(t)

    for i in range(11, 19):
        t = t_email_calendar(i)
        assert validate_trace(t)
        traces.append(t)

    for i in range(19, 27):
        t = t_python_code(i)
        assert validate_trace(t)
        traces.append(t)

    for i in range(27, 35):
        t = t_load_data(i)
        assert validate_trace(t)
        traces.append(t)

    for i in range(35, 40):
        t = t_multi_leases(i)
        assert validate_trace(t)
        traces.append(t)
    for i in range(40, 45):
        t = t_multi_tenants(i)
        assert validate_trace(t)
        traces.append(t)

    for i in range(45, 53):
        t = t_back_correction(i)
        assert validate_trace(t)
        traces.append(t)

    for i in range(53, 61):
        t = t_short(i)
        assert validate_trace(t)
        traces.append(t)

    return traces

traces = generate_all()
assert len(traces) == 60

filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + ".jsonl"

with open(filename, "w") as f:
    for trace in traces:
        f.write(json.dumps(trace) + "\n")

print(f"{filename}")
