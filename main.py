import os
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as Et

import requests
from bs4 import BeautifulSoup


BASE_DIR = Path(__file__)
DATA_DIR = BASE_DIR.parent / "data"
TEXT_FILE = DATA_DIR / "today.txt"
PAGE_FILE = DATA_DIR / "page.html"


def get_movie_data(page_number):
    url = f"https://www.hindimoviestv.com/release-year/2023/page/{page_number}/"
    response = requests.get(url)
    if not response.ok:
        return [
            {
                "title": "Website is DOWN!",
                "image": "https://pbs.twimg.com/profile_images/3265644386/7ca7632af440e704ec24e15057e2385c_400x400.png"
            }
        ]
    soup = BeautifulSoup(response.text, "lxml")
    entries = []
    for movie in soup.select("div.main-content div.ml-item"):
        movie_title = movie.select_one("div.qtip-title").get_text(strip=True)
        if "hindi" in movie_title.lower():
            continue
        entries.append(
            {
                "title": movie_title,
                "image": movie.select_one("img").get("src")
            }
        )
    return entries


# Alternate XML output
def save_to_xml(entries, batch_number):
    root = Et.Element("movies")
    for entry in entries:
        movie_elem = Et.SubElement(root, "movie")
        title_elem = Et.SubElement(movie_elem, "title")
        title_elem.text = entry["title"]
        image_elem = Et.SubElement(movie_elem, "image")
        image_elem.text = entry["image"]
    tree = Et.ElementTree(root)
    file_name = f"movies_{batch_number:02d}.xml"
    tree.write(str(DATA_DIR / f"{file_name}"))


def save_to_html(entries):
    html_header = """
        <!DOCTYPE html>
        <html>
        <head>
        <title>Page Title</title>
        <style>
            body {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            img {
                min-width: 300px;
                max-width: 300px;
            }
        </style>
        </head>
        <body>
    """

    html_list = []
    for entry in entries:
        html_list.append(f'<h1>{entry["title"]}</h1>')
        html_list.append(f'<img src="{entry["image"]}" loading="lazy" />')

    html_content = "".join(html_list)
    html_footer = """
        </body>
        </html>
    """

    with open(str(PAGE_FILE), "a", encoding="utf-8") as f:
        f.write(html_header)
        f.write(html_content)
        f.write(html_footer)


def fake_update():
    # TODO: Use GitHub action and remove fake_update
    """Fake adding update to project to allow GitHub push."""
    today = datetime.now()
    with open(str(TEXT_FILE), "w") as f:
        f.write(str(today))

    with open(str(PAGE_FILE), "w", encoding="utf-8") as f:
        f.write("")


if __name__ == '__main__':
    fake_update()
    for page in range(1, 4):
        movies = get_movie_data(page)
        save_to_html(movies)
    os.chdir(str(BASE_DIR.parent))
    print(os.getcwd())
    os.system('git add . && git commit -m "auto generate xml." && git push')