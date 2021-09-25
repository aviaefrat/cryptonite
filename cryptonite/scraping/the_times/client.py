from cryptonite.scraping.friendly_client import FriendlyClient


class Client:

    def __init__(self, authentication):
        self.client = FriendlyClient(min_interval_between_requests=2)
        self.client.session.cookies.update({
            # these two seem to suffice for puzzles-list
            'acs_tnl': authentication["acs_tnl"],
            'sacs_tnl': authentication["sacs_tnl"],
            # this is required for a crossword page
            authentication["remember_puzzleclub_key"]: authentication["remember_puzzleclub_value"],
        })

    def get(self, url, params):
        result = self.client.request('GET', url, params)
        if 'forgotPasswordLink' in result:
            raise RuntimeError('Try to update the Times authentication config (see the README)')
        return result
