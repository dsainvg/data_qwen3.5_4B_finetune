import json
import random
import uuid
import re

MENUS = {
    "Home": """  1. Employee Records — navigate to Employee Records tools
  2. Onboarding — navigate to Onboarding tools
  3. Leave Management — navigate to Leave Management tools
  4. Payroll — navigate to Payroll tools
  5. Performance — navigate to Performance tools
  6. Recruitment — navigate to Recruitment tools
  7. Company Policies — navigate to Company Policies tools
  8. MEM [note: `string`] — store a memory note (10–20 words exactly)
  9. BACK — go to previous state
  10. DONE — task is complete""",
    "Employee Records": """  1. add_employee [name: `string`, role: `string`]
  2. get_employee [id: `int`]
  3. update_salary [id: `int`, amount: `float`]
  4. MEM [note: `string`]
  5. BACK
  6. DONE""",
    "Onboarding": """  1. assign_onboarding_tasks [emp_id: `int`]
  2. check_onboarding_status [emp_id: `int`]
  3. MEM [note: `string`]
  4. BACK
  5. DONE""",
    "Leave Management": """  1. approve_leave [req_id: `int`]
  2. reject_leave [req_id: `int`]
  3. get_leave_balance [emp_id: `int`]
  4. MEM [note: `string`]
  5. BACK
  6. DONE""",
    "Payroll": """  1. generate_payslip [emp_id: `int`, month: `string`]
  2. process_payroll [date: `date`]
  3. list_bonuses
  4. MEM [note: `string`]
  5. BACK
  6. DONE""",
    "Performance": """  1. schedule_review [emp_id: `int`, date: `date`]
  2. submit_review_notes [emp_id: `int`, notes: `multiline_string`]
  3. MEM [note: `string`]
  4. BACK
  5. DONE""",
    "Recruitment": """  1. post_job [title: `string`, dept: `string`]
  2. list_candidates [job_id: `int`]
  3. schedule_interview [candidate_id: `int`]
  4. MEM [note: `string`]
  5. BACK
  6. DONE""",
    "Company Policies": """  1. upload_policy_doc [path: `path`]
  2. list_policies
  3. send_policy_update_email
  4. MEM [note: `string`]
  5. BACK
  6. DONE"""
}

def format_turn(task, state, memory, result, menu):
    lines = ["USER:"]
    lines.append(f"[TASK]: {task}")
    lines.append(f"[STATE]: {state}")
    if memory:
        lines.append(f"[MEMORY]: {memory}")
    if result:
        lines.append(f"[RESULT]: {result}")
    lines.append(f"[MENU]:\n{menu}")
    return "\n".join(lines)

def extract_id(text):
    match = re.search(r'\b\d+\b', text)
    if match:
        return int(match.group())
    return 1

class TraceBuilder:
    def __init__(self, task):
        self.task = task
        self.state_stack = ["Home"]
        self.memory = None
        self.turns = []
        self.last_result = None

    def get_state(self):
        return self.state_stack[-1]

    def add_turn(self, reason, action, args=None, result=None, change_state=None, update_mem=None, pop_state=False):
        state = self.get_state()
        menu = MENUS[state]
        user_turn = format_turn(self.task, state, self.memory, self.last_result, menu)

        assist_dict = {"reason": reason, "action": action}
        if args is not None:
            assist_dict["args"] = args

        self.turns.append({
            "user": user_turn,
            "assistant": json.dumps(assist_dict)
        })

        # apply state changes for next turn
        self.last_result = result
        if update_mem:
            self.memory = update_mem
        if change_state:
            self.state_stack.append(change_state)
        elif pop_state:
            if len(self.state_stack) > 1:
                self.state_stack.pop()

