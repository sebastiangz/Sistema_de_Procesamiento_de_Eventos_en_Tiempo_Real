import unittest
from src.alerts import AlertManager


class TestAlertManager(unittest.TestCase):

    def test_deduplication(self):
        am = AlertManager(dedup_seconds=1)
        calls = []

        def subscriber(a):
            calls.append(a)

        am.subscribe(subscriber)

        alert = {"pattern": "P", "detail": "x", "count": 1}
        am.notify(alert)
        am.notify(alert)  # should be deduped

        self.assertEqual(len(calls), 1)

    def test_notify_multiple(self):
        am = AlertManager(dedup_seconds=0)
        calls = []

        am.subscribe(lambda a: calls.append(a))
        am.notify({"pattern": "A", "detail": "1"})
        am.notify({"pattern": "B", "detail": "2"})
        self.assertEqual(len(calls), 2)


if __name__ == '__main__':
    unittest.main()
