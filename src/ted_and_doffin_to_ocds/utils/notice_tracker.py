# converters/notice_tracker.py

import sqlite3
import logging
from datetime import datetime, UTC
from collections.abc import Generator
from pathlib import Path
from contextlib import contextmanager, suppress
import threading
from typing import Final

logger = logging.getLogger(__name__)


class NoticeTracker:
    """Thread-safe SQLite connection manager for notice tracking."""

    MAX_WORKERS: Final[int] = 4

    def __init__(self, db_path: str = "notices.db"):
        """Initialize the notice tracker."""
        self.db_path = db_path
        self._local = threading.local()

        # Initialize database and verify schema
        self._init_db()
        self.verify_schema()  # Changed to public method

    def _init_db(self) -> None:
        """Initialize the database if it doesn't exist."""
        try:
            if not Path(self.db_path).exists():
                self.init_db()
            else:
                # Verify we can connect to the database
                with self._init_db_connection() as conn:
                    conn.execute("SELECT 1")
            logger.info("Database initialized successfully at %s", self.db_path)
        except Exception:
            logger.exception("Failed to initialize database")
            raise

    def _init_db_connection(self) -> sqlite3.Connection:
        """Initialize a new database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @property
    def connection(self) -> sqlite3.Connection:
        """Get thread-local connection."""
        if not hasattr(self._local, "connection"):
            self._local.connection = self._init_db_connection()
        return self._local.connection

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection]:
        """Get a connection from thread-local storage with automatic commit/rollback."""
        conn = self.connection
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def __del__(self):
        """Clean up connections on deletion."""
        if hasattr(self._local, "connection"):
            with suppress(Exception):
                self._local.connection.close()
                logger.debug("Closed database connection")

    # Changed from _verify_schema to public verify_schema
    def verify_schema(self) -> None:
        """Verify that all required tables exist."""
        try:
            expected_tables = {"notices", "related_processes", "parts"}
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name IN (?, ?, ?)
                    """,
                    tuple(expected_tables),
                )
                existing_tables = {row[0] for row in cursor.fetchall()}

                if existing_tables != expected_tables:
                    logger.warning("Missing tables, recreating schema")
                    self.init_db()
                else:
                    logger.info("Database schema verified successfully")
        except Exception:
            logger.exception("Schema verification failed")
            raise

    def init_db(self):
        """Create the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create tables if they don't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notices (
                    notice_id TEXT PRIMARY KEY,
                    ocid TEXT NOT NULL,
                    notice_type TEXT NOT NULL,
                    is_pin_only BOOLEAN NOT NULL,
                    publication_date TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS related_processes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_notice_id TEXT NOT NULL,
                    target_notice_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    scheme TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (source_notice_id) REFERENCES notices (notice_id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (target_notice_id) REFERENCES notices (notice_id)
                        ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    notice_id TEXT NOT NULL,
                    part_id TEXT NOT NULL,
                    ocid TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (notice_id) REFERENCES notices (notice_id)
                        ON DELETE CASCADE
                )
            """)

            # Create indices if they don't exist
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notices_ocid
                ON notices(ocid)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notices_publication_date
                ON notices(publication_date)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_parts_notice_id
                ON parts(notice_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_related_source
                ON related_processes(source_notice_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_related_target
                ON related_processes(target_notice_id)
            """)

            conn.commit()

    def get_current_time(self) -> str:
        """Get current UTC time in ISO format."""
        return datetime.now(UTC).isoformat()

    def track_notice(
        self,
        notice_id: str,
        ocid: str,
        notice_type: str,
        is_pin_only: bool,
        publication_date: str,
    ) -> None:
        """
        Track a new notice in the database.
        Args:
            notice_id: Unique identifier for the notice
            ocid: Open Contracting ID (required)
            notice_type: Type of notice
            is_pin_only: Whether this is a PIN-only notice
            publication_date: Date the notice was published
        """
        if not ocid:
            raise ValueError(self.OCID_REQUIRED_MESSAGE)

        current_time = self.get_current_time()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO notices (
                        notice_id, ocid, notice_type, is_pin_only,
                        publication_date, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(notice_id) DO UPDATE SET
                        ocid = excluded.ocid,
                        notice_type = excluded.notice_type,
                        is_pin_only = excluded.is_pin_only,
                        publication_date = excluded.publication_date,
                        updated_at = excluded.updated_at
                """,
                    (
                        notice_id,
                        ocid,
                        notice_type,
                        is_pin_only,
                        publication_date,
                        current_time,
                        current_time,
                    ),
                )
                conn.commit()
                logger.info(
                    "Successfully tracked notice: %s with OCID: %s", notice_id, ocid
                )
            except Exception:
                logging.exception("Error tracking notice %s", notice_id)
                raise

    def track_part(self, notice_id: str, part_id: str, ocid: str) -> None:
        """Track a part from a PIN-only notice."""
        current_time = self.get_current_time()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO parts (notice_id, part_id, ocid, created_at)
                VALUES (?, ?, ?, ?)
            """,
                (notice_id, part_id, ocid, current_time),
            )
            conn.commit()

    def track_related_process(
        self,
        source_notice_id: str,
        target_notice_id: str,
        relationship_type: str,
        scheme: str,
    ) -> None:
        """Track a relationship between notices."""
        current_time = self.get_current_time()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO related_processes (
                    source_notice_id, target_notice_id,
                    relationship_type, scheme, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """,
                (
                    source_notice_id,
                    target_notice_id,
                    relationship_type,
                    scheme,
                    current_time,
                ),
            )
            conn.commit()

    def get_previous_notice(self, notice_id: str) -> tuple | None:
        """
        Get the notice details for a specific notice ID with improved error handling.

        Args:
            notice_id: ID of the notice to retrieve

        Returns:
            Optional[tuple]: (notice_id, ocid, notice_type, is_pin_only, publication_date)
            or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    SELECT notice_id, ocid, notice_type, is_pin_only, publication_date
                    FROM notices
                    WHERE notice_id = ?
                """,
                    (notice_id,),
                )

                result = cursor.fetchone()
                if result:
                    logger.info(
                        "Found previous notice: %s with OCID: %s", notice_id, result[1]
                    )
                    return result

            except Exception:
                logger.exception("Error retrieving previous notice %s", notice_id)
            else:
                logger.warning("Previous notice not found: %s", notice_id)

            return None

    @contextmanager
    def get_statistics(self) -> Generator[dict]:
        """
        Get statistics about the tracked notices and relationships.

        Returns:
            dict: Statistics including counts of notices, parts, and relationships
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get notice count
            cursor.execute("SELECT COUNT(*) FROM notices")
            notice_count = cursor.fetchone()[0]

            # Get parts count
            cursor.execute("SELECT COUNT(*) FROM parts")
            parts_count = cursor.fetchone()[0]

            # Get relationships count
            cursor.execute("SELECT COUNT(*) FROM related_processes")
            relationship_count = cursor.fetchone()[0]

            stats = {
                "notice_count": notice_count,
                "parts_count": parts_count,
                "relationship_count": relationship_count,
            }

            yield stats

    def get_notice_parts(self, notice_id: str) -> list[tuple]:
        """Get all parts associated with a notice."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT part_id, ocid
                FROM parts
                WHERE notice_id = ?
                ORDER BY created_at
            """,
                (notice_id,),
            )
            return cursor.fetchall()

    def get_related_processes(self, notice_id: str) -> list[tuple]:
        """Get all related processes for a notice."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT target_notice_id, relationship_type, scheme
                FROM related_processes
                WHERE source_notice_id = ?
                ORDER BY created_at
            """,
                (notice_id,),
            )
            return cursor.fetchall()
