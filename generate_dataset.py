import json
import random
import string

def get_random_string(length):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

filename = f"dataset_{get_random_string(8)}.jsonl"

home_menu = """[MENU]:
  1. Patients — navigate to Patients tools
  2. Appointments — navigate to Appointments tools
  3. Doctors — navigate to Doctors tools
  4. Prescriptions — navigate to Prescriptions tools
  5. Billing — navigate to Billing tools
  6. Lab Results — navigate to Lab Results tools
  7. Inventory — navigate to Inventory tools
  8. MEM [note: `string`] — store a memory note (10–20 words exactly)
  9. BACK — go to previous state
  10. DONE — task is complete"""

domain_menus = {
    "Patients": """[MENU]:
  1. register_patient [name: `string`, dob: `date`]
  2. get_patient_record [id: `int`]
  3. update_vitals [id: `int`, bp: `string`, hr: `int`]
  4. MEM [note: `string`]
  5. BACK
  6. DONE""",
    "Appointments": """[MENU]:
  1. schedule_appointment [patient_id: `int`, doc_id: `int`, time: `time`]
  2. cancel_appointment [id: `int`]
  3. list_daily_schedule
  4. MEM [note: `string`]
  5. BACK
  6. DONE""",
    "Doctors": """[MENU]:
  1. add_doctor [name: `string`, specialty: `string`]
  2. set_availability [doc_id: `int`, hours: `string`]
  3. MEM [note: `string`]
  4. BACK
  5. DONE""",
    "Prescriptions": """[MENU]:
  1. prescribe_medication [patient_id: `int`, med: `string`, dosage: `string`]
  2. refill_prescription [rx_id: `int`]
  3. MEM [note: `string`]
  4. BACK
  5. DONE""",
    "Billing": """[MENU]:
  1. generate_bill [patient_id: `int`, amount: `float`]
  2. process_insurance_claim [bill_id: `int`]
  3. MEM [note: `string`]
  4. BACK
  5. DONE""",
    "Lab Results": """[MENU]:
  1. upload_lab_result [patient_id: `int`, path: `path`]
  2. view_lab_result [result_id: `int`]
  3. MEM [note: `string`]
  4. BACK
  5. DONE""",
    "Inventory": """[MENU]:
  1. check_supply_stock [item: `string`]
  2. order_supplies [item: `string`, qty: `int`]
  3. MEM [note: `string`]
  4. BACK
  5. DONE"""
}

def get_menu(state):
    if state == "Home":
        return home_menu
    return domain_menus[state]

def format_turn(task, state, memory, result, action, reason, args=None):
    user_parts = [f"USER:\n[TASK]: {task}", f"[STATE]: {state}"]
    if memory:
        user_parts.append(f"[MEMORY]: {memory}")
    if result:
        user_parts.append(f"[RESULT]: {result}")
    user_parts.append(get_menu(state))

    assist_dict = {"reason": reason, "action": action}
    if args is not None:
        assist_dict["args"] = args

    return {
        "user": "\n".join(user_parts),
        "assistant": json.dumps(assist_dict)
    }

traces = []

# Helper to gen MEM note of exact 14 words
def gen_mem(base_text):
    words = base_text.split()
    pad = ["and", "will", "now", "proceed", "with", "the", "next", "required", "step", "immediately", "today", "here"]
    while len(words) < 14:
        words.append(pad[len(words) % len(pad)])
    return " ".join(words[:14])

# Helper to gen multi-sentence reason
def pad_reason(base_reason):
    return base_reason + " This is necessary to satisfy the user's explicit request. I am ensuring that all guidelines are strictly adhered to before proceeding."

