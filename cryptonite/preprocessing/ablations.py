import pandas as pd

from cryptonite.preprocessing.common import save_df_as_jsonl


def add_enumeration(row):
    clue = row['clue']
    enumeration = row['enumeration']
    return f"{clue} {enumeration}"


def create_enumerated_clues(split_name, split_version=''):

    train, val, test = load_split(split_name, split_version)
    for part in (train, val, test):
        part['clue'] = part.apply(lambda row: add_enumeration(row), axis=1)

    save_ablation_split('enumerated', split_name, train, val, test, split_version)


def load_split(name, version=''):

    parts = ['train', 'val', 'test']
    if version != '':
        version = f"{version}_"
    train, val, test = [pd.read_json(f'data/{name}_{version}{part}.jsonl',
                                     orient='columns', lines=True)
                        for part in parts]
    return train, val, test


def save_ablation_split(ablation_name, split_name, train, val, test, version=''):

    if version != "":
        version = f"{version}_"

    for part, part_df in (('train', train), ('val', val), ('test', test)):
        save_df_as_jsonl(part_df, f'data/{split_name}_{version}{ablation_name}_{part}.jsonl')


if __name__ == '__main__':
    pass
