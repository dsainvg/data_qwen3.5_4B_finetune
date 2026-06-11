import json
import random
import uuid

HOME_MENU = """[MENU]:
  1. Episodes — navigate to Episodes tools
  2. Audio Assets — navigate to Audio Assets tools
  3. Guests — navigate to Guests tools
  4. Distribution — navigate to Distribution tools
  5. Analytics — navigate to Analytics tools
  6. Sponsors — navigate to Sponsors tools
  7. Marketing — navigate to Marketing tools
  8. MEM [note: `string`] — store a memory note (10–20 words exactly)
  9. BACK — go to previous state
  10. DONE — task is complete"""

MENUS = {
    "Home": HOME_MENU,
    "Episodes": """[MENU]:
  1. create_episode [title: `string`, num: `int`]
  2. update_show_notes [id: `int`, notes: `multiline_string`]
  3. publish_episode [id: `int`]
  4. MEM [note: `string`]
  5. BACK
  6. DONE""",
    "Audio Assets": """[MENU]:
  1. upload_audio [path: `path`]
  2. trim_audio [file_id: `int`, start: `float`, end: `float`]
  3. apply_compression [file_id: `int`]
  4. MEM [note: `string`]
  5. BACK
  6. DONE""",
    "Guests": """[MENU]:
  1. add_guest [name: `string`, bio: `string`]
  2. schedule_recording [guest_id: `int`, date: `date`]
  3. MEM [note: `string`]
  4. BACK
  5. DONE""",
    "Distribution": """[MENU]:
  1. sync_to_spotify
  2. sync_to_apple_podcasts
  3. get_rss_feed_url
  4. MEM [note: `string`]
  5. BACK
  6. DONE""",
    "Analytics": """[MENU]:
  1. get_total_downloads [episode_id: `int`]
  2. get_listener_demographics
  3. MEM [note: `string`]
  4. BACK
  5. DONE""",
    "Sponsors": """[MENU]:
  1. add_sponsor [name: `string`, rate: `float`]
  2. log_ad_read [episode_id: `int`, sponsor_id: `int`]
  3. MEM [note: `string`]
  4. BACK
  5. DONE""",
    "Marketing": """[MENU]:
  1. generate_audiogram [episode_id: `int`]
  2. draft_newsletter [content: `multiline_string`]
  3. MEM [note: `string`]
  4. BACK
  5. DONE"""
}

class Trace:
    def __init__(self, task):
        self.task = task
        self.turns = []
        self.state_stack = ["Home"]
        self.memory = None

    def current_state(self):
        return self.state_stack[-1]

    def add_turn(self, reason, action, args=None, result=None, change_state=None, set_memory=None, pop_state=False):
        state = self.current_state()

        user_text = f"[TASK]: {self.task}\n[STATE]: {state}"
        if self.memory:
            user_text += f"\n[MEMORY]: {self.memory}"
        if result:
            user_text += f"\n[RESULT]: {result}"
        user_text += f"\n{MENUS[state]}"
        user_text = "USER:\n" + user_text

        ast_dict = {
            "reason": reason,
            "action": action
        }
        if args is not None:
            ast_dict["args"] = args
            if "note" in args:
                words = len(args["note"].split())
                if not (10 <= words <= 20):
                    raise ValueError(f"Memory note '{args['note']}' has {words} words, must be 10-20.")

        self.turns.append({
            "user": user_text,
            "assistant": json.dumps(ast_dict)
        })

        if set_memory:
            self.memory = set_memory
        if change_state:
            self.state_stack.append(change_state)
        if pop_state:
            self.state_stack.pop()

traces = []

