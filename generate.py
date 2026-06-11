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

# ==========================================
# 1. Analytics -> Show Notes (10 traces)
# ==========================================
t1_tasks = [
    "Check how many people downloaded episode 101. Then edit its show notes to add a huge thank you message for hitting that number.",
    "I'm curious about the metrics for our 50th episode. Grab the total download count and put a quick celebratory note in the description.",
    "Find out if episode 105 passed our goal. Get the download number and append a milestone update to its show notes right away.",
    "We need to highlight our success for episode 88. First pull the total downloads, then insert that exact figure into the episode's show notes.",
    "Look up the latest listener metrics for episode 200. Once you see the downloads, modify the show notes to say thanks to the audience.",
    "Can you retrieve the total historical downloads for ep 14? We promised a reward, so update the show notes once you have the count.",
    "Examine the performance for our latest interview, episode 99. Get the download count and revise the show notes to reflect our new record.",
    "Get the all-time download tally for episode 112. After getting the data, patch the show notes to include a grateful listener shoutout.",
    "Investigate how well our Halloween special (episode 31) did. Fetch the download stats and stick a brief milestone message into its text.",
    "Check the analytics for episode 404 to see total downloads. Then write a short update in the show notes thanking our community."
]

for i in range(10):
    ep_id = [101, 50, 105, 88, 200, 14, 99, 112, 31, 404][i]
    dl_count = 5000 + i * 452
    task = t1_tasks[i]
    t = Trace(task)
    t.add_turn(f"The first part of the request requires me to fetch download statistics. I must navigate to the Analytics domain.", 5, change_state="Analytics")
    t.add_turn(f"Now inside Analytics, I can fetch the specific stats. I will execute the tool for episode {ep_id}.", 1, {"episode_id": ep_id}, result=f"Episode {ep_id} has {dl_count} total downloads.")

    mem_notes = [
        f"Episode {ep_id} achieved exactly {dl_count} downloads, and I need to update its show notes.",
        f"The download metric for episode {ep_id} is {dl_count}, next step is updating the show notes.",
        f"I retrieved {dl_count} total downloads for episode {ep_id}, which I must add to the notes.",
        f"Found exactly {dl_count} downloads for ep {ep_id}. I will transition to Episodes to update notes.",
        f"Total downloads for episode {ep_id} reached {dl_count}. I must record this in the show notes.",
        f"Episode {ep_id} has {dl_count} downloads. I need to navigate back and edit its show notes.",
        f"The analytics tool returned {dl_count} downloads for episode {ep_id}. I must update the notes next.",
        f"Remembering that episode {ep_id} got {dl_count} downloads, so I can put it in the show notes.",
        f"I need to insert the count of {dl_count} downloads into the show notes for episode {ep_id}.",
        f"Episode {ep_id} hits {dl_count} downloads. The next action is to navigate to Episodes for updating."
    ]
    mem_note = mem_notes[i]
    t.add_turn(f"Since I need to switch domains, I will store the exact download count in memory so I don't forget.", 3, {"note": mem_note}, set_memory=mem_note, result="Memory note saved.")
    t.add_turn("With the metric saved in memory, I must return to the Home menu to access the Episodes section.", 4, pop_state=True)
    t.add_turn("From the Home menu, I will enter the Episodes domain to edit the show notes.", 1, change_state="Episodes")
    notes_str = f"Thank you all for an amazing {dl_count} downloads! We appreciate your massive support."
    t.add_turn(f"Using the download number from my memory, I will overwrite the show notes for episode {ep_id}.", 2, {"id": ep_id, "notes": notes_str}, result="Show notes updated successfully.")
    t.add_turn("The show notes now reflect the milestone achievement based on the analytics. The task is fully completed.", 6)
    traces.append(t)

