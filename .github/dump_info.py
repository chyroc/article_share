import sys
import json
from datetime import datetime
import base64
import requests
from bs4 import BeautifulSoup

print("hi")

issue_json = base64.b64decode(sys.argv[1]).decode("utf-8")
issue = json.loads(issue_json)
print(json.dumps(issue, indent=2))
issue_number = issue["number"]
issue_body = issue["body"]

url, desc = issue_body.split("### URL")[1].split("### Desc")
url = url.strip()
desc = desc.strip()

r = requests.get(url)
soup = BeautifulSoup(r.text)
title = soup.title.string


data = {
    "issue_number": issue_number,
    "title": title,
    "url": url,
    "desc": desc,
}
print(data)
print(f"::set-output name=issue_number::{issue_number}")
print(f"::set-output name=url::{url}")
print(f"::set-output name=desc::{desc}")
print(f"::set-output name=title::{title}")
