import os
import re
import urllib.request
import json

def get_pinned_repos(username, token):
    url = 'https://api.github.com/graphql'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    
    query = """
    {
      user(login: "%s") {
        pinnedItems(first: 6, types: REPOSITORY) {
          nodes {
            ... on Repository {
              name
            }
          }
        }
      }
    }
    """ % username

    data = json.dumps({'query': query}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            nodes = result.get('data', {}).get('user', {}).get('pinnedItems', {}).get('nodes', [])
            return [node['name'] for node in nodes if 'name' in node]
    except Exception as e:
        print(f"Error fetching pinned repos: {e}")
        return []

def generate_readme_content(repos, username):
    lines = ['<div align="center">']
    for repo in repos:
        lines.append(f'  <a href="https://github.com/{username}/{repo}">')
        lines.append(f'    <img src="https://my-github-readme-stats-brown.vercel.app/api/pin/?username={username}&repo={repo}&theme=transparent&title_color=0e75b6&icon_color=0e75b6" alt="{repo}" />')
        lines.append('  </a>')
    lines.append('</div>')
    return '\n'.join(lines)

def update_readme(new_content):
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()

        start_marker = "<!-- START_PINNED_REPOS -->"
        end_marker = "<!-- END_PINNED_REPOS -->"

        pattern = re.compile(f'{start_marker}.*?{end_marker}', re.DOTALL)
        
        replacement = f'{start_marker}\n{new_content}\n{end_marker}'
        updated_content = pattern.sub(replacement, content)

        if updated_content == content:
            print("No changes made. Markers not found or content is identical.")
        else:
            with open('README.md', 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print("README.md has been successfully updated.")

    except Exception as e:
        print(f"Error updating README.md: {e}")

if __name__ == "__main__":
    GITHUB_TOKEN = os.environ.get("GH_TOKEN")
    USERNAME = "JJYYY-JJY"

    if not GITHUB_TOKEN:
        print("Error: GH_TOKEN environment variable not set.")
        exit(1)

    repos = get_pinned_repos(USERNAME, GITHUB_TOKEN)
    if not repos:
        print("No pinned repositories found or failed to fetch.")
        exit(1)

    print(f"Found pinned repositories: {repos}")
    new_content = generate_readme_content(repos, USERNAME)
    update_readme(new_content)
