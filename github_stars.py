import argparse
import os
import sys
import time
from datetime import datetime, timezone

import requests


# 读取 HTTP 响应头里的时间戳，并转换成可读时间格式
def _rate_limit_reset_time(headers):
    reset = headers.get("X-RateLimit-Reset")
    if not reset:
        return None
    try:
        ts = int(reset)
    except ValueError:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def fetch_total_stars(username, token=None, per_page=100, timeout=10):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-stars-script",
    }
    if token:
        # GitHub accepts either "token" or "Bearer".
        headers["Authorization"] = f"Bearer {token}"

    total_stars = 0
    page = 1

    # 不断分页请求 GitHub API，直到没有仓库为止
    while True:
        url = f"https://api.github.com/users/{username}/repos"
        # 请求参数：每页数量和当前页码
        params = {"per_page": per_page, "page": page}
        
        # 发送 GET 请求，并设置超时时间
        resp = requests.get(url, headers=headers, params=params, timeout=timeout)
        
        # 处理可能的错误情况：用户不存在、速率限制等
        if resp.status_code == 404:
            raise ValueError(f"User not found: {username}")

        if resp.status_code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0":
            reset_time = _rate_limit_reset_time(resp.headers)
            if reset_time:
                raise RuntimeError(
                    f"Rate limit exceeded. Try again after {reset_time.isoformat()}"
                )
            raise RuntimeError("Rate limit exceeded. Try again later.")

        resp.raise_for_status()
        # 解析 JSON 响应，获取仓库列表
        repos = resp.json()

        if not repos:
            break

        for repo in repos:
            total_stars += int(repo.get("stargazers_count", 0))

        page += 1
        time.sleep(0.1)

    return total_stars


def main():
    # 设置命令行参数解析器，允许用户输入 GitHub 用户名、可选的 token、每页数量和超时时间
    parser = argparse.ArgumentParser(
        description="Sum stargazers_count across all public GitHub repos for a user."
    )
    parser.add_argument("username", help="GitHub username")
    parser.add_argument(
        "--token",
        help="GitHub token (or set GITHUB_TOKEN env var)",
        default=os.getenv("GITHUB_TOKEN"),
    )
    parser.add_argument("--per-page", type=int, default=100)
    parser.add_argument("--timeout", type=int, default=10)
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 调用函数获取总星数，并处理可能的异常情况
    try:
        total = fetch_total_stars(
            args.username, token=args.token, per_page=args.per_page, timeout=args.timeout
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"{args.username} total stars: {total}")


if __name__ == "__main__":
    main()
