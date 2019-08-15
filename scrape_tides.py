__author__="Jared Rohe"

'''
File: scrape_tides.py

Usage:

python scrape_tides.py

'''


import requests
from bs4 import BeautifulSoup

LOCATIONS = ("Half-Moon-Bay-California","Huntington-Beach","Providence-Rhode-Island","Wrightsville-Beach-North-Carolina")
URL = "https://www.tide-forecast.com/locations/{}/tides/latest"


def scrape_tide_data():
    for location in LOCATIONS:
        print(f"--- {location} Daylight Tides---")
        for tide_data in get_tides_for_location(location):
            print(tide_data)
        print("----------------------------")

def fetch_tide_table(location):
    url = URL.format(location)

    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError("Could not reach tide data")

    soup = BeautifulSoup(response.content, features="html.parser")

    return soup.find(class_="tide-table")


def get_tides_for_location(location):

    tide_table = fetch_tide_table(location)

    day_data = []
    tide_results = []
    current_day = "even"
    for tr in tide_table.find_all("tr"):

        if tr["class"][0] == current_day:
                day_data.append(tr)
        else:
            tide_results.append(TideDayData("LOCATION", day_data))
            current_day = "odd" if current_day == "even" else "even"
            day_data = [tr]

    return tide_results



class TideDayData:
    def __init__(self, location, tide_day_data: []):
        self.location = location
        self.data = tide_day_data
        self.date = ""
        self._set_date()
        self._filter_data()

    def _filter_data(self):
        sunrise_index, sunset_index = -1, -1
        for index, row in enumerate(self.data):
            tds = row.find_all("td")
            for td in tds:
                if td.string and td.string.strip() == "Sunrise":
                    sunrise_index = index
                if td.string and td.string.strip() == "Sunset":
                    sunset_index = index

        self.data = [self.data[i] for i in range(sunrise_index + 1, sunset_index) if self.data[i].find(class_="tide")]


    def _set_date(self):
        for row in self.data:
            if row.th:
                self.date = row.th.string.strip()

    def __str__(self):
        if not self.data:
            return ""

        strings = [f'-- {self.date}  --']
        for data in self.data:
            if data:
                tide = data.find_all(class_="tide")[1]

                if tide.string:
                    tide =tide.string.strip()

                time = data.find(class_="time tide")
                if time.string:
                    time  =time.string.strip()

                time_zone = data.find(class_="time-zone")
                if time_zone.string:
                    time_zone  =time_zone.string.strip()

                level = data.find(class_="level metric")
                if level.string:
                    level  =level.string.strip()


                strings.append(f"{time} {time_zone} {level} {tide}")

        return "\n".join(strings) + "\n\n"


if __name__ == "__main__":
    scrape_tide_data()
