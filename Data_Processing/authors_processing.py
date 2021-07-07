import sys
import pandas as pd
from pathlib import Path
import pywikibot
import requests
from bs4 import BeautifulSoup
import datetime
from poetry_processing import PROCESSED_DATA_PATH, DATA_PATH

AUTHORS_PROCESSED_PATH = DATA_PATH / Path("authors_processed/authors.csv")


def parse_place(place: str):
    place = place.replace("\n", "$")
    place = place.split("$$$$$$$$$$$$$$$$")[1]
    return place.split("$$$$$$$$$")[0]


def parse_date(date: str):
    date = date.replace("\n", "$")
    date = date.split("$$$$$$$$$$$$$$$$")[1]
    date = date.split("$$$$$$$$$")[0]
    date = date.split("Gregorian")[0]

    if len(date) == 4:
        return datetime.datetime.strptime(date, '%Y')
    return datetime.datetime.strptime(date, '%d %B %Y')


def parse_writer(writer: str, id: int):
    site = pywikibot.Site("he", "wikipedia")
    page = pywikibot.Page(site, writer)
    try:
        item = pywikibot.ItemPage.fromPage(page)
        page_id = item.id
        URL = f"https://www.wikidata.org/wiki/{page_id}"
    except:

        URL = f"https://he.wikipedia.org/?curid={page.pageid}"
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, 'html')
        URL = soup.find('a', {'title' : 'קישור לפריט המשויך במאגר הנתונים [g]'})['href']


    response = requests.get(URL)
    print(response, writer)

    soup = BeautifulSoup(response.text, 'html')


    try:
        sex = soup.find('a', {'title' : 'Q6581097'}).string
    except:
        sex = "female"


    place_of_birth = soup.find("div", {"id": "P19"}).text
    try:
        place_of_birth = parse_place(place_of_birth)
    except:
        print("p birth - ", sys.exc_info())

    place_of_death = soup.find("div", {"id": "P20"}).text
    try:
        place_of_death = parse_place(place_of_death)
    except:
        print("p death - ", sys.exc_info())


    date_of_birth = soup.find("div", {"id": "P569"}).text
    try:
        date_of_birth = parse_date(date_of_birth)
    except:
        print("d birth - ", sys.exc_info())

    date_of_death = soup.find("div", {"id": "P570"}).text
    try:
        date_of_death = parse_date(date_of_death)
    except:
        print("d death - ", sys.exc_info())

    return [id, writer, sex, place_of_birth, place_of_death, date_of_birth, date_of_death]


if __name__ == "__main__":
    songs_df = pd.read_csv(PROCESSED_DATA_PATH, encoding="utf-8")
    writers = songs_df["authors"].unique()
    authors_df = pd.DataFrame(columns=["id", "name", "sex", "p_birth", "p_death", "d_birth", "d_death"], )
    for i, writer in enumerate(writers):
        try:
            authors_df.loc[i] = parse_writer(writer, i)
        except Exception:
            authors_df.loc[i] = [i, writer, None, None, None, None, None]
            print(sys.exc_info())
            print("couldn't complete for", writer, i)
    print(authors_df.head())
    authors_df.to_csv(AUTHORS_PROCESSED_PATH, index=False)