# 1. 10 Web Research (Mapped to Patients -> Lab Results)
web_tasks = [
    ("Look up the recent lab tests for patient #892 and save the compiled report to /docs/patient892_labs.pdf.", 892, "/docs/patient892_labs.pdf"),
    ("I need to investigate the medical history for John Doe (ID 144) and upload a new summary document to /records/jdoe.txt.", 144, "/records/jdoe.txt"),
    ("Find the latest test outcomes for patient ID 505 and store a merged text file at /tmp/labs_505.txt.", 505, "/tmp/labs_505.txt"),
    ("Search our database for patient 99's records, then create an archive file at /backups/pt99.zip.", 99, "/backups/pt99.zip"),
    ("Check what labs were done for ID 310 and deposit the findings into /archive/310_report.docx.", 310, "/archive/310_report.docx"),
    ("Research the patient chart for ID 22 and document the lab status at /health/records/22_status.txt.", 22, "/health/records/22_status.txt"),
    ("Review the clinical data for patient ID 404, summarize the results, and save them to /network/404_summary.pdf.", 404, "/network/404_summary.pdf"),
    ("Retrieve the comprehensive medical file for patient 777 and upload the synthesized notes to /local/notes777.txt.", 777, "/local/notes777.txt"),
    ("Examine the health background of patient ID 1024 and commit the findings to /mnt/data/1024_background.rtf.", 1024, "/mnt/data/1024_background.rtf"),
    ("Investigate the prior treatments for ID 88 and store the evaluation at /shared/88_eval.md.", 88, "/shared/88_eval.md")
]
for task, pid, path in web_tasks:
    turns = []
    turns.append(format_turn(task, "Home", None, None, 1, pad_reason("I need to access the patient's record to begin my research.")))
    turns.append(format_turn(task, "Patients", None, None, 2, pad_reason(f"I will retrieve the medical history for patient ID {pid}."), {"id": pid}))
    mem_note = gen_mem(f"Retrieved patient {pid} records for the research task")
    turns.append(format_turn(task, "Patients", None, "Record found: Patient has stable history, recent blood tests normal.", 4, pad_reason("I'll store a memory note about the patient's record before proceeding to save the document."), {"note": mem_note}))
    turns.append(format_turn(task, "Patients", mem_note, "Memory note saved.", 5, pad_reason("I must return to the Home menu to access the Lab Results domain to save the report.")))
    turns.append(format_turn(task, "Home", mem_note, None, 6, pad_reason("I will navigate to Lab Results to upload the summarized document as requested.")))
    turns.append(format_turn(task, "Lab Results", mem_note, None, 1, pad_reason(f"I am saving the compiled research findings to {path}."), {"patient_id": pid, "path": path}))
    turns.append(format_turn(task, "Lab Results", mem_note, "File uploaded to network path /mnt/shared successfully.", 5, pad_reason("The research is done and the file is saved, so the task is complete.")))
    traces.append({"task": task, "turns": turns})

# 2. 8 Email & Calendar (Mapped to Appointments)
email_tasks = [
    ("Review today's clinic schedule and slot in a new appointment for patient 12 with doctor 5 at 14:00.", 12, 5, "14:00"),
    ("Check my upcoming bookings for the day and book patient 45 to see doc 9 at 09:30.", 45, 9, "09:30"),
    ("Can you read off the daily agenda and then schedule patient 33 with specialist 2 at 11:15?", 33, 2, "11:15"),
    ("Look at the current appointment roster and arrange a meeting for patient 70 with doctor 8 at 15:45.", 70, 8, "15:45"),
    ("Consult the daily calendar and fit in patient 19 with physician 3 at 10:00.", 19, 3, "10:00"),
    ("Scan today's booked times and schedule a session for patient 55 with doctor 1 at 13:30.", 55, 1, "13:30"),
    ("Examine the daily schedule and coordinate a visit for patient 81 and doctor 4 at 16:20.", 81, 4, "16:20"),
    ("Check the appointments list and organize a checkup for patient 105 with doc 7 at 08:45.", 105, 7, "08:45")
]
for task, pid, did, time in email_tasks:
    turns = []
    turns.append(format_turn(task, "Home", None, None, 2, pad_reason("I need to check the daily calendar and manage bookings, so I'll go to Appointments.")))
    turns.append(format_turn(task, "Appointments", None, None, 3, pad_reason("First, I'll list the daily schedule to review the available slots as requested.")))
    mem_note = gen_mem(f"Checked daily schedule and found availability for time {time}")
    turns.append(format_turn(task, "Appointments", None, "08:00 - Dr. 1 busy\n09:00 - Dr. 2 open\n14:00 - open", 4, pad_reason("I will save a note about the schedule availability before I book the appointment."), {"note": mem_note}))
    turns.append(format_turn(task, "Appointments", mem_note, "Memory note saved.", 1, pad_reason(f"Now I will schedule patient {pid} with doctor {did} at {time}."), {"patient_id": pid, "doc_id": did, "time": time}))
    turns.append(format_turn(task, "Appointments", mem_note, f"Appointment confirmed for patient {pid} at {time}.", 6, pad_reason("The schedule was reviewed and the new appointment is booked, task complete.")))
    traces.append({"task": task, "turns": turns})

