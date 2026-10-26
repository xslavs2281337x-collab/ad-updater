import csv
from ldap3 import MODIFY_REPLACE, Server, Connection, SASL, KERBEROS, Tls, ALL_ATTRIBUTES
from dotenv import load_dotenv
import os
import ssl
import logging
from pathlib import Path
import sys

logging.basicConfig(
    filename="updater.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)


load_dotenv()
changes = {}
ldap_changes = {}

# ===========CONNECTION=========== 
server = Server(
    os.getenv("AD_SERVER"),
    port=636,
    use_ssl=True,
    tls=Tls(validate=ssl.CERT_REQUIRED)
)


## CONNECTION_NTLM
#conn = Connection(
#    server,
#    user=os.getenv("AD_USER"),
#    password=os.getenv("AD_PASSWODR"),
#    authentication=NTLM,
#    auto_bind=AUTO_BIND_NO_TLS
#)

# CONNECTION_KERBEROS

conn = Connection(
    server,
    authentication=SASL,
    sasl_mechanism=KERBEROS,
    read_only=False
)

if conn.bind():
    print("Kerberos: successfully ")
    print("LDAP:", conn.extend.standard.who_am_i())
else:
    print("failure:", conn.result)

# ===========CSV=========== 
files = input("name file(default users.csv):") or "users.csv"

try:
    with open(files, newline='', encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, delimiter=";")
        for user in reader:
            newcsv = user
            names_csv = user["ACCOUNT"]
            manager_csv = user["manager"]
            print(names_csv)

except FileNotFoundError as b:
    print("The CSV file was not found")
    logging.error(b)
    sys.exit(1)

except PermissionError as e:
    print("access denied")
    logging.error(e)
    sys.exit(1)
# ===========AD=============
conn.search(
    search_base="DC=loesk,DC=internal",
    search_filter=f"(sAMAccountName={names_csv})",
    attributes=[
        "title",
        "department",
        "displayName",
        "company",
        "manager",
        "distinguishedName"

    ]
)
user = conn.entries[0]

conn.search(
    search_base="DC=loesk,DC=internal",
    search_filter=f"(DisplayName={manager_csv})",
    attributes=[
        "displayName"
    ]
)
manager = conn.entries[0]



for attr in ["title","department","displayName","company"]:
    old = getattr(user, attr).value 
    if old != newcsv[attr] and newcsv[attr]:
        changes[attr] = newcsv[attr]


# ======search difference============
if user.manager.value != manager.entry_dn:
    changes["manager"] = manager.entry_dn



for key, vol in changes.items():
    if key == "department":
        vol = vol[:64]
    ldap_changes[key] = [(MODIFY_REPLACE, [vol])]
 #===========change===========
try:
    success = conn.modify(user.entry_dn, ldap_changes)
    if success:
        print("The changes have been applied")
        logging.info("DONE")
        

    else:
        print(conn.result)
        logging.error(conn.result)
except Exception as e:
    print(f"exception {e}")
    logging.error(e)

    
conn.unbind