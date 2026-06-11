import json
import random
import uuid

def count_words(s):
    return len(s.split())

def validate_word_count(s, min_w=10, max_w=20):
    words = count_words(s)
    if not (min_w <= words <= max_w):
        raise ValueError(f"Word count {words} is not between {min_w} and {max_w}: '{s}'")

home_menu_items = [
    "1. Playback Control — navigate to Playback Control tools",
    "2. Volume & Audio — navigate to Volume & Audio tools",
    "3. Subtitles — navigate to Subtitles tools",
    "4. Playlist — navigate to Playlist tools",
    "5. Video Settings — navigate to Video Settings tools",
    "6. Streaming — navigate to Streaming tools",
    "7. Library — navigate to Library tools",
    "8. MEM [note: `string`] — store a memory note (10–20 words exactly)",
    "9. BACK — go to previous state",
    "10. DONE — task is complete"
]

domain_menus = {
    "Playback Control": [
        "1. play", "2. pause", "3. stop", "4. seek [time: `time`]", "5. set_playback_rate [rate: `float`]",
        "6. MEM [note: `string`]", "7. BACK", "8. DONE"
    ],
    "Volume & Audio": [
        "1. set_volume [level: `int`]", "2. mute", "3. unmute", "4. select_audio_track [id: `int`]",
        "5. MEM [note: `string`]", "6. BACK", "7. DONE"
    ],
    "Subtitles": [
        "1. enable_subtitles", "2. disable_subtitles", "3. select_subtitle_track [lang: `string`]",
        "4. adjust_subtitle_delay [ms: `int`]", "5. MEM [note: `string`]", "6. BACK", "7. DONE"
    ],
    "Playlist": [
        "1. add_to_playlist [url: `url`]", "2. remove_from_playlist [id: `int`]", "3. next_video",
        "4. previous_video", "5. MEM [note: `string`]", "6. BACK", "7. DONE"
    ],
    "Video Settings": [
        "1. set_resolution [res: `enum(1080p,720p,480p)`]", "2. toggle_fullscreen", "3. adjust_brightness [level: `int`]",
        "4. MEM [note: `string`]", "5. BACK", "6. DONE"
    ],
    "Streaming": [
        "1. connect_cast [device: `string`]", "2. disconnect_cast", "3. get_stream_info",
        "4. MEM [note: `string`]", "5. BACK", "6. DONE"
    ],
    "Library": [
        "1. scan_library [path: `path`]", "2. search_library [query: `string`]", "3. list_recent",
        "4. MEM [note: `string`]", "5. BACK", "6. DONE"
    ]
}

def format_menu(items):
    return "\n".join(f"  {item}" for item in items)

class AgentSim:
    def __init__(self, task):
        self.task = task
        self.state = "Home"
        self.state_stack = []
        self.memory_note = None
        self.turns = []
        self.last_result = None

    def _get_menu_text(self):
        if self.state == "Home":
            return format_menu(home_menu_items)
        return format_menu(domain_menus[self.state])

    def _get_user_turn(self):
        lines = []
        lines.append(f"USER:\n[TASK]: {self.task}")
        lines.append(f"[STATE]: {self.state}")
        if self.memory_note:
            lines.append(f"[MEMORY]: {self.memory_note}")
        if self.last_result:
            lines.append(f"[RESULT]: {self.last_result}")
        lines.append("[MENU]:\n" + self._get_menu_text())
        return "\n".join(lines)

    def do_action(self, action_num, reason, args=None, result_str=None, new_state=None):
        user_text = self._get_user_turn()

        assist_obj = {
            "reason": reason,
            "action": action_num
        }
        if args is not None:
            assist_obj["args"] = args

        self.turns.append({
            "user": user_text,
            "assistant": json.dumps(assist_obj)
        })

        menu_items = home_menu_items if self.state == "Home" else domain_menus[self.state]
        action_text = ""
        for item in menu_items:
            if item.strip().startswith(str(action_num) + "."):
                action_text = item
                break

        self.last_result = None

        if "MEM" in action_text:
            self.memory_note = args["note"]
            validate_word_count(self.memory_note)
            self.last_result = f"Memory updated."

        elif "BACK" in action_text:
            if self.state_stack:
                self.state = self.state_stack.pop()

        elif "DONE" in action_text:
            pass

        elif self.state == "Home" and action_num <= 7:
            domains = ["Playback Control", "Volume & Audio", "Subtitles", "Playlist", "Video Settings", "Streaming", "Library"]
            self.state_stack.append(self.state)
            self.state = domains[action_num - 1]

        else:
            if result_str:
                self.last_result = result_str
            else:
                self.last_result = "Success"

        if new_state:
            self.state = new_state

    def finish_done(self, reason):
        menu_items = home_menu_items if self.state == "Home" else domain_menus[self.state]
        done_num = [int(i.split(".")[0]) for i in menu_items if "DONE" in i][0]
        self.do_action(done_num, reason)

    def back(self, reason):
        menu_items = home_menu_items if self.state == "Home" else domain_menus[self.state]
        back_num = [int(i.split(".")[0]) for i in menu_items if "BACK" in i][0]
        self.do_action(back_num, reason)

    def mem(self, reason, note):
        validate_word_count(note)
        menu_items = home_menu_items if self.state == "Home" else domain_menus[self.state]
        mem_num = [int(i.split(".")[0]) for i in menu_items if "MEM" in i][0]
        self.do_action(mem_num, reason, {"note": note})

