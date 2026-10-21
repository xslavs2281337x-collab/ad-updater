import csv
from ldap3 import Server

with open('users.csv', newline='', encoding="utf-8-sig") as file:
    reader = csv.DictReader(file, delimiter=";")
    for user in reader:
        print(user)