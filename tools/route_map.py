"""route_map.py - which function answers each URL? Proof before deleting code."""
from collections import Counter
from taxi_app import app


rules = sorted(app.url_map.iter_rules(), key=lambda r: r.rule)
seen = Counter()
for rule in rules:
    for method in rule.methods - {"HEAD", "OPTIONS"}:
        seen[(rule.rule, method)] += 1

router = app.url_map.bind("localhost")
print("URLs registered more than once:")
for (path, method), count in sorted(seen.items()):
    if count > 1:
        endpoints = [r.endpoint for r in rules if r.rule == path and method in r.methods]
        winner, _ = router.match(path, method=method)
        print(f"   {method} {path}: {count}x {endpoints} -> answers: {winner}")