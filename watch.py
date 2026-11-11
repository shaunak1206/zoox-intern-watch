"""Watch Zoox's Lever job board and open a GitHub issue for each new software-oriented internship."""
import json, os, re, sys, urllib.request

API = "https://api.lever.co/v0/postings/zoox?mode=json"
SEEN_FILE = "seen.json"
NOTIFY = os.environ.get("NOTIFY", "shaunak1206")
TEST = os.environ.get("TEST", "").lower() == "true"

SOFTWARE_TEAMS = re.compile(r"software|data science|information technology|autonomy|perception|planning|simulation|machine learning|\bai\b|infrastructure|firmware", re.I)
SOFTWARE_TITLE = re.compile(r"software|\bswe\b|\bai\b|machine learning|\bml\b|data scien|data engineer|autonomy|perception|planning|prediction|simulation|infrastructure|platform|computer vision|robotics|developer|backend|front.?end|full.?stack|firmware|embedded|applications|security|cloud|devops|compiler|gpu|deep learning|localization|mapping|tools", re.I)
NOT_SOFTWARE = re.compile(r"mechanical|manufacturing|hardware engineer|program manag|process improvement|safety reporting|finance|marketing|legal|people|recruit|supply chain|procurement|facilities|industrial", re.I)


def fetch(url, data=None, method="GET"):
    req = urllib.request.Request(url, data=data, method=method, headers={"User-Agent": "zoox-intern-watch"})
    if "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {os.environ['GH_TOKEN']}")
        req.add_header("Accept", "application/vnd.github+json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def is_intern(p):
    c = p.get("categories") or {}
    return bool(re.search(r"\bintern(ship)?\b|co-?op", f"{p['text']} {c.get('commitment', '')}", re.I))


def is_software(p):
    c = p.get("categories") or {}
    if NOT_SOFTWARE.search(p["text"]) and not re.search(r"software", p["text"], re.I):
        return False
    return bool(SOFTWARE_TITLE.search(p["text"]) or SOFTWARE_TEAMS.search(c.get("team") or ""))


def open_issue(p, test=False):
    c = p.get("categories") or {}
    title = ("[TEST] " if test else "") + f"New Zoox internship: {p['text']}"
    body = (
        f"@{NOTIFY} Zoox posted a new software-oriented internship.\n\n"
        f"**{p['text']}**\n"
        f"- Team: {c.get('team') or 'n/a'}\n"
        f"- Location: {c.get('location') or 'n/a'}\n"
        f"- Posting: {p['hostedUrl']}\n"
        f"- Apply: {p.get('applyUrl') or p['hostedUrl']}\n"
    )
    if test:
        body = "This is a test notification to confirm the watcher can reach you. Close it anytime.\n\n" + body
    repo = os.environ["REPO"]
    issue = fetch(f"https://api.github.com/repos/{repo}/issues", json.dumps({"title": title, "body": body}).encode(), "POST")
    print("opened issue", issue["html_url"])


def main():
    postings = fetch(API)
    if not isinstance(postings, list) or len(postings) < 20:
        sys.exit(f"Zoox board looks wrong: got {type(postings).__name__} with {len(postings) if isinstance(postings, list) else 0} postings")
    interns = [p for p in postings if is_intern(p)]
    software = [p for p in interns if is_software(p)]
    seen = set(json.load(open(SEEN_FILE))) if os.path.exists(SEEN_FILE) else set()
    print(f"{len(postings)} postings, {len(interns)} internships, {len(software)} software-oriented, {len(seen)} already seen")
    if TEST:
        open_issue(max(software or interns, key=lambda p: p.get("createdAt", 0)), test=True)
        return
    for p in sorted(software, key=lambda p: p.get("createdAt", 0)):
        if p["id"] not in seen:
            open_issue(p)
    seen |= {p["id"] for p in interns}
    json.dump(sorted(seen), open(SEEN_FILE, "w"), indent=1)


if __name__ == "__main__":
    main()
