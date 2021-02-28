import math
import datetime

import numpy as np
import pandas as pd

from cryptonite.preprocessing.common import save_df_as_jsonl


def split_randomly(df, val_ratio, test_ratio, seed):

    val_df = df.sample(frac=val_ratio, random_state=seed)
    df = df.drop(val_df.index)

    test_df = df.sample(frac=test_ratio, random_state=seed)
    df = df.drop(test_df.index)

    train_df = df

    return train_df, val_df, test_df


def split_by_answer(df, val_ratio, test_ratio, seed):

    np.random.seed(seed)

    answers = df['answer'].unique()
    answer_counts = df['answer'].value_counts()

    val_answers = set()
    val_size = 0
    expected_val_size = math.ceil(len(df) * val_ratio)

    while val_size < expected_val_size:

        val_answer = np.random.choice(answers)
        if val_answer in val_answers:
            continue

        val_answers.add(val_answer)
        val_size += answer_counts[val_answer]

    val_df = df[df['answer'].isin(val_answers)]

    test_answers = set()
    test_size = 0
    expected_test_size = math.ceil(len(df) * test_ratio)

    while test_size < expected_test_size:

        test_answer = np.random.choice(answers)
        if test_answer in test_answers or test_answer in val_answers:
            continue

        test_answers.add(test_answer)
        test_size += answer_counts[test_answer]

    test_df = df[df['answer'].isin(test_answers)]

    train_df = df[df['answer'].apply(lambda a: a not in val_answers and a not in test_answers)]

    return train_df, val_df, test_df


def create_splits(dataset_path, split_name, n_versions=3, seed=1407):

    split_func = split_mapping[split_name]

    df = pd.read_json(dataset_path, orient='columns', lines=True)
    for i in range(n_versions):
        seed = seed + i
        train_df, val_df, test_df = split_func(df, val_ratio=0.05, test_ratio=0.05, seed=seed)

        version = chr(ord('@') + i + 1)
        save_split(split_name, train_df, val_df, test_df, version)


def _get_non_quick_df(df):
    first_day_of_times_quick_cryptic = datetime.datetime.strptime("10/03/2014", "%d/%m/%Y")
    # we also don't include the Sunday Times as it has no quick cryptic and it starts before the
    # introduction of the times quick cryptic
    non_quick_df = df[(~df['quick']) &
                      (df['publisher'] == "Times") & (df['sub_publisher'] != "The Sunday Times") &
                      (df['date'] >= first_day_of_times_quick_cryptic)]
    return non_quick_df


def create_to_non_quick_splits(dataset_path, n_val_versions=3, val_ratio=0.05, test_ratio=0.05,
                               seed=1407):

    df = pd.read_json(dataset_path, orient='columns', lines=True)

    non_quick_df = _get_non_quick_df(df)
    quick_df = df[df['quick']]

    np.random.seed(seed)

    for i in range(n_val_versions):
        version = chr(ord('@') + i + 1)

        non_quick_to_non_quick_train, x_to_non_quick_val, x_to_non_quick_test = split_by_answer(non_quick_df, val_ratio, test_ratio, seed+i)

        # Do not yet save the non-quick to non-quick train.
        # As there are less quick clues then non-quick clues, and we are trying to compare learning
        # non-quick clues from non-quick clues to learning non-quick clues from quick clues, we
        # need the train sets to be of the same size. In later lines we will also create a quick to
        # non-quick train set from the quick clues, and then sample down from the non-quick train
        # to match the size of the quick train set

        # the val and test sets are shared between and non-quick to non-quick and quick to non-quick
        for part, part_df in (('val', x_to_non_quick_val), ('test', x_to_non_quick_test)):
            save_df_as_jsonl(part_df, f'data/x_to_non-quick_split_{version}_{part}.jsonl')

        # create a quick train set with no answer overlap between it and the non-quick val and test sets
        non_quick_val_answers = x_to_non_quick_val['answer'].unique()
        non_quick_test_answers = x_to_non_quick_test['answer'].unique()
        non_quick_val_and_test_answers = set(non_quick_val_answers) | set(non_quick_test_answers)

        quick_to_non_quick_train_df = quick_df[~quick_df['answer'].isin(non_quick_val_and_test_answers)]
        save_df_as_jsonl(quick_to_non_quick_train_df, f'data/quick_to_non-quick_split_{version}_train.jsonl')

        # sample down the non-quick train set to match the size of the quick train set
        non_quick_to_non_quick_train = non_quick_to_non_quick_train.sample(n=len(quick_to_non_quick_train_df), random_state=seed+i)
        # finally, save the non-quick to non-quick train set
        save_df_as_jsonl(non_quick_to_non_quick_train, f'data/non-quick_to_non-quick_split_{version}_train.jsonl')