# Type 1: Analytics -> Show Notes (10 traces) - Matches "Web research then save result to a file"
t1_tasks = [
    "Check the total downloads for episode {ep_id} and update its show notes to mention this milestone.",
    "Can you see how many downloads episode {ep_id} has, then add a note about it in the show notes?",
    "I need to know episode {ep_id}'s download count. Once you have it, update the show notes with a thank you.",
    "Find out the download numbers for episode {ep_id}, and put a milestone update in its show notes.",
    "Get the download stats for episode {ep_id}, then edit the show notes to celebrate the achievement.",
    "We hit a milestone on episode {ep_id}, grab the download count and update the show notes to reflect it.",
    "Please check total downloads for ep {ep_id} and update the show notes thanking listeners for the support.",
    "Look up the download tally for episode {ep_id} and append a nice milestone message in the show notes.",
    "Retrieve the total download metric for episode {ep_id}, then modify the show notes to highlight this.",
    "I want to celebrate our growth. Check episode {ep_id}'s downloads and update its show notes accordingly."
]
for i in range(10):
    ep_id = 100 + i
    dl_count = 5000 + i*100
    task = t1_tasks[i].format(ep_id=ep_id)
    t = Trace(task)
    t.add_turn("The user wants me to check downloads and then update show notes. First, I need to navigate to the Analytics domain.", 5, change_state="Analytics")
    t.add_turn(f"I am in the Analytics domain. I will use the get_total_downloads tool for episode {ep_id}.", 1, {"episode_id": ep_id}, result=f"Episode {ep_id} has {dl_count} total downloads.")
    mem_note = f"Episode {ep_id} has exactly {dl_count} downloads, I must update the show notes next to include this."
    t.add_turn(f"I have the download count. I will store a memory note to remember the exact number before navigating to Episodes.", 3, {"note": mem_note}, set_memory=mem_note, result="Memory note saved.")
    t.add_turn("Now that I have the download count stored, I need to go back to the Home menu so I can access the Episodes domain.", 4, pop_state=True)
    t.add_turn("I am back at Home. I will now navigate to the Episodes domain to update the show notes.", 1, change_state="Episodes")
    notes_str = f"Thank you for {dl_count} downloads!\nIn this episode we discuss the future of technology."
    t.add_turn(f"I am in the Episodes domain. I will update the show notes for episode {ep_id} with the requested milestone message based on my memory.", 2, {"id": ep_id, "notes": notes_str}, result="Show notes updated successfully.")
    t.add_turn("I have successfully retrieved the download count and updated the show notes. The task is completely finished.", 6)
    traces.append(t)

# Type 2: Guest Add -> Schedule (8 traces) - Matches "Email reading and calendar scheduling"
t2_data = [
    ("Alice", "Author of bestsellers.", "2024-10-01"), ("Bob", "World renowned scientist.", "2024-10-05"), ("Charlie", "Talented local artist.", "2024-10-10"),
    ("Diana", "Senior software engineer.", "2024-10-15"), ("Eve", "Michelin starred chef.", "2024-10-20"), ("Frank", "Commercial airline pilot.", "2024-10-25"),
    ("Grace", "Award winning writer.", "2024-11-01"), ("Heidi", "Chief medical doctor.", "2024-11-05")
]
for i in range(8):
    name, bio, date = t2_data[i]
    task = f"Read the bio '{bio}' for {name}, add them as a guest, and schedule their recording for {date}."
    t = Trace(task)
    t.add_turn("I need to add a new guest and schedule a calendar recording. I will navigate to the Guests domain.", 3, change_state="Guests")
    t.add_turn(f"I am in the Guests domain. I will add {name} with the provided bio.", 1, {"name": name, "bio": bio}, result=f"Guest added with ID {200+i}.")
    mem_note = f"Successfully added guest {name} with ID {200+i}, now I need to schedule the recording for {date}."
    t.add_turn("I will save the new guest ID in memory so I can schedule their recording in the next step.", 3, {"note": mem_note}, set_memory=mem_note, result="Memory note saved.")
    t.add_turn(f"Using the guest ID {200+i} from my memory, I will schedule the calendar recording for {date}.", 2, {"guest_id": 200+i, "date": date}, result="Recording scheduled successfully.")
    t.add_turn("The guest has been added and the recording is scheduled. The user's task is fully complete.", 5)
    traces.append(t)