# ==========================================
# 2. Guest Add -> Schedule (8 traces)
# ==========================================
t2_data = [
    ("Alice Chen", "Author of bestselling sci-fi.", "2024-10-01", "Add author Alice Chen with her bio 'Author of bestselling sci-fi.', and schedule her recording for 2024-10-01."),
    ("Dr. Bob Smith", "Leading expert in quantum computing.", "2024-10-05", "Read the bio 'Leading expert in quantum computing.' for Dr. Bob Smith, add him as a guest, and block his recording for 2024-10-05."),
    ("Charlie Day", "Talented local indie artist.", "2024-10-10", "We booked Charlie Day. His bio is 'Talented local indie artist.'. Create his guest profile and set the recording date to 2024-10-10."),
    ("Diana Prince", "Senior software engineer at TechCorp.", "2024-10-15", "Add a new guest named Diana Prince ('Senior software engineer at TechCorp.') and ensure we schedule the podcast recording on 2024-10-15."),
    ("Chef Eve", "Three-star Michelin culinary master.", "2024-10-20", "Put Chef Eve in our guest database with bio 'Three-star Michelin culinary master.' and immediately schedule her to record on 2024-10-20."),
    ("Capt. Frank", "Commercial airline pilot and instructor.", "2024-10-25", "Create a guest entry for Capt. Frank ('Commercial airline pilot and instructor.') then schedule the recording session for 2024-10-25."),
    ("Grace Kelly", "Award-winning screenwriter and director.", "2024-11-01", "We are interviewing Grace Kelly. Add her bio 'Award-winning screenwriter and director.' to the system, then set the recording date to 2024-11-01."),
    ("Dr. Heidi", "Chief medical doctor in cardiology.", "2024-11-05", "Register Dr. Heidi ('Chief medical doctor in cardiology.') as a guest and schedule her interview for 2024-11-05.")
]

for i in range(8):
    name, bio, date, task = t2_data[i]
    t = Trace(task)
    t.add_turn("This task involves managing guests and scheduling them. I should open the Guests menu to start.", 3, change_state="Guests")
    t.add_turn(f"I will create a profile for {name} using the provided short biography string.", 1, {"name": name, "bio": bio}, result=f"Guest added with ID {200+i}.")

    mem_notes = [
        f"Guest {name} was assigned ID {200+i}. I must now schedule the recording for {date}.",
        f"Successfully added guest {name} under ID {200+i}, next I will schedule them for {date}.",
        f"The new guest ID is {200+i} for {name}. I need to book the {date} recording.",
        f"I registered guest {name} with ID {200+i}, and must schedule a recording on {date}.",
        f"Guest profile created with ID {200+i} for {name}. Next action is scheduling the date {date}.",
        f"Saved guest {name} as ID {200+i}. The remaining step is scheduling the recording on {date}.",
        f"I obtained guest ID {200+i} for {name}, which is required to schedule the {date} recording.",
        f"Created new guest entry ID {200+i} for {name}. I must schedule their recording for {date}."
    ]
    mem_note = mem_notes[i]
    t.add_turn("The scheduling tool requires a guest ID. I will memorize the newly generated ID to use it next.", 3, {"note": mem_note}, set_memory=mem_note, result="Memory note saved.")
    t.add_turn(f"I will recall the guest ID {200+i} from memory to book the calendar recording.", 2, {"guest_id": 200+i, "date": date}, result="Recording scheduled successfully.")
    t.add_turn("Both the guest profile creation and calendar scheduling are complete. The overarching task is finished.", 5)
    traces.append(t)

# ==========================================
# 3. Audio Trim Error -> Fix (8 traces)
# ==========================================
t3_data = [
    (301, 15.5, 2.0, 2.0, 15.5, "Trim the audio file 301 to keep only the segment between 2.0s and 15.5s."),
    (302, 45.0, 10.5, 10.5, 45.0, "Cut audio file 302 so it only contains the audio from 10.5s to 45.0s."),
    (303, 120.0, 15.0, 15.0, 120.0, "We need to slice audio file 303. Just keep the part between 15.0s and 120.0s."),
    (304, 88.2, 5.1, 5.1, 88.2, "Please trim down the asset 304. The good take is from 5.1s to 88.2s."),
    (305, 30.0, 0.5, 0.5, 30.0, "Remove the start and end of audio file 305, leaving only 0.5s to 30.0s."),
    (306, 60.5, 12.2, 12.2, 60.5, "I need you to trim asset 306, saving just the timeframe between 12.2s and 60.5s."),
    (307, 200.0, 45.5, 45.5, 200.0, "Edit audio 307 by trimming it strictly down to the 45.5s through 200.0s portion."),
    (308, 95.0, 22.0, 22.0, 95.0, "Crop the audio file 308 so it starts at 22.0s and ends precisely at 95.0s.")
]

