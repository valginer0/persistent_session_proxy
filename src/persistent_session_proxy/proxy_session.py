"""Persistent proxy session implementation."""
import uuid
from typing import Dict, Optional
import requests
from .session_store import SessionStore

class ProxySession:
    def __init__(self, session_id: Optional[str] = None, 
                 store: Optional[SessionStore] = None):
        """Initialize a persistent proxy session.
        
        Args:
            session_id: Existing session ID to restore. If None, creates new session.
            store: SessionStore instance. If None, creates new one with default settings.
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.store = store or SessionStore()
        self.session = requests.Session()
        self._last_form_data = {}
        self._last_url = None
        
        # Restore session if it exists
        if session_id:
            self._restore_session()
    
    def _restore_session(self):
        """Restore session state from persistent storage."""
        data = self.store.load_session(self.session_id)
        if data:
            self.session.cookies.update(data["cookies"])
            self._last_form_data = data["form_data"]
            self.session.headers.update(data["headers"])
            self._last_url = data["last_url"]
    
    def _save_session(self, form_data: Dict = None):
        """Save current session state to persistent storage."""
        cookies_dict = {k: v for k, v in self.session.cookies.items()}
        
        # Update form data if provided
        if form_data is not None:
            self._last_form_data = form_data
            
        self.store.save_session(
            self.session_id,
            cookies_dict,
            self._last_form_data,
            dict(self.session.headers),
            self._last_url
        )
    
    @property
    def cookies(self) -> Dict:
        """Get current session cookies."""
        return {k: v for k, v in self.session.cookies.items()}
    
    @property
    def last_form_data(self) -> Dict:
        """Get last submitted form data."""
        return self._last_form_data
