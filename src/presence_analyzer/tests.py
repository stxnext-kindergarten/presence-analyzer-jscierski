# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import datetime
import json
import os.path
import unittest

from flask import Response

from presence_analyzer import main
from presence_analyzer.blueprints.api_v1 import utils
from presence_analyzer.blueprints.api_v1.exceptions import UserNotFoundError

TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerApiTestCase(unittest.TestCase):
    """
    API blueprint tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_api_mean_time_weekday(self):
        """
        Test mean presence for user per weekday.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/11')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        expected_result = [
            ['Mon', 24123.0],
            ['Tue', 16564.0],
            ['Wed', 25321.0],
            ['Thu', 22984.0],
            ['Fri', 6426.0],
            ['Sat', 0],
            ['Sun', 0]
        ]
        self.assertEqual(len(data), 7)
        self.assertEqual(data, expected_result)

    def test_api_mean_time_weekday_404(self):
        """
        Test mean presence for user per weekday for nonexistent user.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/0')
        self.assertEqual(resp.status_code, 404)

    def test_api_presence_weekday(self):
        """
        Test sum of presence for user per weekday.
        """
        resp = self.client.get('/api/v1/presence_weekday/11')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        expected_response = [
            ['Weekday', 'Presence (s)'],
            ['Mon', 24123],
            ['Tue', 16564],
            ['Wed', 25321],
            ['Thu', 45968],
            ['Fri', 6426],
            ['Sat', 0],
            ['Sun', 0]
        ]
        self.assertEqual(data, expected_response)
        self.assertEqual(len(data), 8)

    def test_api_presence_weekday_404(self):
        """
        Test sum of presence for user per weekday for nonexistent user.
        """
        resp = self.client.get('/api/v1/presence_weekday/0')
        self.assertEqual(resp.status_code, 404)

    def test_api_presence_start_end(self):
        """
        Test average start and end of presence per weekday.
        """
        resp = self.client.get('/api/v1/presence_start_end/11')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        expected_response = [
            ['Mon', 33134.0, 57257.0],
            ['Tue', 33590.0, 50154.0],
            ['Wed', 33206.0, 58527.0],
            ['Thu', 35602.0, 58586.0],
            ['Fri', 47816.0, 54242.0],
            ['Sat', 0, 0],
            ['Sun', 0, 0]
        ]
        self.assertEqual(data, expected_response)
        self.assertEqual(len(data), 7)

    def test_api_presence_start_end_404(self):
        """
        Test average start and end of presence per weekday
        for nonexistent user.
        """
        resp = self.client.get('/api/v1/presence_start_end/0')
        self.assertEqual(resp.status_code, 404)


class PresenceAnalyzerWebsiteTestCase(unittest.TestCase):
    """
    Website blueprint tests.
    """
    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday')

    def test_presence_weekday(self):
        """
        Test mean time per weekday view.
        """
        resp = self.client.get('/presence_weekday')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h2>Presence by weekday</h2>', resp.data)

    def test_mean_time_weekday(self):
        """
        Test mean time per weekday view.
        """
        resp = self.client.get('/mean_time_weekday')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h2>Presence mean time by weekday</h2>', resp.data)

    def test_presence_start_end(self):
        """
        Test mean time per weekday view.
        """
        resp = self.client.get('/presence_start_end')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<h2>Presence start-end weekday</h2>', resp.data)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_jsonify(self):
        """
        Test jsonify decorator
        """
        test_data = {'key': 'value'}

        def tested_func():
            """
            Just a function to be decorated
            """
            return test_data

        result = utils.jsonify(tested_func)()
        self.assertIsInstance(result, Response)
        self.assertEqual(result.data, json.dumps(test_data))
        self.assertEqual(result.mimetype, 'application/json')

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        expected_response = datetime.time(9, 39, 5)
        self.assertEqual(data[10][sample_date]['start'], expected_response)

    def test_get_user_data(self):
        """
        Test getting CSV file and extracting user-specific data from it.
        """
        global_data = utils.get_data()
        user_data = utils.get_user_data(10)
        self.assertEqual(user_data, global_data[10])

    def test_get_nonexistent_user_data(self):
        """
        Test getting CSV file and extracting user-specific data from it, when
        user does not exist.
        """
        with self.assertRaises(UserNotFoundError):
            utils.get_user_data(0)

    def test_group_by_weekday(self):
        """
        Test grouping by weekday
        """
        data = {
            datetime.date(2016, 7, 18): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 0, 0),
            },
            datetime.date(2016, 7, 19): {
                'start': datetime.time(8, 0, 0),
                'end': datetime.time(18, 0, 0),
            }
        }
        expected_result = [[28800], [36000], [], [], [], [], []]
        self.assertEqual(utils.group_by_weekday(data), expected_result)

    def test_presence_start_end(self):
        """
        Test grouping by weekday start/end entries separately.
        """
        data = {
            datetime.date(2016, 7, 18): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 0, 0),
            },
            datetime.date(2016, 7, 25): {
                'start': datetime.time(8, 0, 0),
                'end': datetime.time(16, 0, 0),
            },
            datetime.date(2016, 7, 19): {
                'start': datetime.time(8, 0, 0),
                'end': datetime.time(18, 0, 0),
            }
        }
        expected_result = {
            0: {'start': [28800, 32400], 'end': [57600, 61200]},
            1: {'start': [28800], 'end': [64800]},
            2: {'start': [], 'end': []},
            3: {'start': [], 'end': []},
            4: {'start': [], 'end': []},
            5: {'start': [], 'end': []},
            6: {'start': [], 'end': []}
        }
        self.assertEqual(
            utils.group_start_end_by_weekday(data),
            expected_result,
        )

    def test_average_start_end_time(self):
        """
        Test average start and end time function
        """
        data = {
            0: {'start': [28800, 32400], 'end': [57600, 61200]},
            1: {'start': [28800], 'end': [64800]},
            2: {'start': [], 'end': []},
            3: {'start': [], 'end': []},
            4: {'start': [], 'end': []},
            5: {'start': [], 'end': []},
            6: {'start': [], 'end': []}
        }
        expected_result = [
            ['Mon', 30600, 59400],
            ['Tue', 28800, 64800],
            ['Wed', 0, 0],
            ['Thu', 0, 0],
            ['Fri', 0, 0],
            ['Sat', 0, 0],
            ['Sun', 0, 0]
        ]
        self.assertEqual(
            utils.count_average_start_end_time(data),
            expected_result,
        )

    def test_seconds_since_midnight(self):
        """
        Test seconds since midnight function
        """
        self.assertEqual(
            utils.seconds_since_midnight(datetime.time(hour=1)),
            3600,
        )
        self.assertEqual(
            utils.seconds_since_midnight(datetime.time(hour=0)),
            0,
        )
        self.assertEqual(
            utils.seconds_since_midnight(
                datetime.time(hour=23, minute=59, second=59)
            ),
            86399,
        )
        self.assertEqual(
            utils.seconds_since_midnight(
                datetime.time(hour=7, minute=34, second=23)
            ),
            27263,
        )

    def test_interval(self):
        """
        Test interval function
        """
        start = datetime.time(hour=0)
        end = datetime.time(hour=0, second=1)

        self.assertEqual(utils.interval(start, end), 1)
        self.assertEqual(utils.interval(end, start), -1)
        end = start
        self.assertEqual(utils.interval(start, end), 0)

    def test_mean(self):
        """
        Test mean function
        """
        self.assertEqual(utils.mean([]), 0)
        self.assertEqual(utils.mean([1, 2]), 1.5)
        self.assertIsInstance(utils.mean([2.5, 7.5]), float)
        self.assertEqual(utils.mean([2.5, 7.5]), 5.0)
        self.assertIsInstance(utils.mean([1, 3]), float)


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerApiTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerWebsiteTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