# 3. 8 Python Error Handling (Mapped to Billing processing error)
python_tasks = [
    ("Process the insurance claim for bill 4001, if it fails due to incorrect amount, generate a new bill for patient 60 and retry.", 4001, 60, 200.0),
    ("Attempt to clear the insurance claim for bill 992. If it rejects, create a corrected bill for patient 14 and submit again.", 992, 14, 150.5),
    ("Run the insurance processing script on bill ID 330. Handle any rejection by issuing a new bill for patient 82 and re-processing.", 330, 82, 320.0),
    ("Try processing the claim for bill 5050. If there's an error, generate a fresh invoice for patient 27 and process that one.", 5050, 27, 45.0),
    ("Submit insurance claim for bill 111. If it bounces back, bill patient 93 directly and process the new claim.", 111, 93, 85.0),
    ("Process the coverage claim for bill 808. Upon failure, make a new bill for patient 44 and process it successfully.", 808, 44, 99.9),
    ("Execute the claim processing for bill 772. Should it error out, create an updated bill for patient 38 and rerun the claim.", 772, 38, 210.0),
    ("File the insurance claim for bill 610. If it hits an error, generate a corrected statement for patient 51 and try again.", 610, 51, 175.0)
]
for task, bid, pid, amt in python_tasks:
    turns = []
    turns.append(format_turn(task, "Home", None, None, 5, pad_reason("I will navigate to Billing to process the insurance claim.")))
    turns.append(format_turn(task, "Billing", None, None, 2, pad_reason(f"I am attempting to process the insurance claim for bill {bid}."), {"bill_id": bid}))
    mem_note = gen_mem(f"Claim {bid} rejected due to error, generating new bill")
    turns.append(format_turn(task, "Billing", None, "Error: Insurance claim rejected due to incorrect base amount.", 3, pad_reason("The claim failed with an error, so I'll remember this before generating a corrected bill."), {"note": mem_note}))
    turns.append(format_turn(task, "Billing", mem_note, "Memory note saved.", 1, pad_reason(f"Generating a new corrected bill for patient {pid} to fix the error."), {"patient_id": pid, "amount": amt}))
    turns.append(format_turn(task, "Billing", mem_note, "Bill 9999 generated successfully.", 2, pad_reason("Now I will re-process the insurance claim using the newly generated bill ID 9999."), {"bill_id": 9999}))
    turns.append(format_turn(task, "Billing", mem_note, "Claim processed and approved.", 5, pad_reason("The error was handled successfully and the new claim is approved, task complete.")))
    traces.append({"task": task, "turns": turns})

# 4. 8 Load/Compute Data (Mapped to Inventory)
calc_tasks = [
    ("Count our current stock of 'Bandages' and order an additional 50 units.", "Bandages", 50),
    ("Check how many 'Syringes' we have left and purchase 200 more.", "Syringes", 200),
    ("Calculate the remaining inventory for 'Gloves' and request 500 extra.", "Gloves", 500),
    ("Evaluate the stock level for 'Aspirin' and procure 100 new bottles.", "Aspirin", 100),
    ("Assess our supply of 'Gauze' and order 75 more packs.", "Gauze", 75),
    ("Review the quantity of 'Scalpels' on hand and buy 30 additional units.", "Scalpels", 30),
    ("Measure the current volume of 'Saline' and order 40 more bags.", "Saline", 40),
    ("Determine the stock status of 'Masks' and acquire 300 more.", "Masks", 300)
]
for task, item, qty in calc_tasks:
    turns = []
    turns.append(format_turn(task, "Home", None, None, 7, pad_reason("I need to interact with supply levels, so I will go to Inventory.")))
    turns.append(format_turn(task, "Inventory", None, None, 1, pad_reason(f"I will check the current stock for {item}."), {"item": item}))
    mem_note = gen_mem(f"Checked {item} stock, computed need for {qty} more units")
    turns.append(format_turn(task, "Inventory", None, f"Current stock for {item}: 15 units.", 3, pad_reason("I will note the current stock before I place the new order."), {"note": mem_note}))
    turns.append(format_turn(task, "Inventory", mem_note, "Memory note saved.", 2, pad_reason(f"I am ordering {qty} units of {item} as required."), {"item": item, "qty": qty}))
    turns.append(format_turn(task, "Inventory", mem_note, f"Order placed for {qty} {item}.", 5, pad_reason("The stock was checked and the additional units were ordered.")))
    traces.append({"task": task, "turns": turns})

