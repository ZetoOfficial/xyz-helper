from datetime import datetime


class SessionNotFound(Exception):
    pass


class MemoryDatabase:
    _storage: dict
    _last_active_for_session_id: dict[str, datetime]

    def __init__(self):
        self._storage = {}
        self._last_active_for_session_id = {}

    async def set(self, key: str, value):
        self._storage[key] = value
        self._last_active_for_session_id[key] = datetime.now()

    async def get(self, key):
        self._last_active_for_session_id[key] = datetime.now()
        return self._storage.get(key)

    async def expire(self, key):
        del self._storage[key]
        del self._last_active_for_session_id[key]

    async def find_by_field(self, field, value):
        for session_id, session_data in self._storage.items():
            if field in session_data and session_data[field] == value:
                self._last_active_for_session_id[session_id] = datetime.now()
                return session_id
        return None


memory_database = MemoryDatabase()
