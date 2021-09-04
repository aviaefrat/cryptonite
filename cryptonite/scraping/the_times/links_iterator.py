from bs4 import BeautifulSoup

from cryptonite.scraping.the_times.client import client


class LinksIterator:
    def __init__(self, p_from, p_to, page=1):
        # paging starts at 1
        self.start_page = page or 1
        self.p_from = p_from
        self.p_to = p_to

    def iterate(self):
        current_page = self.start_page
        while True:
            raw_page = self.fetch_raw_puzzles_list_page(current_page)
            links = self.extract_links_from_raw_page(raw_page)
            if not links:
                break
            yield from links
            current_page += 1

    def fetch_raw_puzzles_list_page(self, page):
        # TODO it would be nice to add a date to this print, as with scrapes of wide ranges all
        #  you see is "Fetching page <PAGE_NUM> [from=16/10/2000, to=31/03/2020]", which does not
        #  give a hint of the progression
        print(f'Fetching page {page} [from={self.p_from}, to={self.p_to}]')
        url = 'https://www.thetimes.co.uk/puzzleclub/crosswordclub/puzzles-list'
        params = {
            'search': '',
            'filter[puzzle_type]': 'Cryptic',
            'filter[publish_at][from]': self.p_from,
            'filter[publish_at][to]': self.p_to,
            'page': page,
        }
        return client.get(url, params=params)

    @staticmethod
    def extract_links_from_raw_page(raw_page):
        soup = BeautifulSoup(raw_page, features='html.parser')
        links_rs = soup.find_all(class_='puzzle-title-link')
        return [link.attrs['href'] for link in links_rs]


def main():
    p_from = '01/04/2020'
    p_to = '01/04/2020'
    iterator = LinksIterator(p_from=p_from, p_to=p_to)
    for link in iterator.iterate():
        print(f'link: {link}')


if __name__ == '__main__':
    main()
