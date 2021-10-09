import sys
import json
from datetime import datetime
import base64
import requests
from bs4 import BeautifulSoup


def get_issue():
    issue_json = base64.b64decode(sys.argv[1]).decode("utf-8")
    issue = json.loads(issue_json)
    print(json.dumps(issue, indent=2))
    return issue


def parse_info(issue_body, issue_number):
    url, desc = issue_body.split("### URL")[1].split("### Desc")
    url = url.strip()
    desc = desc.strip()

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    }
    r = requests.get(url, headers=headers)
    print(r.url, r.text, r.status_code)
    soup = BeautifulSoup(r.text)
    title = soup.title.string

    data = {
        "issue_number": issue_number,
        "title": title,
        "url": url,
        "desc": desc,
    }
    print(data)

    return title, url, desc


def is_exist(url):
    with open("./.github/data.json", "r") as f:
        datas = json.load(f)
    for i in datas:
        if i["url"] == url:
            return True
    return False


def update_data(title, url, desc):
    date = datetime.today().strftime("%Y-%m-%d")

    with open("./.github/data.json", "r") as f:
        datas = json.load(f)

    datas.insert(
        0,
        {
            "date": date,
            "title": title,
            "url": url,
            "desc": desc,
        },
    )

    with open("./.github/data.json", "w") as f:
        json.dump(datas, f, indent=4)

    readme = """# article_share

| Date &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; |  Article   | Desc  |
| ---- |  ----  | ----  |
"""

    for data in datas:
        date, title, url, desc = data["date"], data["title"], data["url"], data["desc"]
        readme += f"| {date} | [{title}]({url})  | {desc} |\n"

    print(readme)
    with open("./README.md", "w") as f:
        f.write(readme)


def main():
    issue = get_issue()

    issue_number = issue["number"]
    print(f"::set-output name=issue_number::{issue_number}")

    title, url, desc = parse_info(issue["body"], issue_number)
    print(f"::set-output name=url::{url}")
    print(f"::set-output name=desc::{desc}")
    print(f"::set-output name=title::{title}")

    exist = is_exist(url)
    if exist:
        print(f"::set-output name=exist::2")
        return

    update_data(title, url, desc)
    print(f"::set-output name=update::2")


if __name__ == "__main__":
    main()
