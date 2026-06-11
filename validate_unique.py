import json

with open("dataset_unique.jsonl", "r") as f:
    lines = f.readlines()

assert len(lines) == 60, f"Expected 60 lines, got {len(lines)}"

used_mem_count = 0
used_back_count = 0
domain_counts = {}

def get_primary_domain(turns):
    for t in turns:
        data = json.loads(t["assistant"])
        # Home menu actions 1-7 navigate to domains
        if t["user"].find("[STATE]: Home") != -1 and 1 <= data["action"] <= 7:
            return ["Transactions", "Accounts", "Budgets", "Investments", "Goals", "Reports", "Bills"][data["action"]-1]
    return "Unknown"

for line_num, line in enumerate(lines, 1):
    try:
        data = json.loads(line)
        has_mem = False
        has_back = False

        domain = get_primary_domain(data["turns"])
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

        for turn_num, turn in enumerate(data["turns"], 1):
            user_text = turn["user"]
            for l in user_text.split('\n'):
                if l.startswith("[MEMORY]: "):
                    note = l.replace("[MEMORY]: ", "").strip()
                    words = note.split()
                    assert 10 <= len(words) <= 20, f"Line {line_num}: Memory note must be 10-20 words, got {len(words)}"

            ast_dict = json.loads(turn["assistant"])

            if "args" in ast_dict and "note" in ast_dict["args"]:
                has_mem = True

            if ast_dict["action"] in [4, 9]:
                # 4 is back in submenus except 9 in home, but check text
                if "BACK" in ast_dict.get("reason", "").upper() or ast_dict["action"] == 4 and "Home" not in turn["user"]:
                    has_back = True

        if has_mem: used_mem_count += 1
        if has_back: used_back_count += 1

    except Exception as e:
        print(f"Error on line {line_num}: {e}")
        raise

print(f"All validations passed!")
print(f"Traces using MEM: {used_mem_count} (needs >= 40)")
print(f"Traces using BACK: {used_back_count} (needs >= 20)")
print(f"Domain distribution: {domain_counts} (All need >= 5)")
