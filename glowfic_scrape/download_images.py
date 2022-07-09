import json
from pathlib import Path
import sys
from typing import Final
from urllib.request import urlopen
from urllib.error import URLError

from .common_types import Story, Url, get_image_filename

SUBDIR: Final = "images"


def main() -> None:
    for arg in sys.argv[1:]:
        process(Path(arg))


def process(filepath: Path) -> None:
    dir = Path(".") / SUBDIR
    dir.mkdir(exist_ok=True, parents=True)
    with filepath.open("r") as f:
        thread: Story = json.load(f)
    total = len(thread["posts"])
    percent = 0
    for i, post in enumerate(thread["posts"], start=1):
        if "icon_url" in post:
            download_image(post["icon_url"], dir)
        p = 100 * i // total
        if p != percent:
            percent = p
            sys.stderr.write("\r%3d %% " % percent)


def download_image(url: Url, dir: Path) -> None:
    filename = dir / get_image_filename(url)
    if not filename.exists():
        try:
            connection = urlopen(url, timeout=10)  # 10 second time out
        except URLError as e:
            raise RuntimeError(f"Can't open: '{url}' for '{filename}'.") from e
        with filename.open("wb") as f:
            f.write(connection.read())


if __name__ == "__main__":
    main()
