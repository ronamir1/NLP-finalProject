# %%

import pandas as pd
import numpy as np
import re
import unicodedata


ONLY_WORDS_AND_DIGITS_REGEX = re.compile(r'[\w\dא-ת]+')


def get_only_words_and_digits(text: str):
    return ONLY_WORDS_AND_DIGITS_REGEX.findall(text)


def invert_words(words: list):
    return [w[::-1] for w in words]


def remove_punct(text):
    punct_pat = re.compile(r'-–,.:;\'’"\)\(?]+')
    return re.sub(punct_pat, " ", text)


def remove_last_line_from_string(s):
    s = s.split("את הטקסט לעיל הפיקו מתנדבי פרויקט בן־יהודה באינטרנט.  הוא זמין תמיד בכתובת הבאה")
    return s[0]


def remove_author_title(s, author, title):
    s = s.replace(title, "", 1)
    return s.replace(author, "")

def normalize_text(s):
    s = re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', s)
    return s.strip()


if __name__ == '__main__':

    catalog_df = pd.read_csv("public_domain_dump-master/pseudocatalogue.csv")
    catalog_df = catalog_df[catalog_df["genre"] == "שירה"]

    content = []
    for index, row in catalog_df.iterrows():
        print(index / catalog_df.shape[0])
        path = row["path"]
        title = normalize_text(row["title"])
        author = row["authors"]
        path = "public_domain_dump-master/txt_stripped" + path + ".txt"
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
            text = remove_last_line_from_string(text)
            text = remove_author_title(text, author, title)
            text = get_only_words_and_digits(text)
            content.append(text)

    catalog_df["content"] = content
    catalog_df.to_csv("poetry.csv")
