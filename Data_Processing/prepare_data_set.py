from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from enum import Enum, auto
from poetry_processing import PROCESSED_DATA_PATH_PICKLE, DATA_PATH
AUTHORS_PROCESSED_PATH = DATA_PATH / "authors_processed" / "authors.csv"
COMBINED_DATA_PATH = DATA_PATH / "data_set.csv"
COMBINED_DATA_PATH_PICKLE = DATA_PATH / "data_set.pkl.gz"

POETRY_COLUMNS = ['title', 'authors', 'translators', 'original_language', 'content', 'content_sep']
DATA_SET_COLUMNS = ['content', 'sex', 'hebrew_speaker', 'birth_period', 'death_period', 'birth_place_israel',
                    'death_place_israel']
ISRAELI_PLACES = {"Tel Aviv", "Jaffa", "Jerusalem", "Haifa", "Nahalal", "Acre", "Ramat Gan", "Givat Hashlosha",
                  "Rishon LeZion", "Petah Tikva", "Zikhron Ya'akov",
                  "Israel", "Mandatory Palestine"}  # This list was compiled manually


class TimePeriods(Enum):
    ancient = auto()
    medieval = auto()
    renaissance = auto()
    enlightenment = auto()
    revival = auto()
    modern = auto()


SEX = {"male": 0,
       "female": 1}
TIME_PERIODS_RANGES = {TimePeriods.ancient: range(-2000, 900),
                       TimePeriods.medieval: range(900, 1400),
                       TimePeriods.renaissance: range(1400, 1700),
                       TimePeriods.enlightenment: range(1700, 1880),
                       TimePeriods.revival: range(1880, 1948),
                       TimePeriods.modern: range(1948, 2030)}


def get_period(date):
    if date is not np.nan:
        year = np.datetime64(date, 'Y').astype('int') + 1970
        for period in TIME_PERIODS_RANGES:
            if year in TIME_PERIODS_RANGES[period]:
                return period
    return date


if __name__ == "__main__":
    poetry_df = pd.read_pickle(PROCESSED_DATA_PATH_PICKLE)[POETRY_COLUMNS].rename(columns={'authors': 'author'})
    authors_df = pd.read_csv(AUTHORS_PROCESSED_PATH).rename(columns={'name': 'author'})
    # additional columns for authors
    authors_df['birth_period'] = authors_df.d_birth.apply(get_period)
    authors_df['death_period'] = authors_df.d_death.apply(get_period)
    authors_df['birth_place_israel'] = authors_df.p_birth.apply(lambda x: x in ISRAELI_PLACES)
    authors_df['death_place_israel'] = authors_df.p_death.apply(lambda x: x in ISRAELI_PLACES)
    # combine authors data with poetry data
    combined_df = poetry_df.merge(authors_df, how='left', on='author')
    combined_df.to_pickle(COMBINED_DATA_PATH_PICKLE, compression='gzip')

    # remove Nan data:
    combined_df.dropna(subset=['birth_period', 'death_period'], inplace=True)

    # make label integers only
    combined_df.sex = combined_df.sex.map(SEX)
    combined_df.birth_period = combined_df.birth_period.apply(lambda x: x.value)
    combined_df.death_period = combined_df.death_period.apply(lambda x: x.value)
    combined_df.birth_place_israel = combined_df.birth_place_israel.apply(lambda x: 1 if x else 0)
    combined_df.death_place_israel = combined_df.death_place_israel.apply(lambda x: 1 if x else 0)
    combined_df.hebrew_speaker = combined_df.hebrew_speaker.apply(lambda x: 1 if x else 0)
    # save all data
    combined_df.to_csv(COMBINED_DATA_PATH, index=False, columns=DATA_SET_COLUMNS)
    # split data set to train,test, validation
    np.random.seed(34)
    train, test = train_test_split(combined_df, test_size=0.3)
    validation, test = train_test_split(test, train_size=0.5)
    train.to_csv(DATA_PATH / "train.csv")
    test.to_csv(DATA_PATH / "test.csv")
    validation.to_csv(DATA_PATH / "validation.csv")


