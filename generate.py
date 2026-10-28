"""Generate the neofetch-style profile cards (dark_mode.svg / light_mode.svg).

Runs daily from .github/workflows/update-profile.yml. Uses only the Python
standard library. GitHub stats come from the public REST API; set GITHUB_TOKEN
(provided automatically in GitHub Actions) for higher rate limits.
"""

import datetime as dt
import json
import os
import urllib.request
from xml.sax.saxutils import escape

USER = "Hussein-Fouani"
WIDTH = 56  # characters in each info line (dot leaders fill the gap)
STARTED_SYNAPSE = dt.date(2024, 5, 1)

ASCII_ART = r"""::::::::::::::::::i||llllllllll|!,,::::,`'
;;;;;;;;;;;;:::::;i|lllllllll||!:..'`,:,.
;;;;;;;;;;;;;;;::;i|lllllll|!:'       ..
;;;;;;;;;;;;;:;;;;i|lllllli,'
[ffft[{{{j|:''`:!|ljjjjjjl|;:`'
kmwwwmf[[[j!,`:l{tttttttt[{|!:,'
w%mffkkt[j|;,,;|{k@@@MMM%kttlii:`
HMHwmmkt{li,`:!l[k@Mwt[{{ljtt[[|!,'    `::
%@MMM@@Hf[[[[[tw%M%Hwkffffftj|i;:`'.   '``
wmwHHHHmt|,,,;|H@@@@%%Hk{|!:`''.     ...
HH%MMM%wj!,``;iwMM@MHHk{;,.
%MMM%%mj;,,,`:!lliil{[l:.                .
kmtj!!;!!!iii|l{jlj{[i,.
{[{{{{{{{jjjjjjj{[tj!`
{[[[[[tt[[[[[{{[tfl;'
kf{[mwHwwkfftfkk{!`.  .'`:;;`
wf{f%@@@Hkfkmk[i`. .`;!!i!il;`
mk[[fmwwHHwwt|,' .';i|jjl|||li'
@MHwH%MMHk[!,'. ,!{[t[[[[{{{{ji:'
%%%H%%Hwt|`.   `!|{{{jjlll||iii!:.
||ii!!;:,'    .''`````````````:|i:'
''''''.......                 ':|l:'
..........                     ,i|;'
...                  ...       ,i|:.
                               !|l;`""".split("\n")

THEMES = {
    "dark_mode.svg": dict(bg="#161b22", text="#c9d1d9", key="#ffa657", value="#a5d6ff", cc="#616e7f", art="#58a6ff"),
    "light_mode.svg": dict(bg="#f6f8fa", text="#24292f", key="#953800", value="#0a3069", cc="#c2cfde", art="#0969da"),
}


def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}", headers={"Accept": "application/vnd.github+json", "User-Agent": USER})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def github_stats():
    user = api(f"/users/{USER}")
    stars, page = 0, 1
    while True:
        repos = api(f"/users/{USER}/repos?type=owner&per_page=100&page={page}")
        if not repos:
            break
        stars += sum(r["stargazers_count"] for r in repos)
        page += 1
    commits = api(f"/search/commits?q=author:{USER}&per_page=1")["total_count"]
    return {"repos": user["public_repos"], "stars": stars, "followers": user["followers"], "commits": commits}


def uptime(today):
    months = (today.year - STARTED_SYNAPSE.year) * 12 + today.month - STARTED_SYNAPSE.month
    y, m = divmod(months, 12)
    return f"{y} year{'s' * (y != 1)}, {m} month{'s' * (m != 1)} (at Synapse)"


