"""
This script only purpose is to fix dates in the authors data and make them at an uniform format.
"""
from dateutil import parser
import pandas as pd
import numpy as np
from pathlib import Path
from poetry_processing import DATA_PATH

authors_manually_processed_path = DATA_PATH / "authors_processed/authors.csv"


def fix_date(date):
    if date is np.nan:
        return date
    elif date.startswith('-'):
        return np.datetime64(date)
    else:
        try:
            return np.datetime64(parser.parse(date).date())
        except parser.ParserError as e:
            date_s = date.split('/')
            if len(date.split('/')) == 3:
                return np.datetime64('-'.join(date_s[::-1]))
            else:
                raise e


if __name__ == "__main__":
    authors_df = pd.read_csv(authors_manually_processed_path, encoding="utf-8")
    authors_df["d_birth"] = authors_df["d_birth"].apply(fix_date)
    authors_df["d_death"] = authors_df["d_death"].apply(fix_date)
    authors_df.to_csv(authors_manually_processed_path, index=False)