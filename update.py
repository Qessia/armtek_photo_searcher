import pandas as pd
import json


with open('update_config.json', encoding='utf-8') as f:
    data = json.load(f)


SOURCE = data['Source']
BLANK = data['Blank']
ON_COL = data['On_column']
UPDATE_COL = data['Update_column']
NEW = 'test.csv'


def main():
    df = pd.read_csv(BLANK, sep=';', encoding='utf-8', low_memory=False)
    src = pd.read_csv(SOURCE, sep=';', encoding='utf-8', low_memory=False)

    print(f'blank len: {len(df)}\nsource len: {len(src)}')

    merged_df = pd.merge(df, src[[ON_COL, UPDATE_COL]], on=ON_COL, how='left')
    merged_df = merged_df.drop_duplicates()

    duplicates = merged_df.duplicated(subset=merged_df.columns[:-1])
    merged_df = merged_df[~duplicates]

    print(f'new len: {len(merged_df)}')

    merged_df.to_csv(NEW, sep=';', encoding='cp1251', index=False)


if __name__ == '__main__':
    main()