def build_lines(stats, today):
    s = stats or {}
    fmt = lambda k: f"{s[k]:,}" if k in s else "…"
    rows = [
        ("title", "hussein@fouani"),
        ("kv", "Role", ".NET Backend Developer"),
        ("kv", "Uptime", uptime(today)),
        ("kv", "Host", "Synapse (Hospital Information System)"),
        ("kv", "Kernel", "C#, .NET, ASP.NET Core"),
        ("kv", "IDE", "Visual Studio, VS Code"),
        ("blank",),
        ("kv", "Languages.Programming", "C#, Java, TypeScript, SQL"),
        ("kv", "Languages.Frameworks", "ASP.NET Core, EF, Spring Boot"),
        ("kv", "Languages.Frontend", "Angular, React"),
        ("kv", "Languages.Real", "English, Arabic"),
        ("blank",),
        ("kv", "Learning.Now", "Python, pandas, scikit-learn"),
        ("kv", "Learning.Next", "PyTorch, LLMs, RAG, MLOps"),
        ("kv", "Hobbies", "Algorithms / LeetCode, AI/ML"),
        ("section", "Contact"),
        ("kv", "LinkedIn", "hussein-fouani"),
        ("kv", "Portfolio", "hussein-fouani.github.io/Portfolio"),
        ("kv", "LeetCode", "hussein_fouani"),
        ("section", "GitHub Stats"),
        ("pair", ("Repos", fmt("repos")), ("Stars", fmt("stars"))),
        ("pair", ("Commits", fmt("commits")), ("Followers", fmt("followers"))),
    ]
    return rows


def dots(n):
    return " " + "." * max(n - 2, 1) + " "


def render(rows, theme):
    t = THEMES[theme]
    line_h, x_art, x_info, y0 = 20, 15, 430, 30
    height = max(len(ASCII_ART), len(rows)) * line_h + 25
    width = 985
    out = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        f'<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{width}px" height="{height}px" font-size="16px">',
        "<style>",
        "@font-face { src: local('Consolas'), local('Consolas Bold'); font-family: 'ConsolasFallback'; font-display: swap; -webkit-size-adjust: 109%; size-adjust: 109%; }",
        f".key {{fill: {t['key']};}} .value {{fill: {t['value']};}} .cc {{fill: {t['cc']};}} .art {{fill: {t['art']};}}",
        "text, tspan {white-space: pre;}",
        "</style>",
        f'<rect width="{width}px" height="{height}px" fill="{t["bg"]}" rx="15"/>',
        f'<text x="{x_art}" y="{y0}" class="art">',
    ]
    for i, line in enumerate(ASCII_ART):
        out.append(f'<tspan x="{x_art}" y="{y0 + i * line_h}">{escape(line)}</tspan>')
    out.append("</text>")
    out.append(f'<text x="{x_info}" y="{y0}" fill="{t["text"]}">')
    for i, row in enumerate(rows):
        y = y0 + i * line_h
        kind = row[0]
        if kind == "title":
            out.append(f'<tspan x="{x_info}" y="{y}">{row[1]}</tspan> -{"—" * (WIDTH - len(row[1]) - 5)}-—-')
        elif kind == "section":
            out.append(f'<tspan x="{x_info}" y="{y}">- {row[1]}</tspan> -{"—" * (WIDTH - len(row[1]) - 7)}-—-')
        elif kind == "blank":
            out.append(f'<tspan x="{x_info}" y="{y}" class="cc">. </tspan>')
        elif kind == "kv":
            _, k, v = row
            fill = WIDTH - 2 - len(k) - 1 - len(v)
            out.append(
                f'<tspan x="{x_info}" y="{y}" class="cc">. </tspan><tspan class="key">{escape(k)}</tspan>:'
                f'<tspan class="cc">{dots(fill)}</tspan><tspan class="value">{escape(v)}</tspan>'
            )
        elif kind == "pair":
            (k1, v1), (k2, v2) = row[1], row[2]
            half = (WIDTH - 2) // 2
            f1 = half - len(k1) - 1 - len(v1)
            f2 = WIDTH - 2 - half - 3 - len(k2) - 1 - len(v2)
            out.append(
                f'<tspan x="{x_info}" y="{y}" class="cc">. </tspan><tspan class="key">{k1}</tspan>:'
                f'<tspan class="cc">{dots(f1)}</tspan><tspan class="value">{v1}</tspan> | '
                f'<tspan class="key">{k2}</tspan>:<tspan class="cc">{dots(f2)}</tspan><tspan class="value">{v2}</tspan>'
            )
    out.append("</text>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    today = dt.date.today()
    try:
        stats = github_stats()
    except Exception as e:  # keep the card working even if the API is unavailable
        print(f"Could not fetch GitHub stats: {e}")
        stats = None
    rows = build_lines(stats, today)
    for name in THEMES:
        with open(name, "w", encoding="utf-8") as f:
            f.write(render(rows, name))
    print("Generated", ", ".join(THEMES), "with stats", stats)


if __name__ == "__main__":
    main()