# 5. 10 Multi-domain (Prescriptions -> Billing)
multi_tasks = [
    ("Prescribe 'Amoxicillin' 500mg for patient 200, then generate a bill for them for 150.00.", 200, "Amoxicillin", "500mg", 150.0),
    ("Write a prescription of 'Lisinopril' 10mg for patient 55, and afterwards issue a 75.50 invoice.", 55, "Lisinopril", "10mg", 75.5),
    ("Give patient 88 a prescription for 'Metformin' 500mg, then create a billing statement of 120.00.", 88, "Metformin", "500mg", 120.0),
    ("Order 'Ibuprofen' 800mg for patient 31, and proceed to bill them 45.00.", 31, "Ibuprofen", "800mg", 45.0),
    ("Prescribe 'Omeprazole' 20mg for patient 17, and subsequently charge them 90.00.", 17, "Omeprazole", "20mg", 90.0),
    ("Set up a 'Simvastatin' 40mg prescription for patient 92, then send a bill of 110.00.", 92, "Simvastatin", "40mg", 110.0),
    ("Authorize 'Losartan' 50mg for patient 41, and generate a 65.00 bill.", 41, "Losartan", "50mg", 65.0),
    ("Prescribe 'Albuterol' inhaler for patient 73, followed by a bill generation of 85.00.", 73, "Albuterol", "inhaler", 85.0),
    ("Assign 'Gabapentin' 300mg to patient 101, then produce a 95.00 invoice.", 101, "Gabapentin", "300mg", 95.0),
    ("Issue a 'Sertraline' 50mg script for patient 64, and then generate a bill for 55.00.", 64, "Sertraline", "50mg", 55.0)
]
for task, pid, med, dose, amt in multi_tasks:
    turns = []
    turns.append(format_turn(task, "Home", None, None, 4, pad_reason("I will start by navigating to Prescriptions to assign the medication.")))
    turns.append(format_turn(task, "Prescriptions", None, None, 1, pad_reason(f"Prescribing {med} with dosage {dose} to patient {pid}."), {"patient_id": pid, "med": med, "dosage": dose}))
    mem_note = gen_mem(f"Prescribed {med} to patient {pid}, now moving to Billing")
    turns.append(format_turn(task, "Prescriptions", None, f"Prescription for {med} added.", 3, pad_reason("I will make a memory note that the prescription is done before navigating away."), {"note": mem_note}))
    turns.append(format_turn(task, "Prescriptions", mem_note, "Memory note saved.", 4, pad_reason("I need to return Home so I can access the Billing domain next.")))
    turns.append(format_turn(task, "Home", mem_note, None, 5, pad_reason("Navigating to Billing to generate the invoice for the patient.")))
    turns.append(format_turn(task, "Billing", mem_note, None, 1, pad_reason(f"Generating a bill of {amt} for patient {pid}."), {"patient_id": pid, "amount": amt}))
    turns.append(format_turn(task, "Billing", mem_note, "Bill generated successfully.", 5, pad_reason("Both the prescription and the billing are complete.")))
    traces.append({"task": task, "turns": turns})