for i in range(8):
    file_id, err_start, err_end, fixed_start, fixed_end, task = t3_data[i]
    t = Trace(task)
    t.add_turn("The request is to manipulate an audio file. I need to navigate to Audio Assets.", 2, change_state="Audio Assets")
    t.add_turn(f"I am attempting to trim file {file_id}. I will accidentally provide the larger number as the start time.", 2, {"file_id": file_id, "start": err_start, "end": err_end}, result="Error: Start time cannot be greater than end time.")

    mem_notes = [
        f"Encountered an error because start {err_start} > end {err_end}. I must swap them and retry.",
        f"The trim failed due to reversed timestamps {err_start} and {err_end}. I must correct the order.",
        f"I made a mistake ordering the timestamps {err_start} and {err_end}. I need to run it properly.",
        f"Got an error from placing start {err_start} after end {err_end}. Re-running with corrected values.",
        f"Start time {err_start} was higher than end time {err_end}. I need to fix this error.",
        f"Trimming failed because I passed {err_start} then {err_end}. I must reverse these parameters to succeed.",
        f"The system threw an error for backwards timestamps {err_start} and {err_end}. I will fix it.",
        f"Error logging shows start {err_start} exceeds end {err_end}. I must submit the smaller value first."
    ]
    mem_note = mem_notes[i]
    t.add_turn("I made an error with the bounds. I will store a note to correct the parameter order.", 4, {"note": mem_note}, set_memory=mem_note, result="Memory note saved.")
    t.add_turn(f"Following my memory note, I am calling trim again with the proper chronological timestamps.", 2, {"file_id": file_id, "start": fixed_start, "end": fixed_end}, result=f"File {file_id} successfully trimmed.")
    t.add_turn("The asset was successfully cropped after fixing the validation error. Everything is resolved.", 6)
    traces.append(t)

# ==========================================
# 4. Sponsor Log / Analytics (8 traces)
# ==========================================
t4_data = [
    ("NordVPN", 25.5, 401, "Add NordVPN as a new sponsor with a CPM rate of $25.5, then log an ad read for episode 401."),
    ("Squarespace", 30.0, 402, "Create a sponsor profile for Squarespace at $30.0 per ad. Once added, log a read for episode 402."),
    ("Manscaped", 18.75, 403, "Register Manscaped as a sponsor (rate $18.75). After you have their ID, log an ad on episode 403."),
    ("BetterHelp", 40.0, 404, "Add BetterHelp at a rate of $40.0. Ensure you record that they sponsored episode 404."),
    ("Audible", 22.5, 405, "Put Audible in our sponsor list with a $22.5 rate, then immediately log an ad read for ep 405."),
    ("Skillshare", 15.0, 406, "We have a $15.0 deal with Skillshare. Add them, then track an ad read for episode 406."),
    ("MeUndies", 28.0, 407, "Create the sponsor MeUndies ($28.0 rate) and use the system to log their ad read on episode 407."),
    ("SimpliSafe", 35.0, 408, "Add SimpliSafe at $35.0 to our sponsors, and log that they were read during episode 408.")
]

for i in range(8):
    s_name, rate, ep_id, task = t4_data[i]
    t = Trace(task)
    t.add_turn("I need to deal with advertising partners. I will enter the Sponsors domain.", 6, change_state="Sponsors")
    t.add_turn(f"Inside Sponsors, I will use the tool to add {s_name} at the specified rate.", 1, {"name": s_name, "rate": rate}, result=f"Sponsor added with ID {500+i}.")

    mem_notes = [
        f"Added sponsor {s_name} with ID {500+i}. Next I must log the ad read for episode {ep_id}.",
        f"The sponsor {s_name} was created as ID {500+i}. I need to track their ad on episode {ep_id}.",
        f"Sponsor ID {500+i} belongs to {s_name}. I must use this to log a read for ep {ep_id}.",
        f"Saved sponsor {s_name} under ID {500+i}. The remaining task is logging the ad for episode {ep_id}.",
        f"Obtained sponsor ID {500+i} for {s_name}, which is needed to log an ad for episode {ep_id}.",
        f"I created sponsor {s_name} (ID {500+i}). I will now log the ad on episode {ep_id}.",
        f"I need to log an ad for episode {ep_id} using the newly created sponsor {s_name} ID {500+i}.",
        f"Sponsor {s_name} is in the system as ID {500+i}. Next step: log ad read for ep {ep_id}."
    ]
    mem_note = mem_notes[i]
    t.add_turn("I must remember the new sponsor's unique ID to correctly associate the upcoming ad read.", 3, {"note": mem_note}, set_memory=mem_note, result="Memory note saved.")
    t.add_turn(f"I will refer to my memory to log the ad for episode {ep_id} against the correct sponsor.", 2, {"episode_id": ep_id, "sponsor_id": 500+i}, result="Ad read logged successfully.")
    t.add_turn("The sponsor was recorded and the ad was successfully tracked. Task is complete.", 5)
    traces.append(t)

