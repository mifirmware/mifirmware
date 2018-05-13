import os
import re
import sys
import json
import shutil
import sqlite3
import hashlib # for the future
import argparse
import zipfile
import requests
import subprocess
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Argument parser stuff
parser = argparse.ArgumentParser()
parser.add_argument("device", help="import device json file")
parser.add_argument("version", help="choose miui version for generate firmware zip")
parser.add_argument("--output", help="output location")
parser.add_argument("--git", help="import device json file from github", action="store_true")
parser.add_argument("--skip-miui-release-check", help="skip miui release check", action="store_true")
args = parser.parse_args()

# Check miui version is available
versions = ["global-stable", "global-dev", "china-stable", "china-dev"]
if not args.version in versions:
    print("Please write any available miui version.")
    sys.exit(1)

# If exists local device.json file, use it. Or fetch from GitHub.
if not args.git:
    with open(args.device, 'r') as device_data_file:
        ddata = json.load(device_data_file)
else:
    ddata = json.loads(requests.get("https://raw.githubusercontent.com/mifirmware/devices/master/%s.json" % args.device).text)

print("Current device/version: %s, %s / %s" % (ddata['codename'], ddata['name'], args.version))

# Parse miui download page
page = requests.get("http://en.miui.com/download-" + ddata['id'] + ".html").text
soup = BeautifulSoup(page, 'html.parser')

for line in soup.find(id=ddata['content_id'][args.version.split('-')[0]]).find_all('a', class_='btn_5'):
    # Define miui download url
    zip_url = line['href']
    # Split miui release and miui zip name
    zip_url_split = list(filter(None, urlparse(zip_url).path.split('/')))
    # Define miui release
    miui_release = zip_url_split[0]
    # Choose dev or stable link according to option
    if re.match("[0-9].[0-9].[0-9]", miui_release) and "dev" in args.version:
        break
    elif "stable" in args.version:
        break

# If not defined zip url, terminate
if not 'zip_url' in globals():
    print("Not found any url")
    sys.exit(1)

print("Found download url: %s" % zip_url)

# Create (if not exists) device db & table for caching last release
cachedb = sqlite3.connect('cache.db')
cursor = cachedb.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS devices (codename TEXT, version TEXT, last_miui_release REAL)")
cursor.execute("INSERT INTO devices(codename, version, last_miui_release) SELECT ?, ?, '0.0.0' WHERE NOT EXISTS(SELECT * FROM devices WHERE codename=? and version=?);", [ddata['codename'], args.version, ddata['codename'], args.version])
cachedb.commit()

# If not defined skip miui release argument, compare last miui release & miui release
if not args.skip_miui_release_check:
    cursor.execute("SELECT * FROM devices WHERE codename=? and version=?", [ddata['codename'], args.version])
    last_miui_release = cursor.fetchone()[2]
    
    if miui_release <= last_miui_release:
        print("Not found new miui build. Terminating..")
        sys.exit(0)
    
    print("Found new miui build: %s > %s" % (miui_release, last_miui_release))

# If not exists folder, create it
if not os.path.exists(miui_release):
    os.makedirs(miui_release)

zip_location = miui_release + "/" + zip_url_split[1]

# Fetch miui zip
if not os.path.isfile(zip_location):
    print("Downloading: %s" % zip_url_split[1])
    with urllib.request.urlopen(zip_url) as response, open(zip_location, 'wb') as outf:
        shutil.copyfileobj(response, outf)

# Test miui zip
with zipfile.ZipFile(zip_location) as zip_file:
    zip_stat = zip_file.testzip()

if zip_stat is not None:
    print("Zip file is bad: %s" % zip_stat)
    sys.exit(1)

out = (miui_release + "/") if not args.output else args.output

# Create firmware zip
subprocess.check_call("xiaomi-flashable-firmware-creator/create_flashable_firmware.sh %s %s" % (zip_location, out), shell=True)
os.remove(zip_location)

print("Created %s flashable firmware." % ddata['codename'])

# If not defined skip miui release argument, commit last miui version
if not args.skip_miui_release_check:
    cursor.execute("UPDATE devices SET last_miui_release=? WHERE codename=? and version=?", [miui_release, ddata['codename'], args.version])
    cachedb.commit()

# Finally close cache db
cachedb.close()
