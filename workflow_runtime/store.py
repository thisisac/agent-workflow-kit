"""One SQLite authority: snapshot and event commit in the same transaction."""
from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3
import time


def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


class Store:
    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / "workflow.sqlite3"
        with self.transaction() as db:
            db.execute("CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY, data TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, at REAL, kind TEXT, data TEXT)")

    @contextmanager
    def transaction(self):
        db = sqlite3.connect(self.path, timeout=5)
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def load(db):
        row = db.execute("SELECT data FROM state WHERE id=1").fetchone()
        return json.loads(row[0]) if row else None

    @staticmethod
    def save(db, state, kind, event):
        state["revision"] += 1
        db.execute("INSERT OR REPLACE INTO state VALUES (1, ?)", (encode(state),))
        db.execute("INSERT INTO events(at, kind, data) VALUES (?, ?, ?)",
                   (time.time(), kind, encode(event)))

    def read(self):
        with self.transaction() as db:
            return self.load(db)

    def events(self):
        with self.transaction() as db:
            return [{"id": row[0], "kind": row[1], "data": json.loads(row[2])}
                    for row in db.execute("SELECT id, kind, data FROM events ORDER BY id")]