def generate_web_research(index):
    # 10 traces
    tasks = [
        "Research the latest IT security policies and upload the consolidated document to /docs/it_sec.pdf.",
        "Check all active company policies on web access and save a new policy doc to /shared/web_policy.pdf.",
        "Find out the latest health and safety rules online and upload them as /policies/health.pdf.",
        "Compile the remote work guidelines from our intranet and store the file in /hr/remote.pdf.",
        "Review the recent changes to the data privacy policy and upload the updated version to /compliance/privacy.pdf.",
        "Gather the current code of conduct details and upload the summary to /docs/conduct.pdf.",
        "Research the updated travel reimbursement policy and save it as /policies/travel.pdf.",
        "Look up the new social media guidelines and upload the PDF to /shared/social_media.pdf.",
        "Investigate the newly proposed environmental policies and upload the document to /docs/environmental.pdf.",
        "Search the system for the intellectual property policy and upload the latest revision to /legal/ip_policy.pdf."
    ]
    tb = TraceBuilder(tasks[index])

    # turn 1: home -> company policies
    tb.add_turn("I need to review our company policies and then upload a new document based on the request. The best place to start is the Company Policies domain. Let me navigate there now to begin the research phase.", 7, change_state="Company Policies")

    # optionally add a BACK trick for traces 0 and 1
    if index < 2:
        tb.add_turn("Wait, let me double check if there's a dedicated document upload domain on the main menu. I'll go back to verify. It is always good to explore available options before committing.", 5, pop_state=True)
        tb.add_turn("There is no separate document domain available on the main menu. I will proceed into the Company Policies domain to handle this upload properly. This domain contains the required policy tools.", 7, change_state="Company Policies")

    # turn 2: list_policies
    tb.add_turn("I will list the current policies to research the necessary information for the user's request. Understanding the current context is essential. Once I see the existing policies, I can prepare for the upload step.", 2, result="1. IT Security 2023\n2. Health and Safety v2\n3. Remote Work Guidelines")

    # turn 3: MEM
    note = f"Found existing policy docs, will now upload the newly compiled {index} policy file."
    # ensure exactly 10-20 words
    words = note.split()
    while len(words) < 14:
        words.append("doc")
    note = " ".join(words[:14])

    tb.add_turn(f"I need to remember that I've completed the research phase. I will store a memory note summarizing my progress before uploading. This will ensure I stay on track with the final requirement.", 4, args={"note": note}, update_mem=note)

    # turn 4: upload
    path = tasks[index].split()[-1].strip(".")
    tb.add_turn(f"Now I will upload the finalized policy document to the specified path {path}. This completes the action part of the user's request. I expect the system to confirm the upload is recorded.", 1, args={"path": path}, result=f"Uploaded policy document size: 4.2 MB to path: {path}")

    # turn 5: DONE
    tb.add_turn("I have researched the policies and successfully uploaded the requested document. All requirements specified in the user prompt have been met. The task is fully complete, so I can finish now.", 6)
    return tb

def generate_email_calendar(index):
    # 8 traces
    tasks = [
        "Check candidate schedules via email and schedule an interview for candidate 102.",
        "Read the recruitment emails to find candidate 305's availability, then schedule their interview.",
        "Review manager availability emails and schedule a performance review for employee 50 on 2024-11-01.",
        "Check the team inbox for employee 12's preferred review date, then schedule it for 2024-10-15.",
        "Find candidate 88's email response and book their interview slot accordingly.",
        "Read the latest emails about employee 44, then schedule their performance review on 2024-12-01.",
        "Review candidate 77's scheduling email and set up the interview.",
        "Check performance emails for employee 9, then schedule their review for 2024-11-20."
    ]
    tb = TraceBuilder(tasks[index])

    is_recruitment = "candidate" in tasks[index]
    domain_idx = 6 if is_recruitment else 5
    domain_name = "Recruitment" if is_recruitment else "Performance"

    tb.add_turn(f"I need to schedule an event based on email correspondence. The {domain_name} domain is the appropriate place to find the required scheduling tools. I will navigate there to get started.", domain_idx, change_state=domain_name)

    if is_recruitment:
        tb.add_turn("I will list the candidates to check the schedule details before booking the interview. This ensures the candidate is active and available. Let's see the current candidate roster.", 2, args={"job_id": 10}, result="Candidate 102: Available 2024-10-10\nCandidate 305: Available 2024-10-12\nCandidate 88: Available 2024-10-14\nCandidate 77: Available 2024-10-16")

        note = f"Checked candidate availability emails, proceeding to schedule the interview for candidate {index}."
        words = note.split()
        while len(words) < 12: words.append("now")
        note = " ".join(words[:13])
        tb.add_turn("I'll store a memory note that the availability has been verified. Keeping track of this check is important before making scheduling commitments. This helps avoid double bookings.", 4, args={"note": note}, update_mem=note)

        cand_id = extract_id(tasks[index])
        tb.add_turn(f"I will now schedule the interview for candidate {cand_id}. I have the availability confirmed from the email records. The system should book the slot and return a confirmation.", 3, args={"candidate_id": cand_id}, result=f"Interview for candidate {cand_id} scheduled for 14:00 at Room B.")
        tb.add_turn("The interview has been scheduled as requested based on the email data. I have verified the outcome and there are no further actions needed. This task is complete.", 6)
    else:
        emp_id = extract_id(tasks[index])
        date_str = [s for s in tasks[index].split() if "2024" in s][0].strip(".,")
        tb.add_turn(f"I will schedule the performance review directly based on the date {date_str} mentioned in the task. This fulfills the calendar requirement extracted from the emails. I am entering the employee ID and date now.", 1, args={"emp_id": emp_id, "date": date_str}, result=f"Review scheduled for employee {emp_id} on {date_str} at 10:00 AM.")

        note = f"Successfully scheduled the performance review for the employee based on email request."
        words = note.split()
        while len(words) < 11: words.append("done")
        note = " ".join(words[:12])
        tb.add_turn("I'll make a quick note that the scheduling is complete before finishing. It serves as a record that the requested date was applied. This is a good practice for tracking progress.", 3, args={"note": note}, update_mem=note)
        tb.add_turn("The review is securely scheduled in the calendar. I have completed all the required steps for this task. I am marking it as done.", 5)

    return tb

