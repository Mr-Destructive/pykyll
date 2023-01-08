import functools
import http.server
import os
import socketserver

from jinja2 import Template
from pathlib import Path
from slugify import slugify

import frontmatter
import markdown
import tomli


class PykyllTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def load_config(file_path: str) -> dict:
    with open(file_path, mode='rb') as f:
        config_file = tomli.load(f)
    return config_file

def runserver(path: str):
    PORT = 8000
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=path)
    with PykyllTCPServer(("", PORT), handler) as httpd:
        try:
            print("Server started at localhost:" + str(PORT))
            httpd.serve_forever()
        except KeyboardInterrupt as _:
            httpd.server_close()

def render_template(post: frontmatter.Post, title: str, html_content: str, config: dict):
    slug = post.get("slug")

    with open(config["templates"]["post_template"]) as f:
        template = Template(f.read())

    post_html = template.render(
        title=title,
        author=config["author"]["name"],
        user_blog=config["author"]["blog_link"],
        content=html_content,
    )
    with open(Path(config["outputs"]["output_dir"]) / (slug + ".html"), "w") as f:
        f.write(post_html)

def load_pages(pages_path, output_dir):
    onlyfiles = os.listdir(pages_path)
    pages = []
    for file in onlyfiles:
        with open(Path(pages_path) / file, "r") as f:
            content = f.read()
            post = frontmatter.loads(content)
            html_content = markdown.markdown(post.content, extensions=["fenced_code"],)
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
            default_title = file.split(".")[0]
            title = str(post.get("title", default_title))
            post["title"] = title
            post["slug"] = slugify(str(post.get("title", title)))
            pages.append(post)
            config = load_config("pages.toml")
            render_template(post, title, html_content, config) 
    return pages

def load_feed(config: dict, posts: list):

    with open(config["templates"]["feed_template"]) as f:
        template = Template(f.read())

    feed_html = template.render(
        site_name=config["pages"]["site_name"],
        posts=posts,
    )
    with open(Path(config["outputs"]["output_dir"]) / "index.html", "w") as f:
        f.write(feed_html)

def main():
    config = load_config("pages.toml")
    pages_dir = Path(config["pages"]["pages_dir"])
    output_dir = os.path.abspath(config["outputs"]["output_dir"])

    posts = load_pages(pages_dir, output_dir)
    load_feed(config, posts)
    runserver(output_dir)

main()
