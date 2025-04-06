import requests
import os
from dotenv import load_dotenv
load_dotenv()

GITHUB_API_URL = "https://api.github.com"
TOKEN = os.environ.get('TOKEN')


def commit_history_file(repo_url: str, file_path: str):
    response = requests.get(
        f'{GITHUB_API_URL}/repos/{repo_url}/commits?path={file_path}&per_page=100', headers={'Authorization': f'Bearer {TOKEN}'})

    if not response.ok:
        raise Exception(f'Cannot get commits list: {response.text}')

    return response.json()