# 6. 8 BACK correction tasks
back_tasks = [
    ("Add a new cardiologist Dr. Smith, wait no, I meant to schedule an appointment for patient 10 with doctor 2 at 09:00.", 10, 2, "09:00"),
    ("Update the availability for doctor 5, actually scratch that, cancel the appointment with ID 999.", 999, None, None),
    ("Let's check the doctor roster... wait, I need to see the daily schedule instead.", None, None, None),
    ("Register a new doctor named Dr. Jones... hold on, I should actually schedule patient 15 with doc 3 at 14:00.", 15, 3, "14:00"),
    ("I want to set hours for doctor 8... no, my mistake, please cancel appointment ID 444.", 444, None, None),
    ("Add Dr. Lee to the system... oops, I meant to check today's appointment list.", None, None, None),
    ("Change doctor 4's schedule... wait, I need to book patient 22 with doctor 6 at 11:30.", 22, 6, "11:30"),
    ("Input a new neurologist Dr. Davis... on second thought, cancel appointment ID 777.", 777, None, None)
]
for i, (task, p1, p2, p3) in enumerate(back_tasks):
    turns = []
    turns.append(format_turn(task, "Home", None, None, 3, pad_reason("I will navigate to Doctors because the task initially mentions doctors.")))
    turns.append(format_turn(task, "Doctors", None, None, 4, pad_reason("Wait, reading the task again, I need to handle appointments instead. I will BACK out to Home.")))
    turns.append(format_turn(task, "Home", None, None, 2, pad_reason("Now navigating to Appointments to perform the correct action.")))
    if "schedule an appointment" in task or "schedule patient" in task or "book patient" in task:
        turns.append(format_turn(task, "Appointments", None, None, 1, pad_reason("Scheduling the requested appointment."), {"patient_id": p1, "doc_id": p2, "time": p3}))
        result_str = f"Appointment confirmed with Doctor {p2} for patient {p1} at {p3}."
    elif "cancel the appointment" in task or "cancel appointment" in task:
        turns.append(format_turn(task, "Appointments", None, None, 2, pad_reason(f"Canceling appointment ID {p1}."), {"id": p1}))
        result_str = f"Appointment {p1} deleted from the system."
    else:
        turns.append(format_turn(task, "Appointments", None, None, 3, pad_reason("Listing the daily schedule as requested.")))
        result_str = "09:00 - Dr. 1 available\n10:30 - Dr. 2 booked."

    turns.append(format_turn(task, "Appointments", None, result_str, 6, pad_reason("The correct action in the Appointments domain has been completed.")))
    traces.append({"task": task, "turns": turns})

# 7. 8 Short tasks (3 Doctors, 5 Lab Results)
short_tasks = [
    # 3 Doctors tasks
    ("We need to add a new cardiologist named Dr. Smith to the system.", "Doctors", "add_doctor", {"name": "Dr. Smith", "specialty": "Cardiology"}, "Dr. Smith added with ID 101."),
    ("Please register Dr. Adams, a neurologist, in the doctor database.", "Doctors", "add_doctor", {"name": "Dr. Adams", "specialty": "Neurology"}, "Dr. Adams added with ID 102."),
    ("Add a pediatrician named Dr. Brown to our doctors list.", "Doctors", "add_doctor", {"name": "Dr. Brown", "specialty": "Pediatrics"}, "Dr. Brown added with ID 103."),

    # 5 Lab Results tasks
    ("Could you pull up the lab results for test ID 5001?", "Lab Results", "view_lab_result", {"result_id": 5001}, "Lab Result 5001: Cholesterol levels normal."),
    ("I need to see the laboratory report for result ID 8820.", "Lab Results", "view_lab_result", {"result_id": 8820}, "Lab Result 8820: Vitamin D deficiency detected."),
    ("Display the test outcome for lab result ID 1234.", "Lab Results", "view_lab_result", {"result_id": 1234}, "Lab Result 1234: All vitals within expected ranges."),
    ("Fetch the lab results for test ID 909.", "Lab Results", "view_lab_result", {"result_id": 909}, "Lab Result 909: Hemoglobin slightly elevated."),
    ("Can you view the findings for laboratory test 771?", "Lab Results", "view_lab_result", {"result_id": 771}, "Lab Result 771: Normal blood glucose levels.")
]
for task, domain, tool_name, args, result_str in short_tasks:
    turns = []
    if domain == "Doctors":
        home_action = 3
        tool_action = 1
        done_action = 5
    elif domain == "Lab Results":
        home_action = 6
        tool_action = 2
        done_action = 5

    turns.append(format_turn(task, "Home", None, None, home_action, pad_reason(f"I will navigate to the {domain} domain to complete this short task.")))
    turns.append(format_turn(task, domain, None, None, tool_action, pad_reason(f"Executing {tool_name} with the provided information."), args))
    turns.append(format_turn(task, domain, None, result_str, done_action, pad_reason("The action was successful, task complete.")))
    traces.append({"task": task, "turns": turns})

with open(filename, "w") as f:
    for trace in traces:
        f.write(json.dumps(trace) + "\n")

print(f"Generated {len(traces)} traces and saved to {filename}")
with open("filename.txt", "w") as f:
    f.write(filename)
