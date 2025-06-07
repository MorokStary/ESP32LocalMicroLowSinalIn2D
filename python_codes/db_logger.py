import sqlite3
from datetime import datetime

DB_PATH = 'logs.db'

# Initialize DB
conn = sqlite3.connect(DB_PATH)
conn.execute(
    '''CREATE TABLE IF NOT EXISTS events(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    amplitude REAL,
    x REAL,
    y REAL,
    z REAL
)'''
)
conn.commit()


def log_event(amplitude, x, y, z, db_path=DB_PATH):
    """Store an event in the SQLite database and return the timestamp."""
    ts = datetime.utcnow().isoformat()
    with sqlite3.connect(db_path) as c:
        c.execute(
            'INSERT INTO events(timestamp, amplitude, x, y, z) VALUES (?,?,?,?,?)',
            (ts, amplitude, x, y, z),
        )
        c.commit()
    return ts


