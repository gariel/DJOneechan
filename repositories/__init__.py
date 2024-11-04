import dataclasses
import datetime
from typing import Optional

from pymongo.synchronous.database import Database

def _build_fake(default):
    def fake(*args, **kwargs):
        return default
    return fake

def with_default(default):
    def wrapper(func):
        func.__default__ = _build_fake(default)
        return func

    return wrapper


class BaseRepository:
    def __init__(self, client: Optional[Database]):
        self._is_valid = client is not None

    def __getattribute__(self, item):
        attr = super(BaseRepository, self).__getattribute__(item)
        if item.startswith("_") or self._is_valid:
            return attr

        if hasattr(attr, "__default__"):
            return attr.__default__

        if not hasattr(attr, "__annotations__"):
            return attr

        if "return" not in attr.__annotations__:
            return attr

        return _build_fake(attr.__annotations__["return"]())

    def _convert(self, item):
        if type(item) is not dict:
            item = dataclasses.asdict(item)

        return {
            "at": datetime.datetime.now(datetime.UTC),
            **item,
        }

    def _unconvert(self, tp: type, data: dict):
        data_fields = [f.name for f in dataclasses.fields(tp)]
        return tp(**{f: data.get(f) for f in data_fields})

    def _unconvert_n(self, tp: type, items: list[dict]):
        return [
            self._unconvert(tp, item)
            for item in items
        ]