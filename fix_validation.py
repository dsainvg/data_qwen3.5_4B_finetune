import json

def get_primary_domain(turns):
    for t in turns:
        data = json.loads(t["assistant"])
        # Home menu actions 1-7 navigate to domains
        if "[STATE]: Home" in t["user"] and 1 <= data["action"] <= 7:
            return ["Transactions", "Accounts", "Budgets", "Investments", "Goals", "Reports", "Bills"][data["action"]-1]
    return "Unknown"

with open("dataset_unique.jsonl", "r") as f:
    lines = f.readlines()

domain_counts = {}
for line in lines:
    data = json.loads(line)
    domain = get_primary_domain(data["turns"])
    domain_counts[domain] = domain_counts.get(domain, 0) + 1

print(f"Domain distribution: {domain_counts} (All need >= 5)")
