import json
import re
import sys
from typing import Any, TypedDict
from typing_extensions import NotRequired
from urllib.request import urlopen

from .common_types import HtmlCode, PostInfo, Story, Url


def get_json(url: Url) -> Any:
    return json.load(urlopen(url))


class UserInfo(TypedDict):
    id: int
    username: str


class CharacterInfo(TypedDict, total=False):
    id: int
    name: str


class IconInfo(TypedDict):
    id: int
    url: Url
    keyword: str


class ThreadInfo(TypedDict):
    """Info about a whole thread (or story)."""

    id: int
    authors: list[UserInfo]
    content: HtmlCode
    created_at: str
    num_replies: int
    subject: str
    character: NotRequired[CharacterInfo]


class RawPost(TypedDict):
    id: int
    content: HtmlCode
    created_at: str
    user: UserInfo
    character: NotRequired[CharacterInfo]
    icon: NotRequired[IconInfo]


def proc(main_post: int) -> Story:
    comments_url = Url(f"https://www.glowfic.com/posts/{main_post:d}")
    main_url = Url(f"https://www.glowfic.com/api/v1/posts/{main_post:d}")
    thread: ThreadInfo = get_json(main_url)
    title: str = thread["subject"]
    authors = " & ".join(a["username"] for a in thread["authors"])
    num_replies = thread["num_replies"]

    permalink = Url(f"https://www.glowfic.com/posts/{main_post:d}")

    all_posts: list[PostInfo] = []
    all_posts.append(_dopost(thread, permalink, thread["authors"][0]))

    index = 1
    percent = 0
    while True:
        replies_url = Url(
            f"https://www.glowfic.com/api/v1/posts/{main_post:d}/replies?page={index:d}"
        )
        posts: list[RawPost] = get_json(replies_url)
        index += 1
        if not posts:
            break
        for post in posts:
            postid = post["id"]
            permalink = Url(
                f"https://www.glowfic.com/replies/{postid:d}#reply-{postid:d}"
            )
            all_posts.append(_dopost(post, permalink, post["user"]))
            p = 100 * len(all_posts) // num_replies
            if p != percent:
                percent = p
                sys.stderr.write("\r%3d %% " % percent)
    sys.stderr.write("\r       \r")
    return {
        "title": title,
        "authors": authors,
        "comments": comments_url,
        "posts": all_posts,
    }


def _dopost(post: ThreadInfo | RawPost, permalink: Url, author: UserInfo) -> PostInfo:
    ret: PostInfo = {
        "id": post["id"],
        "permalink": permalink,
        "author": author["username"],
        "author_url": Url(f"https://www.glowfic.com/users/{author['id']:d}"),
        "posted": post["created_at"],
        "content": post["content"],
    }
    c = post.get("character")
    if c and "name" in c and "id" in c:
        ret["character"] = c["name"]
        ret["character_url"] = Url(f"https://www.glowfic.com/characters/{c['id']:d}")
    i: IconInfo | None = post.get("icon")
    if i is not None:
        ret["icon_url"] = i["url"]
    return ret


def main(postid: int):
    thread = proc(postid)
    ofilename = re.sub(r"\W+", "_", thread["title"]) + ".json"
    with open(ofilename, "w") as o:
        json.dump(thread, o)
    sys.stderr.write('wrote to "%s".\n' % ofilename)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        main(int(arg))
