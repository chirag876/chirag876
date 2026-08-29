"""
GitHub Profile README Generator
Fetches public repos from GitHub API and regenerates README.md
Run via GitHub Actions weekly OR manually.
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ──────────────────────────────────────────────
# STATIC DATA  (edit this section to update info)
# ──────────────────────────────────────────────

GITHUB_USERNAME = "chirag876"

PROFILE = {
    "name": "Chirag Gupta",
    "title": "Backend Engineer",
    "email": "chirag1706gupta@gmail.com",
    "phone": "8769240601",
    "linkedin": "https://linkedin.com/in/chiraggupta1706",
    "github": "https://github.com/chirag876",
    "location": "Jaipur, Rajasthan, India",
    "availability": "Immediate Joiner · Open to Remote & On-site across India",
}

CAREER_SUMMARY = """Backend systems should run seamlessly, reliably, and without 2 AM firefighting.
That is the standard I build towards.

I am a Backend Engineer with **3.2 years of experience** building high-throughput APIs,
event-driven pipelines, and cloud-native backend services.

**Key Technical Impact Delivered:**
- 🚀 **High-Scale Assessment Engine** — FastAPI & MongoDB platform supporting 10,000+ active users with sub-200ms API response times.
- 📡 **Real-Time Integration** — Enterprise Zoom integration handling 1,000+ daily live sessions at 99.9% uptime.
- ☁️ **Cloud ETL Pipelines** — Serverless Python/GCP event-driven pipelines to process, transform, and load client data dynamically into BigQuery."""

SKILLS = {
    "Languages & Frameworks": [
        "Python", "SQL", "FastAPI", "Flask", "Django",
        "Asyncio", "Pydantic", "SQLAlchemy", "Pandas", "NumPy"
    ],
    "Databases & Cloud": [
        "MongoDB", "MySQL", "Google BigQuery", "SQL Server",
        "GCP (Cloud Functions · Pub/Sub)", "AWS (S3 · EC2)"
    ],
    "Architecture & Tools": [
        "RESTful APIs", "Microservices", "Multi-Tenant Architecture",
        "CQRS", "OAuth 2.0", "Event-Driven ETL",
        "Docker", "Git", "GitHub", "Postman", "Swagger"
    ],
    "Analytics & BI": ["Power BI", "Qlik Sense"],
}

EXPERIENCE = [
    {
        "role": "Backend Engineer",
        "company": "Edufusion Tech",
        "period": "Sept 2025 – May 2026",
        "stack": "FastAPI · MongoDB · AWS S3 · Zoom OAuth · Docker",
        "highlights": [
            "Engineered a scalable Digital Assessment & Submission Platform with automated scoring, optimizing MongoDB queries from O(N²) to O(N) for 10K+ students with sub-200ms response times.",
            "Architected a Real-Time Classroom System with multi-tenant scheduling and clash detection, maintaining 99.9% uptime across 1,000+ daily meetings.",
            "Designed an Exam Registration Workflow with dynamic IST time-window validation, slashing registration errors by 60% and support ticket load by 80%.",
        ],
    },
    {
        "role": "Associate Cloud Native SDE",
        "company": "D3V Technology Solutions",
        "period": "Apr 2025 – Jun 2025",
        "stack": "Python · GCP Cloud Functions · Pub/Sub · BigQuery · Asyncio · MySQL",
        "highlights": [
            "Architected a cloud-native, event-driven ETL pipeline using Asyncio and GCP Pub/Sub for cross-environment BigQuery migrations with dynamic schema adaptation.",
            "Implemented MySQL-backed pipeline metadata tracking with automated retry mechanisms, service account authentication, and structured error auditing.",
        ],
    },
    {
        "role": "Software Engineer",
        "company": "Spectral Tech AI",
        "period": "Jan 2023 – Mar 2025",
        "stack": "Python · Django · Flask · Azure · RESTful APIs · CQRS · NLP · SQL",
        "highlights": [
            "Developed microservices for a Flask-based CRM and time-tracking system using CQRS pattern, providing real-time executive analytics on leads and resource utilization.",
            "Architected a full-stack Django POC (WhiteSpace Admin) for real-time collaborative whiteboarding with session management and dynamic PDF/image export.",
            "Engineered Azure Data Pipelines and LLM prompt pipelines for insurance data extraction across distributed systems.",
        ],
    },
]

EDUCATION = {
    "degree": "B.Tech — Information Technology",
    "college": "Poornima College of Engineering",
    "location": "Jaipur, Rajasthan",
    "period": "Aug 2019 – Jul 2023",
}

INTERESTS = {
    "intro": "Beyond code, here's what keeps me curious:",
    "items": [
        {
            "icon": "🎵",
            "label": "Music",
            "detail": "Constant companion — from Bollywood classics to whatever mood demands.",
        },
        {
            "icon": "🎬",
            "label": "Cinema",
            "detail": "Bollywood storytelling, screenwriting craft, and what makes a film land.",
        },
        {
            "icon": "✈️",
            "label": "Aviation (Deep Interest)",
            "detail": "Airline operations, airport systems, and especially accident/incident investigations — the engineering and human-factors side of why things go wrong and how aviation keeps getting safer.",
        },
        {
            "icon": "🏛️",
            "label": "Archaeological History & World Mysteries",
            "detail": "Ancient civilisations, unexplained discoveries, and the unsolved corners of human history that textbooks gloss over.",
        },
    ],
}

# Repos to always exclude from the Projects section
EXCLUDED_REPOS = {GITHUB_USERNAME.lower(), "chirag876"}  # profile repo itself


# ──────────────────────────────────────────────
# GITHUB API HELPERS
# ──────────────────────────────────────────────

def fetch_repos(username: str) -> list[dict]:
    """Fetch all public non-fork repos for the given username."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    repos, page = [], 1
    while True:
        url = (
            f"https://api.github.com/users/{username}/repos"
            f"?type=public&sort=updated&per_page=100&page={page}"
        )
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                batch = json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            print(f"[WARN] GitHub API returned {exc.code} — skipping repo fetch.")
            return []

        if not batch:
            break

        for r in batch:
            # Skip forks and the profile repo itself
            if r.get("fork"):
                continue
            if r["name"].lower() in EXCLUDED_REPOS:
                continue
            repos.append(r)

        page += 1

    return repos


