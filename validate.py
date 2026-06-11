import json

filename = "bi0c7p4syj.jsonl"
with open(filename, "r") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
assert len(lines) == 60

for idx, line in enumerate(lines):
    try:
        data = json.loads(line)
        assert "task" in data
        assert "turns" in data
        for turn in data["turns"]:
            assert "user" in turn
            assert "assistant" in turn

            # The "assistant" field value is the JSON object serialised as a string
            assist_data = json.loads(turn["assistant"])
            assert "reason" in assist_data
            assert "action" in assist_data

            if "args" in assist_data and "note" in assist_data["args"]:
                note = assist_data["args"]["note"]
                words = len(note.split())
                if not (10 <= words <= 20):
                    print(f"Error at line {idx+1}: Note word count is {words} - '{note}'")
                    assert False

    except Exception as e:
        print(f"Error parsing line {idx+1}: {e}")
        raise

print("Validation passed!")
