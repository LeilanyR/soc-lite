import json

# Open the log file and read every event into a list
events = []
with open("data/cloudtrail_exfiltration.json") as f:
    for line in f:
        if line.strip():
            events.append(json.loads(line))

# Get all unique event names (no duplicates) so we know what's in the file
event_names = set(e["eventName"] for e in events)

# Print them alphabetically
for name in sorted(event_names):
    print(name)