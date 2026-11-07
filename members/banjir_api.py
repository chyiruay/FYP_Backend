# members/banjir_api.py
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# (code, name) for every state the source site covers.
STATES = [
    ("JHR", "Johor"),
    ("KDH", "Kedah"),
    ("KTN", "Kelantan"),
    ("MLK", "Melaka"),
    ("NSN", "Negeri Sembilan"),
    ("PHG", "Pahang"),
    ("PRK", "Perak"),
    ("PLS", "Perlis"),
    ("PNG", "Pulau Pinang"),
    ("SBH", "Sabah"),
    ("SWK", "Sarawak"),
    ("SGR", "Selangor"),
    ("TRG", "Terengganu"),
    ("KUL", "Kuala Lumpur"),
    ("LBN", "Labuan"),
    ("PJY", "Putrajaya"),
]

def scrape_state_banjir_data(state_code):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    # The source site is slow; without a limit a hung page blocks the whole run.
    driver.set_page_load_timeout(60)
    url =f"https://publicinfobanjir.water.gov.my/aras-air/data-paras-air/?state={state_code}&lang=en"
    try:
        driver.get(url)
        time.sleep(3)
        html = driver.page_source
    finally:
        # Always close Chrome, or failed runs leak browser processes.
        driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr", class_="item")

    result = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 12:
            result.append({
                "station_id": cols[1].text.strip(),
                "station_name": cols[2].text.strip(),
                "district": cols[3].text.strip(),
                "main_basin": cols[4].text.strip(),
                "sub_basin": cols[5].text.strip(),
                "last_update": cols[6].text.strip(),
                "water_level": cols[7].text.strip(),
                "normal": cols[8].text.strip(),
                "alert": cols[9].text.strip(),
                "warning": cols[10].text.strip(),
                "danger": cols[11].text.strip(),
                "state_code": state_code,
            })
    return result