def generate_python_error(index):
    # 8 traces
    tasks = [
        "Write a python script to calculate performance scores for employee 10, submit it as notes, fix any errors, and rerun.",
        "Generate automated performance notes for employee 22 using a python script, handle the expected formatting error, and resubmit.",
        "Write python logic to summarize employee 33's review, submit it, correct the syntax error, and rerun.",
        "Submit a python-based review analysis for employee 44, handle the validation error, and fix the notes.",
        "Process payroll dynamically for 2024-10-01 using a python script, fix the date format error, and rerun.",
        "Run a python script to process payroll for 2024-11-15, catch the system error, correct the date, and resubmit.",
        "Use a python script to generate payroll on 2024-12-01, handle the invalid argument error, and retry.",
        "Submit a python automation script for payroll processing on 2024-09-30, fix the missing header error, and rerun."
    ]
    tb = TraceBuilder(tasks[index])

    is_perf = "review" in tasks[index] or "notes" in tasks[index]
    domain_idx = 5 if is_perf else 4
    domain_name = "Performance" if is_perf else "Payroll"

    tb.add_turn(f"I need to run a python script to handle this task automatically. The {domain_name} domain has the specific processing tools I require. I will enter that domain now to input my script.", domain_idx, change_state=domain_name)

    if is_perf:
        emp_id = extract_id(tasks[index])
        bad_code = "def calc_score():\n  return 100"
        tb.add_turn(f"I will submit the initial python script as review notes for employee {emp_id}. The system will parse the script and return any execution results. Let's see if the format is accepted.", 2, args={"emp_id": emp_id, "notes": bad_code}, result="Error: Python script rejected due to missing standard formatting headers (requires # STANDARD HEADERS).")

        note = f"Received formatting error on python script submission, need to add headers and resubmit."
        words = note.split()
        while len(words) < 14: words.append("now")
        note = " ".join(words[:14])
        tb.add_turn("I will save a note about the missing headers error before fixing the code. This ensures I remember the exact requirement when I resubmit. Storing this memory helps avoid repeating the mistake.", 3, args={"note": note}, update_mem=note)

        good_code = "# STANDARD HEADERS\ndef calc_score():\n  return 100"
        tb.add_turn("I will resubmit the python script, this time including the required standard headers to fix the error. The logic is identical but the formatting now matches the system requirements. I expect this to succeed.", 2, args={"emp_id": emp_id, "notes": good_code}, result="Review notes accepted: Script executed, returned score 100.")
        tb.add_turn("The script ran successfully and the automated notes are now submitted. I handled the formatting error and reran the job as requested. The task is fully complete.", 5)
    else:
        date_str = [s for s in tasks[index].split() if "2024" in s][0].strip(".,")
        tb.add_turn(f"I will execute the python script to process payroll dynamically. I am intentionally passing an incorrect date format first to test the error handling. Let's trigger the expected failure.", 2, args={"date": "invalid-format"}, result="Error: Date format invalid in python script arguments, expected YYYY-MM-DD. Traceback (most recent call last).")

        note = f"Python script for payroll failed due to date format, will fix it immediately."
        words = note.split()
        while len(words) < 13: words.append("yes")
        note = " ".join(words[:13])
        tb.add_turn("I'll note the validation error so I remember to use the correct strict date format on the next try. It's important to document the failure reason. Now I am ready to retry.", 4, args={"note": note}, update_mem=note)

        tb.add_turn(f"I will rerun the script with the correctly formatted date {date_str}. This should bypass the previous validation failure and process the payroll normally. The format is now strictly correct.", 2, args={"date": date_str}, result=f"Processed 145 employee records for date {date_str}. Total payroll: $450,200.")
        tb.add_turn("The payroll script executed perfectly after fixing the date error. The automation task is completed successfully and the results look valid. I am done.", 6)

    return tb

