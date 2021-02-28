import os

import pandas as pd

from cryptonite.preprocessing.common import default_dtypes, save_df_as_jsonl


def merge_publisher_specific_preprocessed_data(per_publisher_preprocessed_data_dir,
                                               output_path=None):

    preprocessed_paths = [entry.path for entry in os.scandir(per_publisher_preprocessed_data_dir)
                          if entry.name.endswith('_preprocessed.jsonl')]

    dfs_to_merge = [pd.read_json(p, orient='columns', dtype=default_dtypes,
                                 lines=True)
                    for p in preprocessed_paths]

    df = pd.concat(dfs_to_merge, axis='index', ignore_index=True)

    if output_path is not None:
        save_df_as_jsonl(df, output_path)

    return df


def dedup_same_clue_same_answer(df):

    df = df.sort_values(by=['date', 'publisher'], axis='index')
    num_entries_before_dedup = len(df)
    print(f"# entries before removing (clue, answer) duplicates: {num_entries_before_dedup}")
    df = df.drop_duplicates(subset=['clue', 'answer'], keep='first')
    print(f"# entries after removing (clue, answer) duplicates:  {len(df)}")
    print(f"# duplicate (clue, answer) entries removed:          {num_entries_before_dedup - len(df)}")

    return df


def dedup_same_clue_different_answer(df):

    num_entries_before_dedup = len(df)
    print(f"# entries before removing all identical clues with different answers: {num_entries_before_dedup}")
    df = df[~df.duplicated('clue', keep=False)]
    print(f"# entries after removing all identical clues with different answers:  {len(df)}")
    print(f"# identical clues with different answers:                             {num_entries_before_dedup - len(df)}")

    return df


def preprocess(per_publisher_preprocessed_data_dir='../data/', output_path='../data/dataset.jsonl'):

    df = merge_publisher_specific_preprocessed_data(
        per_publisher_preprocessed_data_dir,
        output_path='../data/merged_per_publisher_preprocessing.jsonl')

    df = dedup_same_clue_same_answer(df)
    df = dedup_same_clue_different_answer(df)

    save_df_as_jsonl(df, output_path)
    print(f'successfully saved as {output_path}')


if __name__ == '__main__':
    preprocess()
