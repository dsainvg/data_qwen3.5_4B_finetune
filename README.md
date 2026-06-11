this is a repo for data set with this prompt as main but may have different purpose 
You are building a high-quality SFT (Supervised Fine-Tuning) dataset in JSONL format 
to fine-tune Qwen3.5-4B to navigate tasks using a custom menu-based agent interface. 
 
--- 
 
## WHAT THIS AGENT IS 
 
This agent does NOT call tools by name. It navigates a hierarchical menu interface. 
At every step it sees its current state and a short numbered menu, picks a number, 
and either drills deeper or executes a tool. 
It has memory and back navigation. 
 
--- 
 
## EXACT FORMAT OF ONE TURN 
 
USER: 
[TASK]: <the user's original task, repeated every turn> 
[STATE]: <where the agent currently is, e.g. "Home" or "Web & Search"> 
[MEMORY]: <stored note, only present if MEM was used earlier in this trace> 
[RESULT]: <output of the last tool call, only present after a tool was executed> 
[MENU]: 
  1. Web & Search — search, browse, summarise pages 
  2. Files & Docs — read, write, edit files 
  3. Calendar & Email — schedule, send, read mail 
  4. Code & Dev — run code, git, debug 
  5. Data & Math — compute, analyse, plot 
  6. System & OS — manage processes, clipboard, system info 
  7. Memory & Notes — store and recall personal notes 
  8. MEM [note: `string`] — store a memory note (10–20 words exactly) 
  9. BACK — go to previous state 
  10. DONE — task is complete 
 
ASSISTANT: 
{ 
  "reason": "<2–4 sentences of genuine reasoning about what to do next and why>", 
  "action": <number>, 
  "args": { "<field>": <value matching the type> } 
} 
 
Rules for the JSON: 
- "reason" is always present, always a non-empty string 
- "action" is always an integer from the menu 
- "args" is ONLY present when the chosen menu option has typed placeholders 
- If the chosen option has no args, omit "args" entirely 
- For MEM: args is {"note": "<10–20 words exactly>"} 
- The entire assistant response is this single JSON object and nothing else 
- No XML tags, no markdown, no text outside the JSON object 
 
--- 
 
## ARG TYPE SYSTEM 
 
Menu options that require input show typed placeholders in backticks. 
The agent must fill args with values that match the declared type exactly. 
 
Type reference: 
  `string`           — plain text, single line 
  `multiline_string` — code, file contents, email body (use \n for newlines) 
  `int`              — whole number, e.g. 42 
  `float`            — decimal number, e.g. 3.14 
  `bool`             — true or false (JSON boolean, no quotes) 
  `path`             — file or directory path, e.g. "/home/user/notes.txt" 
  `url`              — full URL, e.g. "https://example.com/article" 
  `email`            — email address, e.g. "alice@example.com" 
  `date`             — ISO date, e.g. "2024-03-15" 
  `time`             — 24hr time, e.g. "14:30" 
  `math_expr`        — mathematical expression, e.g. "sqrt(144) + 5^2" 
  `list`             — JSON array, e.g. ["a", "b", "c"] 
  `enum(a,b,c)`      — exactly one of the listed values as a string 
  `sql`              — SQL query string 
  `json`             — arbitrary JSON object or array 
 
Examples of correctly typed args: 
  run_python [code: `multiline_string`] 
    → "args": {"code": "import math\nprint(math.sqrt(144))"} 
 
  create_event [title: `string`, date: `date`, time: `time`] 
    → "args": {"title": "Q3 Review", "date": "2024-09-10", "time": "10:00"} 
 
  plot_chart [data: `list`, type: `enum(bar,line,pie,scatter)`] 
    → "args": {"data": [12, 45, 7, 33], "type": "bar"} 
 
  send_email [to: `email`, subject: `string`, body: `multiline_string`] 
    → "args": {"to": "boss@work.com", "subject": "Update", "body": "Hi,\nHere is the update.\nRegards"} 
 
  search_web [query: `string`] 
    → "args": {"query": "latest climate change report 2024"} 
 
--- 
 
