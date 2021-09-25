import pandas as pd

from cryptonite.preprocessing.common import save_df_as_jsonl


def dedup_same_clue_same_answer(df):
    """ For the reasoning behind this implementation, see the `remove_duplicates` notebook
    """
    df = df.sort_values(by=['date', 'publisher'], axis='index')
    num_entries_before_dedup = len(df)
    print(f"# entries before removing (clue, answer) duplicates: {num_entries_before_dedup}")
    df = df.drop_duplicates(subset=['clue', 'answer'], keep='first')
    print(f"# entries after removing (clue, answer) duplicates:  {len(df)}")
    print(f"# duplicate (clue, answer) entries removed:          {num_entries_before_dedup - len(df)}")

    return df


def dedup_same_clue_different_answer(df):
    """ For the reasoning behind this implementation, see the `remove_duplicates` notebook
    """
    num_entries_before_dedup = len(df)
    print(f"# entries before removing all identical clues with different answers: {num_entries_before_dedup}")
    df = df[~df.duplicated('clue', keep=False)]
    print(f"# entries after removing all identical clues with different answers:  {len(df)}")
    print(f"# identical clues with different answers:                             {num_entries_before_dedup - len(df)}")

    return df


def add_enumeration_to_clue(row):
    clue = row['clue']
    enumeration = row['enumeration']
    return f"{clue} {enumeration}"


def preprocess(publisher_dfs, output_path, add_enumeration=True):

    df = pd.concat(publisher_dfs, axis='index', ignore_index=True)

    df = dedup_same_clue_same_answer(df)
    df = dedup_same_clue_different_answer(df)

    # add enumeration
    if add_enumeration:
        df['clue'] = df.apply(lambda row: add_enumeration_to_clue(row), axis=1)

    save_df_as_jsonl(df, output_path)
    print(f'successfully created {output_path}')

    return df
