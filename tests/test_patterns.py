import unittest
import rx
from rx import operators as ops
from src.streams import Event
from src.patterns import check_high_volatility, high_volatility_pattern, detect_pattern

class TestPatterns(unittest.TestCase):

    def create_event(self, change):
        return Event("TICK", {"price": 100, "change": change})

    def test_check_high_volatility_true(self):
        """Prueba la funcion pura de chequeo de volatilidad (True)"""
        # Cambios: [3.0, 3.0, 1.0], promedio = 7.0 / 3 = 2.33, mayor a 2.0 (umbral)
        events = [
            self.create_event(3.0),
            self.create_event(3.0),
            self.create_event(1.0)
        ]
        self.assertTrue(check_high_volatility(events))

    def test_check_high_volatility_false(self):
        """Prueba la funcion pura de chequeo de volatilidad (False)"""
        # Cambios: [0.5, 0.5, 0.5], promedio = 1.5 / 3 = 0.5, menor a 2.0
        events = [
            self.create_event(0.5),
            self.create_event(0.5),
            self.create_event(0.5)
        ]
        self.assertFalse(check_high_volatility(events))

    def test_detect_pattern_operator(self):
        """Prueba el operador detect_pattern con windowing"""
        events = [
            self.create_event(1.0), # Ventana 1: [1.0, 4.0, 4.0] -> True
            self.create_event(4.0), 
            self.create_event(4.0), 
            self.create_event(0.5), # Ventana 2: [4.0, 4.0, 0.5] -> True
            self.create_event(0.1)  # Ventana 3: [4.0, 0.5, 0.1] -> False
        ]
        source = rx.from_iterable(events)
        results = []
        
        # Configurar deteccion de alta volatilidad con ventana de 3 y paso de 1
        detector_pipeline = detect_pattern(high_volatility_pattern, window_size=3, step=1)
        
        source.pipe(detector_pipeline).subscribe(
            on_next=lambda alert: results.append(alert["pattern"])
        )
        
        # Esperamos 2 alertas
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], "HIGH_VOLATILITY")

if __name__ == '__main__':
    unittest.main()