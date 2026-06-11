import json

STATES = {
    "Home": """  1. Library & Search — search songs, browse artists, view albums
  2. Playback & Queue — play, pause, skip, manage queue
  3. Playlists & Favorites — create, edit, like tracks
  4. Audio & Equalizer — adjust EQ, volume, spatial audio
  5. Devices & Casting — connect bluetooth, cast to speakers
  6. Podcasts & Radio — browse podcasts, start artist radio
  7. Memory & Notes — store and recall listener preferences
  8. MEM [note: `string`] — store a memory note (10–20 words exactly)
  9. BACK — go to previous state
  10. DONE — task is complete""",

    "Library & Search": """  1. search_library [query: `string`]
  2. get_artist_info [artist: `string`]
  3. view_album [album: `string`]
  4. get_lyrics
  5. MEM [note: `string`]
  6. BACK
  7. DONE""",

    "Playback & Queue": """  1. play_track [track_id: `string`]
  2. pause_playback
  3. skip_track
  4. add_to_queue [track_id: `string`]
  5. view_queue
  6. MEM [note: `string`]
  7. BACK
  8. DONE""",

    "Playlists & Favorites": """  1. create_playlist [name: `string`]
  2. add_to_playlist [track_id: `string`, playlist_name: `string`]
  3. like_track [track_id: `string`]
  4. list_playlists
  5. MEM [note: `string`]
  6. BACK
  7. DONE""",

    "Audio & Equalizer": """  1. set_volume [level: `int`]
  2. set_eq_preset [preset: `enum(bass_boost,acoustic,electronic,vocal,flat)`]
  3. toggle_spatial_audio [enable: `bool`]
  4. MEM [note: `string`]
  5. BACK
  6. DONE""",

    "Devices & Casting": """  1. scan_devices
  2. connect_device [device_id: `string`]
  3. disconnect_device
  4. MEM [note: `string`]
  5. BACK
  6. DONE""",

    "Podcasts & Radio": """  1. search_podcasts [query: `string`]
  2. play_episode [episode_id: `string`]
  3. start_artist_radio [artist: `string`]
  4. MEM [note: `string`]
  5. BACK
  6. DONE""",

    "Memory & Notes": """  1. save_preference [content: `multiline_string`]
  2. read_preferences
  3. delete_preference [id: `int`]
  4. MEM [note: `string`]
  5. BACK
  6. DONE"""
}

def get_action_num(state, text):
    menu = STATES[state]
    for line in menu.split('\n'):
        parts = line.split('.', 1)
        if len(parts) > 1:
            action_part = parts[1].strip()
            core_token = action_part.split(' ')[0]
            if text in ["Library & Search", "Playback & Queue", "Playlists & Favorites",
                        "Audio & Equalizer", "Devices & Casting", "Podcasts & Radio", "Memory & Notes"]:
                if action_part.startswith(text):
                    return int(parts[0].strip())
            elif core_token == text:
                return int(parts[0].strip())
            elif text == "MEM" and action_part.startswith("MEM"):
                return int(parts[0].strip())
            elif text == "BACK" and action_part.startswith("BACK"):
                return int(parts[0].strip())
            elif text == "DONE" and action_part.startswith("DONE"):
                return int(parts[0].strip())
    raise ValueError(f"Action '{text}' not found in state '{state}'")

