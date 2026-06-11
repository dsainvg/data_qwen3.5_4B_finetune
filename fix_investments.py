import json

with open("dataset_unique.jsonl", "r") as f:
    traces = [json.loads(line) for line in f]

# We need 5 traces to strictly start with Investments. Let's modify the first 5 traces of Group 6
# Currently they go: Home -> Reports -> BACK -> Investments.
# If we want Investments as primary, they should go Home -> Investments, and then maybe mistake BACK -> something else, or just be a direct trace.
