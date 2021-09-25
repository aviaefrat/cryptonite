import argparse

from cryptonite.defaults import (DATA_DIR, SCRAPED_TELEGRAPH_PATH, SCRAPED_TIMES_PATH,
                                 DATASET_PATH, DATASET_WITHOUT_ENUMERATION_PATH)
from cryptonite.preprocessing.dataset import preprocess as preprocess_dataset
from cryptonite.preprocessing.telegraph import preprocess as preprocess_telegraph
from cryptonite.preprocessing.the_times import preprocess as preprocess_the_times
from cryptonite.preprocessing.splits import create_splits


def preprocess(the_telegraph_scraping_path=SCRAPED_TELEGRAPH_PATH,
               the_times_scraping_path=SCRAPED_TIMES_PATH,
               create_non_enumerated_dataset=False, create_random_split=False,
               n_versions=1):

    preprocessed_telegraph = preprocess_telegraph(the_telegraph_scraping_path)
    preprocessed_the_times = preprocess_the_times(the_times_scraping_path)

    publisher_dfs = [preprocessed_telegraph, preprocessed_the_times]
    dataset_dfs = {}

    # create the enumerated dataset
    preprocessed_dataset = preprocess_dataset(
        publisher_dfs=publisher_dfs, output_path=DATASET_PATH
    )
    dataset_dfs["default"] = preprocessed_dataset

    # create the non-enumerated dataset
    if create_non_enumerated_dataset:
        preprocessed_non_enumerated_dataset = preprocess_dataset(
            publisher_dfs=publisher_dfs, output_path=DATASET_WITHOUT_ENUMERATION_PATH
        )
        dataset_dfs["non_enumerated"] = preprocessed_non_enumerated_dataset

    # create answer split
    for modifier, df in dataset_dfs.items():
        if modifier == "default":
            enumeration_modifier = ''
        else:
            enumeration_modifier = modifier

        create_splits(df, split_name="answer_split", output_dir=DATA_DIR,
                      enumeration_modifier=enumeration_modifier, n_versions=n_versions)

    # create random split
    if create_random_split:
        create_splits(preprocessed_dataset, split_name="random_split", output_dir=DATA_DIR,
                      enumeration_modifier='', n_versions=n_versions)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--telegraph-data", default=SCRAPED_TELEGRAPH_PATH)
    parser.add_argument("--times-data", default=SCRAPED_TIMES_PATH)
    parser.add_argument("--create-non-enumerated", action='store_true')
    parser.add_argument("--create-random-split", action='store_true')
    parser.add_argument("--n-split-instances", default=1, type=int)
    args = parser.parse_args()

    preprocess(
        the_telegraph_scraping_path=args.telegraph_data,
        the_times_scraping_path=args.times_data,
        create_non_enumerated_dataset=args.create_non_enumerated,
        create_random_split=args.create_random_split,
        n_versions=args.n_split_instances
    )
