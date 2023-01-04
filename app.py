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


def main():
    post_path = Path("pages")
    output_path = os.path.abspath("pyites")

    onlyfiles = os.listdir(post_path)
    for file in onlyfiles:
        with open(Path(post_path) / file, "r") as f:
            content = f.read()
            post = frontmatter.loads(content)
            html_content = markdown.markdown(post.content)
            if not os.path.exists(output_path):
                os.mkdir(output_path)
            title = str(post.get("title", "pykyll-test")) + ".html"

            with open(Path(output_path) / "index.html", "a") as f:
                f.write(f"<li><a href='#'>{post.get('title', 'test')}</a></li>")
            with open(Path(output_path) / title, "w") as f:
                f.write(html_content)
    runserver(output_path)


main()