def create_to_quick_splits(dataset_path, n_val_versions=3, val_ratio=0.05, test_ratio=0.05,
                           seed=1407):

    df = pd.read_json(dataset_path, orient='columns', lines=True)

    quick_df = df[df['quick']]
    non_quick_df = _get_non_quick_df(df)
    non_quick_answer_counts = non_quick_df['answer'].value_counts()
    all_non_quick_answers = non_quick_df['answer'].unique()

    np.random.seed(seed)

    for i in range(n_val_versions):

        quick_to_quick_train, x_to_quick_val, x_to_quick_test = split_by_answer(quick_df, val_ratio, test_ratio, seed+i)
        version = chr(ord('@') + i + 1)

        save_df_as_jsonl(quick_to_quick_train, f'data/quick_to_quick_split_{version}_train.jsonl')

        # the val and test sets are shared between quick_to_quick and non-quick_to_quick
        for part, part_df in (('val', x_to_quick_val), ('test', x_to_quick_test)):
            save_df_as_jsonl(part_df, f'data/x_to_quick_split_{version}_{part}.jsonl')

        # create a non-quick training set whose size is equal to the quick training set, and there
        # is no answer overlap between it and the quick val and test sets
        quick_val_answers = x_to_quick_val['answer'].unique()
        quick_test_answers = x_to_quick_test['answer'].unique()
        quick_val_and_test_answers = set(quick_val_answers) | set(quick_test_answers)

        non_quick_answer_pool = set(all_non_quick_answers) - quick_val_and_test_answers
        non_quick_answer_pool = np.array(list(non_quick_answer_pool), dtype=object)
        chosen_non_quick_train_answers = set()

        quick_train_size = len(quick_to_quick_train)
        non_quick_train_size = 0

        while non_quick_train_size < quick_train_size:
            non_quick_train_answer = np.random.choice(non_quick_answer_pool)
            if non_quick_train_answer not in chosen_non_quick_train_answers:
                chosen_non_quick_train_answers.add(non_quick_train_answer)
                non_quick_train_size += non_quick_answer_counts[non_quick_train_answer]

        non_quick_to_quick_train_df = non_quick_df[non_quick_df['answer'].isin(chosen_non_quick_train_answers)]

        save_df_as_jsonl(non_quick_to_quick_train_df, f'data/non-quick_to_quick_split_{version}_train.jsonl')


def create_publisher_answer_splits(dataset_path, n_versions_per_publisher=3,
                                   val_ratio=0.05, test_ratio=0.05, seed=1407):

    df = pd.read_json(dataset_path, orient='columns', lines=True)

    # get a list of all the different publishers in the dataset
    publishers = df['publisher'].unique()

    publisher_dfs = dict()

    for publisher in publishers:
        publisher_dfs[publisher] = df[df['publisher'] == publisher]

    # publishers don't have the same number of clues, and we want to make a fair comparison.
    # therefore we set the number of clues in each publisher to the number of clues in the smallest
    # publisher
    min_publisher_size = min([len(df) for df in publisher_dfs.values()])

    for publisher in publishers:
        publisher_dfs[publisher] = publisher_dfs[publisher].sample(n=min_publisher_size, random_state=seed)
        split_name = f"{publisher}_answer_split".lower()

        for i in range(n_versions_per_publisher):
            train_df, val_df, test_df = split_by_answer(publisher_dfs[publisher], val_ratio, test_ratio, seed+i)
            version = chr(ord('@') + i + 1)
            save_split(split_name, train_df, val_df, test_df, version)


def save_split(name, train_df, val_df, test_df, version=""):

    if version != '':
        version = f"{version}_"

    for part, part_df in (('train', train_df), ('val', val_df), ('test', test_df)):
        save_df_as_jsonl(part_df, f'data/{name}_{version}{part}.jsonl')


split_mapping = {
    'random_split': split_randomly,
    'answer_split': split_by_answer
}


if __name__ == '__main__':
    pass
