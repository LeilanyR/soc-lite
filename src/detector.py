import os
import sqlite3
import yaml


def load_rules(rules_path):
    """Load detection rules from YAML file."""
    # Open the YAML file and read all the rules into a Python list
    with open(rules_path) as f:
        data = yaml.safe_load(f)
    return data["rules"]


def run_detection(db_path, rules_path):
    """Run all rules against the database and return alerts."""
    # Load the rules from YAML
    rules = load_rules(rules_path)

    # Connect to the database where our parsed events live
    conn = sqlite3.connect(db_path)

    # This list will hold any alerts we find
    alerts = []

    # Go through each rule one by one
    for rule in rules:
        # Get the conditions from the rule (e.g., event_name: ListBuckets)
        conditions = rule["conditions"]

        # Build a database query from the rule's conditions
        # Example: if conditions are {event_name: ListBuckets, principal_type: AssumedRole}
        # we build: "WHERE event_name = ? AND principal_type = ?"
        where_parts = []
        values = []
        for field, value in conditions.items():
            where_parts.append(f"{field} = ?")
            values.append(value)

        # Join all conditions with AND
        where_clause = " AND ".join(where_parts)

        # Full query: find all events that match this rule's conditions
        query = f"SELECT timestamp, event_name, user, source_ip FROM events WHERE {where_clause}"

        # Run the query and get all matching events
        matches = conn.execute(query, values).fetchall()

        # If we found matches, this rule triggered — create an alert
        if matches:
            alerts.append({
                "rule": rule["name"],
                "severity": rule["severity"],
                "description": rule["description"],
                "match_count": len(matches),
                "sample_events": matches[:3], # only show first 3 examples
            })

    conn.close()
    return alerts


def print_alerts(alerts):
    """Display alerts in a readable format."""
    # If no rules triggered, say so and exit
    if not alerts:
        print("[*] No alerts triggered.")
        return

    # Print a header
    print(f"\n{'='*60}")
    print(f" SOC-LITE ALERT REPORT - {len(alerts)} rules triggered")
    print(f"{'='*60}\n")

    # Sort alerts by severity (CRITICAL first, LOW last) and print each one
    for alert in sorted(alerts, key=lambda a: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}[a["severity"]]):
        print(f" [{alert['severity']}] {alert['rule']}")
        print(f" {alert['description']}")
        print(f" Matches: {alert['match_count']} events")
        print(f" Sample:")
        # Show up to 3 example events that triggered this rule
        for event in alert["sample_events"]:
            print(f" {event[0]} | {event[1]} | {event[2]} | {event[3]}")
        print()


# This runs when you execute: python src/detector.py
if __name__ == "__main__":
    # Figure out where the project root is
    root = os.path.join(os.path.dirname(__file__), "..")

    # Path to the database (created by main.py)
    db_path = os.path.join(root, "soc_lite.db")

    # Path to our detection rules
    rules_path = os.path.join(root, "src", "rules.yaml")

    # Run all rules against the database
    alerts = run_detection(db_path, rules_path)

    # Save the alerts to a JSON file so we have a record of them
    from alerter import save_alerts
    save_alerts(alerts, os.path.join(root, "output"))

    # Print the results
    print_alerts(alerts)
