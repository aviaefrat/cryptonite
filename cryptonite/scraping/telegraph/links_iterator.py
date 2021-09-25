import urllib.parse

import arrow
from bs4 import BeautifulSoup


class MultiLinksIterator:

    def __init__(self, start_date, end_date, client):
        self.client = client
        self.date_fmt = 'DD/MM/YYYY'

        # the code below is basically optimization to avoid making a single request
        # for each day in the range. For months that contain the full range, we make
        # a month query, instead of a day query, reducing the number of requests
        # greatly

        start = arrow.get(start_date, self.date_fmt)
        end = arrow.get(end_date, self.date_fmt)
        all_days = list(arrow.Arrow.range('day', start, end))

        month_ranges = {}
        for day in all_days:
            month_range = month_ranges.setdefault(day.floor('month'), {})
            month_range['min'] = min(day, month_range.get('min', day))
            month_range['max'] = max(day, month_range.get('max', day))

        full_months = []
        for month, m_range in month_ranges.items():
            month_min = m_range['min']
            month_max = m_range['max']
            includes_first_day_of_month = month_min.date() == month_min.floor('month').date()
            includes_last_day_of_month = month_max.date() == month_max.ceil('month').date()
            if includes_first_day_of_month and includes_last_day_of_month:
                full_months.append(month)

        def is_standalone_day(d):
            return not any(d.is_between(m, m.ceil('month'), bounds='[]') for m in full_months)

        self.full_months = full_months
        self.standalone_days = [d for d in all_days if is_standalone_day(d)]

    def iterate(self):
        for day in self.standalone_days:
            links_iterator = LinksIterator(
                date_day=day.day,
                date_month=day.month,
                date_year=day.year,
                client=self.client,
            )
            yield from links_iterator.iterate()
        for month in self.full_months:
            links_iterator = LinksIterator(
                date_month=month.month,
                date_year=month.year,
                client=self.client,
            )
            yield from links_iterator.iterate()


class LinksIterator:

    def __init__(self, date_day=0, date_month=0, date_year=0, client=None):
        # paging starts at 0
        self.start_page = 0
        self.date_day = date_day
        self.date_month = date_month
        self.date_year = date_year
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
        print(f'Fetching page {page} [day={self.date_day}, month={self.date_month}, year={self.date_year}]')
        url = 'https://puzzles.telegraph.co.uk/search_results'
        params = {
            'async': 'search',
            'page': page,
            'puzzle-type': 'cryptic',
            'puzzle-date-day': self.date_day,
            'puzzle-date-month': self.date_month,
            'puzzle-date-year': self.date_year,
        }
        return self.client.post(url, params=params)

    @staticmethod
    def extract_links_from_raw_page(raw_page):
        result = []
        soup = BeautifulSoup(raw_page, features='html.parser')
        link_parents = soup.find_all('div', class_='search-puzzle-btn')
        for link_parent in link_parents:
            link = link_parent.find_all('a')[0]['href']
            parsed_link = urllib.parse.urlparse(link)
            parsed_query = urllib.parse.parse_qs(parsed_link.query)
            puzzle_id = parsed_query['puzzle_id'][0]
            final_link = f'{parsed_link.scheme}://{parsed_link.netloc}{parsed_link.path}?puzzle_id={puzzle_id}'
            result.append(final_link)
        return result
