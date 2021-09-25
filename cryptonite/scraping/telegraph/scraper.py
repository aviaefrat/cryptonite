import logging

from cryptonite.scraping.telegraph.client import Client
from cryptonite.scraping.telegraph.crossword_parser import fetch_crossword_entries
from cryptonite.scraping.telegraph.links_iterator import MultiLinksIterator


logger = logging.getLogger('telegraph')


class Scraper:
    def __init__(self, start_date, end_date, authentication):
        self.client = Client(authentication)
        self.links_iterator = MultiLinksIterator(start_date=start_date, end_date=end_date,
                                                 client=self.client)

    def scrape(self):
        for puzzle_url in self.links_iterator.iterate():
            try:
                yield from fetch_crossword_entries(puzzle_url, self.client)
            except Exception:  # TODO yes this is too broad. I just what to see what happens for now
                logger.info(f"general crossword problem in: {puzzle_url}", exc_info=True)
                logger.warning(f"skipped crossword {puzzle_url.split('=')[-1]} because of a general problem")
