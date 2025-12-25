# habit/database.py
import sqlite3
from datetime import datetime, date
import os

HERE = os.path.dirname(__file__)
DEFAULT_DB = os.path.join(HERE, "habits.db")
#used to fix the python 3.12+ sqlite depracation warnings by telling it to save dates in ISOformat
def adapt_date(d):
    return d.isoformat()

def adapt_datetime(dt):
    return dt.isoformat()
#these registers adapters so that SQLite knows how to save dates as strings
sqlite3.register_adapter(date, adapt_date)
sqlite3.register_adapter(datetime, adapt_datetime)

#tells Python how to read the dates back into Python
def convert_date(val):
    return date.fromisoformat(val.decode("utf-8"))

def convert_timestamp(val):
    return datetime.fromisoformat(val.decode("utf-8"))

# Register these converters for the specific SQL types
sqlite3.register_converter("DATE", convert_date)
sqlite3.register_converter("TIMESTAMP", convert_timestamp)

def get_connection(db_path: str = None):
    """Return a sqlite3.Connection configured for our app."""
    path = db_path or DEFAULT_DB
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(conn):
    """Initialize tables if they don't exist."""
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            frequency TEXT NOT NULL CHECK(frequency IN ('Daily','Weekly','Monthly')),
            last_checked DATE,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS habit_completion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            date DATE NOT NULL,
            FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
    """)
    conn.commit()

def ensure_db(db_path: str = None):
    """Create DB file and tables if needed; return connection."""
    conn = get_connection(db_path)
    init_db(conn)
    return conn
