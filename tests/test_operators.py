import unittest
import rx
from rx import operators as ops
from src.streams import Event
from src.operators import scale_event, filter_above, compose_pipeline

class TestOperators(unittest.TestCase):

    def test_scale_event(self):
        """Prueba la funcion pura de escalado"""
        source = rx.just(Event("DATA", {"value": 10.0, "other": "A"}))
        results = []
        
        source.pipe(scale_event(factor=2.5)).subscribe(
            on_next=lambda e: results.append(e.data["value"])
        )
        
        self.assertEqual(results, [25.0])

    def test_filter_above(self):
        """Prueba la funcion pura de filtrado"""
        events = [
            Event("DATA", {"value": 50}),
            Event("DATA", {"value": 100}),
            Event("DATA", {"value": 49.9})
        ]
        source = rx.from_iterable(events)
        results = []
        
        source.pipe(filter_above(threshold=50)).subscribe(
            on_next=lambda e: results.append(e.data["value"])
        )
        
        # Solo el evento con valor 100 debe pasar el filtro > 50
        self.assertEqual(results, [100])
        
    def test_compose_pipeline(self):
        """Prueba la composicin de multiples operadores"""
        source = rx.from_iterable([
            Event("DATA", {"value": 10}),
            Event("DATA", {"value": 60})
        ])
        results = []
        
        pipeline = compose_pipeline(
            filter_above(50),      # 1. Filtra solo el 60
            scale_event(factor=10) # 2. Lo escala a 600
        )
        
        source.pipe(pipeline).subscribe(
            on_next=lambda e: results.append(e.data["value"])
        )
        
        self.assertEqual(results, [600])

if __name__ == '__main__':
    unittest.main()