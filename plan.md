1. Use `run_in_bash_session` to rewrite `generate.py` (using `cat << 'EOF' > generate.py`) with the updated logic and exact category counts.
2. Use `run_in_bash_session` to run `python3 -m py_compile generate.py` to verify the script was updated correctly and contains no syntax errors.
3. Run `python3 generate.py` to generate the `.jsonl` dataset.
4. Use `sed` to update the filename in `validate.py`.
5. Run `python3 validate.py` to test the output.
6. Use `run_in_bash_session` with `rm` to delete the temporary Python scripts.
7. Use `run_in_bash_session` with `ls -la` to verify that the temporary scripts have been successfully removed.
8. Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
9. Submit the change with a descriptive commit message.
