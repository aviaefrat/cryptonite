import time

import requests

user_agent = 'Dan the Friendly Data Science Bot'
_headers = {
    'User-Agent': user_agent,
}


# todo make the two specific clients inherit from this client?
class FriendlyClient:

    def __init__(self, min_interval_between_requests=0):
        self.min_interval_between_requests = min_interval_between_requests
        self.session = requests.Session()
        self.session.headers.update(_headers)

    def request(self, method, url, params, headers=None):
        params_key = 'params' if method.lower() == 'get' else 'data'
        headers = headers or {}
        response = self.session.request(method, url, headers=headers, **{params_key: params})
        response.raise_for_status()
        return response.text


client = FriendlyClient()
