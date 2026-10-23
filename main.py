import csv
from ldap3 import MODIFY_REPLACE, Server, Connection, SASL, KERBEROS, Tls, ALL_ATTRIBUTES
from dotenv import load_dotenv
import os
import ssl


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
#files = input("name file:")
with open("test.csv", newline='', encoding="utf-8-sig") as file:
    reader = csv.DictReader(file, delimiter=";")

    for user in reader:
        new = user
        names_csv = user["ACCOUNT"]
        print(names_csv)
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
#print(user.displayName.value)
#print(user.title.value)
#print(user.department.value)
#print(user.company.value)
#print(user.manager.value)

for attr in ["title","department","displayName","company"]:
    old = getattr(user, attr).value 
    
    if old != new[attr] and new[attr]:
        changes[attr] = new[attr]


for key, vol in changes.items():
    if key == "department":
        vol = vol[:64]
    ldap_changes[key] = [(MODIFY_REPLACE, [vol])]
 


conn.modify(user.entry_dn, ldap_changes)
print(conn.result)
print(conn.read_only)
print(ldap_changes)
print(user)
conn.unbind