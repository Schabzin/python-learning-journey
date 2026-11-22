"""env_flags.py - why text from the environment fools a quick True/False check."""
samples = ["True", "False", "false", "0", "", " true "]

for raw in samples:
    careless = bool(raw)
    careful = raw.strip().lower() in ("1", "true", "yes")
    print(f"{raw!r:10} careless={careless!s:6} careful={careful}")