from datetime import timedelta

from flask import Blueprint, abort, g, redirect, render_template, request

import models as db
from utils import utcnow

bp = Blueprint('challenges', __name__)


@bp.route('/challenge')
def challenge_index():
    return redirect('/challenge/list')


@bp.route('/challenge/list')
def challenge_list():
    # return abort(404)
    challenges = db.Challenge.select()\
        .order_by(db.Challenge.solved_count, db.Challenge.category, db.Challenge.title)

    event = request.args.get('event', '')
    if event not in g.event_dict and event not in {'', 'all'}:
        return abort(404)
    if event not in {'', 'all'}:
        challenges = challenges.where(db.Challenge.event == event)

    category = request.args.get('category', '')
    if category not in g.category_dict and category not in {'', 'all'}:
        return abort(404)
    if category not in {'', 'all'}:
        challenges = challenges.where(db.Challenge.category == category)

    if g.user:
        query = db.Submission.select()\
            .where(db.Submission.status == 'CORRECT')\
            .where(db.Submission.user_id == g.user.id)
        solved = {e.challenge_id for e in query}
        status = 'all'
        if request.args.get('status') in {'solved', 'not-solved'}:
            status = request.args['status']

    return render_template('challenge/list.html', **locals())


@bp.route('/challenge/<int:challenge_id>', methods=['GET', 'POST'])
def challenge_view(challenge_id):
    challenge = db.Challenge.get_or_404(db.Challenge.id == challenge_id)

    solved_users = db.Submission.select()\
        .where(db.Submission.status == 'CORRECT')\
        .where(db.Submission.challenge_id == challenge_id)\
        .order_by(db.Submission.created_at.desc())
    users = {u.id: u for u in db.User.select()}

    if not g.user:
        return render_template('challenge/view.html', **locals())

    assert g.user

    solved = db.Submission.select()\
        .where(db.Submission.status == 'CORRECT')\
        .where(db.Submission.challenge_id == challenge_id)\
        .where(db.Submission.user_id == g.user.id)\
        .get_or_none()

    if request.method == 'POST' and request.form['action'] == 'flag':  #2
        # status: already solved
        if solved:
            return redirect(request.path)

        # status: brute-force attempt
        recent = db.Submission().select()\
            .where(db.Submission.user_id == g.user.id)\
            .where(db.Submission.challenge_id == challenge_id)\
            .where(db.Submission.status == 'INCORRECT')\
            .order_by(db.Submission.id.desc())\
            .get_or_none()

        if recent and recent.created_at + timedelta(seconds=30) >= utcnow():
            status = 'brute_force_attempt'
            wait = (recent.created_at + timedelta(seconds=30)) - utcnow()
            return render_template('challenge/view.html', **locals())

        # status: incorrect
        submission = db.Submission()
        submission.challenge_id = challenge_id
        submission.user_id = g.user.id
        submission.flag = request.form['flag']
        if request.form['flag'] != challenge.flag:
            submission.status = 'INCORRECT'
            submission.save()
            status = 'incorrect'
            return render_template('challenge/view.html', **locals())

        # status: correct
        submission.status = 'CORRECT'
        submission.save()
        status = 'correct'

        solved_count = db.Submission.select()\
            .where(db.Submission.challenge_id == challenge_id)\
            .where(db.Submission.status == 'CORRECT')\
            .count()
        new_score = max(10, 1000 - solved_count * (solved_count - 1) // 2)
        old_score = challenge.score
        if new_score != old_score:
            challenge.score = new_score
        challenge.solved_count += 1
        challenge.save()
        g.user.solved_count += 1
        g.user.scores += new_score
        g.user.save()

        if solved_count <= 45:
            query = db.Submission.select()\
                .where(db.Submission.challenge_id == challenge_id)\
                .where(db.Submission.status == 'CORRECT')
            for s in query:
                if s.user_id == g.user.id:
                    continue
                user = db.User.get_or_none(db.User.id == s.user_id)
                user.scores = user.scores - old_score + new_score
                user.save()

        return render_template('challenge/view.html', **locals())
        # endfold2

    return render_template('challenge/view.html', **locals())
