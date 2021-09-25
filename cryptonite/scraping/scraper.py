from pathlib import Path
import argparse
import json
import os

from cryptonite.defaults import V1_CONFIGURATION_PATH, DATA_DIR
from cryptonite.scraping.loggers import setup_loggers
from cryptonite.scraping.telegraph.scraper import Scraper as TelegraphScraper
from cryptonite.scraping.the_times.scraper import Scraper as TheTimesScraper


publisher_to_scraper = {
    'the_times': TheTimesScraper,
    'the_telegraph': TelegraphScraper
}

publisher_to_authentication = {
    'the_times': {"acs_tnl", "sacs_tnl", "remember_puzzleclub_key", "remember_puzzleclub_value"},
    'the_telegraph': {"details", "rememberme"}
}


def _iterate_scraper_and_write(output_dir, filename, scraper):
    output_dir = os.path.expanduser(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    with open(output_path, 'w') as f:
        for entry in scraper.scrape():
            f.write(json.dumps(entry))
            f.write('\n')
            f.flush()


def scrape(publisher, start_date, end_date, output_dir, authentication):
    scraper = publisher_to_scraper[publisher](start_date=start_date, end_date=end_date,
                                              authentication=authentication)
    filename = f'{publisher}-{start_date.replace("/", "-")}-{end_date.replace("/", "-")}.jsonl'
    _iterate_scraper_and_write(output_dir, filename, scraper)


def _load_configuration(path):
    # if no config is given, use the original cryptonite config (v1)
    if path is None:
        path = V1_CONFIGURATION_PATH
        print(f"No config file given. Defaulting to the original Cryptonite configuration (v1) at {path}.")
        if not path.is_file():
            raise FileNotFoundError(f"Original Cryptonite configuration not found at {path}. Aborting.")

    # load config file
    print(f"reading configuration from {path}")
    with open(path) as f:
        config = json.load(f)

    # deal with missing data sources
    if not config.get("data_sources"):
        raise KeyError("No data sources were listed in the config."
                       "Does your config contain a top-level `data_sources` field?")

    # deal with missing publishers
    for i, data_source in enumerate(config["data_sources"]):
        if not data_source.get("publisher"):
            raise KeyError(f"Data source #{i} is missing a publisher field.")
        publisher = data_source["publisher"]
        if publisher not in publisher_to_scraper.keys():
            raise ValueError(f'Invalid publisher for data source #{i}: {publisher}. '
                             f'Value should be either "the_times" or "the_telegraph".')

    # deal with missing authentication
    for data_source in config["data_sources"]:
        publisher = data_source["publisher"]
        authentication = data_source.get("authentication")
        if not authentication:
            raise KeyError(f'publisher "{publisher}" is missing an authentication field. '
                           f'Refer to the README for more details.')

        supplied_auth_fields = authentication.keys()
        expected_auth_fields = publisher_to_authentication[publisher]

        missing_keys = expected_auth_fields - supplied_auth_fields
        if len(missing_keys) > 0:
            raise ValueError(f'Publisher {publisher} is missing the following authentication keys {missing_keys}. '
                             f'Refer to the README for more details.')

    # deal with a missing output dir
    if not config.get("output_dir"):
        print(f"No output dir given. Defaulting to {DATA_DIR}")
        config["output_dir"] = DATA_DIR

    return config


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    args = parser.parse_args()

    config = _load_configuration(args.config)
    output_dir = Path(config["output_dir"]).resolve()

    print("Make sure you don't get disconnected from the Internet. The current scraper is rather gentle =)\n")
    # scrape each data source
    for data_source in config["data_sources"]:
        publisher = data_source["publisher"]
        start_date = data_source["start_date"]
        end_date = data_source["end_date"]
        authentication = data_source["authentication"]

        setup_loggers(start_date, end_date, publisher, output_dir)

        print(f"Starting to collect crosswords from {publisher}.")
        print(f"Output dir: {output_dir}\n")

        scrape(
            publisher=publisher,
            start_date=start_date,
            end_date=end_date,
            output_dir=output_dir,
            authentication=authentication,
        )
        print(f"Finished getting crosswords from {publisher}. See the log at {output_dir} for details.")


if __name__ == '__main__':
    main()
