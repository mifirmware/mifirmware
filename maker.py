import os
import re
import sys
import json
import shutil
import sqlite3
import hashlib # for future
import argparse
import requests
import subprocess
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urlparse

parser = argparse.ArgumentParser()
parser.add_argument("device", help="import device json file")
parser.add_argument("version", help="choose miui version for generate firmware zip")
parser.add_argument("--output", help="output location")
parser.parse_args()
args = parser.parse_args()

with open(args.device, 'r') as device_data_file:
    ddata = json.load(device_data_file)

print("Current device: %s, %s" % (ddata['codename'], ddata['name']))

page = requests.get("http://en.miui.com/download-" + ddata['id'] + ".html").text
soup = BeautifulSoup(page, 'html.parser')

for line in soup.find(id=ddata['content_id'][args.version.split('-')[0]]).find_all('a', class_='btn_5'):
    zip_url = line['href']
    zip_url_split = list(filter(None, urlparse(zip_url).path.split('/')))
    miui_release = zip_url_split[0]
    if re.match("[0-9].[0-9].[0-9]", miui_release) and "dev" in args.version:
        break
    elif "stable" in args.version:
        break

if not 'zip_url' in globals():
    print("Not found any url")
    sys.exit(1)

print("Found download url: %s" % zip_url)

cachedb = sqlite3.connect('cache.db')
cursor = cachedb.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS devices (codename TEXT, version TEXT, last_miui_release REAL)")
cursor.execute("INSERT INTO devices(codename, version, last_miui_release) SELECT ?, ?, '0.0.0' WHERE NOT EXISTS(SELECT * FROM devices WHERE codename=? and version=?);", [ddata['codename'], args.version, ddata['codename'], args.version])
cachedb.commit()

cursor.execute("SELECT * FROM devices WHERE codename=? and version=?", [ddata['codename'], args.version])
last_miui_release = cursor.fetchone()[2]

if miui_release <= last_miui_release:
    print("Not found new miui build. Terminating..")
    sys.exit(0)

print("Found new miui build: %s > %s" % (miui_release, last_miui_release))

if not os.path.exists(miui_release):
    os.makedirs(miui_release)

zip_location = miui_release + "/" + zip_url_split[1]

if not os.path.isfile(zip_location):
    print("Downloading: %s" % zip_url_split[1])
    with urllib.request.urlopen(zip_url) as response, open(zip_location, 'wb') as outf:
        shutil.copyfileobj(response, outf)

subprocess.check_call("xiaomi-flashable-firmware-creator/create_flashable_firmware.sh %s %s" % (zip_location, miui_release + "/"), shell=True)
os.remove(zip_location)

print("Created %s flashable firmware." % ddata['codename'])
cursor.execute("UPDATE devices SET last_miui_release=? WHERE codename=? and version=?", [miui_release, ddata['codename'], args.version])
cachedb.commit()
cachedb.close()
