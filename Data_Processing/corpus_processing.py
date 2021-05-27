"""
This script need to take the data from https://github.com/projectbenyehuda/public_domain_dump
and process it for our project.
"""

import pandas as pd
import re
from pathlib import Path
from hebtokenizer import HebTokenizer

DATA_PATH = Path(__file__).parent.parent / Path("Data")
RAW_DATA_PATH = DATA_PATH / Path("public_domain_dump-master")
PROCESSED_DATA_PATH = DATA_PATH / Path("poetry.csv")
PROCESSED_DATA_PATH_PICKLE = DATA_PATH / Path("poetry.pkl.gz")
CATALOG_DATA_PATH = RAW_DATA_PATH / Path("pseudocatalogue.csv")
STRIPPED_TEXT_DATA_PATH = RAW_DATA_PATH / Path("txt_stripped")
REPORT_PROGRESS = 20
LAST_LINE_PREFIX = "את הטקסט לעיל הפיקו מתנדבי פרויקט בן־יהודה באינטרנט.  הוא זמין תמיד בכתובת הבאה"

STOP_POINTS_REGEX = re.compile(r'[!|.|?]')
ONLY_WORDS_AND_DIGITS_REGEX = re.compile(r'[\w\dא-ת]+')


def get_only_words_and_digits(text: str):
    return ONLY_WORDS_AND_DIGITS_REGEX.findall(text)


def invert_words(words: list):
    return [w[::-1] for w in words]


def remove_punct(text):
    punct_pat = re.compile(r'-–,.:;\'’"\)\(?]+')
    return re.sub(punct_pat, " ", text)


def remove_last_line_from_string(s):
    s = s.split(LAST_LINE_PREFIX)
    return s[0]


def remove_author_title(s, author, title):
    s = s.replace(title, "", 1)
    return s.replace(author, "")


def normalize_text(s):
    # removing Niqqud
    s = re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', s)
    return s.strip()


def split_text_to_sentences(text: str) -> list:
    tokenizer = HebTokenizer()
    tokens = [word for (part, word) in tokenizer.tokenize(text)]
    sentences = []
    # Finding next sentence break.
    while(True):
        stop_points = [h for h in [i for i, e in enumerate(tokens) if STOP_POINTS_REGEX.match(e)]]
        if len(stop_points) > 0:
            stop_point = min(stop_points)
            # Keep several sentence breaker as 1 word, like "...." or "???!!!"
            while True:
                stop_points.remove(stop_point)
                if len(stop_points) > 1 and min(stop_points) == (stop_point + 1):
                    stop_point = stop_point + 1
                else:
                    break

            sentences.append(" ".join(tokens[:stop_point + 1]))
            tokens = tokens[stop_point + 1:]
        else:
            break
    if len(stop_points) > 0:
        sentences.append(" ".join(tokens))
    return sentences


if __name__ == '__main__':
    catalog_df = pd.read_csv(CATALOG_DATA_PATH)
    catalog_df = catalog_df[catalog_df.genre == "שירה"]
    catalog_df.reset_index(inplace=True)

    content = []
    content_sep = []
    print("starting to process data")
    for index, row in catalog_df.iterrows():
        if index % REPORT_PROGRESS == 0:
            print("{:.2%}".format(index / catalog_df.shape[0]))
        path = row.path
        title = normalize_text(row.title)
        author = row.authors
        path = str(STRIPPED_TEXT_DATA_PATH) + str(Path(path + ".txt"))
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
            text = remove_last_line_from_string(text)
            text = remove_author_title(text, author, title)
            text = text.replace('\n', ' ').replace('\r', ' ').replace(r'\s\s+', ' ') # removing newlines and unneeded space
            content.append(text)
            text = split_text_to_sentences(text)
            content_sep.append(text)
    print("100.00% - finish processing")

    catalog_df["content"] = content
    catalog_df.to_csv(PROCESSED_DATA_PATH, index=False)
    catalog_df["content_sep"] = content_sep
    catalog_df.to_pickle(PROCESSED_DATA_PATH_PICKLE, compression='gzip')