# ==========================================
# 5. Multi-domain: Episode + Distribution (10 traces)
# ==========================================
t5_data = [
    (601, "Publish episode 601 and then immediately sync it to Apple Podcasts."),
    (602, "We are ready to go live with episode 602. Publish it and sync our feed to Spotify."),
    (603, "Please hit publish on episode 603, then make sure it syncs over to Apple Podcasts."),
    (604, "Publish ep 604, and right after that, trigger the Spotify sync."),
    (605, "Time to release episode 605. Publish it first, then sync to the Apple platform."),
    (606, "Make episode 606 public by publishing it, then run the Spotify sync."),
    (607, "I need episode 607 published right now, and also synced to Apple Podcasts."),
    (608, "Go ahead and publish episode 608, followed by an immediate sync to Spotify."),
    (609, "Release episode 609 by publishing, and then ensure it gets synced to Apple."),
    (610, "Publish our latest episode 610, and don't forget to sync it with Spotify.")
]

for i in range(10):
    ep_id, task = t5_data[i]
    is_spotify = i % 2 != 0
    platform = "Spotify" if is_spotify else "Apple Podcasts"
    tool_action = 1 if is_spotify else 2

    t = Trace(task)
    t.add_turn("The user wants me to make an episode public. I need to navigate to Episodes.", 1, change_state="Episodes")
    t.add_turn(f"I will execute the publishing tool to push episode {ep_id} live.", 3, {"id": ep_id}, result=f"Episode {ep_id} published successfully.")

    mem_notes = [
        f"Episode {ep_id} is successfully published. I must now sync the feed to {platform} via Distribution.",
        f"I published episode {ep_id} just now. My next goal is to run a {platform} sync.",
        f"The publish action for episode {ep_id} succeeded. I need to navigate to Distribution for {platform}.",
        f"Episode {ep_id} is live. I will store this so I can safely navigate to sync to {platform}.",
        f"I managed to publish episode {ep_id}. The next domain is Distribution to sync to {platform}.",
        f"Publishing of episode {ep_id} is done. I have to go to Distribution to trigger {platform} sync.",
        f"Episode {ep_id} status is published. I am leaving this domain to initiate the {platform} sync.",
        f"I successfully set episode {ep_id} to public. Next, I must trigger the {platform} feed sync.",
        f"Confirmed episode {ep_id} publish. I need to return to Home, then Distribution for {platform} sync.",
        f"Episode {ep_id} released. I must store this state before heading to Distribution for {platform}."
    ]
    mem_note = mem_notes[i]
    t.add_turn("Before navigating to a different module, I will record the successful publish state.", 4, {"note": mem_note}, set_memory=mem_note, result="Memory note saved.")
    t.add_turn("I must return to the main menu first in order to reach the Distribution section.", 5, pop_state=True)
    t.add_turn("From the home screen, I will navigate into Distribution to push the feed updates.", 4, change_state="Distribution")
    t.add_turn(f"Now in Distribution, I will trigger the specific sync tool for {platform}.", tool_action, result=f"Sync to {platform} initiated.")
    t.add_turn("The episode is live and the syndication platform has been pinged. I am finished.", 6)
    traces.append(t)

# ==========================================
# 6. BACK correction (8 traces)
# ==========================================
t6_data = [
    (701, "Generate a promotional audiogram for episode 701.", "promotional audiograms"),
    (702, "Create an audiogram for episode 702 so we can share it on Instagram.", "social media assets"),
    (703, "I need a short video audiogram for episode 703 for our social media team.", "video snippets"),
    (704, "Please run the audiogram generator on episode 704 for our upcoming marketing push.", "marketing collateral"),
    (705, "Make an audiogram for episode 705, we need it for Twitter today.", "promotional videos"),
    (706, "Produce a marketing audiogram for episode 706.", "visual audiograms"),
    (707, "We need promotional materials. Generate an audiogram for episode 707.", "social media audiograms"),
    (708, "Use the marketing tools to create an audiogram snippet for episode 708.", "audiogram visuals")
]

