"""In-process event bus for real-time client updates (SSE).

The backend is a single local process, so an in-memory subscriber set is
sufficient. Events: attendance.recorded, student.*, device.*.
"""

from __future__ import annotations

import asyncio
import json


class EventBus:
    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        self._subscribers.discard(queue)

    def publish(self, event_type: str, payload: dict) -> None:
        message = json.dumps({"type": event_type, "data": payload})
        for queue in list(self._subscribers):
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                pass


BUS = EventBus()
