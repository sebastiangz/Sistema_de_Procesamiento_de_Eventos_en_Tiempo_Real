import rx
from rx import operators as ops
from rx.subject import Subject
from rx.scheduler.eventloop import AsyncIOThreadSafeScheduler
from datetime import datetime
import asyncio
from typing import Iterable, Callable, Optional


class Event:
    def __init__(self, event_type: str, data: dict):
        self.type = event_type
        self.data = data
        self.timestamp = datetime.now()

    def __repr__(self):
        # Muestra la hora de emision
        return f"<Event {self.type} {self.data} @ {self.timestamp.strftime('%H:%M:%S')}>"


class EventStream:
    """Wrapper alrededor de un Subject para streams 'hot'.

    - `emit(event)` publica el evento y hace print (para visibilidad)
    - `pipe(*ops)` devuelve el observable piped
    """
    def __init__(self, name: str, subject: Optional[Subject] = None):
        self.name = name
        self._subject = subject if subject is not None else Subject()

    def emit(self, event: Event):
        print(f"[{self.name}] → {event}")
        self._subject.on_next(event)

    def pipe(self, *operators):
        return self._subject.pipe(*operators)

    def as_observable(self):
        return self._subject

    @staticmethod
    def cold_from_iterable(items: Iterable):
        """Crea un cold observable desde un iterable (no multicast)."""
        return rx.from_iterable(items)

    @staticmethod
    def hot_subject(name: str):
        """Crea un hot EventStream (Subject) para publicar eventos en vivo."""
        return EventStream(name)

    @staticmethod
    def connectable_from_cold(cold_observable, name: str):
        """Convierte un cold observable en un connectable hot usando Subject multicast."""
        subject = Subject()
        # Subscribe cold to subject so multiple subscribers see the same events
        cold_observable.subscribe(subject)
        return EventStream(name, subject=subject)

    @staticmethod
    def interval(seconds: float):
        """Wrapper para rx.interval (segundos)."""
        return rx.interval(seconds)


def create_event_stream(name: str) -> EventStream:
    print(f"Creando stream: {name}")
    return EventStream.hot_subject(name)


# Helper: scheduler compatible con asyncio
def get_async_scheduler(loop: Optional[asyncio.AbstractEventLoop] = None):
    loop = loop or asyncio.get_event_loop()
    return AsyncIOThreadSafeScheduler(loop)