import unittest

import requests

from parsers.stepic import get_data
from settings import PORT, HOST
from utils.stepik_api import get_token


class StepicParserTests(unittest.TestCase):
    def setUp(self):
        self.data = get_data(1)

    def test_get_data(self):
        if not self.data[1]:
            self.fail('Stepiс have minimum one page')


class StepicApiTests(unittest.TestCase):
    def test_token(self):
        token = get_token()

        if not token or len(token) == 0:
            self.fail('Stepiс token not valid')


class ApiTest(unittest.TestCase):
    def test_add_course(self):
        res = requests.post('http://{}:{}/api/add/'.format(HOST, PORT),
                            json={"title": "Test", 'type': 'special', "specific_id": "test",
                                  "text": "Целью проведения сессии является усовершенствование действующей модели"})
        if res.ok:
            answer = res.json()

            if 'error' in answer:
                self.fail(answer['error']['message'])
        else:
            self.fail('Please, run API service')


if __name__ == '__main__':
    unittest.main()
