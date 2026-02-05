import os
from datetime import timedelta

import peewee
from flask import Flask, g, redirect, request, session
from flask_seasurf import SeaSurf

import models as db
from blueprints.api import bp as api_bp
from blueprints.auth import bp as auth_bp
from blueprints.challenges import bp as challenges_bp
from blueprints.contests import bp as contests_bp
from blueprints.core import bp as core_bp
from utils import utcnow

app = Flask(__name__)
app.secret_key = os.environ['SESSION_KEY']
app.jinja_options = {
    'line_comment_prefix': '#:',
    'line_statement_prefix': '%',
    'keep_trailing_newline': True,
    'extensions': ['jinja2.ext.loopcontrols', 'jinja2.ext.do'],
}
app.jinja_env.add_extension('utils.JinjaExt')
csrf = SeaSurf(app)
csrf._exempt_views.add('blueprints.api.api_challenge')
csrf._exempt_views.add('blueprints.api.api_contest_challenge')
app.register_blueprint(auth_bp)
app.register_blueprint(core_bp)
app.register_blueprint(challenges_bp)
app.register_blueprint(contests_bp)
app.register_blueprint(api_bp)

#1 before first request
with app.app_context():
    #2 Connect to database
    db.database.connect()

    #2 Create tables
    tables = []
    for f in dir(db):
        possible_model = getattr(db, f)
        if not repr(possible_model).startswith('<Model: '):
            continue
        if repr(possible_model) == '<Model: Model>':
            continue
        tables.append(possible_model)
    db.database.create_tables(tables)

    #2 Fix table sequences (on local)
    if os.environ.get('FLASK_DEBUG'):
        for f in dir(db):
            possible_model = getattr(db, f)
            if not repr(possible_model).startswith('<Model: '):
                continue
            if repr(possible_model) == '<Model: Model>':
                continue

            table_name = possible_model._meta.table_name
            query = f'''SELECT SETVAL('{table_name}_id_seq', (SELECT MAX(id)  FROM "{table_name}"));'''
            db.database.execute_sql(query)


@app.before_request
def before_request():
    try:
        db.database.connect()
    except peewee.OperationalError:
        pass

    if request.host == 'www.ctf.mn':
        url = request.url.replace('www.', '', 1)
        url = url.replace('http://', 'https://', 1)
        code = 301  # permanent
        return redirect(url, code=code)

    # if request.url.startswith('http://'):
    #     url = request.url.replace('http://', 'https://', 1)
    #     code = 301  # permanent
    #     return redirect(url, code=code)

    if session.get('user'):
        g.user = db.User.get_or_none(db.User.email == session['user']['email'])
        try:
            g.contest = db.Contest.get(db.Contest.id == 4)
            g.contest_team = db.ContestTeam.select()\
                .where(db.ContestTeam.contest_id == g.contest.id)\
                .where(db.ContestTeam.members.contains(f'|{g.user.name}|'))\
                .get_or_none()
        except db.Contest.DoesNotExist:
            pass
    else:
        g.user = None

    g.category_list = [
        ('crypto', 'Cryptography'),
        ('forensic', 'Forensics'),
        ('misc', 'Miscellaneous'),
        ('osint', 'OSINT'),
        ('programming', 'Programming'),
        ('pwn', 'Pwn'),
        ('reverse', 'Reverse Engineering'),
        ('stego', 'Steganography'),
        ('web', 'Web'),
    ]
    g.category_dict = {k: v for k, v in g.category_list}
    g.event_list = [
        ('haruulzangi-2013', 'Харуул Занги: 2013'),
        ('haruulzangi-2018', 'Харуул Занги: 2018'),
        ('haruulzangi-2019', 'Харуул Занги: 2019'),
        ('haruulzangi-2020', 'Харуул Занги: 2020'),
        ('haruulzangi-2021', 'Харуул Занги: 2021'),
        ('haruulzangi-2022', 'Харуул Занги: 2022'),
        ('haruulzangi-2023', 'Харуул Занги: 2023'),
        ('haruulzangi-2024', 'Харуул Занги: 2024'),
        ('haruulzangi-2025', 'Харуул Занги: 2025'),

        ('haruulzangi-u18-2017', 'Харуул Занги U18: 2017'),
        ('haruulzangi-u18-2018', 'Харуул Занги U18: 2018'),
        ('haruulzangi-u18-2022', 'Харуул Занги U18: 2022'),
        ('haruulzangi-u18-2023', 'Харуул Занги U18: 2023'),
        ('haruulzangi-u18-2024', 'Харуул Занги U18: 2024'),
        ('haruulzangi-u18-2025', 'Харуул Занги U18: 2025'),

        ('must-2023', 'MUST CTF: 2023'),
        ('must-2024', 'MUST CTF: 2024'),
        ('must-2025', 'MUST CTF: 2025'),

        ('ctf-mn', 'CTF.mn league'),
        ('mazala', 'Mazala'),
        ('shambala', 'Shambala'),
        ('ccs', 'CCS Club')
    ]
    g.event_dict = {k: v for k, v in g.event_list}
    g.timezone_fix = timedelta(hours=8)


@app.after_request
def after_request(response):
    db.database.close()
    return response


@app.context_processor
def context_processor():
    return {
        'now': utcnow(),
        'timedelta': timedelta,
    }
