import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from log_parser import parse_database
from database import init_db, insert_events


def main():
    root = os.path.join(os.path.dirname(__file__), "..")
    log_file = os.path.join(root, "data", "cloudtrail_exfiltration.json")

    print("[*] Parsing CloudTrail logs...")
    events = parse_database(log_file)
    print(f"[+] Parsed {len(events)} events")

    print("[*] Storing in database...")
    db_path = os.path.join(root, "soc_lite.db")
    conn = init_db(db_path)
    insert_events(conn, events)
    print("[+] Done! Events stored in soc_lite.db")

    print("\n[*] Sample events:")
    cursor = conn.execute(
        "SELECT timestamp, event_name, user, source_ip FROM events LIMIT 5"
    )
    for row in cursor:
        print(f" {row[0]} | {row[1]} | {row[2]} | {row[3]}")

    conn.close()


if __name__ == "__main__":
    main()