traces = []

# 1. 10 traces - "Search & Save" (Library -> Playlist). Primary: Library.
templates_1 = [
    "I need you to search for {topic} in the library and then add it to my current playlist.",
    "Could you please find the movie {topic} in our media collection and queue it up in the playlist?",
    "Look up {topic} using the library search tool, and make sure it gets added to the playlist.",
    "Do a quick search for {topic} and drop the found video into my active playlist.",
    "I want to watch {topic} tonight. Find it in the library first, then put it on the playlist.",
    "Please locate {topic} in the local library database and add its URL to the playlist.",
    "Can you search the media library for {topic} and then append it to my playlist?",
    "Search the local catalog for {topic} and place the exact video URL into the playlist.",
    "Help me find {topic} in the library so we can add it to the video playlist.",
    "I'd like to add {topic} to the playlist, but you'll have to search the library for it first."
]
topics_1 = ["Inception", "The Matrix", "Interstellar", "Batman", "Avengers", "Nature Documentary", "Comedy Special", "Music Concert", "Tech Talk", "Sci-Fi Series"]

for i in range(10):
    topic = topics_1[i]
    task = templates_1[i].format(topic=topic)
    sim = AgentSim(task)

    sim.do_action(7, f"I need to navigate to the Library menu first to search for the requested {topic} video.", None)
    sim.do_action(2, f"I will use the search tool to find '{topic}' in the library to get the correct URL.", {"query": topic}, f"1. {topic} Original - https://lib.local/{topic.lower().replace(' ', '')}\n2. {topic} Behind the Scenes")

    mem_note = f"I found the media URL for {topic}, and the user wants it added to the playlist."
    sim.mem(f"I found the URL, so I'll store a memory note about the video {topic}.", mem_note)

    sim.back("I have the URL and need to add it to the playlist, which requires returning to the Home menu.")
    sim.do_action(4, "Now I will enter the Playlist menu to add the URL I just found.")
    sim.do_action(1, f"Adding the URL for {topic} to the user's playlist so they can watch it later.", {"url": f"https://lib.local/{topic.lower().replace(' ', '')}"}, f"Successfully added https://lib.local/{topic.lower().replace(' ', '')} to the playlist.")
    sim.finish_done("The video has been successfully found in the library and added to the playlist as requested.")
    traces.append({"task": sim.task, "turns": sim.turns})

# 2. 8 traces - "Info & Schedule" (Streaming -> Playback Control). Primary: Streaming.
templates_2 = [
    "Connect to the {device}, grab the current stream information, and hit play.",
    "I want you to hook up the {device}, check its stream info, and start the playback.",
    "Please connect cast to {device}, retrieve the stream stats, and then initiate video playback.",
    "Link up with the {device}, ensure the stream info looks good, and begin playing.",
    "Cast to the {device}, fetch the connection stream details, and start the video.",
    "Set up a connection to {device}, get the streaming specs, and trigger the play command.",
    "We need to connect to the {device}, check out the stream info, and start playing the media.",
    "Establish cast connection to the {device}, read back the stream info, and play the movie."
]
devices_2 = ["Living Room TV", "Bedroom Apple TV", "Kitchen Hub", "Office Monitor", "Projector", "Tablet", "Phone", "Garage Speaker"]

for i in range(8):
    device = devices_2[i]
    task = templates_2[i].format(device=device)
    sim = AgentSim(task)

    sim.do_action(6, f"I must first go to the Streaming menu to establish a connection with the {device}.", None)
    sim.do_action(1, f"Attempting to connect to the target cast device named {device}.", {"device": device}, f"Successfully connected to the cast device: {device}.")
    sim.do_action(3, "Retrieving the stream information to ensure the connection is fully stable before playback.", None, "Current stream info: 1080p, 60fps, 5Mbps bitrate.")

    mem_note = f"Successfully connected to the {device} and verified the stream info, moving to start the video playback."
    sim.mem("I should remember that the connection and info check succeeded, and now I just need to start playback.", mem_note)

    sim.back("The streaming setup is complete, so I need to return to the Home menu to control playback.")
    sim.do_action(1, "Entering the Playback Control menu to initiate the video playback on the connected device.")
    sim.do_action(1, "Executing the play command to start the video stream on the cast device.", None, "Playback has been started on the connected cast device.")
    sim.finish_done("The device was connected, stream info was checked, and playback was successfully started.")
    traces.append({"task": sim.task, "turns": sim.turns})