def generate_load_compute(index):
    # 8 traces
    emp_id = 100 + index
    tasks = [
        f"Get the current salary for employee {emp_id}, compute a 10% raise, and update their salary.",
        f"Load employee {emp_id}'s record, calculate a flat $5000 bonus addition to their base, and update the salary.",
        f"Fetch employee {emp_id}'s details, calculate a 5% inflation adjustment, and apply the salary update.",
        f"Retrieve the salary for employee {emp_id}, apply a 15% promotion increase, and update it.",
        f"Check employee {emp_id}'s salary, compute a 3% merit increase, and save the updated amount.",
        f"Load data for employee {emp_id}, calculate a $2500 adjustment, and update the salary.",
        f"Get employee {emp_id}, calculate a 12% market adjustment, and update their salary.",
        f"Fetch the base pay for employee {emp_id}, calculate a 8% raise, and update the record."
    ]
    tb = TraceBuilder(tasks[index])

    tb.add_turn("I need to access employee records to load the current salary data for computation. This is the first step before I can apply any mathematical adjustments. I am navigating to Employee Records.", 1, change_state="Employee Records")
    tb.add_turn(f"I will retrieve the employee record for ID {emp_id} to see their current base salary. I need this exact number to perform my calculation accurately. Let's fetch the data now.", 2, args={"id": emp_id}, result="Name: Alex Jenkins, Role: Developer, Salary: 80000.00")

    note = f"Loaded employee data showing 80000 salary, will now calculate and apply the raise."
    words = note.split()
    while len(words) < 14: words.append("promptly")
    note = " ".join(words[:14])
    tb.add_turn("I will store the current salary amount in memory while I calculate the new value. It helps to keep track of the original base pay before overriding it. This is a safe step to take.", 4, args={"note": note}, update_mem=note)

    tb.add_turn(f"Having computed the new amount based on the requested raise percentage or flat value, I will now update the salary for employee {emp_id}. The calculated new salary is 88000.0. I will submit the update now.", 3, args={"id": emp_id, "amount": 88000.0}, result="Salary updated to 88000.0. Previous value was 80000.0.")
    tb.add_turn("The salary has been updated with the correctly calculated new amount. I have verified the result matches my computation. The task is fully complete.", 6)

    return tb

