import sys
import json
from datetime import datetime
import base64
import requests
import re


def get_title_url_from_title(test_str):
    regex = r"\[(.*?)\]\((.*?)\)"
    matches = re.finditer(regex, test_str, re.MULTILINE)
    res = []
    for matchNum, match in enumerate(matches, start=1):
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            res.append(match.group(groupNum))
    return res


def get_title_from_comments(comments):
    bot_comments = list(
        filter(
            lambda i: i["user"]["type"] == "Bot"
            and i["body"].strip().startswith("Article"),
            comments,
        )
    )
    bot_comments = [i["body"].strip() for i in bot_comments]
    bot_comment = bot_comments[0]
    title, desc = bot_comment.split("article:")[1].split("- desc:")
    title = title.strip()
    desc = desc.strip()
    title, url = get_title_url_from_title(title)
    return title, url, desc


def merge(comments):
    print("/merge")

    title, url, desc = get_title_from_comments(comments)
    date = datetime.today().strftime("%Y-%m-%d")
    print(title, url, desc)

    with open("./.github/data.json", "r") as f:
        datas = json.load(f)

    print("data", datas)
    for i in datas:
        if i["url"] == url:
            print(f"::set-output name=close::2")
            return

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

| Date |  Article   | Desc  |
| ---- |  ----  | ----  |
"""
    for data in datas:
        readme += f"| {date} | [{title}]({url})  | {desc} |\n"

    print(readme)
    with open("./README.md", "w") as f:
        f.write(readme)

    print(f"::set-output name=update::2")
    print(f"::set-output name=close::2")


def close(**kwargs):
    print("/close")
    print(f"::set-output name=close::2")


def default(**kwargs):
    print("default")


def main():
    print("hi")

    issue_json = base64.b64decode(sys.argv[1]).decode("utf-8")
    issue = json.loads(issue_json)
    print(json.dumps(issue, indent=2))
    comments_url = issue["comments_url"]

    comments = requests.get(comments_url).json()
    command_comments = list(filter(lambda i: i["user"]["type"] != "Bot", comments))
    command_comments = [i["body"].strip() for i in command_comments]
    print("command_comments", command_comments)

    if len(command_comments) == 0:
        print("没有控制命令")
        return

    command = command_comments[-1]

    {"/merge": merge, "/close": close,}.get(
        command, default
    )(comments=comments)


if __name__ == "__main__":
    main()
