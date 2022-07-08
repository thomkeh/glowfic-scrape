#! /usr/bin/env python

import datetime
import json
import re
import sys
from typing import Final, Iterable

import lxml.html

from .common_types import HtmlCode, Story, Url, get_image_filename

TEMPLATE: Final = HtmlCode(
    """
<div id="{postid}" class="box">
  <div class="author-name">
    {author} ({posted})
  </div>
  {picture}
  {character}
</div>
<div class="content">
{content}
</div>
<hr>
"""
)

HEADER: Final = HtmlCode(
    """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#000000">
<title>{title}</title>

<!--
authors: {authors}
comments: {comments}
title: {title}
-->

<style>
body{{margin:8px auto;max-width:32em;padding:0 8px;text-align:left;}}
pre{{overflow-x:auto;}}
div p{{text-indent:2em;margin-top:0;margin-bottom:0}}
div p:first-child{{text-indent:0;}}
h1{{text-align:center;}}
div.box{{font-style:italic}}
a:link, a:hover, a:active, a:visited {{color:inherit;}}
div.character-name{{font-weight:bold}}
div.character-pic img{{height:100px;max-width:400px;}}
div.spoiler{{background:WhiteSmoke;margin:8px 0;}}
p.spoiler-summary{{font-weight:bold;margin-bottom:8px;text-align:center;}}
</style>
</head>
<body>
<h1>{title}</h1>
<div>{authors}</div>
<div>{comments}</div>
<hr>
"""
)


PARAGRAPH_TWO_BRS: Final = re.compile(r"\s*((<br\s*/?>|\n)\s*){2,}", flags=re.I)


def process(filename: str):
    with open(filename, "r") as f:
        thread: Story = json.load(f)
    ofilename = re.sub(r"\W+", "_", thread["title"]) + ".html"
    with open(ofilename, "w") as o:
        o.write(
            HEADER.format(
                title=thread["title"],
                authors=thread["authors"],
                comments=thread["comments"],
            )
        )
        for post in thread["posts"]:
            o.write(
                TEMPLATE.format(
                    postid=post["id"],
                    author=post["author"],
                    # author_url=post["author_url"],
                    picture=picture(post.get("icon_url")),
                    character=character(post.get("character")),
                    posted=format_time(post["posted"]),
                    # permalink=post["permalink"],
                    content=clean_html(to_paragraphs(post["content"])),
                )
            )
        o.write("<hr>\n</body>\n</html>\n")
    sys.stderr.write('wrote to "%s".\n' % ofilename)


def to_paragraphs(src: HtmlCode) -> HtmlCode:
    return HtmlCode(
        src
        if ("<p>" in src)
        else PARAGRAPH_TWO_BRS.sub("</p><p>", "<p>" + src + "</p>")
    )


def clean_html(src: HtmlCode) -> HtmlCode:
    post = lxml.html.fragment_fromstring(src, create_parent="post")
    # relative links confuse `ebook-convert`; it thinks they are chapters
    post.make_links_absolute("https://www.glowfic.com")
    _replace_spoilers(post)
    for child in post:
        _replace_spoilers(child)
    return HtmlCode(
        html_to_string(e for e in post.iterchildren() if e.text or e.tail or len(e) > 0)
    )


def _replace_spoilers(el: lxml.html.HtmlElement) -> None:
    """Replace <details> and <summary> tags."""
    for details_tag in el.findall("details"):
        details_tag.tag = "div"
        details_tag.classes |= ["spoiler"]
        for summary_tag in details_tag.findall("summary"):
            summary_tag.tag = "p"
            summary_tag.classes |= ["spoiler-summary"]


def html_to_string(elements: Iterable[lxml.html.HtmlElement]) -> str:
    # this is apparently the way to do it...
    return "".join(lxml.html.tostring(el, encoding=str) for el in elements)


def character(char_name: str | None) -> str:
    if char_name is None:
        return ""
    return f'<div class="character-name">{char_name}</div>\n'


def picture(pic_url: Url | None) -> str:
    if pic_url is None:
        return ""
    return f'<div class="character-pic"><img src="images/{get_image_filename(pic_url)}"></div>\n'


def format_time(t: str) -> str:
    return datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
        "%Y-%m-%d %H:%M"
    )


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        process(arg)
