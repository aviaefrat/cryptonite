from cryptonite.scraping.friendly_client import FriendlyClient

# After subscribing to The Times, locate the your https://www.thetimes.co.uk cookie, and:
asc_tnl = ''  # set this to be the value of `asc_tnl`
sacs_tnl = ''  # set this to be the value of `sacs_tnl`
# the following are a little trickier because I think the key name is dynamic as well
remember_key = ''  # set this to be the key name that starts with `remember_puzzleclub`
                   # e.g. 'remember_puzzleclub_ae1407addc2b2fa4015806014caf58e34e30989d'
remember_value = '' # set this to be value of the above key


class Client:

    def __init__(self):
        self.client = FriendlyClient(min_interval_between_requests=2)
        self.client.session.cookies.update({
            # these two seem to suffice for puzzles-list
            'acs_tnl': asc_tnl,
            'sacs_tnl': sacs_tnl,
            # this is required for a crossword page
            remember_key: remember_value,
        })

    def get(self, url, params):
        result = self.client.request('GET', url, params)
        if 'forgotPasswordLink' in result:
            raise RuntimeError('Update the value of `asc_tnl`, `sacs_tnl`, `remember_key` and `remember_value` from your https://www.thetimes.co.uk cookie (see the beginning of this file)')
        return result


client = Client()
