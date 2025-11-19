import unittest
from datetime import datetime
from rx.subject import Subject
from src.streams import Event, EventStream
from rx.testing import TestScheduler
from rx import operators as ops

class TestStreams(unittest.TestCase):
    
    def test_event_creation(self):
        """Verifica que el objeto Event se cree correctamente con timestamp."""
        event = Event("TEST", {"key": 100})
        self.assertEqual(event.type, "TEST")
        self.assertEqual(event.data["key"], 100)
        self.assertIsInstance(event.timestamp, datetime)
        
    def test_eventstream_emit_and_subscribe(self):
        """Verifica que emitir un evento lo pase al suscriptor."""
        stream = EventStream("TestStream")
        results = []
        
        stream._subject.subscribe(on_next=lambda e: results.append(e.type))
        
        test_event = Event("PING", {})
        stream.emit(test_event)
        
        self.assertEqual(results, ["PING"])
        
    def test_eventstream_pipe(self):
        """Verifica que el método pipe() aplique un operador correctamente."""
        stream = EventStream("TestPipe")
        results = []
        
        # Flujo: Emitir un evento, filtrar solo si el valor es > 50
        filtered_stream = stream.pipe(
            ops.filter(lambda e: e.data.get("value", 0) > 50)
        )
        
        filtered_stream.subscribe(on_next=lambda e: results.append(e.type))
        
        stream.emit(Event("A", {"value": 60}))
        stream.emit(Event("B", {"value": 40}))
        stream.emit(Event("C", {"value": 70}))
        
        self.assertEqual(results, ["A", "C"])

if __name__ == '__main__':
    unittest.main()