import json

with open("dataset_final.jsonl", "r") as f:
    lines = f.readlines()

assert len(lines) == 60, f"Expected 60 lines, got {len(lines)}"

for line_num, line in enumerate(lines, 1):
    try:
        data = json.loads(line)
        for turn_num, turn in enumerate(data["turns"], 1):

            user_text = turn["user"]
            for l in user_text.split('\n'):
                if l.startswith("[MEMORY]: "):
                    note = l.replace("[MEMORY]: ", "").strip()
                    words = note.split()
                    assert 10 <= len(words) <= 20, f"Line {line_num}, Turn {turn_num}: Memory note must be 10-20 words, got {len(words)}: {note}"

            ast_dict = json.loads(turn["assistant"])

            # Action check
            assert isinstance(ast_dict["action"], int)

            # Check MEM action logic: if args has "note", it's MEM
            if "args" in ast_dict and "note" in ast_dict["args"]:
                note_val = ast_dict["args"]["note"]
                words = note_val.split()
                assert 10 <= len(words) <= 20, f"MEM args must be 10-20 words, got {len(words)}"

    except Exception as e:
        print(f"Error on line {line_num}: {e}")
        raise

print("All validations passed!")
