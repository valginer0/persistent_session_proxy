"""Session storage implementation using SQLite for persistence."""
import json
import sqlite3
from pathlib import Path
from typing import Dict, Optional, Any
import pickle


class SessionStore:
    def __init__(self, db_path: Optional[str] = None):
        """Initialize session store with SQLite backend.
        
        Args:
            db_path: Path to SQLite database file. If None, uses ~/.persistent_sessions/sessions.db
        """
        if db_path is None:
            db_path = str(Path.home() / ".persistent_sessions" / "sessions.db")
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    cookies TEXT,
                    form_data TEXT,
                    headers TEXT,
                    last_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def save_session(self, session_id: str, cookies: Dict, form_data: Dict, 
                    headers: Dict, last_url: str):
        """Save session data to persistent storage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sessions 
                (session_id, cookies, form_data, headers, last_url, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                session_id,
                json.dumps(cookies),
                json.dumps(form_data),
                json.dumps(headers),
                last_url
            ))
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data from persistent storage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?", 
                (session_id,)
            ).fetchone()
            
            if row is None:
                return None
                
            return {
                "cookies": json.loads(row["cookies"]),
                "form_data": json.loads(row["form_data"]),
                "headers": json.loads(row["headers"]),
                "last_url": row["last_url"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
    
    def delete_session(self, session_id: str):
        """Delete a session from persistent storage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
