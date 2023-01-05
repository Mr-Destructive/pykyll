import functools
import http.server
import os
import socketserver

import frontmatter
import markdown

from pathlib import Path


def runserver(path: str):
    PORT = 8000
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=path)
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        try:
            print("Server started at localhost:" + str(PORT))
            httpd.serve_forever()
        except KeyboardInterrupt as _:
            httpd.server_close()

def load_pages(pages_path, output_dir):
    onlyfiles = os.listdir(pages_path)
    pages = []
    for file in onlyfiles:
        with open(Path(pages_path) / file, "r") as f:
            content = f.read()
            post = frontmatter.loads(content)
            html_content = markdown.markdown(post.content)
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
            default_title = file.split(".")[0]
            title = str(post.get("title", default_title)) + ".html"
            post["title"] = title
            pages.append(post)
            with open(Path(output_dir) / "index.html", "a") as f:
                f.write(f"<li><a href='#'>{post.get('title', 'test')}</a></li>")
            with open(Path(output_dir) / title, "w") as f:
                f.write(html_content)
    return pages


def main():
    pages_dir = Path("pages")
    output_dir = os.path.abspath("pyites")

    load_pages(pages_dir, output_dir)
    runserver(output_dir)

main()
