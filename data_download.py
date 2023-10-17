import requests
from bs4 import BeautifulSoup
import json
import html_to_json
from tqdm import tqdm
import pandas as pd

BASE_URL = "https://www.formula1.com"
YEARS = range(1950, 2024)

def get_race_urls_by_year(year):
    response = requests.get(BASE_URL + "/en/results.html/" + str(year) + "/races.html")
    soup = BeautifulSoup(response.text, 'html.parser')

    js = soup.find_all("table", class_="resultsarchive-table")
    return [{"name":race.text.replace("\n","").replace("  ",""), "href":race["href"]} for race in js[0].find_all("a")]


def get_results(url):

    url = BASE_URL + url

    payload = {}
    headers = {
      'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Accept-Encoding': 'gzip, deflate, br',
      'Connection': 'keep-alive',
      'Cookie': 'consentUUID=d9bed607-161e-4ce3-acaa-0fc4202db0fe_24; consentDate=2023-10-17T04:22:20.943Z',
      'Upgrade-Insecure-Requests': '1',
      'Sec-Fetch-Dest': 'document',
      'Sec-Fetch-Mode': 'navigate',
      'Sec-Fetch-Site': 'none',
      'Sec-Fetch-User': '?1'
    }
    
    response = requests.request("GET", url, headers=headers, data=payload)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    js = soup.find_all("table", class_="resultsarchive-table")

    return html_to_json.convert_tables(str(js))[0]

def get_all_results():
    driver_results = []
    for year in tqdm(YEARS):
        
        urls = get_race_urls_by_year(year)
        for url in urls:
            results = get_results(url["href"])
    
            for result in results:
                driver_results.append({
                    "driver_name":  result["Driver"].replace("\n", " "),
                    "pos": result["Pos"],
                    "car": result["Car"],
                    "points": result["PTS"],
                    "laps": result["Laps"],
                    "retired": result["Time/Retired"] == "DNF",
                    "time-retired": result["Time/Retired"],
                    "race": url["name"],
                    "year": year
                })

    df = pd.DataFrame.from_records(driver_results)

    return df

if __name__ == "__main__":
    
    df = get_all_results()
    df.to_csv("data/results.csv")