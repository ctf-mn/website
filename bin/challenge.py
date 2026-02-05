# /// script
# dependencies = ['httpx', 'pyyaml']
# ///
import os
import sys
from pathlib import Path

import httpx
import yaml

def parse():
    if len(sys.argv) < 2:
        print('Usage: python challenge.py path/to/challenge.yml')
        exit()
    else:
        path = sys.argv[1]

    with open(path) as f:
        result = yaml.safe_load(f)
    dir_path = str(Path(path).resolve().parent)
    slug = dir_path.rsplit('--', 1)[1]
    result['cwd'] = dir_path
    result['slug'] = slug
    return result


def key():
    return os.environ['CTF_MN_API_KEY']


def send(data):
    url = 'https://ctf.mn/api/challenge'
    data['key'] = key()
    r = httpx.post(url, data=data)
    open(Path(__file__).parent.joinpath('log.txt'), 'a').write(r.text + '\n\n')
    return r.text


def description(challenge):
    result = challenge['description']

    print('challenge:', challenge)
    if challenge['id'] < 400:
        address = '139.162.5.230'
    else:
        address = '139.59.230.119'

    if challenge.get('service') == 'web':
        result += f'\n\nhttp://{address}:10{challenge["id"]:03d}/'
    if challenge.get('service') == 'nc':
        result += f'\n\n```\nnc {address} 10{challenge["id"]:03d}\n```'

    if not challenge.get('files'):
        return result

    files = challenge['files']
    if isinstance(files, str):
        files = [files]

    base = '/Users/mb/ctf/CTF.mn/files'
    slug = f'{challenge["id"]:03d}' + '--' + challenge['slug']
    cwd = challenge.pop('cwd')
    category = challenge['category']

    if files:
        result += '\n**Files:**'
    for name in files:
        print(f'Copy file: {name}')
        os.system(f'mkdir -p {base}/{category}/{slug}')
        os.system(f'cp -u "{cwd}/files/{name}" "{base}/{category}/{slug}/{name}"')
        result += f'\n- [{name}](https://d17zlucxou2y8w.cloudfront.net/{category}/{slug}/{name})'

    os.system(f'cd {base}; ./sync.py {category}')
    return result


def contest_description(challenge):
    result = challenge['description']

    address = '139.162.5.230'
    address = '13.124.117.173'
    if challenge.get('service') == 'web':
        result += f'\n\nhttp://{address}:1{challenge["id"]:04d}/'
    if challenge.get('service') == 'nc':
        result += f'\n\n```\nnc {address} 1{challenge["id"]:04d}\n```'

    if not challenge.get('files'):
        return result

    files = challenge['files']
    if isinstance(files, str):
        files = [files]

    files = challenge['files']
    if isinstance(files, str):
        files = [files]

    base = '/Users/mb/ctf/CTF.mn/files'
    slug = f'{10000+challenge["id"]:03d}' + '--' + challenge['slug']
    category = challenge['category']

    if files:
        result += '\n**Files:**'
    for name in files:
        print(f'Copy file: {name}')
        os.system(f'mkdir -p {base}/{category}/{slug}')
        os.system(f'cp -u "files/{name}" "{base}/{category}/{slug}/{name}"')
        result += f'\n- [{name}](https://d17zlucxou2y8w.cloudfront.net/{category}/{slug}/{name})'

    os.system(f'cd {base}; ./sync.py {category}')
    return result


def contest_send(data):
    url = 'https://ctf.mn/api/contest-challenge'
    data['key'] = 'ja5ooKae8quahr4ieFiobeecoo3shuok'
    r = httpx.post(url, data=data)
    open(Path(__file__).parent.joinpath('log.txt'), 'a').write(r.text + '\n\n')
    return r.text


challenge = parse()
if 'contest' in challenge:
    data = {
        'name': challenge['name'],
        'contest': challenge['contest'],
        'author': challenge['author'],
        'category': challenge['category'],
        'description': contest_description(challenge),
        'flag': challenge['flag'],
        'id': challenge['id'],
    }
    print(contest_send(data))
    print(f'https://ctf.mn/contest/{challenge["contest"]}/challenge/{challenge["id"]}')
else:
    assert 'event' in challenge
    data = {
        'name': challenge['name'],
        'author': challenge['author'],
        'event': challenge['event'],
        'category': challenge['category'],
        'description': description(challenge),
        'flag': challenge['flag'],
        'id': challenge['id'],
    }
    print(send(data))
    print('https://ctf.mn/challenge/' + str(challenge['id']))
