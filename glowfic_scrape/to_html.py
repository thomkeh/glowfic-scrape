#! /usr/bin/env python

import datetime
import json
import re
import sys
from typing import Final

import lxml.html

from .common_types import Result, Url, HtmlCode

TEMPLATE: Final = HtmlCode(
    """
<div id="{postid}" class="box">
  <div class="author-name">
    {author} ({posted})
  </div>
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


def to_paragraphs(src: HtmlCode) -> HtmlCode:
    return HtmlCode(
        src
        if ("<p>" in src)
        else PARAGRAPH_TWO_BRS.sub("</p><p>", "<p>" + src + "</p>")
    )


def clean_html(src: HtmlCode) -> HtmlCode:
    return HtmlCode(
        "".join(
            lxml.html.tostring(e, encoding=str)
            for e in lxml.html.fragments_fromstring(src)
            if e.text or e.tail or len(e) > 0
        )
    )


def character(char_name: str | None, char_url: Url | None) -> str:
    if not char_name or not char_url:
        return ""
    return f'<div class="character-name">{char_name}</div>\n'


def format_time(t: str) -> str:
    return datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
        "%Y-%m-%d %H:%M"
    )


def process(filename: str):
    with open(filename, "r") as f:
        thread: Result = json.load(f)
    ofilename = re.sub(r"\W+", "_", thread["title"]) + ".html"
    with open(ofilename, "w") as o:
        o.write(
            HEADER.format(
                title=thread.get("title"),
                authors=thread.get("authors"),
                comments=thread.get("comments"),
            )
        )
        for post in thread["posts"]:
            o.write(
                TEMPLATE.format(
                    postid=post["id"],
                    author=post["author"],
                    # author_url=post["author_url"],
                    character=character(
                        post.get("character"), post.get("character_url")
                    ),
                    posted=format_time(post["posted"]),
                    # permalink=post["permalink"],
                    content=clean_html(to_paragraphs(post["content"])),
                )
            )
        o.write("<hr>\n</body>\n</html>\n")
    sys.stderr.write('wrote to "%s".\n' % ofilename)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        process(arg)
