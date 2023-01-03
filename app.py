import frontmatter
import markdown
import os 
from pathlib import Path

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
        with open(Path(output_path) / title, 'w') as f:
            f.write(html_content)
