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

    def do_action(self, action_num, reason, args=None, result_str=None, mem_note=None, new_state=None):
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

        # apply action logic for state tracking
        menu_items = home_menu_items if self.state == "Home" else domain_menus[self.state]
        action_text = ""
        for item in menu_items:
            if item.strip().startswith(str(action_num) + "."):
                action_text = item
                break

        self.last_result = None # Clear result unless we executed a tool

        if "MEM" in action_text:
            self.memory_note = args["note"]
            validate_word_count(self.memory_note)
            self.last_result = f"Memory updated: {self.memory_note}"

        elif "BACK" in action_text:
            if self.state_stack:
                self.state = self.state_stack.pop()

        elif "DONE" in action_text:
            pass # We're done

        elif self.state == "Home" and action_num <= 7:
            domains = ["Playback Control", "Volume & Audio", "Subtitles", "Playlist", "Video Settings", "Streaming", "Library"]
            self.state_stack.append(self.state)
            self.state = domains[action_num - 1]

        else:
            # It's a tool!
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

# 1. 10 traces - "Web research then save result" equivalent -> Search library then add to playlist + memory
for i in range(10):
    topic = random.choice(["Inception", "The Matrix", "Interstellar", "Batman", "Avengers", "Nature Documentary", "Comedy Special", "Music Concert", "Tech Talk", "Sci-Fi Series"])
    sim = AgentSim(f"Search our library for {topic} and add it to my playlist. Note that I want to watch this tonight.")
    # Home -> Library
    sim.do_action(7, "I need to search the library for the requested video first.", None)
    # Library -> search_library
    sim.do_action(2, f"I will search the library for '{topic}' to find the right URL.", {"query": topic}, f"1. {topic} Directors Cut - https://lib.local/{topic.lower().replace(' ', '')}\n2. {topic} Behind the Scenes")
    # Store memory
    sim.mem(f"I found the video URL. I will save a memory note about the user wanting to watch {topic} tonight.", f"User requested to watch the {topic} video tonight, adding found URL to playlist now.")
    # Back to home
    sim.back("I have the URL and need to add it to the playlist, which requires the Playlist menu.")
    # Home -> Playlist
    sim.do_action(4, "I will navigate to the Playlist domain to add the video URL I found.")
    # Playlist -> add_to_playlist
    sim.do_action(1, f"I am adding the found URL for {topic} to the playlist so the user can watch it.", {"url": f"https://lib.local/{topic.lower().replace(' ', '')}"}, "Added to playlist successfully.")
    # Done
    sim.finish_done("The video has been located and successfully added to the playlist as requested.")
    traces.append({"task": sim.task, "turns": sim.turns})

# 2. 8 traces - "Email reading and calendar" -> Scan library and configure subtitles
for i in range(8):
    lang = random.choice(["Spanish", "French", "German", "Japanese", "Korean", "Italian", "Portuguese", "Dutch"])
    path = f"/media/hdd{i}/movies"
    sim = AgentSim(f"Scan the folder {path} for new videos, then enable {lang} subtitles with a 500ms delay.")
    sim.do_action(7, "I need to go to the Library menu to scan the requested folder path.")
    sim.do_action(1, f"Scanning the library path {path} for new media files.", {"path": path}, f"Scanned {path}: 3 new videos found and added to index.")

    sim.mem("I should remember that the user wants Spanish subtitles enabled with a delay after the scan.", f"Library scan completed for new videos, moving to configure the requested {lang} subtitles with delay.")

    sim.back("Scan is complete. I need to return to Home to access the Subtitles menu.")
    sim.do_action(3, "Navigating to Subtitles menu to enable the requested language and delay.")
    sim.do_action(1, "Enabling subtitles globally before selecting the specific language track.", None, "Subtitles enabled.")
    sim.do_action(3, f"Setting the subtitle track to {lang}.", {"lang": lang}, f"Subtitle track set to {lang}.")
    sim.do_action(4, "Adjusting the subtitle delay to 500ms as requested.", {"ms": 500}, "Subtitle delay set to 500ms.")
    sim.finish_done("The folder has been scanned and the subtitle settings are fully configured.")
    traces.append({"task": sim.task, "turns": sim.turns})

