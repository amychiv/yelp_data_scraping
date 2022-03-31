from asyncio import trsock
import sqlite3
import csv
import os
from bs4 import BeautifulSoup
import requests

f = open("detroit_restaurants.csv", "r")
data = f.readlines()
f.close()

url = "https://en.wikipedia.org/wiki/List_of_restaurant_chains_in_the_United_States"
page = requests.get(url)
soup = BeautifulSoup(page.text, "html.parser")

fast_food = []
trs = soup.find_all('tr')

tds = []
for tr in trs:
    try:
        tds.append(tr.find_all('td')[0])
    except:
        print("row head")

for td in tds:
    if "\n" not in td.text.strip():
        fast_food.append(td.text.strip())

fast_food += ["Little Caesars Pizza"]
fast_food += ["Domino's Pizza"]
fast_food += ["Popeyes Louisiana Kitchen"]

path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path+'/detroit_restaurants.db')
cur = conn.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS
    Restaurants (id TEXT PRIMARY KEY, name TEXT, review_count INTEGER, rating TEXT, latitude NUMBER, longitude NUMBER, price INTEGER, zip TEXT)
    """
)
conn.commit()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS
    Chains (id TEXT PRIMARY KEY, name TEXT, review_count INTEGER, rating NUMBER, latitude NUMBER, longitude NUMBER, price INTEGER, zip TEXT)
    """
)
conn.commit()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS
    Local_Chains (id TEXT PRIMARY KEY, name TEXT, review_count INTEGER, rating NUMBER, latitude NUMBER, longitude NUMBER, price INTEGER, zip TEXT)
    """
)
conn.commit()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS
    Prices (id NUMBER PRIMARY KEY, price TEXT)
    """
)
conn.commit()

price_data = ['NA', '$', '$$', '$$$', '$$$$']
for i in range(len(price_data)):
    cur.execute(
        """
        INSERT OR IGNORE INTO Prices
        (id, price) VALUES (?, ?)
        """, (i, price_data[i])
    )

restaurants = []
for row in data[1:]:
    restaurants.append(row.strip().split(',')[1])

counts = {}
for r in restaurants:
    counts[r] = counts.get(r, 0) + 1


for row in data[1:]:
    line = row.strip().split(',')
    cur.execute(
        """
        SELECT id FROM Prices
        WHERE price = ?
        """, (line[6], )
    )
    conn.commit()
    price_id = cur.fetchall()

    if line[1] in fast_food:
        cur.execute(
            """
            INSERT OR IGNORE INTO Chains
            (id, name, review_count, rating, latitude, longitude, price, zip)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (line[0], line[1], line[2], line[3], line[4], line[5], price_id[0][0], line[7])
        )
    elif counts[line[1]] > 1:
        cur.execute(
            """
            INSERT OR IGNORE INTO Local_Chains
            (id, name, review_count, rating, latitude, longitude, price, zip)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (line[0], line[1], line[2], line[3], line[4], line[5], price_id[0][0], line[7])
        )
    else:
        cur.execute(
            """
            INSERT OR IGNORE INTO Restaurants
            (id, name, review_count, rating, latitude, longitude, price, zip)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (line[0], line[1], line[2], line[3], line[4], line[5], price_id[0][0], line[7])
        )
    conn.commit()

with open("detroit_chains.csv", "w") as csvfile:
    csvwriter = csv.writer(csvfile)
    cur.execute(
        """
        SELECT * FROM Chains
        """
    )
    conn.commit()
    csvwriter.writerow(["id", "name", "review_count", "rating", "latitude", "longitude", "price", "zip_code"])
    csvwriter.writerows(cur.fetchall())

with open("detroit_local_chains.csv", "w") as csvfile:
    csvwriter = csv.writer(csvfile)
    cur.execute(
        """
        SELECT * FROM Local_Chains
        """
    )
    conn.commit()
    csvwriter.writerow(["id", "name", "review_count", "rating", "latitude", "longitude", "price", "zip_code"])
    csvwriter.writerows(cur.fetchall())

with open("detroit_only_restaurants.csv", "w") as csvfile:
    csvwriter = csv.writer(csvfile)
    cur.execute(
        """
        SELECT * FROM Restaurants
        """
    )
    conn.commit()
    csvwriter.writerow(["id", "name", "review_count", "rating", "latitude", "longitude", "price", "zip_code"])
    csvwriter.writerows(cur.fetchall())

