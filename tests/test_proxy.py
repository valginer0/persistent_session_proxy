"""Tests for the persistent session proxy."""
import pytest
from pathlib import Path
import tempfile
from persistent_session_proxy.session_store import SessionStore
from persistent_session_proxy.proxy_session import ProxySession

@pytest.fixture
def temp_db():
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        yield f.name
    Path(f.name).unlink()

@pytest.fixture
def session_store(temp_db):
    """Create a session store with temporary database."""
    return SessionStore(temp_db)

def test_session_store_init(session_store):
    """Test session store initialization."""
    assert Path(session_store.db_path).exists()

def test_session_store_save_load(session_store):
    """Test saving and loading session data."""
    session_id = "test_session"
    cookies = {"cookie1": "value1"}
    form_data = {"field1": "value1"}
    headers = {"User-Agent": "test"}
    last_url = "https://example.com"
    
    session_store.save_session(session_id, cookies, form_data, headers, last_url)
    data = session_store.load_session(session_id)
    
    assert data is not None
    assert data["cookies"] == cookies
    assert data["form_data"] == form_data
    assert data["headers"] == headers
    assert data["last_url"] == last_url

def test_proxy_session_init():
    """Test proxy session initialization."""
    session = ProxySession()
    assert session.session_id is not None
    assert session._last_form_data == {}
    assert session._last_url is None

def test_proxy_session_restore(session_store):
    """Test session restoration."""
    # Create and save a session
    session_id = "test_restore"
    cookies = {"cookie1": "value1"}
    form_data = {"field1": "value1"}
    headers = {"User-Agent": "test"}
    last_url = "https://example.com"
    
    session_store.save_session(session_id, cookies, form_data, headers, last_url)
    
    # Restore the session
    session = ProxySession(session_id=session_id, store=session_store)
    
    assert session.cookies == cookies
    assert session.last_form_data == form_data
