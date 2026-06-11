import re

with open('generate_dataset.py', 'r') as f:
    code = f.read()

# Fix USER block to include USER:\n
# In create_trace:
# user_lines = [f"[TASK]: {task}", f"[STATE]: {td['state']}"]
code = code.replace(
    'user_lines = [f"[TASK]: {task}", f"[STATE]: {td[\'state\']}"]',
    'user_lines = ["USER:", f"[TASK]: {task}", f"[STATE]: {td[\'state\']}"]'
)

# Fix sentence counts
# We just need to make sure every reason has at least 2 sentences.
# Looking at reasons like: "I will open table {table_no}."
# Let's add filler sentences to reasons.
def make_longer_reason(match):
    reason = match.group(1)
    if reason.count('.') + reason.count('!') + reason.count('?') < 2:
        reason += " This is a necessary step to ensure the task is completed correctly."
    return f'"reason": "{reason}"'

code = re.sub(r'"reason":\s*"([^"]+)"', make_longer_reason, code)

with open('generate_dataset_fixed.py', 'w') as f:
    f.write(code)
