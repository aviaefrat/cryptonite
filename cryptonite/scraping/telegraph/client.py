from cryptonite.scraping.friendly_client import FriendlyClient

# After subscribing to The Telegraph, locate the your https://puzzles.telegraph.co.uk cookie, and:
details = ''  # set this to be the value of `details`
rememberme = ''  # set this to be the value of `rememberme` (probably '604800')


class Client:

    def __init__(self):
        self.client = FriendlyClient(min_interval_between_requests=0.3)
        self.client.session.cookies.update({
            'details': details,
            'rememberme': rememberme,
        })

    def get(self, url, params):
        result = self.client.request('GET', url, params)
        if 'Need assistance' in result:
            # this also happens when trying to fetch solutions that have not been published yet.
            # need code to handle this more gracefully
            raise RuntimeError('Maybe update `details` and `rememberme` from the https://puzzles.telegraph.co.uk cookie (see the beginning of this file)')
        return result

    def post(self, url, params, headers=None):
        # Not sure what's the output on unauthenticated request here, as this endpoint
        # seems to work with no cookies at all
        return self.client.request('POST', url, params, headers=headers)


client = Client()
