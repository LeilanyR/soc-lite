import sqlite3

# Connect to the database and see what event names are stored
conn = sqlite3.connect("soc_lite.db")

#Count event per event_name
cursor = conn.execute("SELECT event_name, COUNT(*) FROM events GROUP BY event_name ORDER BY event_name")

for row in cursor:
    print(f"{row[0]}: {row[1]} events")

# Check what principle_type is stored for key events
print("=== AssumeRole events ===")
for row in conn.execute("SELECT timestamp, user, principle_type FROM events WHERE event_name = 'AssumeRole'"):
    print(f" {row}")

print("\n=== ListBuckets events ===")
for row in conn.execute("SELECT timestamp, user, principle_type FROM events WHERE event_name = 'ListBuckets'"):
    print(f" {row}")

print("\n=== GetObject events ===")
for row in conn.execute("SELECT timestamp, user, principle_type FROM events WHERE event_name = 'GetObject'"):
    print(f" {row}")

conn.close()