class TraceBuilder:
    def __init__(self, task):
        self.task = task
        self.turns = []
        self.state_stack = ["Home"]
        self.memory = None
        self.result = None

    @property
    def current_state(self):
        return self.state_stack[-1]

    def step(self, reason, text_action, args=None, result_text=None, new_state=None, memory_note=None):
        user_str = f"[TASK]: {self.task}\n[STATE]: {self.current_state}"
        if self.memory:
            user_str += f"\n[MEMORY]: {self.memory}"
        if self.result:
            user_str += f"\n[RESULT]: {self.result}"

        user_str += "\n[MENU]:\n" + STATES[self.current_state]

        action_num = get_action_num(self.current_state, text_action)

        ast_dict = {"reason": reason, "action": action_num}
        if args is not None:
            ast_dict["args"] = args

        self.turns.append({
            "user": user_str,
            "assistant": json.dumps(ast_dict)
        })

        if text_action == "MEM":
            self.memory = memory_note
            self.result = None
        elif new_state:
            self.state_stack.append(new_state)
            self.result = None
        elif text_action == "BACK":
            self.state_stack.pop()
            self.result = None
        elif text_action == "DONE":
            self.result = None
        else:
            self.result = result_text

    def nav(self, reason, domain_text, new_state):
        self.step(reason, domain_text, new_state=new_state)

    def tool(self, reason, tool_text, args=None, result_text=None):
        self.step(reason, tool_text, args=args, result_text=result_text)

    def mem(self, reason, note):
        words = note.split()
        assert 10 <= len(words) <= 20, f"MEM note '{note}' has {len(words)} words. Must be 10-20. Text: {note}"
        self.step(reason, "MEM", args={"note": note}, memory_note=note)

    def back(self, reason):
        self.step(reason, "BACK")

    def done(self, reason):
        self.step(reason, "DONE")

    def to_dict(self):
        return {
            "task": self.task,
            "turns": self.turns
        }

traces = []

# Category 1: 10 traces — Search for a song/artist and queue or play it
for i in range(1, 11):
    tb = TraceBuilder(f"Find the song 'Track {i}' by Artist {i} and play it immediately.")
    tb.nav(f"The user wants me to find a specific song, 'Track {i}'. To do this, I must first locate the correct search tools. I will navigate to the Library & Search domain to use the search_library tool.", "Library & Search", "Library & Search")
    tb.tool(f"Now that I am in the Library & Search domain, I can execute a search. I will look for 'Track {i}' by Artist {i} to find the exact track ID.", "search_library", {"query": f"Track {i} Artist {i}"}, f"1. 'Track {i}' - Artist {i} (ID: trk_1{i:02d})\n2. 'Track {i} Remix' - Artist {i} (ID: trk_2{i:02d})")
    tb.mem(f"The search returned multiple results, including a remix. The user specifically asked to play the original track. I should store this detail in memory for future reference.", f"User requested the immediate playback of the original track {i} version.")
    tb.back("I have obtained the correct track ID (trk_1{0:02d}) from the search results. I must return to the Home menu so I can access the Playback domain.".format(i))
    tb.nav("From the Home menu, I need to enter the Playback & Queue domain. This will allow me to initiate playback for the track I just found.", "Playback & Queue", "Playback & Queue")
    tb.tool("I am in the correct domain to control audio. I will use the play_track tool with the ID I found earlier.", "play_track", {"track_id": f"trk_1{i:02d}"}, f"Now playing: 'Track {i}' by Artist {i}.")
    tb.done("The song is now actively playing as requested by the user. There are no further actions required to fulfill this task.")
    traces.append(tb.to_dict())

# Category 2: 8 traces — Create playlists and manage favorites
for i in range(1, 9):
    tb = TraceBuilder(f"Create a new playlist called 'Vibes {i}' and add track trk_vibe{i} to it.")
    tb.nav("The user is asking to create and manage a playlist. These capabilities are found in the Playlists & Favorites domain, so I will navigate there first.", "Playlists & Favorites", "Playlists & Favorites")
    tb.tool(f"I need to establish the playlist before I can add anything to it. I will create a new playlist named 'Vibes {i}'.", "create_playlist", {"name": f"Vibes {i}"}, f"Playlist 'Vibes {i}' created successfully.")
    if i % 2 == 0:
        tb.mem("The user has been making several of these mood-based playlists. I will make a quick note that they enjoy creating custom vibe playlists.", "The user has a strong preference for creating custom vibe playlists frequently.")
    tb.tool(f"The playlist now exists in the system. I will proceed to add the specified track trk_vibe{i} to it.", "add_to_playlist", {"track_id": f"trk_vibe{i}", "playlist_name": f"Vibes {i}"}, f"Added track trk_vibe{i} to playlist 'Vibes {i}'.")
    tb.done("The new playlist was created and the track has been successfully added to it. The objective is fully achieved.")
    traces.append(tb.to_dict())