def generate_multi_domain(index):
    # 10 traces
    tasks = [
        "Add a new employee named Bob (role: Engineer), then assign them onboarding tasks.",
        "Add a new employee named Alice (role: Manager), then check their onboarding status.",
        "Create a new employee record for Charlie (role: Designer), then assign onboarding.",
        "Register a new employee David (role: QA), then assign onboarding tasks to them.",
        "Add employee Eve (role: HR), then verify her onboarding status.",
        "Check the leave balance for employee 42, then generate their payslip for October.",
        "Approve leave request 99, then process payroll for 2024-11-01.",
        "Reject leave request 55, then list the current bonuses in the payroll system.",
        "Get leave balance for employee 7, then generate a payslip for November.",
        "Approve leave request 88, then generate the payslip for employee 88 for December."
    ]
    tb = TraceBuilder(tasks[index])

    if index < 5:
        # Employee Records -> Onboarding
        tb.add_turn("I need to add a new employee first, which means I have to interact with the Employee Records domain. After that, I'll handle the onboarding phase. I am entering Employee Records now.", 1, change_state="Employee Records")
        name = tasks[index].split("named ")[1].split(" ")[0] if "named" in tasks[index] else tasks[index].split("employee ")[1].split(" ")[0]
        tb.add_turn(f"I will add the new employee {name} with the specified role. The system should generate a new employee ID for them. Let's submit the registration data.", 1, args={"name": name, "role": "Staff"}, result="Created new record. Employee added with ID: 205")

        note = f"Successfully added employee {name} with ID 205, proceeding to the onboarding domain next."
        words = note.split()
        while len(words) < 14: words.append("now")
        note = " ".join(words[:14])
        tb.add_turn("I will remember the newly generated employee ID 205 to use in the onboarding step. I cannot proceed without this ID, so a memory note is perfect here. I am saving it now.", 4, args={"note": note}, update_mem=note)

        tb.add_turn("I must return to the Home menu to switch over to the Onboarding domain. The current domain doesn't have the necessary tools. I am navigating back.", 5, pop_state=True)
        tb.add_turn("Now I will enter the Onboarding domain to assign tasks or check status for the new hire. This is the second and final phase of the user's request. Entering domain now.", 2, change_state="Onboarding")

        if "assign" in tasks[index]:
            tb.add_turn("I will assign the standard onboarding tasks for the newly created employee ID 205. They need to receive their initial IT setup and HR forms. I am executing the assignment tool.", 1, args={"emp_id": 205}, result="Assigned 4 pending onboarding tasks to employee 205.")
        else:
            tb.add_turn("I will check the current onboarding status for employee ID 205 to see if they've started. This completes the verification part of the task. Checking status now.", 2, args={"emp_id": 205}, result="Status: Pending Tasks. Completed 0/4.")
        tb.add_turn("Both parts of the task are complete across the two distinct domains. The employee is created and their onboarding is handled. I am done here.", 5)
    else:
        # Leave Management -> Payroll
        tb.add_turn("I need to handle a leave request first before moving to payroll. The Leave Management domain is where I'll find those tools. Let me navigate there to start.", 3, change_state="Leave Management")

        if "Approve" in tasks[index]:
            req_id = extract_id(tasks[index])
            tb.add_turn(f"I will approve the leave request {req_id} exactly as specified. This will update the employee's available leave balance in the system. Submitting approval now.", 1, args={"req_id": req_id}, result=f"Leave request {req_id} approved. Balance deducted by 3 days.")
        elif "Reject" in tasks[index]:
            req_id = extract_id(tasks[index])
            tb.add_turn(f"I will formally reject the leave request {req_id}. The system will notify the employee of the rejection. Executing rejection action.", 2, args={"req_id": req_id}, result=f"Leave request {req_id} rejected. Status updated to Denied.")
        else:
            emp_id = extract_id(tasks[index])
            tb.add_turn(f"I will check the current leave balance for employee {emp_id}. I need to see how many days they have accrued. Fetching balance details.", 3, args={"emp_id": emp_id}, result=f"Employee {emp_id} has a Leave Balance of 12 days.")

        note = f"Completed the leave management portion of the task, now switching over to payroll."
        words = note.split()
        while len(words) < 14: words.append("soon")
        note = " ".join(words[:14])
        tb.add_turn("I will store a note that the leave step is completely done. It helps track my progress through this multi-step task. Writing memory note now.", 4, args={"note": note}, update_mem=note)

        tb.add_turn("I need to go back to the Home menu to access the Payroll tools. Leave Management and Payroll are entirely separate domains. Going back to Home.", 5, pop_state=True)
        tb.add_turn("Navigating to the Payroll domain to complete the second half of the task. This domain handles payslips and bonuses. Let's enter it.", 4, change_state="Payroll")

        if "payslip" in tasks[index]:
            tb.add_turn("I will generate the requested payslip for the given employee and month. This will create the official financial document. Generating the slip now.", 1, args={"emp_id": 88, "month": "October"}, result="Generated PDF payslip for employee 88 for month: October.")
        elif "process" in tasks[index]:
            tb.add_turn("I will execute the main process payroll tool for the requested date. This will run the calculations for all active employees. Starting the payroll batch job.", 2, args={"date": "2024-11-01"}, result="Batch payroll processing completed for 2024-11-01. Total: $340,000.")
        else:
            tb.add_turn("I will list the current active bonuses in the payroll system. This gives an overview of the variable compensation payouts. Listing bonuses now.", 3, result="Active bonuses: Q3 Performance ($500), Signing Bonus ($1000).")

        tb.add_turn("The entire multi-domain task is complete. I handled both the leave action and the subsequent payroll action smoothly. No further work is needed.", 6)

    return tb

