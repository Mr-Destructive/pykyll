import functools
import http.server
import os
import shutil
import socketserver

from jinja2 import Template
from pathlib import Path
from slugify import slugify

import frontmatter
import markdown
import tomli

from vials.rss import generate_rss


class PykyllTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def load_config(file_path: str) -> dict:
    with open(file_path, mode='rb') as f:
        config_file = tomli.load(f)
    return config_file


def runserver(path: str):
    PORT = 8000
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=path)
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
        site_name=config["pages"]["site_name"],
        content=html_content,
    )
    post_html = post_html.replace(
        "<pre class=", "<div class='highlight'><pre class=")
    post_html = post_html.replace("</pre>", "</pre></div>")
    with open(Path(config["outputs"]["output_dir"]) / (slug + ".html"), "w") as f:
        f.write(post_html)


def load_pages(pages_path, output_dir):
    onlyfiles = os.listdir(pages_path)
    pages = []
    logger.info(f"Loading pages from {pages_path}")
    for file in onlyfiles:
        with open(Path(pages_path) / file, "r") as f:
            content = f.read()
            post = frontmatter.loads(content)
            html_content = markdown.markdown(post.content, extensions=[
                                             'fenced_code', 'codehilite',])
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


def load_feed(config: dict, posts: list, feed_type: str):

    with open(config["templates"]["feed_template"]) as f:
        template = Template(f.read())

    feed_html = template.render(
        site_name=config["pages"]["site_name"],
        posts=posts,
    )
    
    output_dir = Path(config["outputs"]["output_dir"])
    with open(output_dir / feed_type /  "index.html", "w") as f:
        f.write(feed_html)


def copy_static_files(output_dir: str, feed: str, static_dir: str):
    shutil.copytree(static_dir, output_dir, dirs_exist_ok=True)
    shutil.copytree(static_dir, Path(output_dir)/feed, dirs_exist_ok=True)


def main():
    config = load_config("pages.toml")
    pages_dir = Path(config["pages"]["pages_dir"])
    output_dir = os.path.abspath(config["outputs"]["output_dir"])

    for feed_type in config["feed_types"]:
        pages_dir = Path(config["pages"]["pages_dir"])
        feeds_dir = pages_dir / feed_type

        if not os.path.exists(Path(output_dir)):
            os.mkdir(Path(output_dir) )
        if not os.path.exists(Path(output_dir) / feed_type):
            os.mkdir(Path(output_dir) / feed_type)
        posts = load_pages(feeds_dir, output_dir)
        load_feed(config, posts, feed_type)
        copy_static_files(config["outputs"]["output_dir"], feed_type, "static/")
        generate_rss()
    runserver(output_dir)


main()
