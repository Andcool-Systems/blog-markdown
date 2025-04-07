import github
import logging
import os
import re
import json
import sys
from dotenv import load_dotenv
load_dotenv()

PAGES_PATH = 'pages'
REPO_PATH = os.environ.get('REPO_PATH') or 'Andcool-Systems/blog-markdown'
COMMIT_SHA = os.environ.get('COMMIT_SHA')
RE_EXPR = r"[^\w\-\.~]"

logger = logging.getLogger('Index')
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S'
)


def check_meta(content: dict):
    if not content.get('title'):
        raise Exception('Key `title` cannot be empty or not found!')

    if not content.get('description'):
        raise Exception('Key `description` cannot be empty or not found!')


def get_meta_for_page(path: str):
    with open(f'{path}/meta.json', 'r', encoding='utf-8') as meta_file:
        return json.load(meta_file)


def check_page(path: str) -> bool:
    logger.log(logging.INFO, f'Checking {path} page')

    if not os.path.isfile(f'{path}/page.md'):
        raise FileNotFoundError(f'Page file on path {path}/page.md not found!')

    if not os.path.isfile(f'{path}/meta.json'):
        raise FileNotFoundError(
            f'Meta file on path {path}/meta.json not found!')

    with open(f'{path}/meta.json', 'r', encoding='utf-8') as meta_file:
        meta = json.load(meta_file)

    check_meta(meta)


with open('index.json', 'r', encoding='utf-8') as index_f:
    index_json = json.load(index_f)

affected_files = github.get_commit_changes(REPO_PATH, COMMIT_SHA).get('files')
if not affected_files:
    logger.log(logging.ERROR, 'No affected files found, exiting...')
    sys.exit(0)

affected_paths = list({
    '/'.join(file['filename'].split('/')[:2])
    for file in affected_files
    if file['filename'].startswith(f'{PAGES_PATH}/')
})

if not affected_paths:
    logger.log(logging.ERROR, 'No affected pages found, exiting...')
    sys.exit(0)

for path in affected_paths:
    page = path.replace(f'{PAGES_PATH}/', '')
    if re.search(RE_EXPR, page) or '/' in page:
        raise Exception(f'Page name contains forbidden characters!')
    check_page(path)

    logger.log(logging.INFO, 'Updating index...')
    commits = github.commit_history_file(REPO_PATH, f'{path}')

    counts = {}
    for commit in commits:
        login = commit['author']['login']
        counts[login] = counts.get(login, 0) + 1

    collaborators = [login for login, _ in sorted(
        counts.items(), key=lambda item: item[1], reverse=True)]

    file_meta = get_meta_for_page(path)
    if page not in index_json:
        author = commits[-1]['commit']['author']
        author_login = commits[-1]['author']['login']

        index_json[page] = {
            'title': file_meta['title'],
            'description': file_meta['description'],
            'created': author['date'],
            'original_author': author_login,
            'collaborators': collaborators
        }

    else:
        index_json[page]['title'] = file_meta['title']
        index_json[page]['description'] = file_meta['description']
        index_json[page]['collaborators'] = collaborators

with open('index.json', 'w+', encoding='utf-8') as index_file:
    json.dump(index_json, index_file, indent=4, ensure_ascii=False)

logger.log(logging.INFO, 'Index updated and saved to index.json')
