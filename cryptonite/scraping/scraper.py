import argparse
import json
import os

from cryptonite.scraping.loggers import setup_loggers
from cryptonite.scraping.telegraph.scraper import Scraper as TelegraphScraper
from cryptonite.scraping.telegraph.scraper import SingleDateScraper as SingleDayTelegraphScraper
from cryptonite.scraping.the_times.scraper import Scraper as TheTimesScraper

publisher_data = {
    'the-times': {
        'scraper': TheTimesScraper, 'p_from': '16/10/2000', 'p_to': '31/10/2020'
    },
    'telegraph': {
        'scraper': TelegraphScraper, 'p_from': '26/11/2001', 'p_to': '31/10/2020'
    }
}


def _iterate_scraper_and_write(output_dir, publisher, scraper):
    output_dir = os.path.expanduser(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, publisher)
    with open(output_path, 'w') as f:
        for entry in scraper.scrape():
            f.write(json.dumps(entry))
            f.write('\n')
            f.flush()


def scrape(publisher, p_from, p_to, output_dir, page):
    scraper = publisher_data[publisher]['scraper'](p_from=p_from, p_to=p_to, page=page)
    publisher = f'{publisher}-{p_from.replace("/", "-")}-{p_to.replace("/", "-")}-{page}.jsonl'
    _iterate_scraper_and_write(output_dir, publisher, scraper)


def scrape_telegraph_single_date(output_dir, day=0, month=0, year=0, page=0):
    scraper = SingleDayTelegraphScraper(day=day, month=month, year=year, page=page)
    name = f'telegraph-{day}-{month}-{year}-{page}.jsonl'
    _iterate_scraper_and_write(output_dir, name, scraper)


def main(publisher):
    p_from = publisher_data[publisher]['p_from']
    p_to = publisher_data[publisher]['p_to']
    output_dir = '../../data'

    setup_loggers(p_from, p_to, publisher, output_dir)

    scrape(
        publisher=publisher,
        p_from=p_from,
        p_to=p_to,
        output_dir=output_dir,
        page=None,
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--publisher", choices=["telegraph", "the-times", "all"], default="all")
    args = parser.parse_args()
    publisher = args.publisher
    if publisher == 'all':
        for publisher in publisher_data:
            main(publisher)
    else:
        main(publisher)
