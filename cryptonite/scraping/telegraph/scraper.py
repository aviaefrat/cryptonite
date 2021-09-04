import json
import logging

from cryptonite.scraping.telegraph.crossword_parser import fetch_crossword_entries
from cryptonite.scraping.telegraph.links_iterator import MultiLinksIterator, LinksIterator


logger = logging.getLogger('telegraph')


class Scraper:
    def __init__(self, p_from, p_to, page=None):  # TODO add default range: 26/11/2001 -> yesterday
        assert not page, 'page not supported with date ranges. Use SingleDateScraper'
        self.links_iterator = MultiLinksIterator(p_from=p_from, p_to=p_to)

    def scrape(self):
        for puzzle_url in self.links_iterator.iterate():
            try:
                yield from fetch_crossword_entries(puzzle_url)
            except Exception:  # TODO yes this is too broad. I just what to see what happens for now
                logger.info(f"general crossword problem in: {puzzle_url}", exc_info=True)
                logger.warning(f"skipped crossword {puzzle_url.split('=')[-1]} because of a general problem")


class SingleDateScraper:
    def __init__(self, day=0, month=0, year=0, page=0):
        self.links_iterator = LinksIterator(
            date_day=day,
            date_month=month,
            date_year=year,
            page=page,
        )

    def scrape(self):
        for puzzle_url in self.links_iterator.iterate():
            yield from fetch_crossword_entries(puzzle_url)