# Category 3: 8 traces — Device connection and audio/EQ adjustments
eqs = ["bass_boost", "acoustic", "electronic", "vocal", "flat"]
for i in range(1, 9):
    eq = eqs[i % 5]
    tb = TraceBuilder(f"Set the EQ to {eq} and connect to device dev_{i}.")

    if i <= 5: # Audio primary
        tb.nav("The user wants to configure the audio settings first. I will navigate to the Audio & Equalizer domain to access the equalizer options.", "Audio & Equalizer", "Audio & Equalizer")
        tb.tool(f"Now I am in the audio settings. I will apply the {eq} EQ preset to modify the sound profile.", "set_eq_preset", {"preset": eq}, f"Equalizer preset applied successfully: {eq}.")
        tb.back("The EQ has been successfully configured. I now need to connect a device, so I must go back to the Home menu first.") # using "BACK" tool string isn't required by function but reason is good
        tb.nav("I am back at the Home menu. I will now enter the Devices & Casting domain to handle the hardware connection.", "Devices & Casting", "Devices & Casting")
        tb.tool("I have the device ID provided in the prompt. I will use the connect_device tool to establish a link.", "connect_device", {"device_id": f"dev_{i}"}, f"Successfully connected to device dev_{i}.")
        tb.mem("Both the device and the specific audio profile have been set up. I will record these preferences for future reference.", f"The user requires device connection and a specific audio equalizer preset applied.")
    else: # Devices primary
        tb.nav("The task involves connecting to external hardware. I must first enter the Devices & Casting domain to manage connections.", "Devices & Casting", "Devices & Casting")
        tb.tool("I will initiate the connection sequence to link the system with the specified external speaker.", "connect_device", {"device_id": f"dev_{i}"}, f"Successfully connected to device dev_{i}.")
        tb.back("The device is now connected and active. I need to adjust the sound signature next, which means returning to the Home menu.")
        tb.nav("From the Home menu, I will navigate into the Audio & Equalizer domain to access the EQ presets.", "Audio & Equalizer", "Audio & Equalizer")
        tb.tool(f"I will apply the requested {eq} equalizer preset to ensure the audio sounds correct.", "set_eq_preset", {"preset": eq}, f"Equalizer preset applied successfully: {eq}.")
        tb.mem("The user has explicit requirements for both their speaker hardware and sound profile. I should note this down.", f"The user requires device connection and a specific audio equalizer preset applied.")

    tb.done("The specified device has been successfully connected and the EQ preset is applied. The multi-part task is completely finished.")
    traces.append(tb.to_dict())

# Category 4: 8 traces — Podcast searches and episode playback
for i in range(1, 9):
    tb = TraceBuilder(f"Find the podcast 'Tech Talk {i}' and play episode ep_tech{i}.")
    tb.nav("The user is requesting a podcast episode rather than a music track. I need to enter the Podcasts & Radio domain to perform this search.", "Podcasts & Radio", "Podcasts & Radio")
    if i % 2 != 0:
        tb.mem("This user seems very interested in technology-related content. I should record this genre preference to personalize future recommendations.", "The user frequently searches for and listens to technology related podcast episodes.")
    tb.tool("I am in the correct domain. I will search for the podcast by name to see available episodes.", "search_podcasts", {"query": f"Tech Talk {i}"}, f"1. Tech Talk {i} (Episodes: ep_tech{i}, ep_other)")
    tb.tool("The search results confirm the episode exists. I will now start playback for the specific episode ID requested.", "play_episode", {"episode_id": f"ep_tech{i}"}, f"Now playing podcast episode: ep_tech{i}.")
    tb.done("The designated podcast episode has started playing correctly. The user's request has been fulfilled.")
    traces.append(tb.to_dict())

