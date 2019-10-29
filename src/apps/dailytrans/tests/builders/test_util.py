import datetime
from dashboard.testing import BuilderBackendTestCase
from apps.dailytrans.builders.utils import date_transfer, date_delta, date_generator


class UtilTestCase(BuilderBackendTestCase):

    def test_date_transfer(self):

        date = datetime.date(year=2017, month=1, day=1)

        # test datetime transfer to string

        string = date_transfer(sep='.', date=date, zfill=True, roc_format=True)
        self.assertEqual(string, '106.01.01')

        string = date_transfer(sep='-', date=date, zfill=True, roc_format=True)
        self.assertEqual(string, '106-01-01')

        string = date_transfer(sep='.', date=date, zfill=False, roc_format=True)
        self.assertEqual(string, '106.1.1')

        string = date_transfer(sep='.', date=date, zfill=False, roc_format=False)
        self.assertEqual(string, '2017.1.1')

        self.assertRaises(NotImplementedError, date_transfer, sep='.', date=date, roc_format=False)

        # test string transfer to datetime

        string = '106.01.01'

        self.assertRaises(NotImplementedError, date_transfer, sep='.', string=string, date=date, roc_format=False)

        test_date = date_transfer(sep='.', string=string, roc_format=True)
        self.assertEqual(date, test_date)

        test_date = date_transfer(sep='-', string='106-1-1', roc_format=True)
        self.assertEqual(date, test_date)

        self.assertRaises(ValueError, date_transfer, sep='.', string='106.1.1.1', roc_format=False)

        # test sep = ''
        self.assertRaises(OverflowError, date_transfer, sep='', string='106011', roc_format=True)

        test_date = date_transfer(sep='', string='1060101', roc_format=True)
        self.assertEqual(date, test_date)

        test_date = date_transfer(sep='', string='20170101', roc_format=False)
        self.assertEqual(date, test_date)

    def test_date_delta(self):

        start_date, end_date = date_delta(3)

        self.assertEqual(start_date, datetime.date.today())
        self.assertEqual(end_date, datetime.date.today() + datetime.timedelta(3))

        start_date, end_date = date_delta(-3)

        self.assertEqual(end_date, datetime.date.today())
        self.assertEqual(start_date, datetime.date.today() + datetime.timedelta(-3))

    def test_date_generator(self):
        start_date = datetime.date(year=2016, month=1, day=1)
        end_date = datetime.date(year=2018, month=1, day=1)
        delta = 120

        result = []
        for s, e in date_generator(start_date, end_date, delta):
            self.assertIsInstance(s, datetime.date)
            self.assertIsInstance(e, datetime.date)
            result.append((s, e))

        self.assertEqual(len(result), 7)

    def test_date_generator_single(self):
        start_date = datetime.date(year=2016, month=1, day=1)
        end_date = datetime.date(year=2016, month=1, day=5)
        delta = 1

        result = []
        for s, e in date_generator(start_date, end_date, delta):
            self.assertIsInstance(s, datetime.date)
            self.assertIsInstance(e, datetime.date)
            result.append((s, e))

        self.assertEqual(len(result), 5)
