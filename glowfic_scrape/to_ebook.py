#!/usr/bin/env python

import re
import subprocess
import sys
from typing import Final

from .common_types import HtmlCode

## Depends on having Calibre's `ebook-convert` in your PATH.
## On MacOS, install Calibre then:
##   export PATH="${PATH}:/Applications/calibre.app/Contents/MacOS"
## On Debian, `sudo apt install calibre` should do it.
EBOOK_CONVERT: Final = "ebook-convert"


def ebook_convert(src: str) -> None:
    with open(src) as f:
        contents = HtmlCode(f.read())
    info: dict[str, str] = {}
    for field in ["authors", "comments", "title"]:
        m = re.search(rf"^{field}: (.*)$", contents, flags=re.M)
        if m:
            info[field] = m.group(1)

    name = re.sub(r"\.html$", "", src)
    for fmt in ["epub"]:  # ["mobi", "epub"]:
        output = "%s.%s" % (name, fmt)
        options = [
            "--chapter",
            "//*[name()='h1' or name()='h2' or name()='h3']",
            "--language",
            "en_us",
        ]
        for field, value in info.items():
            options += ["--" + field, value]
        cmd = [EBOOK_CONVERT, src, output] + options
        print(cmd)
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        ebook_convert(arg)
