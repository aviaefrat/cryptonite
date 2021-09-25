from bs4 import BeautifulSoup


class LinksIterator:
    def __init__(self, start_date, end_date, client):
        # paging starts at 1
        self.start_page = 1
        self.start_date = start_date
        self.end_date = end_date
        self.client = client

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
        print(f'Fetching page {page} [from={self.start_date}, to={self.end_date}]')
        url = 'https://www.thetimes.co.uk/puzzleclub/crosswordclub/puzzles-list'
        params = {
            'search': '',
            'filter[puzzle_type]': 'Cryptic',
            'filter[publish_at][from]': self.start_date,
            'filter[publish_at][to]': self.end_date,
            'page': page,
        }
        return self.client.get(url, params=params)

    @staticmethod
    def extract_links_from_raw_page(raw_page):
        soup = BeautifulSoup(raw_page, features='html.parser')
        links_rs = soup.find_all(class_='puzzle-title-link')
        return [link.attrs['href'] for link in links_rs]
