import os

from flask import Blueprint, abort, g, request

import models as db

bp = Blueprint('api', __name__)


@bp.route('/api/contest-challenge', methods=['POST'])
def api_contest_challenge():
    if request.form.get('key') != os.environ['API_CHALLENGE_KEY']:
        return abort(404)

    # validate
    if request.form['category'] not in g.category_dict:
        return {'error': 'Unknown category: ' + request.form['category']}

    c = db.ContestChallenge.get_or_none(db.ContestChallenge.id == int(request.form.get('id')))
    force_insert = False
    if not c:
        force_insert = True
        c = db.ContestChallenge(score=1000, solved_count=0, id=int(request.form.get('id')))

    old = {
        'name': c.title,
        'description': c.content,
        'author': c.author,
        'category': c.category,
        'flag': c.flag,
    }
    c.contest_id = int(request.form['contest'])
    c.title = request.form['name']
    c.content = request.form['description']
    c.author = request.form['author']
    c.category = request.form['category']
    c.flag = request.form['flag']
    new = {
        'name': c.title,
        'description': c.content,
        'author': c.author,
        'category': c.category,
        'flag': c.flag,
    }
    for k in list(old.keys()):
        if old[k] == new[k]:
            old.pop(k)
            new.pop(k)
    c.save(force_insert=force_insert)

    return {'old': old, 'new': new}
    # endfold2


@bp.route('/api/challenge', methods=['POST'])
def api_challenge():
    if request.form.get('key') != os.environ['API_CHALLENGE_KEY']:
        return abort(404)

    # validate
    if request.form['event'] not in g.event_dict:
        return {'error': 'Unregistered event: ' + request.form['event']}
    if request.form['category'] not in g.category_dict:
        return {'error': 'Unknown category: ' + request.form['category']}

    c = db.Challenge.get_or_none(db.Challenge.id == int(request.form.get('id')))
    force_insert = False
    if not c:
        force_insert = True
        c = db.Challenge(score=1000, solved_count=0, id=int(request.form.get('id')))

    old = {
        'name': c.title,
        'description': c.content,
        'author': c.author,
        'event': c.event,
        'category': c.category,
        'flag': c.flag,
    }
    c.title = request.form['name']
    c.content = request.form['description']
    c.author = request.form['author']
    c.event = request.form['event']
    c.category = request.form['category']
    c.flag = request.form['flag']
    new = {
        'name': c.title,
        'description': c.content,
        'author': c.author,
        'event': c.event,
        'category': c.category,
        'flag': c.flag,
    }
    for k in list(old.keys()):
        if old[k] == new[k]:
            old.pop(k)
            new.pop(k)
    c.save(force_insert=force_insert)

    return {'old': old, 'new': new}
