import json
import urllib.request
import urllib.error
import os
from mcp.server.fastmcp import FastMCP

# ── GitHub Personal Access Token ──
GITHUB_TOKEN = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "")

mcp = FastMCP("GitHub-MCP-Server")

def github_request(endpoint: str) -> dict:
    """Makes an authenticated GET request to GitHub REST API."""
    url = f"https://api.github.com{endpoint}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "GitHub-MCP-Server")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_my_profile() -> str:
    """Returns the authenticated GitHub user's profile information."""
    data = github_request("/user")
    if "error" in data:
        return f"Error: {data['error']}"
    return json.dumps({
        "username":    data.get("login"),
        "name":        data.get("name"),
        "email":       data.get("email"),
        "company":     data.get("company"),
        "location":    data.get("location"),
        "public_repos": data.get("public_repos"),
        "followers":   data.get("followers"),
        "following":   data.get("following"),
        "profile_url": data.get("html_url")
    }, indent=2)


@mcp.tool()
def list_my_repositories(repo_type: str = "all", sort: str = "updated") -> str:
    """
    Lists all repositories for the authenticated user.
    repo_type: all | public | private | forks | sources
    sort: updated | created | pushed | full_name
    """
    data = github_request(f"/user/repos?type={repo_type}&sort={sort}&per_page=30")
    if isinstance(data, dict) and "error" in data:
        return f"Error: {data['error']}"
    repos = []
    for r in data:
        repos.append({
            "name":        r.get("name"),
            "full_name":   r.get("full_name"),
            "description": r.get("description"),
            "language":    r.get("language"),
            "stars":       r.get("stargazers_count"),
            "forks":       r.get("forks_count"),
            "visibility":  r.get("visibility"),
            "updated_at":  r.get("updated_at"),
            "url":         r.get("html_url")
        })
    return json.dumps(repos, indent=2)


@mcp.tool()
def get_repository(owner: str, repo: str) -> str:
    """
    Returns details of a specific GitHub repository.
    owner: GitHub username or org name
    repo: repository name
    """
    data = github_request(f"/repos/{owner}/{repo}")
    if "error" in data:
        return f"Error: {data['error']}"
    return json.dumps({
        "name":           data.get("name"),
        "full_name":      data.get("full_name"),
        "description":    data.get("description"),
        "language":       data.get("language"),
        "stars":          data.get("stargazers_count"),
        "forks":          data.get("forks_count"),
        "open_issues":    data.get("open_issues_count"),
        "default_branch": data.get("default_branch"),
        "visibility":     data.get("visibility"),
        "created_at":     data.get("created_at"),
        "updated_at":     data.get("updated_at"),
        "url":            data.get("html_url")
    }, indent=2)


@mcp.tool()
def list_repository_issues(owner: str, repo: str, state: str = "open") -> str:
    """
    Lists issues for a GitHub repository.
    owner: GitHub username or org name
    repo: repository name
    state: open | closed | all
    """
    data = github_request(f"/repos/{owner}/{repo}/issues?state={state}&per_page=20")
    if isinstance(data, dict) and "error" in data:
        return f"Error: {data['error']}"
    issues = []
    for i in data:
        if "pull_request" in i:
            continue  # skip PRs
        issues.append({
            "number":     i.get("number"),
            "title":      i.get("title"),
            "state":      i.get("state"),
            "author":     i.get("user", {}).get("login"),
            "labels":     [l.get("name") for l in i.get("labels", [])],
            "created_at": i.get("created_at"),
            "url":        i.get("html_url")
        })
    return json.dumps(issues, indent=2)


@mcp.tool()
def list_recent_commits(owner: str, repo: str, branch: str = "main") -> str:
    """
    Lists recent commits for a GitHub repository.
    owner: GitHub username or org name
    repo: repository name
    branch: branch name (default: main)
    """
    data = github_request(f"/repos/{owner}/{repo}/commits?sha={branch}&per_page=10")
    if isinstance(data, dict) and "error" in data:
        return f"Error: {data['error']}"
    commits = []
    for c in data:
        commits.append({
            "sha":     c.get("sha", "")[:7],
            "message": c.get("commit", {}).get("message", "").split("\n")[0],
            "author":  c.get("commit", {}).get("author", {}).get("name"),
            "date":    c.get("commit", {}).get("author", {}).get("date"),
            "url":     c.get("html_url")
        })
    return json.dumps(commits, indent=2)


@mcp.tool()
def list_pull_requests(owner: str, repo: str, state: str = "open") -> str:
    """
    Lists pull requests for a GitHub repository.
    owner: GitHub username or org name
    repo: repository name
    state: open | closed | all
    """
    data = github_request(f"/repos/{owner}/{repo}/pulls?state={state}&per_page=20")
    if isinstance(data, dict) and "error" in data:
        return f"Error: {data['error']}"
    prs = []
    for pr in data:
        prs.append({
            "number":     pr.get("number"),
            "title":      pr.get("title"),
            "state":      pr.get("state"),
            "author":     pr.get("user", {}).get("login"),
            "base":       pr.get("base", {}).get("ref"),
            "head":       pr.get("head", {}).get("ref"),
            "created_at": pr.get("created_at"),
            "url":        pr.get("html_url")
        })
    return json.dumps(prs, indent=2)


@mcp.tool()
def search_repositories(query: str, sort: str = "stars") -> str:
    """
    Searches GitHub public repositories by keyword.
    query: search keyword (e.g. 'mcp server python')
    sort: stars | forks | updated
    """
    encoded_query = query.replace(" ", "+")
    data = github_request(f"/search/repositories?q={encoded_query}&sort={sort}&per_page=10")
    if "error" in data:
        return f"Error: {data['error']}"
    results = []
    for r in data.get("items", []):
        results.append({
            "name":        r.get("full_name"),
            "description": r.get("description"),
            "language":    r.get("language"),
            "stars":       r.get("stargazers_count"),
            "url":         r.get("html_url")
        })
    return json.dumps(results, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
