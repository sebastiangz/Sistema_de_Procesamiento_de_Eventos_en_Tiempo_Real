import unittest
from src.alerts import AlertManager


class TestAlertManagerExtra(unittest.TestCase):

    def test_notify_multiple_rules(self):
        am = AlertManager(dedup_seconds=1)
        rec = []
        am.subscribe(lambda a: rec.append(a))

        a1 = {'pattern': 'A', 'count': 1}
        a2 = {'pattern': 'B', 'count': 2}

        am.notify(a1)
        am.notify(a2)

        self.assertEqual(len(rec), 2)


if __name__ == '__main__':
    unittest.main()
