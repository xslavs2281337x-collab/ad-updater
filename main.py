import csv
from ldap3 import Server, Connection, SASL, KERBEROS, Tls
from dotenv import load_dotenv
import os
import ssl


load_dotenv()


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
conn.unbind()

# ===========CSV=========== 
files = input("name file:")
with open(files, newline='', encoding="utf-8-sig") as file:
    reader = csv.DictReader(file, delimiter=";")
    for user in reader:
        print(user)