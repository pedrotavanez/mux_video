import unittest
import requests
import json
from video.helpers.integration_config import options

class TestIntegrationMethods(unittest.TestCase):

    def test_mux_api(self):
        # No Auth
        mux_token_id = None
        mux_secret = None
        headers = {"Content-Type": "application/json"}
        mux_live = options['mux_api']
        r = requests.get(
            mux_live, headers=headers, auth=(mux_token_id, mux_secret)
        )
        self.assertEqual(r.status_code, 401)
        r_good = requests.get(
        mux_live, headers=headers, auth=(options["mux_token_id"], options["mux_secret"])
        )
        self.assertEqual(r_good.status_code, 200)
        self.assertEqual(type(json.loads(r_good.text)['data']), list)


if __name__ == '__main__':
    unittest.main()