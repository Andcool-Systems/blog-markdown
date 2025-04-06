from github import commit_history_file
import logging
import os
import json
from dotenv import load_dotenv
load_dotenv()


PAGES_PATH = 'pages'
REPO_PATH = os.environ.get('REPO_PATH') or 'Andcool-Systems/blog-markdown'


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


with open('index.json', 'r') as index_f:
    index_json = json.load(index_f)


pages = os.listdir(PAGES_PATH)
for page in pages:
    path = f'{PAGES_PATH}/{page}'
    check_page(path)

    commits = commit_history_file(REPO_PATH, f'{path}/page.md')
    if page not in index_json:
        file_meta = get_meta_for_page(path)
        author = commits[-1]['commit']['committer']

        index_json['page'] = {
            'title': file_meta['title'],
            'description': file_meta['description'],
            'created': author['date'],
            'original_author': author['name']
        }

print(index_json)
