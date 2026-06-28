import sqlite3

def init_db(db_path="soc-lite.db"):
    """create the events table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_name TEXT,
            event_source TEXT,
            source_ip TEXT,
            user TEXT,
            principle_type TEXT,
            region TEXT,
            user_agent TEXT,
            request_params TEXT,
            resources TEXT,
            raw_log TEXT
        )
    """)
    conn.commit()
    return conn

def insert_events(conn, events):
    """insert parsed events into the database."""
    conn.executemany("""
        INSERT INTO events (timestamp, event_name, event_source, source_ip, 
                     user, principle_type, region, user_agent, request_params, resources, raw_log)
        VALUES (:timestamp, :event_name, :event_source, :source_ip,
                :user, :principle_type, :region, :user_agent, :request_params, :resources, :raw_log)
    """, events)
    conn.commit()