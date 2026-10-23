import csv
from ldap3 import Server, Connection, SASL, KERBEROS, Tls, ALL_ATTRIBUTES
from dotenv import load_dotenv
import os
import ssl


load_dotenv()
changes = {}

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
    read_only=True
)

if conn.bind():
    print("Kerberos: successfully ")
    print("LDAP:", conn.extend.standard.who_am_i())
else:
    print("failure:", conn.result)

# ===========CSV=========== 
#files = input("name file:")
with open("test.csv", newline='', encoding="utf-8-sig") as file:
    reader = csv.DictReader(file, delimiter=";")

    for user in reader:
        new = user
# ===========AD=============
conn.search(
    search_base="DC=loesk,DC=internal",
    search_filter="(sAMAccountName=demidov-va)",
    attributes=[
        "title",
        "department",
        "displayName",
        "company",
        "manager"

    ]
)


user = conn.entries[0]
#print(user.displayName.value)
#print(user.title.value)
#print(user.department.value)
#print(user.company.value)
#print(user.manager.value)

for attr in ["title","department","displayName","company","manager"]:
    old = getattr(user, attr).value 
    
    if old != new[attr]:
        changes[attr] = new[attr]

print(changes)

conn.unbind