def generate_back_correction(index):
    # 8 traces
    tasks = [
        "Check the onboarding status for employee 404.",
        "Assign onboarding tasks to employee 505.",
        "Post a new job for a Senior Developer in Engineering.",
        "List all candidates for job ID 22.",
        "Approve leave request 123.",
        "Reject leave request 321.",
        "Generate a payslip for employee 10 for August.",
        "Process the payroll for 2024-08-30."
    ]
    tb = TraceBuilder(tasks[index])

    if index < 2:
        # Wants Onboarding, goes to Payroll
        tb.add_turn("I will navigate to the Payroll domain to handle this employee onboarding task. Sometimes onboarding is linked to setting up initial pay details. Let's see if the tools are here.", 4, change_state="Payroll")
        tb.add_turn("Wait, I am currently in the Payroll domain, but the tools here are strictly for payslips and bonuses. I need to check onboarding status, so this is the wrong place. I must go back to the Home menu.", 5, pop_state=True)
        tb.add_turn("Now I will correctly select the dedicated Onboarding domain. This domain has the specific tools for checking statuses and assigning tasks. Entering domain.", 2, change_state="Onboarding")
        tb.add_turn("I will perform the required onboarding action now that I am in the right place. The system should return the correct employee status details. Executing tool.", 2 if "status" in tasks[index] else 1, args={"emp_id": 404}, result="Status retrieved: Employee 404 has 2 pending onboarding tasks.")
        tb.add_turn("The task is completed after correcting my earlier domain navigation error. I successfully found the onboarding tools and got the result. I am done.", 5)
    elif index < 4:
        # Wants Recruitment, goes to Leave Management
        tb.add_turn("I'll go to Leave Management to see if there are tools to post the job or list candidates. I'm guessing HR tools might be grouped together. Navigating to Leave Management.", 3, change_state="Leave Management")
        tb.add_turn("I made a mistake. Leave Management only contains tools for approving and checking leave balances; it doesn't have recruitment tools. I need to go back to the main menu.", 5, pop_state=True)
        tb.add_turn("I will now navigate to the proper Recruitment domain. This is definitely where I can post jobs and review candidates. Entering Recruitment.", 6, change_state="Recruitment")
        if "Post" in tasks[index]:
            tb.add_turn("I will post the new job with the specified title and department. This will create a public opening in our system. Posting job now.", 1, args={"title": "Senior Developer", "dept": "Engineering"}, result="Job ID 89 posted successfully to Engineering department.")
        else:
            tb.add_turn("I will list the currently active candidates for the given job ID. This will let me review applicants. Fetching candidate list.", 2, args={"job_id": 22}, result="Candidate 1: John Doe, Candidate 2: Jane Smith.")
        tb.add_turn("The recruitment task is finished. My navigation error was corrected and the right tool was executed. I am done.", 6)
    elif index < 6:
        # Wants Leave Management, goes to Performance
        tb.add_turn("I need to handle a leave request, so I'll try going to Performance first. Maybe time off requests are tied to performance reviews. Let's look.", 5, change_state="Performance")
        tb.add_turn("This is the Performance domain, which focuses entirely on reviews and notes. It is incorrect for handling leave requests. I will use the back action to return to Home.", 4, pop_state=True)
        tb.add_turn("Let's go to Leave Management instead, which explicitly handles time off. This is the correct choice. Entering Leave Management.", 3, change_state="Leave Management")
        req_id = extract_id(tasks[index])
        tb.add_turn(f"I will execute the specific leave action requested for request {req_id}. The system should process the approval or rejection immediately. Executing action.", 1 if "Approve" in tasks[index] else 2, args={"req_id": req_id}, result=f"Processed leave request {req_id}. System updated.")
        tb.add_turn("The leave action is fully completed. I corrected my path and successfully used the Leave Management tools. The task is finished.", 6)
    else:
        # Wants Payroll, goes to Company Policies
        tb.add_turn("I'll navigate to Company Policies for this payroll task. I thought maybe payroll dates or payslip templates were stored as policy documents. Entering domain.", 7, change_state="Company Policies")
        tb.add_turn("Oops, Company Policies only allows uploading or listing documents. It cannot actually generate dynamic payslips or process batches. I am going back to Home.", 5, pop_state=True)
        tb.add_turn("Now entering the Payroll domain, which contains the dynamic processing tools I need. This is the right place for financial actions. Let's proceed.", 4, change_state="Payroll")
        if "payslip" in tasks[index]:
            tb.add_turn("I am generating the specific payslip for the employee and month requested. This action executes the reporting tool. Generating slip.", 1, args={"emp_id": 10, "month": "August"}, result="Payslip for employee 10 for August successfully generated.")
        else:
            tb.add_turn("I am running the process payroll batch job for the requested date. This handles all global transactions. Processing now.", 2, args={"date": "2024-08-30"}, result="Payroll process complete. Total run time: 4s.")
        tb.add_turn("The payroll task is complete. My brief navigation mistake was fixed and the correct tools were used. Done.", 6)

    return tb

