import logging

from cryptonite.scraping.the_times.client import Client
from cryptonite.scraping.the_times.crossword_parser import fetch_crossword_entries
from cryptonite.scraping.the_times.links_iterator import LinksIterator


logger = logging.getLogger('the-times')


class Scraper:
    def __init__(self, start_date, end_date, authentication):
        self.client = Client(authentication)
        self.links_iterator = LinksIterator(start_date=start_date, end_date=end_date, client=self.client)

    def scrape(self):
        for puzzle_url in self.links_iterator.iterate():
            try:
                yield from fetch_crossword_entries(puzzle_url, self.client)
            except Exception:  # TODO yes this is too broad. I just what to see what happens for now
                logger.info(f"general crossword problem in: {puzzle_url}", exc_info=True)
                puzzle_id = puzzle_url.split('/')[-1].replace('?header=false', '')  # TODO less hacky
                logger.warning(f"skipped crossword {puzzle_id} because of a general problem")
