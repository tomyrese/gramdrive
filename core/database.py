import os
import sqlite3
import shutil
from typing import Dict, Any, List, Optional

class Database:
    def __init__(self, db_path: str = "database/telegram_drive.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    type TEXT,
                    upload_date TEXT,
                    telegram_message_id TEXT,
                    telegram_file_id TEXT,
                    chunk_index INTEGER DEFAULT 0,
                    total_chunks INTEGER DEFAULT 1,
                    encrypted INTEGER DEFAULT 0,
                    hash TEXT,
                    local_cache_path TEXT,
                    tags TEXT DEFAULT '',
                    favorite INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()

    def save_setting(self, key: str, value: str) -> None:
        with self.get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )
            conn.commit()

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default

    def add_file(self, file_data: Dict[str, Any]) -> int:
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO files (
                    filename, size, type, upload_date, telegram_message_id, 
                    telegram_file_id, chunk_index, total_chunks, encrypted, 
                    hash, local_cache_path, tags, favorite
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file_data.get("filename"),
                file_data.get("size"),
                file_data.get("type"),
                file_data.get("upload_date"),
                file_data.get("telegram_message_id"),
                file_data.get("telegram_file_id"),
                file_data.get("chunk_index", 0),
                file_data.get("total_chunks", 1),
                file_data.get("encrypted", 0),
                file_data.get("hash"),
                file_data.get("local_cache_path"),
                file_data.get("tags", ""),
                file_data.get("favorite", 0)
            ))
            conn.commit()
            return cursor.lastrowid

    def get_all_files(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM files ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    def search_files(self, query: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM files WHERE filename LIKE ? OR tags LIKE ? ORDER BY id DESC",
                (f"%{query}%", f"%{query}%")
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_file(self, file_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM files WHERE id = ?", (file_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_file_chunks(self, filename: str, file_hash: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM files WHERE filename = ? AND hash = ? ORDER BY chunk_index ASC",
                (filename, file_hash)
            )
            return [dict(row) for row in cursor.fetchall()]

    def delete_file(self, file_id: int) -> None:
        with self.get_connection() as conn:
            conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
            conn.commit()

    def delete_file_group(self, filename: str, file_hash: str) -> None:
        with self.get_connection() as conn:
            conn.execute("DELETE FROM files WHERE filename = ? AND hash = ?", (filename, file_hash))
            conn.commit()

    def update_favorite(self, file_id: int, favorite: int) -> None:
        with self.get_connection() as conn:
            conn.execute("UPDATE files SET favorite = ? WHERE id = ?", (favorite, file_id))
            conn.commit()

    def update_tags(self, file_id: int, tags: str) -> None:
        with self.get_connection() as conn:
            conn.execute("UPDATE files SET tags = ? WHERE id = ?", (tags, file_id))
            conn.commit()

    def get_total_usage(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(DISTINCT hash) as total_files, SUM(size) as total_size FROM files")
            row = cursor.fetchone()
            return {
                "total_files": row["total_files"] if row["total_files"] else 0,
                "total_size": row["total_size"] if row["total_size"] else 0
            }

    def backup_database(self, dest_path: str) -> None:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(self.db_path, dest_path)

    def restore_database(self, src_path: str) -> None:
        if os.path.exists(src_path):
            shutil.copy2(src_path, self.db_path)
