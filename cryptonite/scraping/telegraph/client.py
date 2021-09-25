from cryptonite.scraping.friendly_client import FriendlyClient


class Client:

    def __init__(self, authentication):
        self.client = FriendlyClient(min_interval_between_requests=0.3)
        self.client.session.cookies.update({
            'details': authentication["details"],
            'rememberme': authentication["rememberme"]
        })

    def get(self, url, params):
        result = self.client.request('GET', url, params)
        if 'Need assistance' in result:
            # this also happens when trying to fetch solutions that have not been published yet.
            # need code to handle this more gracefully
            raise RuntimeError('Try to update the Telegraph authentication config (see the README)')
        return result

    def post(self, url, params, headers=None):
        # Not sure what's the output on unauthenticated request here, as this endpoint
        # seems to work with no cookies at all
        return self.client.request('POST', url, params, headers=headers)