def generate_short_tasks(index):
    # 8 traces
    tasks = [
        "Check the leave balance for employee 80.",
        "List all company policies.",
        "List current bonuses.",
        "Check onboarding status for employee 90.",
        "List candidates for job 5.",
        "Check leave balance for employee 99.",
        "List bonuses.",
        "List policies."
    ]
    tb = TraceBuilder(tasks[index])

    domain_map = {
        "Leave": (3, "Leave Management", 3, {"emp_id": 80}),
        "policies": (7, "Company Policies", 2, None),
        "bonuses": (4, "Payroll", 3, None),
        "onboarding": (2, "Onboarding", 2, {"emp_id": 90}),
        "candidates": (6, "Recruitment", 2, {"job_id": 5}),
        "leave": (3, "Leave Management", 3, {"emp_id": 99}),
        "List bonuses.": (4, "Payroll", 3, None),
        "List policies.": (7, "Company Policies", 2, None)
    }

    key = next(k for k in domain_map.keys() if k in tasks[index])
    d_idx, d_name, t_idx, args = domain_map[key]

    if key == "leave":
        args = {"emp_id": 99}

    specific_results = {
        "Company Policies": "1. Code of Conduct v4\n2. Remote Work Policy\n3. Expense Guidelines",
        "Payroll": "Bonuses: Q1 Profit Share ($1200), Tech Referral ($500).",
        "Leave Management": "Leave Balance: 18 days of Annual Leave remaining.",
        "Onboarding": "Status: 3/4 tasks completed. Pending: ID Card photo.",
        "Recruitment": "Candidates for Job: Mark T., Sarah L., Omar K."
    }
    result_text = specific_results.get(d_name, "Data retrieved specifically.")

    tb.add_turn(f"I will navigate to the {d_name} domain to quickly retrieve this specific information. The task is straightforward and should only take one tool call. Entering domain.", d_idx, change_state=d_name)
    tb.add_turn(f"I will execute the tool to fetch the requested data directly. No intermediate steps are required for this simple read action. Fetching data now.", t_idx, args=args, result=result_text)
    tb.add_turn("I have successfully fetched the requested information. The results are visible and there are no further actions needed. The task is complete.", 6 if d_idx != 2 and d_idx != 5 else 5)

    return tb

def main():
    traces = []

    for i in range(10): traces.append(generate_web_research(i))
    for i in range(8): traces.append(generate_email_calendar(i))
    for i in range(8): traces.append(generate_python_error(i))
    for i in range(8): traces.append(generate_load_compute(i))
    for i in range(10): traces.append(generate_multi_domain(i))
    for i in range(8): traces.append(generate_back_correction(i))
    for i in range(8): traces.append(generate_short_tasks(i))

    random.shuffle(traces)

    out_file = f"dataset_{uuid.uuid4().hex[:8]}.jsonl"
    with open(out_file, "w") as f:
        for t in traces:
            json.dump({
                "task": t.task,
                "turns": t.turns
            }, f)
            f.write("\n")

    print(f"Saved to {out_file}")

if __name__ == "__main__":
    main()
