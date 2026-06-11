1. **Analyze Requirements**:
   - Ensure the JSONL matches the specified formats and constraints.
   - Use provided menu, domain states, formatting strings, typed args.
   - Exactly 10-20 words for memory notes.
   - Traces 3-8 turns long.
   - Handle exact distribution: 10 web research, 8 email/cal, 8 py code, 8 load/plot data, 10 multi-domain, 8 BACK correction, 8 short tasks.
   - At least 40 MEM uses, at least 20 BACK uses.
   - Each domain is the primary domain at least 5 times.
   - Reason 2-4 sentences.
2. **Execute Generation Script**:
   - Write a python script to iterate through the desired traces and produce `9dc71b37a0.jsonl` (or similar).
   - Validation script passes locally.
3. **Submit the newly created JSONL**:
   - Call `pre_commit_instructions`
   - Run tests if required.
   - Submit.
