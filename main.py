import os
from datetime import datetime
import xml.etree.ElementTree as Et

import requests
from bs4 import BeautifulSoup


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
        entries.append(
            {
                "title": movie.select_one("div.qtip-title").get_text(strip=True),
                "image": movie.select_one("img").get("src")
            }
        )
    return entries


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
    tree.write(f"data/{file_name}")


def save_to_html(entries):
    html_header = """
        <!DOCTYPE html>
        <html>
        <head>
        <title>Page Title</title>
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

    with open("data/page.html", "w", encoding="utf-8") as f:
        f.write(html_header)
        f.write(html_content)
        f.write(html_footer)


def fake_update():
    today = datetime.now()
    with open("data/today.txt", "w") as f:
        f.write(str(today))


if __name__ == '__main__':
    fake_update()
    movies = get_movie_data(1)
    save_to_html(movies)
    batch_size = 10
    for i in range(0, len(movies), batch_size):
        batch = movies[i:i + batch_size]
        save_to_xml(batch, i // batch_size + 1)
    os.system('git add . && git commit -m "auto generate xml." && git push')
