import requests
from github import Github
import os
import re

USERNAME = "dheena017"
README_PATH = "README.md"
DEVTO_FEED = f"https://dev.to/feed/{USERNAME}"

BLOG_START = "<!-- BLOG-POST-LIST:START -->"
BLOG_END = "<!-- BLOG-POST-LIST:END -->"
PROJECTS_START = "<h2>🌟 Featured Projects</h2>"
PROJECTS_END = "</ul>"
CONTRIBS_START = "<h2>🤝 Open Source Contributions</h2>"
CONTRIBS_END = "</ul>"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

def fetch_devto_posts():
    try:
        import feedparser
    except ImportError:
        import sys
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "feedparser"])
        import feedparser
    feed = feedparser.parse(DEVTO_FEED)
    posts = []
    for entry in feed.entries[:3]:
        posts.append(f'<li><a href="{entry.link}">{entry.title}</a></li>')
    return "\n".join(posts)

def fetch_featured_projects():
    g = Github(GITHUB_TOKEN)
    user = g.get_user(USERNAME)
    repos = sorted(user.get_repos(), key=lambda r: r.stargazers_count, reverse=True)[:3]
    lines = [PROJECTS_START, "<ul>"]
    for repo in repos:
        lines.append(f'<li><a href="{repo.html_url}"><b>{repo.name}</b></a> &mdash; {repo.description or "No description"} <img src="https://img.shields.io/github/stars/{USERNAME}/{repo.name}?style=social" alt="Stars"/></li>')
    lines.append("</ul>")
    return "\n".join(lines)

def fetch_contributions():
    g = Github(GITHUB_TOKEN)
    user = g.get_user(USERNAME)
    events = user.get_events()
    contribs = set()
    for event in events:
        if hasattr(event, 'repo') and event.repo.name != f"{USERNAME}/{USERNAME}":
            contribs.add(event.repo.name)
        if len(contribs) >= 3:
            break
    lines = [CONTRIBS_START, "<ul>"]
    for repo in contribs:
        lines.append(f'<li>Contributor to <a href="https://github.com/{repo}">{repo}</a></li>')
    lines.append("</ul>")
    return "\n".join(lines)

def update_section(content, start, end, new_block):
    pattern = re.compile(f"{re.escape(start)}.*?{re.escape(end)}", re.DOTALL)
    return pattern.sub(f"{start}\n{new_block}\n{end}", content)

def main():
    with open(README_PATH, encoding="utf-8") as f:
        content = f.read()
    # Update blog posts
    blog_html = fetch_devto_posts()
    content = update_section(content, BLOG_START, BLOG_END, f"<ul>\n{blog_html}\n</ul>")
    # Update featured projects
    projects_html = fetch_featured_projects()
    content = update_section(content, PROJECTS_START, PROJECTS_END, projects_html)
    # Update contributions
    contribs_html = fetch_contributions()
    content = update_section(content, CONTRIBS_START, CONTRIBS_END, contribs_html)
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
