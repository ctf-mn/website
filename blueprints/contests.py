import math
from datetime import timedelta

from flask import Blueprint, abort, g, redirect, render_template, request

import models as db
from utils import utcnow

bp = Blueprint('contests', __name__)


@bp.route('/contest/<int:contest_id>', methods=['GET', 'POST'])
def contest_scoreboard(contest_id):
    contest = db.Contest.get_or_404(db.Contest.id == contest_id)
    teams = db.ContestTeam.select()\
        .where(db.ContestTeam.contest_id == contest_id)\
        .order_by(db.ContestTeam.scores.desc(), db.ContestTeam.last_solved_at, db.ContestTeam.id)

    if request.args.get('status') == 'success':  #2
        return render_template('contest/scoreboard--success.html', **locals())
    # endfold2
    if request.method == 'POST':  #2
        # return redirect(request.path)
        if contest_id != 5:
            return redirect(request.path)

        db.ContestTeam.create(
            contest_id=contest_id,
            members=f'|{g.user.name}|' if g.user else '|',
            title=request.form.get('title'),
            service='',
            status='DRAFT',
            scores=0,
            solved_count=0,
        )
        return redirect(f'/contest/{contest_id}?status=success')
    # endfold2

    return render_template('contest/scoreboard.html', **locals())


@bp.route('/contest/<int:contest_id>/challenge')
def contest_challenge_index(contest_id):
    return redirect(f'/contest/{contest_id}/challenge/list')


@bp.route('/contest/<int:contest_id>/challenge/list')
def contest_challenge_list(contest_id):
    contest = db.Contest.get_or_404(db.Contest.id == contest_id)

    if contest.start_at < utcnow():
        challenges = db.ContestChallenge.select()\
            .where(db.ContestChallenge.contest_id == contest_id)\
            .order_by(db.ContestChallenge.category, db.ContestChallenge.id)
    else:
        challenges = []

    if g.user and g.contest_team:
        query = db.ContestSubmission.select()\
            .where(db.ContestSubmission.status == 'CORRECT')\
            .where(db.ContestSubmission.team_id == g.contest_team.id)
        solved = {e.challenge_id for e in query}

    return render_template('contest/challenges.html', **locals())


@bp.route('/contest/<int:contest_id>/challenge/<int:challenge_id>', methods=['GET', 'POST'])
def contest_challenge_view(contest_id, challenge_id):
    if not (g.user and g.contest_team):
        return abort(404)

    contest = db.Contest.get_or_404(db.Contest.id == contest_id)

    challenge = db.ContestChallenge.get_or_404(db.ContestChallenge.id == challenge_id)
    solved = db.ContestSubmission.select()\
        .where(db.ContestSubmission.status == 'CORRECT')\
        .where(db.ContestSubmission.challenge_id == challenge_id)\
        .where(db.ContestSubmission.team_id == g.contest_team.id)\
        .get_or_none()
    solved_teams = db.ContestSubmission.select()\
        .where(db.ContestSubmission.status == 'CORRECT')\
        .where(db.ContestSubmission.challenge_id == challenge_id)\
        .order_by(db.ContestSubmission.created_at.desc())

    if request.method == 'POST' and request.form['action'] == 'flag':  #2
        if contest.finish_at < utcnow():
            return redirect(request.path)

        if solved:
            return redirect(request.path)

        #3 status: brute-force attempt
        recent = db.ContestSubmission().select()\
            .where(db.ContestSubmission.user_id == g.user.id)\
            .where(db.ContestSubmission.challenge_id == challenge_id)\
            .where(db.ContestSubmission.status == 'INCORRECT')\
            .order_by(db.ContestSubmission.id.desc())\
            .get_or_none()

        if recent and recent.created_at + timedelta(seconds=30) >= utcnow():
            status = 'brute_force_attempt'
            wait = (recent.created_at + timedelta(seconds=30)) - utcnow()
            return render_template('contest/challenge_view.html', **locals())
        # endfold3
        #3 status: incorrect
        submission = db.ContestSubmission()
        submission.contest_id = contest_id
        submission.challenge_id = challenge_id
        submission.team_id = g.contest_team.id
        submission.user_id = g.user.id
        submission.flag = request.form['flag']

        correct = False
        if challenge.flag == request.form['flag']:
            correct = True
        if not correct:
            submission.status = 'INCORRECT'
            submission.save()
            status = 'incorrect'
            return render_template('contest/challenge_view.html', **locals())
        # endfold3
        #3 status: correct
        submission.status = 'CORRECT'
        submission.save()
        status = 'correct'

        solved_count = db.ContestSubmission.select()\
            .where(db.ContestSubmission.challenge_id == challenge_id)\
            .where(db.ContestSubmission.status == 'CORRECT')\
            .count()
        initial, minimum, decay = 1000, 10, 15
        new_score = math.ceil((((minimum - initial) / (decay ** 2)) * ((solved_count - 1) ** 2)) + initial)
        old_score = challenge.score
        if new_score != old_score:
            challenge.score = new_score
        challenge.solved_count += 1
        challenge.save()

        g.contest_team.solved_count += 1
        g.contest_team.scores += new_score
        g.contest_team.last_solved_at = utcnow()
        g.contest_team.save()

        # update other team scores
        query = db.ContestSubmission.select()\
            .where(db.ContestSubmission.challenge_id == challenge_id)\
            .where(db.ContestSubmission.status == 'CORRECT')
        for s in query:
            if s.team_id == g.contest_team.id:
                continue
            team = db.ContestTeam.get(db.ContestTeam.id == s.team_id)
            team.scores = team.scores - old_score + new_score
            team.save()
        # endfold3

        return render_template('contest/challenge_view.html', **locals())
    # endfold2

    return render_template('contest/challenge_view.html', **locals())


@bp.route('/contest/<int:contest_id>/activity')
def contest_activity(contest_id):
    contest = db.Contest.get_or_404(db.Contest.id == contest_id)
    teams = {e.id: e.title for e in db.ContestTeam.select().where(db.ContestTeam.contest_id == contest_id)}
    users = {}
    for t in db.ContestTeam.select().where(db.ContestTeam.contest_id == contest_id):
        for u in t.member_users:
            users[u.id] = u.name
    challenges = {e.id: e.title for e in db.ContestChallenge.select().where(db.ContestChallenge.contest_id == contest_id)}

    submissions = db.ContestSubmission.select()\
        .where(db.ContestSubmission.contest_id == contest_id)\
        .order_by(db.ContestSubmission.id.desc())\

    return render_template('contest/activity.html', **locals())
