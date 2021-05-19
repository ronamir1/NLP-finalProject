import requests
import pandas as pd
from pathlib import Path
import json
from constants import YAP_TOKEN


if __name__ == "__main__":
    # from https://benyehuda.org/read/24331
    text = "פה יושב אנכי, ושם יושב הצל."
    text= text.replace(r'"', r'\"')
    url = f'https://www.langndata.com/api/heb_parser?token={YAP_TOKEN}'
    _json='{"data":"'+text+'"}'
    r = requests.post(url,  data=_json.encode('utf-8'), headers={'Content-type': 'application/json; charset=utf-8'})
    with open("Data/yap_test.json", 'w') as file:
        json.dump(r.json(), file, ensure_ascii=False, indent='\t')