# Type 3: Audio Trim Error -> Fix (8 traces) - Matches "Write and run Python code, handle an error, fix and rerun"
t3_tasks = [
    "Trim the audio file {file_id} to keep only the segment between {fixed_start}s and {fixed_end}s.",
    "Cut audio file {file_id} so it only contains the audio from {fixed_start}s to {fixed_end}s.",
    "We need to slice audio file {file_id}. Just keep the part between {fixed_start}s and {fixed_end}s.",
    "Please trim down the asset {file_id}. The good take is from {fixed_start}s to {fixed_end}s.",
    "Remove the start and end of audio file {file_id}, leaving only {fixed_start}s to {fixed_end}s.",
    "I need you to trim asset {file_id}, saving just the timeframe between {fixed_start}s and {fixed_end}s.",
    "Edit audio {file_id} by trimming it strictly down to the {fixed_start}s through {fixed_end}s portion.",
    "Crop the audio file {file_id} so it starts at {fixed_start}s and ends precisely at {fixed_end}s."
]
for i in range(8):
    file_id = 300 + i
    start, end = 15.5, 2.0  # error state
    fixed_start, fixed_end = 2.0, 15.5
    task = t3_tasks[i].format(file_id=file_id, fixed_start=fixed_start, fixed_end=fixed_end)
    t = Trace(task)
    t.add_turn("The user wants me to trim an audio file. I need to enter the Audio Assets domain.", 2, change_state="Audio Assets")
    t.add_turn(f"I will trim audio file {file_id}. I will accidentally swap the start and end times by mistake.", 2, {"file_id": file_id, "start": start, "end": end}, result="Error: Start time cannot be greater than end time.")
    mem_note = f"Encountered an error because start time {start} was greater than end time {end}. I must swap them."
    t.add_turn("I made a mistake with the timestamps. I will store a memory note to remind myself to fix the order.", 4, {"note": mem_note}, set_memory=mem_note, result="Memory note saved.")
    t.add_turn("I will call the trim tool again, this time correctly using the smaller value for the start parameter.", 2, {"file_id": file_id, "start": fixed_start, "end": fixed_end}, result=f"File {file_id} successfully trimmed.")
    t.add_turn("The audio has been properly trimmed after fixing the timestamp error. The task is fully complete.", 6)
    traces.append(t)

# Type 4: Sponsor Log / Analytics (8 traces) - Matches "Load or compute data, plot or calculate a result"
sponsor_names = ["NordVPN", "Squarespace", "Manscaped", "BetterHelp", "Audible", "Skillshare", "MeUndies", "Simplisafe"]
for i in range(8):
    s_name = sponsor_names[i]
    rate = 25.5 + i
    ep_id = 400 + i
    task = f"Add {s_name} as a new sponsor with a rate of ${rate}, then log an ad read for episode {ep_id}."
    t = Trace(task)
    t.add_turn("I need to manage sponsors and log ad reads. I will navigate to the Sponsors domain.", 6, change_state="Sponsors")
    t.add_turn(f"I am in the Sponsors domain. I will add the new sponsor {s_name} with the requested rate.", 1, {"name": s_name, "rate": rate}, result=f"Sponsor added with ID {500+i}.")
    mem_note = f"Added sponsor {s_name} with assigned ID {500+i}, now I will log an ad read for episode {ep_id}."
    t.add_turn("I will save the newly generated sponsor ID in memory so I can calculate the ad read properly.", 3, {"note": mem_note}, set_memory=mem_note, result="Memory note saved.")
    t.add_turn(f"Using the sponsor ID {500+i} from memory, I will log the ad read for episode {ep_id}.", 2, {"episode_id": ep_id, "sponsor_id": 500+i}, result="Ad read logged successfully.")
    t.add_turn("The sponsor has been added and the ad read has been successfully logged. The task is complete.", 5)
    traces.append(t)

# Type 5: Multi-domain: Episode + Distribution (10 traces) - Matches "Multi-domain: task requires visiting exactly 2 different domains"
t5_tasks = [
    "Publish episode {ep_id} and then immediately sync it to Apple Podcasts.",
    "We are ready to go live with episode {ep_id}, publish it and sync to Apple.",
    "Please hit publish on episode {ep_id}, then make sure it syncs over to Apple Podcasts.",
    "Publish ep {ep_id}, and right after that, trigger the Apple Podcasts sync.",
    "Time to release episode {ep_id}. Publish it first, then sync to the Apple platform.",
    "Make episode {ep_id} public by publishing it, then run the Apple Podcasts sync.",
    "I need episode {ep_id} published right now, and also synced to Apple Podcasts.",
    "Go ahead and publish episode {ep_id}, followed by an immediate sync to Apple Podcasts.",
    "Release episode {ep_id} by publishing, and then ensure it gets synced to Apple.",
    "Publish our latest episode {ep_id}, and don't forget to sync it with Apple Podcasts."
]
for i in range(10):
    ep_id = 600 + i
    task = t5_tasks[i].format(ep_id=ep_id)
    t = Trace(task)
    t.add_turn("The user wants me to publish an episode and sync it. I will go to the Episodes domain first.", 1, change_state="Episodes")
    t.add_turn(f"I am in the Episodes domain. I will execute the tool to publish episode {ep_id}.", 3, {"id": ep_id}, result=f"Episode {ep_id} published successfully.")
    mem_note = f"Successfully published episode {ep_id}, the next step is to navigate and sync it to the Apple platform."
    t.add_turn("I will store a memory note confirming the episode is published before I navigate away for distribution.", 4, {"note": mem_note}, set_memory=mem_note, result="Memory note saved.")
    t.add_turn("To sync the podcast to a new platform, I must return to the Home menu to find Distribution.", 5, pop_state=True)
    t.add_turn("I am at the Home menu. I will now enter the Distribution domain to complete the sync.", 4, change_state="Distribution")
    t.add_turn("I am inside Distribution. I will trigger the tool to sync our feed to Apple Podcasts.", 2, result="Sync to Apple Podcasts initiated.")
    t.add_turn("The episode was published and the distribution sync has been fully initiated. My task is complete.", 6)
    traces.append(t)

