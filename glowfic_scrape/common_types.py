import hashlib
from typing import NewType, TypedDict
from typing_extensions import NotRequired

__all__ = ["Url", "HtmlCode", "Story", "PostInfo", "get_image_filename"]

Url = NewType("Url", str)
HtmlCode = NewType("HtmlCode", str)


class PostInfo(TypedDict):
    """Processed information about an individual post in a thread."""

    id: int
    author: str
    author_url: Url
    content: HtmlCode
    permalink: Url
    posted: str
    character: NotRequired[str]
    character_url: NotRequired[Url]
    icon_url: NotRequired[Url]


class Story(TypedDict):
    title: str
    authors: str
    comments: Url
    posts: list[PostInfo]


def get_image_filename(url: Url) -> str:
    return hashlib.sha256(url.encode("utf8")).hexdigest()[:20] + ".jpg"
