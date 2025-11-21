import unittest
import rx
from src.patterns import detect_correlation, detect_pattern, cep_operator, ml_anomaly_detector, Pattern
from src.streams import Event
from rx import operators as ops


class TestPatternsExtra(unittest.TestCase):

    def test_detect_correlation(self):
        # Create events with perfect correlation between a and b
        events = [Event('E', {'a': i, 'b': i}) for i in range(1, 6)]
        results = []

        pattern = detect_correlation('a', 'b', threshold=0.9)
        # use detect_pattern to convert Pattern into an operator
        rx.from_iterable(events).pipe(
            detect_pattern(pattern, window_size=3)
        ).subscribe(on_next=lambda alert: results.append(alert))

        self.assertTrue(len(results) >= 1)

    def test_cep_operator(self):
        # Simple CEP rule: emit if sum of prices in window > 100
        def rule(win):
            s = sum(e.data.get('price', 0) for e in win)
            return {'pattern': 'SUM_GT_100', 'events': win} if s > 100 else None

        events = [Event('T', {'price': p}) for p in [30, 40, 50, 10, 5]]
        results = []
        rx.from_iterable(events).pipe(
            cep_operator([rule], window_size=3)
        ).subscribe(on_next=lambda x: results.append(x))

        self.assertTrue(len(results) >= 1)

    def test_ml_anomaly_detector(self):
        # Create a window where the last value is an outlier
        values = [10]*19 + [1000]
        events = [Event('T', {'val': v}) for v in values]
        results = []
        rx.from_iterable(events).pipe(
            ml_anomaly_detector('val', z_thresh=3.0, window=20)
        ).subscribe(on_next=lambda a: results.append(a))

        self.assertTrue(len(results) >= 1)


if __name__ == '__main__':
    unittest.main()
