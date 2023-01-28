import os
import re
import tomli
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


def load_config(file_path: str) -> dict:
    with open(file_path, mode='rb') as f:
        config_file = tomli.load(f)
    return config_file


def generate_rss():
    rss = Element('rss', {'version': '2.0'})
    channel = SubElement(rss, 'channel')

    config = load_config("pages.toml")
    output_dir = config["outputs"]["output_dir"]
    title = SubElement(channel, 'title')
    title.text = config["pages"]["site_name"]
    link = SubElement(channel, 'link')
    link.text = config["author"]["blog_link"]
    description = SubElement(channel, 'description')
    description.text = config["pages"]["description"]

    for file in os.listdir(output_dir):
        if file.endswith('.html'):
            with open(output_dir + file, 'r') as f:
                html = f.read()
            title_match = re.search(r'<title>(.+)</title>', html)
            description_match = re.search(
                r'<meta name="description" content="(.+)"', html)
            if title_match and description_match:
                item = SubElement(channel, 'item')
                item_title = SubElement(item, 'title')
                item_title.text = title_match.group(1)
                item_link = SubElement(item, 'link')
                item_link.text = config["pages"]["site_name"] + file
                item_description = SubElement(item, 'description')
                item_description.text = description_match.group(1)
                item_pubdate = SubElement(item, 'pubDate')
                item_pubdate.text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %Z")

    rss_str = minidom.parseString(
        tostring(rss, 'utf-8')).toprettyxml(indent='  ')
    with open(output_dir + 'rss.xml', 'w') as f:
        f.write(rss_str)