# 3. 8 traces - "Error handling & Retry" (Subtitles). Primary: Subtitles.
templates_3 = [
    "Switch on the subtitles, set them to {lang}, and add a 500ms delay.",
    "I need {lang} subtitles enabled right now, but please give them a 500ms offset.",
    "Turn on closed captions, choose the {lang} track, and set the delay to 500ms.",
    "Enable the subtitle feature, pick {lang} as the language, and delay by 500ms.",
    "Make sure subtitles are enabled, select {lang}, and apply exactly a 500ms delay.",
    "Please activate the subtitles, change the track to {lang}, and put a 500ms delay.",
    "Get the subtitles working in {lang} and ensure there is a 500 millisecond delay.",
    "Enable the text track, make it {lang}, and shift the timing by 500ms."
]
langs_3 = ["Spanish", "French", "German", "Japanese", "Korean", "Italian", "Portuguese", "Dutch"]

for i in range(8):
    lang = langs_3[i]
    task = templates_3[i].format(lang=lang)
    sim = AgentSim(task)

    sim.do_action(3, "I need to navigate to the Subtitles domain to configure the requested subtitle settings.", None)
    sim.do_action(1, "I will first enable subtitles globally before trying to select a specific language track.", None, "Error: Subtitles are currently disabled by the system override.")

    mem_note = "The initial subtitle enable command failed due to a system override, so I must try again."
    sim.mem("The subtitle enable command failed. I will note this and attempt to force enable it.", mem_note)

    sim.do_action(1, "Retrying the enable subtitles command. Overrides usually clear on the second attempt.", None, "Subtitles successfully enabled.")
    sim.do_action(3, f"Now that subtitles are on, I will set the language track to {lang}.", {"lang": lang}, f"Subtitle track successfully set to the {lang} language.")
    sim.do_action(4, "Adjusting the subtitle delay to exactly 500ms as requested by the user.", {"ms": 500}, "Subtitle delay adjusted to 500ms.")
    sim.finish_done("Subtitles were successfully enabled, language set, and delay configured after recovering from an error.")
    traces.append({"task": sim.task, "turns": sim.turns})

# 4. 8 traces - "Compute/Calculate result" (Volume & Audio). Primary: Volume & Audio.
templates_4 = [
    "The volume is currently {start_vol}. Please increase it by 15 and then select audio track 2.",
    "Calculate the new volume if we add 15 to {start_vol}, set it, and switch to audio track 2.",
    "Bump the sound up by 15 from {start_vol}, and make sure audio track 2 is selected.",
    "Starting from a volume of {start_vol}, raise it by 15 levels and change the audio track to 2.",
    "Increase the current {start_vol} volume by exactly 15 steps, then pick audio track 2.",
    "Take the base volume of {start_vol}, add 15 to it, set that level, and use audio track 2.",
    "I need the volume 15 notches higher than {start_vol}, and I also want audio track number 2.",
    "If the volume is {start_vol}, increase it by 15. Also, enable audio track 2."
]

for i in range(8):
    start_vol = 20 + i * 5
    target_vol = start_vol + 15
    task = templates_4[i].format(start_vol=start_vol)
    sim = AgentSim(task)

    sim.do_action(2, "I need to go to the Volume & Audio menu to change the volume level and audio track.", None)

    mem_note = f"The requested volume increase from {start_vol} calculates to {target_vol}, which I will now apply."
    sim.mem(f"I am calculating the final volume: {start_vol} + 15 = {target_vol}. I'll store this in memory.", mem_note)

    sim.do_action(1, f"Setting the volume level to the calculated target of {target_vol}.", {"level": target_vol}, f"System volume successfully set to level {target_vol}.")
    sim.do_action(4, "Selecting audio track number 2 as specified in the original request.", {"id": 2}, "Audio track 2 has been selected and is now active.")
    sim.finish_done("The volume was correctly calculated and set, and the audio track was updated.")
    traces.append({"task": sim.task, "turns": sim.turns})

