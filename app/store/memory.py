from typing import Any, Dict


class MemoryStore:
    _data: Dict[str, Any] = {}

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        cls._data[key] = value

    @classmethod
    def get(cls, key: str) -> Any:
        return cls._data.get(key)

    @classmethod
    def clear(cls) -> None:
        cls._data.clear()