# Type 6: BACK correction (8 traces) - Matches "BACK correction: agent goes to wrong domain, backs out, corrects"
t6_tasks = [
    "Generate a promotional audiogram for episode {ep_id}.",
    "Create an audiogram for episode {ep_id} so we can share it on Instagram.",
    "I need a short video audiogram for episode {ep_id} for our social media team.",
    "Please run the audiogram generator on episode {ep_id} for our upcoming marketing push.",
    "Make an audiogram for episode {ep_id}, we need it for Twitter today.",
    "Produce a marketing audiogram for episode {ep_id}.",
    "We need promotional materials. Generate an audiogram for episode {ep_id}.",
    "Use the marketing tools to create an audiogram snippet for episode {ep_id}."
]
for i in range(8):
    ep_id = 700 + i
    task = t6_tasks[i].format(ep_id=ep_id)
    t = Trace(task)
    t.add_turn("I need to generate an audiogram. I will navigate to the Episodes domain to find the tool.", 1, change_state="Episodes")
    t.add_turn("I am in the Episodes domain, but the audiogram generation tool is not here. I need to go BACK.", 5, pop_state=True)
    t.add_turn("I am back at the Home menu. The correct domain for generating promotional audiograms is Marketing.", 7, change_state="Marketing")
    t.add_turn(f"I am in the Marketing domain. I will run the audiogram generator for episode {ep_id}.", 1, {"episode_id": ep_id}, result=f"Audiogram generated at /assets/audiograms/ep_{ep_id}.mp4.")
    mem_note = f"I generated the audiogram for episode {ep_id} correctly after initially navigating to the wrong domain by mistake."
    t.add_turn("I will store a brief note about completing the audiogram generation to document the task progress accurately.", 3, {"note": mem_note}, set_memory=mem_note, result="Memory note saved.")
    t.add_turn("The requested audiogram has been successfully generated and saved. The user's task is fully resolved.", 5)
    traces.append(t)

# Type 7: Short tasks (8 traces) - Matches "Short tasks: completed in exactly 2–3 turns, DONE chosen early"
t7_tasks = [
    "Fetch the main RSS feed URL so I can share it with a new partner.",
    "Can you grab the RSS feed URL? I need to paste it into our website.",
    "I need the direct RSS feed link to submit our podcast to a new directory.",
    "Please retrieve the RSS feed URL, a sponsor is asking for it.",
    "Find our RSS feed link. We are setting up a new marketing tool.",
    "Get the RSS feed URL for me quickly, I'm updating our media kit.",
    "I forgot our RSS feed URL, please fetch it so I can share it on Twitter.",
    "Grab the RSS feed URL so I can verify our submission on a new app."
]
for i in range(8):
    task = t7_tasks[i]
    t = Trace(task)
    t.add_turn("The user wants the RSS feed URL. This is managed in the Distribution domain, so I will go there.", 4, change_state="Distribution")
    t.add_turn("I am in the Distribution domain. I will call the tool to get the RSS feed URL.", 3, result="RSS Feed URL: https://feed.podcast.com/main.xml")
    t.add_turn("I successfully retrieved the RSS feed URL as requested. The task is simple and now completely finished.", 6)
    traces.append(t)

filename = f"dataset_{uuid.uuid4().hex[:8]}.jsonl"
with open(filename, "w") as f:
    for t in traces:
        json_obj = {
            "task": t.task,
            "turns": t.turns
        }
        f.write(json.dumps(json_obj) + "\n")

print(f"File created: {filename}")
print(f"Total traces generated: {len(traces)}")