## STATE MACHINE RULES 
 
- Start state is always "Home" 
- Picking a domain (1–7) from Home → enters that domain's sub-menu 
- Sub-menus show 4–8 specific tools for that domain with typed arg hints, plus MEM / BACK / DONE always at the bottom 
- Picking a tool → executes it → next USER turn shows [RESULT] + updated [STATE] + refreshed [MENU] 
- BACK → returns to previous state (stack-based, usable up to 2 times per trace) 
- DONE → ends the trace, no further turns 
- [MEMORY] line appears in every USER turn after MEM has been used at least once in that trace 
- [RESULT] line only appears after a tool was executed, not after domain navigation or BACK 
 
--- 
 
## DOMAIN SUB-MENUS WITH TYPED ARGS 
 
When the agent enters a domain, show this sub-menu (STATE updates accordingly): 
 
### Web & Search  [STATE: "Web & Search"] 
  1. search_web [query: `string`] 
  2. open_url [url: `url`] 
  3. summarise_page 
  4. extract_links 
  5. get_page_title 
  6. MEM [note: `string`] 
  7. BACK 
  8. DONE 
 
### Files & Docs  [STATE: "Files & Docs"] 
  1. read_file [path: `path`] 
  2. write_file [path: `path`, content: `multiline_string`] 
  3. append_file [path: `path`, content: `multiline_string`] 
  4. list_directory [path: `path`] 
  5. delete_file [path: `path`] 
  6. MEM [note: `string`] 
  7. BACK 
  8. DONE 
 
### Calendar & Email  [STATE: "Calendar & Email"] 
  1. read_emails 
  2. send_email [to: `email`, subject: `string`, body: `multiline_string`] 
  3. create_event [title: `string`, date: `date`, time: `time`] 
  4. list_events 
  5. check_availability [date: `date`] 
  6. MEM [note: `string`] 
  7. BACK 
  8. DONE 
 
### Code & Dev  [STATE: "Code & Dev"] 
  1. run_python [code: `multiline_string`] 
  2. run_shell [command: `string`] 
  3. git_status 
  4. git_commit [message: `string`] 
  5. read_error_logs 
  6. MEM [note: `string`] 
  7. BACK 
  8. DONE 
 
### Data & Math  [STATE: "Data & Math"] 
  1. calculate [expression: `math_expr`] 
  2. plot_chart [data: `list`, type: `enum(bar,line,pie,scatter)`] 
  3. analyse_csv [path: `path`] 
  4. convert_units [value: `float`, from: `string`, to: `string`] 
  5. run_sql [query: `sql`] 
  6. MEM [note: `string`] 
  7. BACK 
  8. DONE 
 
### System & OS  [STATE: "System & OS"] 
  1. get_clipboard 
  2. set_clipboard [content: `string`] 
  3. list_processes 
  4. get_system_info 
  5. take_screenshot 
  6. MEM [note: `string`] 
  7. BACK 
  8. DONE 
 
### Memory & Notes  [STATE: "Memory & Notes"] 
  1. save_note [content: `multiline_string`] 
  2. read_notes 
  3. delete_note [id: `int`] 
  4. search_notes [keyword: `string`] 
  5. MEM [note: `string`] 
  6. BACK 
  7. DONE 
 
--- 
 
## TOOL RESULT FORMAT 
 
After a tool executes, the next USER turn includes [RESULT] with specific, realistic output. 
Never write vague results. Always match what the tool would actually return. 
 
Examples: 
  search_web    → "1. 'NASA Climate Report 2024 — nasa.gov/climate'\n2. 'IPCC Summary — ipcc.ch'\n3. 'BBC News: Record Temperatures — bbc.com/news/climate'" 
  read_file     → "# Meeting Notes\n- Budget approved: $42,000\n- Launch date: March 15\n- Owner: Priya" 
  run_python    → "Output:\n[12.4, 15.1, 9.8, 22.3]\nNo errors." 
  read_emails   → "3 unread:\n1. From: boss@work.com — 'Q3 Review Tomorrow at 10am'\n2. From: noreply@github.com — 'PR merged'\n3. From: alice@team.com — 'Lunch Tuesday?'" 
  calculate     → "Result: 156.25" 
  git_status    → "On branch main\nModified: src/agent.py\nUntracked: tests/test_new.py" 
  run_shell     → "total 48\ndrwxr-xr-x  3 user user 4096 Sep 10 14:22 src\n-rw-r--r--  1 user user 1832 Sep 10 14:21 README.md" 
  get_system_info → "OS: Ubuntu 22.04\nCPU: 8 cores @ 3.2GHz\nRAM: 6.2GB / 16GB used\nDisk: 42GB / 256GB used" 
 
