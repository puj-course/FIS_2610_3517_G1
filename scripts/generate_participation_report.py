import json
import os
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path


REPO = os.getenv("GITHUB_REPOSITORY", "puj-course/FIS_2610_3517_G1")
SPRINTS_PATH = Path(".github/agile/sprints.json")
OUTPUT_PATH = Path("reports/agile/participation_report.md")


def run_command(command):
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True
    )
    return result.stdout.strip()


def load_sprints():
    with open(SPRINTS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def parse_github_date(value):
    if not value:
        return None

    return datetime.fromisoformat(value.replace("Z", "+00:00")).date()


def date_in_range(value, start, end):
    if not value:
        return False

    return start <= value <= end


def load_prs():
    output = run_command([
        "gh", "pr", "list",
        "--repo", REPO,
        "--state", "all",
        "--limit", "1000",
        "--json", "number,title,state,author,mergedAt,createdAt,closedAt,labels,reviewDecision"
    ])

    return json.loads(output)


def load_pr_reviews(pr_number):
    try:
        output = run_command([
            "gh", "pr", "view", str(pr_number),
            "--repo", REPO,
            "--json", "reviews"
        ])

        data = json.loads(output)
        return data.get("reviews", [])

    except subprocess.CalledProcessError:
        return []


def get_commits_for_sprint(start, end):
    output = run_command([
        "git", "log",
        f"--since={start} 00:00:00",
        f"--until={end} 23:59:59",
        "--pretty=format:%H%x09%an%x09%ae%x09%ad%x09%s",
        "--date=iso-strict"
    ])

    if not output:
        return []

    commits = []

    for line in output.splitlines():
        parts = line.split("\t")

        if len(parts) < 5:
            continue

        commit_hash = parts[0]
        author_name = parts[1]
        author_email = parts[2]
        commit_date = parts[3]
        subject = parts[4]

        commits.append({
            "hash": commit_hash,
            "short_hash": commit_hash[:7],
            "author_name": author_name,
            "author_email": author_email,
            "date": commit_date,
            "subject": subject
        })

    return commits


def get_author_login(item):
    author = item.get("author") or {}
    return author.get("login", "sin_autor")


def filter_prs_by_sprint(prs, sprint):
    start = datetime.fromisoformat(sprint["start"]).date()
    end = datetime.fromisoformat(sprint["end"]).date()

    sprint_prs = []

    for pr in prs:
        merged_at = parse_github_date(pr.get("mergedAt"))

        if date_in_range(merged_at, start, end):
            sprint_prs.append(pr)

    return sprint_prs


def count_reviews_by_member(reviews):
    counter = Counter()

    for review in reviews:
        author = review.get("author") or {}
        login = author.get("login")

        if login:
            counter[login] += 1

    return counter


def build_sprint_detail(sprint, prs):
    commits = get_commits_for_sprint(sprint["start"], sprint["end"])
    sprint_prs = filter_prs_by_sprint(prs, sprint)

    reviews = []

    for pr in sprint_prs:
        reviews.extend(load_pr_reviews(pr["number"]))

    commits_by_member = Counter()

    for commit in commits:
        commits_by_member[commit["author_name"]] += 1

    prs_by_member = Counter()

    for pr in sprint_prs:
        prs_by_member[get_author_login(pr)] += 1

    reviews_by_member = count_reviews_by_member(reviews)

    return {
        "sprint": sprint,
        "commits": commits,
        "prs": sprint_prs,
        "reviews": reviews,
        "commits_by_member": commits_by_member,
        "prs_by_member": prs_by_member,
        "reviews_by_member": reviews_by_member
    }


def add_counter_table(lines, title, first_column, second_column, counter):
    lines.append(f"\n## {title}\n")
    lines.append(f"| {first_column} | {second_column} |")
    lines.append("|---|---:|")

    if not counter:
        lines.append("| Sin registros | 0 |")
        return

    for member, count in counter.most_common():
        lines.append(f"| {member} | {count} |")


def add_sprint_detail(lines, detail):
    sprint = detail["sprint"]

    lines.append(f"\n# Detalle {sprint['name']}\n")
    lines.append(f"- Rango: **{sprint['start']} a {sprint['end']}**")

    lines.append("\n## Commits por integrante\n")

    if detail["commits_by_member"]:
        for member, count in detail["commits_by_member"].most_common():
            lines.append(f"- {member}: {count}")
    else:
        lines.append("- No se registran commits en este sprint.")

    lines.append("\n## Commits registrados\n")

    if detail["commits"]:
        for commit in detail["commits"]:
            lines.append(
                f"- `{commit['short_hash']}` — {commit['author_name']} — {commit['subject']}"
            )
    else:
        lines.append("- No se registran commits en este sprint.")

    lines.append("\n## PRs integrados\n")

    if detail["prs"]:
        for pr in detail["prs"]:
            author = get_author_login(pr)
            lines.append(f"- PR #{pr['number']} — {pr['title']} — {author}")
    else:
        lines.append("- No se registran PRs integrados en este sprint.")

    lines.append("\n## Revisiones por integrante\n")

    if detail["reviews_by_member"]:
        for member, count in detail["reviews_by_member"].most_common():
            lines.append(f"- {member}: {count}")
    else:
        lines.append("- No se registran revisiones en este sprint.")


def build_report():
    sprints = load_sprints()
    prs = load_prs()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    sprint_details = []

    global_commits_by_member = Counter()
    global_prs_by_member = Counter()
    global_reviews_by_member = Counter()

    total_commits = 0
    total_prs = 0
    total_reviews = 0

    for sprint in sprints:
        detail = build_sprint_detail(sprint, prs)

        sprint_details.append(detail)

        total_commits += len(detail["commits"])
        total_prs += len(detail["prs"])
        total_reviews += len(detail["reviews"])

        global_commits_by_member.update(detail["commits_by_member"])
        global_prs_by_member.update(detail["prs_by_member"])
        global_reviews_by_member.update(detail["reviews_by_member"])

    sprint_count = len(sprints)

    average_commits = round(total_commits / sprint_count, 2) if sprint_count else 0
    average_prs = round(total_prs / sprint_count, 2) if sprint_count else 0
    average_reviews = round(total_reviews / sprint_count, 2) if sprint_count else 0

    lines = []

    lines.append("# Reporte automático de participación técnica por sprint\n")
    lines.append(
        "Este reporte consolida evidencia cuantitativa de participación del equipo "
        "a partir de commits, pull requests integrados y revisiones realizadas.\n"
    )
    lines.append(
        "Nota: este reporte no calcula historias de usuario cerradas, ya que esa métrica "
        "se gestiona en otro reporte del equipo.\n"
    )

    lines.append("## Resumen general\n")
    lines.append(f"- Total de commits registrados: **{total_commits}**")
    lines.append(f"- Total de PRs integrados: **{total_prs}**")
    lines.append(f"- Total de revisiones registradas: **{total_reviews}**")
    lines.append(f"- Promedio de commits por sprint: **{average_commits}**")
    lines.append(f"- Promedio de PRs integrados por sprint: **{average_prs}**")
    lines.append(f"- Promedio de revisiones por sprint: **{average_reviews}**")

    lines.append("\n## Resumen por sprint\n")
    lines.append("| Sprint | Rango | Commits | PRs integrados | Revisiones |")
    lines.append("|---|---|---:|---:|---:|")

    for detail in sprint_details:
        sprint = detail["sprint"]

        lines.append(
            f"| {sprint['name']} | {sprint['start']} a {sprint['end']} | "
            f"{len(detail['commits'])} | {len(detail['prs'])} | {len(detail['reviews'])} |"
        )

    add_counter_table(
        lines,
        "Distribución global de commits por integrante",
        "Integrante",
        "Commits",
        global_commits_by_member
    )

    add_counter_table(
        lines,
        "Distribución global de PRs integrados por integrante",
        "Integrante",
        "PRs integrados",
        global_prs_by_member
    )

    add_counter_table(
        lines,
        "Distribución global de revisiones por integrante",
        "Integrante",
        "Revisiones",
        global_reviews_by_member
    )

    for detail in sprint_details:
        add_sprint_detail(lines, detail)

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"Reporte generado en {OUTPUT_PATH}")


if __name__ == "__main__":
    build_report()