for i in range(8):
    ep_id, task, thought_focus = t6_data[i]
    t = Trace(task)
    t.add_turn("I need to manage something related to an episode, so I will naturally look in the Episodes domain.", 1, change_state="Episodes")
    t.add_turn(f"I am in Episodes, but I realize tools for {thought_focus} aren't here. I must go BACK.", 5, pop_state=True)
    t.add_turn(f"Back at Home. To create {thought_focus}, the correct choice is obviously the Marketing domain.", 7, change_state="Marketing")
    t.add_turn(f"I will now trigger the proper generator tool to render the audiogram for episode {ep_id}.", 1, {"episode_id": ep_id}, result=f"Audiogram generated at /assets/audiograms/ep_{ep_id}.mp4.")

    mem_notes = [
        f"Successfully generated an audiogram for episode {ep_id} after realizing my initial domain navigation was incorrect.",
        f"I created the audiogram for episode {ep_id} in the Marketing domain after a brief misstep.",
        f"The audiogram generation for episode {ep_id} worked perfectly once I navigated to the correct Marketing domain.",
        f"I backed out of the wrong menu and successfully built the promotional audiogram for episode {ep_id}.",
        f"Audiogram for episode {ep_id} was saved. I initially went to Episodes, but Marketing was correct.",
        f"I corrected my path and generated the visual audiogram for episode {ep_id} in the Marketing section.",
        f"Successfully produced the audiogram for episode {ep_id} by using the Marketing tools instead of Episodes.",
        f"The asset for episode {ep_id} is generated. I learned that audiograms belong in the Marketing menu."
    ]
    mem_note = mem_notes[i]
    t.add_turn("I will drop a quick note acknowledging the successful completion after my initial navigation error.", 3, {"note": mem_note}, set_memory=mem_note, result="Memory note saved.")
    t.add_turn("The audiogram has been generated and the user request is fully satisfied.", 5)
    traces.append(t)

# ==========================================
# 7. Short tasks (8 traces)
# ==========================================
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

    reasons = [
        "The RSS feed represents our syndication root, which is managed inside the Distribution domain.",
        "To get the feed URL, I should open the Distribution menu where syndication is handled.",
        "The user wants the raw podcast feed. I will enter the Distribution section to find it.",
        "RSS feeds are distributed to podcast players. I will check the Distribution options.",
        "I must look inside the Distribution domain for tools related to the global RSS feed.",
        "To obtain the direct feed link, the most logical place is the Distribution menu.",
        "The Distribution domain should contain the necessary tooling to fetch the RSS feed URL.",
        "I will navigate to Distribution, as that is where syndication URLs are typically kept."
    ]
    t.add_turn(reasons[i], 4, change_state="Distribution")

    call_reasons = [
        "I found the relevant tool. I will execute it to fetch the raw RSS feed URL.",
        "I will use the get_rss_feed_url tool to instantly retrieve the requested link.",
        "I'll call the RSS tool to output the string the user is asking for.",
        "This tool provides the exact URL needed. I will trigger it now.",
        "I am running the tool to fetch the master RSS feed link.",
        "I'll trigger the RSS fetch tool so the result is displayed back to the user.",
        "Executing the tool to get the RSS feed URL immediately.",
        "I'll pull the URL using the dedicated RSS fetch option in this menu."
    ]
    t.add_turn(call_reasons[i], 3, result="RSS Feed URL: https://feed.podcast.com/main.xml")

    done_reasons = [
        "I successfully retrieved the RSS feed URL as requested. This quick task is now completely finished.",
        "The URL has been outputted to the user. There is nothing else left to do here.",
        "I grabbed the RSS link. The core objective is met, so I can terminate the task.",
        "The RSS feed was provided. I am marking this simple request as fully complete.",
        "Since the tool returned the exact requested URL, the job is done.",
        "The user has the feed link now. I'll cleanly wrap up the interaction.",
        "The syndication URL was delivered successfully. I will end the task execution.",
        "Task completed. The direct RSS link was successfully fetched and presented."
    ]
    t.add_turn(done_reasons[i], 6)
    traces.append(t)

filename = "dataset_final.jsonl"
with open(filename, "w") as f:
    for t in traces:
        json_obj = {
            "task": t.task,
            "turns": t.turns
        }
        f.write(json.dumps(json_obj) + "\n")

print(f"File created: {filename}")
print(f"Total traces generated: {len(traces)}")
