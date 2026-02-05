from flask import Blueprint, abort, g, redirect, render_template, request

import models as db

bp = Blueprint('core', __name__)


@bp.route('/')
def index():
    return redirect('/challenge/list')


@bp.route('/scoreboard')
def scoreboard():
    page = int(request.args.get('page', '1'))
    per_page = 100
    users = db.User.select()\
        .order_by(db.User.scores.desc(), db.User.last_solved_at, db.User.id)\
        .paginate(page, per_page)
    total_page = (db.User.select().count() + per_page - 1) // per_page
    request_full_path = request.path

    return render_template('scoreboard.html', **locals())


@bp.route('/activity')
def activity():
    submissions = db.Submission.select()\
        .order_by(db.Submission.id.desc())\
        .limit(100)

    challenges = {c.id: c for c in db.Challenge.select()}
    users = {u.id: u for u in db.User.select()}

    return render_template('activity.html', **locals())


@bp.route('/discord')
def discord():
    return redirect('https://discord.gg/z9vfpxy5KS')


@bp.route('/user/<name>')
def user_profile(name):
    user = db.User.get_or_404(db.User.name == name)
    submissions = db.Submission.select()\
        .where(db.Submission.user_id == user.id)\
        .where(db.Submission.status == 'CORRECT')\
        .order_by(db.Submission.created_at.desc())
    challenges = {c.id: c for c in db.Challenge.select()}

    return render_template('user_profile.html', **locals())


@bp.route('/author/<name>')
def author_profile(name):
    challenges = db.Challenge.select()\
        .where(db.Challenge.author == name)\
        .order_by(db.Challenge.id.desc())
    if challenges.count() == 0:
        return abort(404)

    return render_template('author_profile.html', **locals())
