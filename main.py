#!/usr/bin/env python3
import os, requests, datetime, time, sqlite3
from bs4 import BeautifulSoup as BS
from send_telegram import send_telegram


def save(data, db_name):
    if os.path.exists(db_name):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM apartments")
        conn.commit()
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS apartments (
            address TEXT,
            price TEXT,
            metro TEXT,
            time_metro TEXT,
            link TEXT
        )
    """)
    conn.commit()
    for row in data:
        address, price, metro, time_metro, link = row[:5]
        cursor.execute("""
            INSERT INTO apartments (address, price, metro, time_metro, link)
            VALUES (?, ?, ?, ?, ?)
        """, (address, price, metro, time_metro, link))
        conn.commit()
    conn.close()


def lst_old(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM apartments")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_html():
    url = 'https://www.avito.ru/ekaterinburg/kvartiry/prodam/1-komnatnye/vtorichka-ASgBAgICA0SSA8YQ5geMUsoIgFk?context=H4sIAAAAAAAA_wEjANz_YToxOntzOjg6ImZyb21QYWdlIjtzOjc6ImNhdGFsb2ciO312FITcIwAAAA&f=ASgBAQECCkSSA8YQ5geMUsoIgFnmFub8Aay~DaTHNcDBDbr9N47eDgKQ3g4CkPgO_rDjArCzFP6hjwMBQIK9DiTQpNEB0qTRAQJFhAkVeyJmcm9tIjoyOSwidG8iOm51bGx9xpoMHXsiZnJvbSI6MjgwMDAwMCwidG8iOjU1MDAwMDB9&footWalkingMetro=15'
    headers = {"Accept": "*/*", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0)"}
    return requests.get(url, headers=headers)


def get_data(html):
    lst_data = []
    soup = BS(html.text, 'lxml')
    catalog = soup.find('div', {'data-marker': 'catalog-serp'})
    list_of_apartments = catalog.find_all('div', {'data-marker': 'item'})
    for apartment in list_of_apartments:
        address = apartment.find('div', {'data-marker': 'item-address'}).find('p').text.replace('  ', ' ').replace('ул.', '').replace(' ,', ',').replace(', ', ',').strip()
        price = apartment.find('p', {'data-marker': 'item-price'}).text.replace('\xa0', '').replace('₽', '').strip()
        metro = apartment.find('a', {'data-marker': 'metro_link'}).text.strip()
        time_metro = apartment.find('div', {'data-marker': 'item-address'}).find_all('span')[-1].text
        link = 'https://avito.ru' + apartment.find('a').get('href').split('?context=')[0]
        data = (address, price, metro, time_metro, link)
        lst_data.append(data)
    return lst_data


def verify_news():
    ref_lst = lst_old('apartments.db')
    new_lst = get_data(get_html())
    freshs_lst = []
    for new in new_lst:
        if new not in ref_lst:
            freshs_lst.append(new)
    if freshs_lst:
        save(new_lst, 'apartments.db')
        for i in freshs_lst:
            send_telegram(f"{i[0]} {i[1]} {i[2]} {i[3]} {i[4]}")


count = 0
def main():
    global count
    now = datetime.datetime.now()
    try:
        if os.path.exists('apartments.db'):
            verify_news()
            print(str(now.strftime('%d-%m-%Y %H:%M:%S ')) + 'ok')
        else:
            save(get_data(get_html()), 'apartments.db')
    except Exception as ex:
        if count < 2:
            print(str(now.strftime('%d-%m-%Y %H:%M:%S ')) + 'count: ' + str(count))
            count += 1
            time.sleep(5)
            main()
        else:
            print(str(now.strftime('%d-%m-%Y %H:%M:%S ')) + str(ex))


if __name__ == '__main__':
    main()
