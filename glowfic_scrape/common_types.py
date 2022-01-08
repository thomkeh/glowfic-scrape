from typing import NewType, TypedDict
from typing_extensions import NotRequired

__all__ = ["Url", "HtmlCode", "Result", "PostInfo"]

Url = NewType("Url", str)
HtmlCode = NewType("HtmlCode", str)


class PostInfo(TypedDict):
    id: int
    author: str
    author_url: Url
    content: HtmlCode
    permalink: Url
    posted: str
    character: NotRequired[str]
    character_url: NotRequired[Url]


class Result(TypedDict):
    title: str
    authors: str
    comments: Url
    posts: list[PostInfo]
