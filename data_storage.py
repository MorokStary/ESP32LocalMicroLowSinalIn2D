import sqlite3
import json
import threading
from queue import Queue
from typing import Any, Iterable, Tuple


class DataStorage:
    """Asynchronous SQLite writer with indexed tables."""

    def __init__(self, path: str = "data.db") -> None:
        self.path = path
        self._queue: "Queue[Tuple[str, Tuple[Any, ...]]]" = Queue()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._setup_db()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def _setup_db(self) -> None:
        cur = self._conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                timestamp REAL,
                x REAL,
                y REAL,
                intensity REAL
            )
            """
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_ts ON events(timestamp)"
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS filter_params (
                timestamp REAL,
                params TEXT
            )
            """
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_filter_ts ON filter_params(timestamp)"
        )
        self._conn.commit()

    def _run(self) -> None:
        while True:
            action, args = self._queue.get()
            if action == "STOP":
                break
            if action == "EVENT":
                self._insert_event(*args)
            elif action == "FILTER":
                self._insert_filter(*args)
            self._queue.task_done()

    def _insert_event(self, timestamp: float, x: float, y: float, intensity: float) -> None:
        self._conn.execute(
            "INSERT INTO events VALUES (?, ?, ?, ?)",
            (timestamp, x, y, intensity),
        )
        self._conn.commit()

    def _insert_filter(self, timestamp: float, params_json: str) -> None:
        self._conn.execute(
            "INSERT INTO filter_params VALUES (?, ?)", (timestamp, params_json)
        )
        self._conn.commit()

    def insert_event(self, timestamp: float, x: float, y: float, intensity: float) -> None:
        self._queue.put(("EVENT", (timestamp, x, y, intensity)))

    def insert_filter_params(self, timestamp: float, params: dict) -> None:
        self._queue.put(("FILTER", (timestamp, json.dumps(params))))

    def query_events(self, start: float | None = None, end: float | None = None) -> Iterable[tuple]:
        query = "SELECT timestamp, x, y, intensity FROM events"
        params: list[Any] = []
        if start is not None or end is not None:
            clauses = []
            if start is not None:
                clauses.append("timestamp >= ?")
                params.append(start)
            if end is not None:
                clauses.append("timestamp <= ?")
                params.append(end)
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY timestamp"
        return self._conn.execute(query, params).fetchall()

    def query_filter_params(self, start: float | None = None, end: float | None = None) -> Iterable[tuple]:
        query = "SELECT timestamp, params FROM filter_params"
        params: list[Any] = []
        if start is not None or end is not None:
            clauses = []
            if start is not None:
                clauses.append("timestamp >= ?")
                params.append(start)
            if end is not None:
                clauses.append("timestamp <= ?")
                params.append(end)
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY timestamp"
        return self._conn.execute(query, params).fetchall()

    def close(self) -> None:
        self._queue.put(("STOP", ()))
        self._worker.join()
        self._conn.close()
