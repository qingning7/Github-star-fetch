# GitHub Stars Counter

This small script fetches the total number of stars across all public repositories
for a given GitHub username using the GitHub REST API.

## Requirements
- Python 3.10+
- `requests`

## Install
```
pip install -r requirements.txt
```

## Run
```
python github_stars.py <username>
```

Optional token (helps avoid rate limits):
```
python github_stars.py <username> --token <token>
```

Or use environment variable:
```
set GITHUB_TOKEN=YOUR_TOKEN
python github_stars.py <username>
```

## Notes
- This counts **public** repositories by default.
- Private repositories require a token that has access to them.
- If you hit rate limits, the script will tell you when you can retry.
