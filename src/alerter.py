import json
import os
from datetime import datetime

def save_alerts(alerts, output_dir="output"):
    """Save alerts to a JSON file so they're persisted, not just printed."""

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Build the output filename with current date/time so each run is unique
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"alerts_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    # Format alerts for saving — convert tuples to readable dicts
    formatted_alerts = []
    for alert in alerts:
        formatted_alerts.append({
            "rule": alert["rule"],
            "severity": alert["severity"],
            "description": alert["description"],
            "match_count": alert["match_count"],
            # Convert each sample event tuple into a labeled dictionary
            "sample_events": [
            {
                "timestamp": event[0],
                "event_name": event[1],
                "user": event[2],
                "source_ip": event[3],
            }
            for event in alert["sample_events"]
        ],
    })

    # Write the alerts to a JSON file (indent=2 makes it human-readable)
    with open(filepath, "w") as f:
        json.dump(formatted_alerts, f, indent=2)

    print(f"[+] Alerts saved to {filepath}")
    return filepath