def get_repo_languages(username: str, repo_name: str, headers: dict) -> list[str]:
    """Return top-3 languages for a repo (by byte count)."""
    url = f"https://api.github.com/repos/{username}/{repo_name}/languages"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            langs = json.loads(resp.read().decode())
        return list(langs.keys())[:3]
    except Exception:
        return []


# ──────────────────────────────────────────────
# README BUILDER
# ──────────────────────────────────────────────

def badge(label: str, color: str = "0d1117") -> str:
    text = label.replace(" ", "_").replace("-", "--")
    return f"![{label}](https://img.shields.io/badge/{text}-{color}?style=flat-square)"


def skill_badges(items: list[str], color: str) -> str:
    return " ".join(
        f"![{s}](https://img.shields.io/badge/{s.replace(' ', '_').replace('(', '').replace(')', '').replace('·', '%C2%B7')}-{color}?style=flat-square&logo={s.split()[0].lower()}&logoColor=white)"
        for s in items
    )


def build_readme(repos: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%d %b %Y · %H:%M UTC")
    p = PROFILE

    lines = []

    # ── HEADER ──────────────────────────────────
    lines += [
        f"<h1 align=\"center\">Hi, I'm {p['name']} 👋</h1>",
        f"<h3 align=\"center\">{p['title']} · {p['location']}</h3>",
        "",
        "<p align=\"center\">",
        f"  <a href=\"mailto:{p['email']}\"><img src=\"https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white\"/></a>&nbsp;",
        f"  <a href=\"{p['linkedin']}\"><img src=\"https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white\"/></a>&nbsp;",
        f"  <a href=\"{p['github']}\"><img src=\"https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white\"/></a>",
        "</p>",
        "",
        "<p align=\"center\">",
        f"  <img src=\"https://komarev.com/ghpvc/?username={GITHUB_USERNAME}&style=flat-square&color=blue\" alt=\"Profile Views\"/>",
        "  &nbsp;",
        f"  <img src=\"https://img.shields.io/badge/📍_{p['location'].replace(' ', '_')}-informational?style=flat-square\" alt=\"Location\"/>",
        "  &nbsp;",
        f"  <img src=\"https://img.shields.io/badge/✅_Immediate_Joiner-success?style=flat-square\" alt=\"Availability\"/>",
        "</p>",
        "",
        "---",
        "",
    ]

    # ── HIRE ME ─────────────────────────────────
    lines += [
        "## 💼 Open to Opportunities",
        "",
        "> **Immediately available.** Looking for Backend Engineering roles with strong technical depth — across India or Remote.",
        ">",
        f"> 📧 [{p['email']}](mailto:{p['email']}) &nbsp;|&nbsp; 📞 {p['phone']} &nbsp;|&nbsp; [LinkedIn]({p['linkedin']})",
        "",
        "---",
        "",
    ]

    # ── ABOUT ───────────────────────────────────
    lines += [
        "## 🧠 About Me",
        "",
        CAREER_SUMMARY,
        "",
        "---",
        "",
    ]

    # ── SKILLS ──────────────────────────────────
    COLORS = {
        "Languages & Frameworks": "3776AB",
        "Databases & Cloud": "FF6F00",
        "Architecture & Tools": "6E40C9",
        "Analytics & BI": "21A366",
    }

    lines += ["## 🛠️ Tech Stack", ""]
    for category, items in SKILLS.items():
        color = COLORS.get(category, "555555")
        lines.append(f"**{category}**")
        lines.append("")
        for item in items:
            safe = item.replace(" ", "%20").replace("(", "").replace(")", "").replace("·", "%C2%B7").replace("#", "%23")
            logo_name = item.split()[0].lower().replace("(", "").replace(")", "")
            lines.append(
                f"![{item}](https://img.shields.io/badge/{safe}-{color}?style=flat-square&logoColor=white)"
            )
        lines[-len(items):] = [" ".join(lines[-len(items):])]  # join badges in one line
        lines.append("")

    lines += ["---", ""]

    # ── EXPERIENCE ──────────────────────────────
    lines += ["## 💼 Experience", ""]
    for exp in EXPERIENCE:
        lines += [
            f"### {exp['role']} — *{exp['company']}*",
            f"**{exp['period']}** &nbsp;|&nbsp; `{exp['stack']}`",
            "",
        ]
        for h in exp["highlights"]:
            lines.append(f"- {h}")
        lines.append("")

    lines += ["---", ""]

    # ── PROJECTS FROM GITHUB ─────────────────────
    lines += ["## 🚀 Projects", ""]

    if repos:
        token = os.environ.get("GITHUB_TOKEN", "")
        headers = {"Accept": "application/vnd.github+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        for repo in repos:
            name = repo["name"]
            desc = repo.get("description") or "_No description provided._"
            url = repo["html_url"]
            stars = repo.get("stargazers_count", 0)
            forks = repo.get("forks_count", 0)
            topics = repo.get("topics", [])

            langs = get_repo_languages(GITHUB_USERNAME, name, headers)
            lang_str = " · ".join(f"`{l}`" for l in langs) if langs else ""
            topic_str = " ".join(f"`{t}`" for t in topics[:4]) if topics else ""

            lines += [
                f"#### [{name}]({url})",
                f"{desc}",
                "",
            ]
            meta = []
            if lang_str:
                meta.append(f"**Stack:** {lang_str}")
            if topic_str:
                meta.append(f"**Tags:** {topic_str}")
            meta.append(f"⭐ {stars} &nbsp; 🍴 {forks}")
            lines.append(" &nbsp;·&nbsp; ".join(meta))
            lines.append("")
    else:
        lines += [
            "_Could not fetch repositories at this time. Check back soon!_",
            "",
        ]

    lines += ["---", ""]

    # ── EDUCATION ───────────────────────────────
    edu = EDUCATION
    lines += [
        "## 🎓 Education",
        "",
        f"**{edu['degree']}**  ",
        f"{edu['college']} · {edu['location']}  ",
        f"_{edu['period']}_",
        "",
        "---",
        "",
    ]

    # ── GITHUB STATS ────────────────────────────
    lines += [
        "## 📊 GitHub Stats",
        "",
        "<p align=\"center\">",
        f"  <img src=\"https://github-readme-stats.vercel.app/api?username={GITHUB_USERNAME}&show_icons=true&theme=tokyonight&hide_border=true&count_private=true\" height=\"165\"/>",
        "  &nbsp;",
        f"  <img src=\"https://github-readme-stats.vercel.app/api/top-langs/?username={GITHUB_USERNAME}&layout=compact&theme=tokyonight&hide_border=true\" height=\"165\"/>",
        "</p>",
        "",
        "---",
        "",
    ]

    # ── INTERESTS ───────────────────────────────
    lines += [
        "## 🌍 Beyond the Terminal",
        "",
        f"_{INTERESTS['intro']}_",
        "",
    ]
    for item in INTERESTS["items"]:
        lines.append(f"- {item['icon']} **{item['label']}** — {item['detail']}")
    lines.append("")
    lines += ["---", ""]

    # ── FOOTER ──────────────────────────────────
    lines += [
        "<p align=\"center\">",
        f"  <sub>🔄 README auto-generated by GitHub Actions · Last updated: <b>{now}</b></sub>",
        "</p>",
        "",
    ]

    return "\n".join(lines)


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print(f"[INFO] Fetching repos for @{GITHUB_USERNAME} ...")
    repos = fetch_repos(GITHUB_USERNAME)
    print(f"[INFO] Found {len(repos)} public non-fork repos.")

    readme = build_readme(repos)

    out_path = os.environ.get("README_PATH", "README.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"[INFO] README written to {out_path}")
