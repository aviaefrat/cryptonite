import time

import requests

user_agent = 'Dan the Friendly Data Science Bot'
_headers = {
    'User-Agent': user_agent,
}


class FriendlyClient:

    def __init__(self, min_interval_between_requests=0):
        self.last_request_time = 0
        self.min_interval_between_requests = min_interval_between_requests
        self.session = requests.Session()
        self.session.headers.update(_headers)

    def request(self, method, url, params, headers=None):
        params_key = 'params' if method.lower() == 'get' else 'data'
        headers = headers or {}
        time_since_last_request = time.time() - self.last_request_time
        time_to_sleep = self.min_interval_between_requests - time_since_last_request
        if time_to_sleep > 0:
            print(f"slept {time_to_sleep:.3f}s before url {url}")
            time.sleep(time_to_sleep)
        self.last_request_time = time.time()
        response = self.session.request(method, url, headers=headers, **{params_key: params})
        response.raise_for_status()
        return response.text


client = FriendlyClient()