# 5. 10 traces - "Multi-domain" (Playlist -> Video Settings). Primary: Playlist.
templates_5 = [
    "Skip to the next video in the playlist, then ensure the video resolution is set to {res}.",
    "Move on to the next item in the playlist and change the screen resolution to {res}.",
    "Go to the next video in our current queue, and configure the display resolution to {res}.",
    "Play the next video from the list, but make sure it runs at {res} resolution.",
    "I want to watch the next video in the playlist at {res} resolution. Please set it up.",
    "Trigger the next video in the sequence and force the video resolution to {res}.",
    "Advance the playlist by one video and then adjust the playback resolution to {res}.",
    "Hit next on the playlist, and immediately swap the video quality setting to {res}.",
    "We need to skip this video, go to the next, and set the resolution down to {res}.",
    "Fast forward to the next playlist entry, and update the display mode to {res} resolution."
]
res_opts_5 = ["1080p", "720p", "480p", "1080p", "720p", "480p", "1080p", "720p", "480p", "1080p"]

for i in range(10):
    res = res_opts_5[i]
    task = templates_5[i].format(res=res)
    sim = AgentSim(task)

    sim.do_action(4, "I will navigate to the Playlist domain to skip to the next video first.", None)
    sim.do_action(3, "Executing the next_video command to move to the next item in the user's playlist.", None, "Skipped to the next video in the current playlist.")

    mem_note = f"Successfully skipped to the next playlist video, now I must navigate to configure the {res} resolution."
    sim.mem("I have completed the playlist action and need to remember to change the resolution next.", mem_note)

    sim.back("The playlist task is done. I need to return to the Home menu to access video settings.")
    sim.do_action(5, "Entering the Video Settings menu to configure the requested screen resolution.")
    sim.do_action(1, f"Setting the specific video resolution to {res} to match the user's preference.", {"res": res}, f"Video playback resolution has been changed to {res}.")
    sim.finish_done("The video was skipped and the resolution was correctly configured across two different domains.")
    traces.append({"task": sim.task, "turns": sim.turns})

# 6. 8 traces - "BACK correction" (Video Settings -> BACK -> Playback). Primary: Video Settings.
templates_6 = [
    "I need you to change the playback rate to {rate}x so I can watch this faster.",
    "Please alter the video speed to {rate}x.",
    "Adjust the current playback multiplier to {rate}x.",
    "Set the speed of the video to exactly {rate}x.",
    "Modify the media playback rate so it plays at {rate}x.",
    "Can you bump the playback speed to {rate}x for me?",
    "I would like the video to play at {rate}x speed.",
    "Update the stream to run at a {rate}x playback rate."
]
rates_6 = [1.25, 1.5, 1.75, 2.0, 0.5, 0.75, 1.1, 1.2]

for i in range(8):
    rate = rates_6[i]
    task = templates_6[i].format(rate=rate)
    sim = AgentSim(task)

    sim.do_action(5, "I think playback speed might be in the Video Settings menu, so I'll check there.", None)

    mem_note = "I incorrectly entered the Video Settings menu and must now back out to find Playback Control."
    sim.mem("I navigated to Video Settings but realized playback rate is likely in the Playback Control menu instead.", mem_note)

    sim.back("I realize now that playback rate is not in Video Settings. I need to use BACK to return Home.")
    sim.do_action(1, "Now navigating to the correct Playback Control menu where the rate setting is located.")
    sim.do_action(5, f"Setting the playback rate to {rate}x as originally requested by the user.", {"rate": rate}, f"Playback rate successfully adjusted to {rate}x.")
    sim.finish_done("I successfully corrected my navigation mistake and applied the playback rate setting.")
    traces.append({"task": sim.task, "turns": sim.turns})

# 7. 8 traces - "Short tasks" (Playback Control). Primary: Playback Control.
templates_7 = [
    "Please seek the current video forward to exactly {time}.",
    "I want you to jump the video directly to {time}.",
    "Can you skip ahead to the {time} mark in the video?",
    "Fast forward the media right to {time}.",
    "Seek to {time} so we can skip the boring intro.",
    "I need the video to be at {time} right now.",
    "Please adjust the timeline so it plays from {time}.",
    "Move the playback position to exactly {time}."
]
times_7 = ["01:30", "02:45", "10:00", "00:15", "05:20", "12:00", "08:10", "20:00"]

for i in range(8):
    t = times_7[i]
    task = templates_7[i].format(time=t)
    sim = AgentSim(task)

    sim.do_action(1, "The user wants to seek within the video, which is located in the Playback Control menu.", None)
    sim.do_action(4, f"Executing the seek command to jump directly to the {t} timestamp in the video.", {"time": t}, f"Video successfully skipped to timestamp {t}.")
    sim.finish_done(f"The video has been successfully seeked to {t} and the short task is complete.")
    traces.append({"task": sim.task, "turns": sim.turns})

# Write out the dataset to a random filename as requested
import string
random_filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + ".jsonl"

with open(random_filename, "w", encoding="utf-8") as f:
    for t in traces:
        f.write(json.dumps(t) + "\n")

print(f"Generated {len(traces)} traces. Saved to {random_filename}.")
with open("filename.txt", "w") as f:
    f.write(random_filename)