--- 
 
## MEMORY NOTE RULE — CRITICAL 
 
The "note" value must be exactly 10–20 words. Count every word before writing. 
 
BAD (8 words):  "User wants the BBC article saved to file" 
BAD (22 words): "Found a BBC article about climate change from 2024 that the user wants summarised and then saved to a notes file" 
GOOD (14 words): "Found BBC climate article 2024, user wants summary written to /home/user/climate.txt" 
 
After MEM is used, [MEMORY]: <note> appears in every subsequent USER turn in that trace. 
The agent's "reason" field in later turns must reference the memory when it is relevant. 
 
--- 
 
## TRACE QUALITY CHECKLIST 
 
Every trace must satisfy all of these: 
 
1. Starts at [STATE]: "Home" with the Home menu 
2. "reason" field shows genuine step-by-step thinking, not generic filler 
3. Tool args are filled with realistic specific values — never "string", "value", "example" 
4. [RESULT] content is specific and matches what the tool actually would return 
5. DONE is only chosen when the task objective is fully achieved 
6. Traces are 3–8 turns long (not counting the final DONE turn) 
7. The agent never writes a tool name in "action" — always an integer 
8. "args" is omitted when the chosen option has no typed placeholders 
9. For multi-domain traces: agent uses BACK to return to Home before entering second domain 
10. For BACK-correction traces: agent navigates to wrong domain, realises in "reason", uses BACK, then corrects 
 
--- 
 
## OUTPUT FORMAT 
 
Each line of the JSONL file is one complete trace: 
 
{ 
  "task": "<the user's task as a natural language string>", 
  "turns": [ 
    { 
      "user": "<full USER block as a single string with \n for newlines>", 
      "assistant": "<the assistant JSON object serialised as a string>" 
    } 
  ] 
} 
 
The "assistant" field value is the JSON object serialised as a string (JSON-in-JSON). 
Every line must be valid JSON. 
Validate every MEM note is 10–20 words before writing the line. 
 
--- 
 
## TASK DIVERSITY — generate 60 traces total 
 
  10 traces — Web research then save result to a file 
   8 traces — Email reading and calendar scheduling 
   8 traces — Write and run Python code, handle an error, fix and rerun 
   8 traces — Load or compute data, plot or calculate a result 
  10 traces — Multi-domain: task requires visiting exactly 2 different domains 
   8 traces — BACK correction: agent goes to wrong domain, backs out, corrects 
   8 traces — Short tasks: completed in exactly 2–3 turns, DONE chosen early 
 
Across all 60 traces: 
  - At least 40 traces use MEM at least once 
  - At least 20 traces use BACK at least once 
  - Every domain must appear as the primary domain in at least 5 traces 
  - Task descriptions must be natural, varied, and realistic — no two tasks the same 
 
--- 
 
## WHAT TO AVOID 
 
- No XML tags of any kind — no <think>, no <reason>, nothing 
- No text outside the JSON object in assistant turns 
- No tool names as the "action" value — integers only 
- No "args" key when the chosen option has no typed placeholders 
- No vague tool results: never "success", "done", "result returned", "output here" 
- No memory notes under 10 words or over 20 words 
- No DONE before the task is genuinely complete 
- No invented tool names outside the domain sub-menus above 
- No placeholder values in args like "your_query", "example.com", "some text" 
 
--- 
 
## DELIVERABLE 
 
Filename: agent_menu_dataset.jsonl
Validate MEM word counts before writing each line.
take time to do a single file with random string as name 
