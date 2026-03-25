import requests
from bs4 import BeautifulSoup
import re

USERNAME = "dheena017"
README_PATH = "README.md"

ACHIEVEMENTS_START = "<h3>🏅 GitHub Achievements</h3>"
ACHIEVEMENTS_END = "</ul>"

ACHIEVEMENT_SECTION_PATTERN = re.compile(
    rf"{re.escape(ACHIEVEMENTS_START)}.*?{re.escape(ACHIEVEMENTS_END)}",
    re.DOTALL
)

def fetch_achievements(username):
    url = f"https://github.com/{username}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    achievements = []
    for item in soup.select('div.js-profile-achievements-container img[alt]'):
        alt = item.get('alt', '').replace('Achievement: ', '').strip()
        src = item.get('src', '')
        count = item.parent.find_next_sibling('span')
        count_text = f" x{count.text.strip()}" if count and count.text.strip().isdigit() else ""
        achievements.append((alt, src, count_text))
    return achievements

def format_achievements(achievements):
    lines = [ACHIEVEMENTS_START, "<ul>"]
    for alt, src, count in achievements:
        lines.append(f'  <li>{alt} <img src="{src}" width="24" alt="{alt}"/>{count}</li>')
    lines.append("</ul>")
    return "\n".join(lines)

def update_readme(achievements_html):
    with open(README_PATH, encoding="utf-8") as f:
        content = f.read()
    if ACHIEVEMENT_SECTION_PATTERN.search(content):
        content = ACHIEVEMENT_SECTION_PATTERN.sub(achievements_html, content)
    else:
        # Insert after Achievements & Certifications section
        content = content.replace(
            "</ul>\n\n<h3>🏅 GitHub Achievements", f"</ul>\n\n{achievements_html}\n\n"
        )
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    achievements = fetch_achievements(USERNAME)
    achievements_html = format_achievements(achievements)
    update_readme(achievements_html)

if __name__ == "__main__":
    main()