# Category 5: 10 traces — Multi-domain
# 5 traces starting with Memory & Notes
for i in range(1, 6):
    tb = TraceBuilder(f"Check my saved preferences for EQ {i} and apply the preferred EQ preset.")
    tb.nav("The user wants me to recall a previously saved preference. I must first navigate to the Memory & Notes domain to read the stored data.", "Memory & Notes", "Memory & Notes")
    tb.tool("I am in the memory domain. I will read the user's stored preferences to identify their preferred EQ setting.", "read_preferences", None, f"1. Prefers acoustic EQ for jazz.\n2. User likes setting EQ {i} to acoustic.")
    tb.back("I have retrieved the preference, which indicates the user wants an acoustic EQ. I must return to Home to access the audio settings.")
    tb.nav("Now I need to change the audio output. I will navigate to the Audio & Equalizer domain to make the adjustment.", "Audio & Equalizer", "Audio & Equalizer")
    tb.tool("I will use the tool to set the EQ preset to acoustic, matching the preference I just read.", "set_eq_preset", {"preset": "acoustic"}, "Equalizer preset applied successfully: acoustic.")
    tb.mem(f"I should note that I successfully retrieved and applied the acoustic EQ for request {i}. This confirms the system is working as intended.", f"The user requested checking preferences and applying the acoustic equalizer setting accordingly.")
    tb.done("The stored preference was successfully read and the corresponding equalizer setting has been applied.")
    traces.append(tb.to_dict())

# 5 traces starting with Devices & Casting
for i in range(6, 11):
    tb = TraceBuilder(f"Connect my speaker dev_spk{i} and start an artist radio for 'Artist {i}'.")
    tb.nav("The first step is to establish a connection with the user's speaker. I will navigate to Devices & Casting to handle this.", "Devices & Casting", "Devices & Casting")
    tb.tool("I am in the devices menu. I will connect to the requested speaker using the provided device ID.", "connect_device", {"device_id": f"dev_spk{i}"}, f"Successfully connected to device dev_spk{i}.")
    tb.back("The speaker connection is active and stable. I must now return to the Home menu to find the radio features.")
    tb.nav("To start a radio station, I need to be in the Podcasts & Radio domain. I will navigate there now.", "Podcasts & Radio", "Podcasts & Radio")
    tb.tool("I will initiate the artist radio station based on the specific artist requested by the user.", "start_artist_radio", {"artist": f"Artist {i}"}, f"Started artist radio for Artist {i}.")
    tb.mem(f"The user likes to listen to Artist {i} radio on their external speaker. I will store this combination as a preference.", f"User likes connecting their device to listen to the specific artist radio.")
    tb.done("Both the hardware connection and the audio playback have been initiated successfully. The task is complete.")
    traces.append(tb.to_dict())

# Category 6: 8 traces — BACK correction
for i in range(1, 9):
    tb = TraceBuilder(f"Search for the album 'Nostalgia {i}' and view its tracks.")
    tb.nav("I need to find a specific album. I will mistakenly go to the Playlists & Favorites domain thinking albums are stored there.", "Playlists & Favorites", "Playlists & Favorites")
    tb.back("Wait, this is the wrong domain. Albums are not searched here. I need to use the BACK option to return to Home.")
    tb.nav("Now I will correctly navigate to the Library & Search domain, where the album lookup tools are located.", "Library & Search", "Library & Search")
    tb.tool("I am in the correct menu now. I will use the view_album tool to retrieve the tracklist for the requested album.", "view_album", {"album": f"Nostalgia {i}"}, f"Album 'Nostalgia {i}' tracks:\n1. Intro\n2. Main Theme")
    tb.mem("This user enjoys listening to albums with a nostalgic theme. This is a very useful preference to keep track of.", "User frequently searches for and views albums that have a nostalgic theme.")
    tb.done("The album tracks have been successfully retrieved and presented to the user. The correction was handled and the task is done.")
    traces.append(tb.to_dict())

# Category 7: 8 traces — Short tasks (2-3 turns)
for i in range(1, 9):
    tb = TraceBuilder(f"Pause the music right now, quick action {i}.")
    tb.nav("The user wants to immediately pause the current audio playback. This control is located in the Playback & Queue menu.", "Playback & Queue", "Playback & Queue")
    tb.tool("I am in the playback domain. I will execute the pause command to stop the audio output right now.", "pause_playback", None, "Playback paused.")
    tb.done("The music has been successfully paused without any delay. This short task is completely finished.")
    traces.append(tb.to_dict())

# Check total count
print(f"Generated {len(traces)} traces.")

with open("music_agent_traces_x7k9p2.jsonl", "w") as f:
    for t in traces:
        f.write(json.dumps(t) + "\n")