# 3. 8 traces - "Python code, handle error" -> Streaming connect error, retry
for i in range(8):
    device = random.choice(["Living Room TV", "Bedroom Apple TV", "Kitchen Hub", "Office Monitor"])
    sim = AgentSim(f"Connect to the {device} for streaming and get the current stream info.")
    sim.do_action(6, "I will go to the Streaming domain to connect to the requested cast device.")
    sim.do_action(1, f"Attempting to connect to the {device}.", {"device": device}, f"Error: {device} not found on network.")
    sim.mem("The device connection failed. I need to store this information and try checking the exact device name.", f"First connection attempt to the {device} failed due to network error, will try connecting again.")
    sim.do_action(1, "Retrying the connection to the device, maybe the network just dropped momentarily.", {"device": device}, f"Connected to {device} successfully.")
    sim.do_action(3, "Fetching the stream info now that the connection is established.", None, "Stream info: 1080p, 60fps, 5Mbps bitrate.")
    sim.finish_done("Successfully connected to the cast device and retrieved the stream information.")
    traces.append({"task": sim.task, "turns": sim.turns})

# 4. 8 traces - "Load data, compute" -> Volume and Video Settings
for i in range(8):
    vol = random.randint(20, 80)
    res = random.choice(["1080p", "720p", "480p"])
    sim = AgentSim(f"Set the volume to {vol} and change the video resolution to {res}.")
    sim.do_action(2, "I need to access the Volume & Audio menu first to set the volume.")
    sim.do_action(1, f"Setting the volume level to {vol}.", {"level": vol}, f"Volume set to {vol}.")
    sim.back("Volume is set. Returning to Home to access Video Settings.")
    sim.do_action(5, "Navigating to Video Settings to change the resolution.")
    sim.do_action(1, f"Setting the video resolution to {res}.", {"res": res}, f"Resolution changed to {res}.")
    sim.mem("Both volume and resolution have been configured.", f"Successfully changed the volume level to {vol} and the video resolution to {res} as requested.")
    sim.finish_done("The requested volume and resolution settings have been applied.")
    traces.append({"task": sim.task, "turns": sim.turns})

# 5. 10 traces - Multi-domain
for i in range(10):
    action1 = random.choice(["play", "pause"])
    vol = random.randint(10, 50)
    sim = AgentSim(f"Please {action1} the video and turn the volume down to {vol}.")
    sim.do_action(1, "I will first go to Playback Control to change the playback state.", None)

    if action1 == "play":
        sim.do_action(1, "Starting video playback.", None, "Playback started.")
    else:
        sim.do_action(2, "Pausing the video.", None, "Playback paused.")

    sim.back("Playback state changed. I need to go back to Home to adjust the volume.")
    sim.do_action(2, "Entering Volume & Audio menu to adjust the sound.")
    sim.do_action(1, f"Setting volume to {vol}.", {"level": vol}, f"Volume set to {vol}.")
    sim.mem("Playback and volume tasks are completed.", f"I have successfully executed the {action1} command and adjusted the system volume to {vol}.")
    sim.finish_done("Task complete: playback state altered and volume adjusted.")
    traces.append({"task": sim.task, "turns": sim.turns})

# 6. 8 traces - BACK correction
for i in range(8):
    sim = AgentSim(f"Check the current stream information. {uuid.uuid4().hex[:6]}")
    sim.do_action(5, "I will check the stream info. I think that might be in Video Settings.", None)
    sim.do_action(5, "Wait, stream info is not in Video Settings. I need to go BACK to Home and find the Streaming menu.")
    sim.do_action(6, "Navigating to the Streaming domain where the stream info tool is located.")
    sim.do_action(3, "Getting the current stream info.", None, "Stream info: 4K HDR, 25Mbps, connected via Ethernet.")
    sim.finish_done("Successfully retrieved the streaming information.")
    traces.append({"task": sim.task, "turns": sim.turns})

# 7. 8 traces - Short tasks
for i in range(8):
    sim = AgentSim(f"Just stop the playback. {uuid.uuid4().hex[:6]}")
    sim.do_action(1, "The user wants to stop playback, so I will navigate to Playback Control.", None)
    sim.do_action(3, "Executing the stop command.", None, "Playback stopped completely.")
    sim.finish_done("Playback has been stopped as requested.")
    traces.append({"task": sim.task, "turns": sim.turns})


with open("dataset.jsonl", "w") as f:
    for t in traces:
        f.write(json.dumps(t) + "\n")

print(f"Generated {len(traces)} traces.")
