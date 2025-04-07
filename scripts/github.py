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


def get_commit_changes(repo_url: str, sha: str) -> dict:
    latest_run = get_latest_workflow(repo_url)['workflow_runs'][0]['head_sha']
    response = requests.get(
        f'{GITHUB_API_URL}/repos/{repo_url}/compare/{latest_run}...{sha}', headers={'Authorization': f'Bearer {TOKEN}'})

    if not response.ok:
        raise Exception(f'Cannot get commit changes: {response.text}')

    return response.json()


def get_latest_workflow(repo_url: str):
    response = requests.get(
        f'{GITHUB_API_URL}/repos/{repo_url}/actions/workflows/index.yaml/runs?status=success&branch=master&per_page=1', headers={'Authorization': f'Bearer {TOKEN}'})

    if not response.ok:
        raise Exception(f'Cannot get latest workflow run: {response.text}')

    return response.json()
