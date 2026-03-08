import requests
import time
import pandas as pd

BASE = "https://www.izkor.gov.il"

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Cookie":  # EDIT THE COOKIES
        "PASTE_YOUR_COOKIE_HERE"
}


def get_cemeteries():
    url = f"{BASE}/search/list-fields"
    r = session.get(url, headers=headers)
    r.raise_for_status()

    # print(r.text)
    data = r.json()
    return data["cemeteriesSearch"]["data"]


def get_fallen(cemetery):
    url = f"{BASE}/search/extended"

    page = 0
    results = []

    while True:

        payload = {
            "cemetery": cemetery,
            "page": page
        }

        r = session.post(url, headers=headers, json=payload)
        r.raise_for_status()

        data = r.json()["data"]

        if not data:
            break

        results.extend(data)

        print(f"{cemetery['name']} page {page} -> {len(data)}")

        page += 1
        time.sleep(0.3)

    return results


def filter_cemeteries(cemeteries, filters):

    filtered = []

    for cemetery in cemeteries:

        name = cemetery.get("name", "")

        for f in filters:
            if f in name:
                filtered.append(cemetery)
                break

    return filtered


def load_filters(filename="filter_cities.txt"):
    with open(filename, encoding="utf8") as f:
        return [line.strip() for line in f if line.strip()]


def save_to_excel_file(all_fallen):
    df = pd.DataFrame(all_fallen)
    df.to_excel("izkor_data.xlsx", index=False)


def main():

    cemeteries = get_cemeteries()

    filters = load_filters()

    cemeteries = filter_cemeteries(cemeteries, filters)

    print(f"cemeteries list after filter: {[cemetery['name'] for cemetery in cemeteries]}")
    all_fallen = []

    for cemetery in cemeteries:

        if cemetery["legacy_id"] is None:
            continue

        print("Fetching", cemetery["name"])

        fallen = get_fallen(cemetery)
        for one_fallen in fallen:
            one_fallen["cemetery"] = cemetery['name']

        all_fallen.extend(fallen)

    print("Total:", len(all_fallen))

    save_to_excel_file(all_fallen)


if __name__ == "__main__":
    main()