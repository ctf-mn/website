import os
from datetime import UTC, datetime

import peewee
from playhouse.db_url import connect
from playhouse.flask_utils import get_object_or_404

database = connect(os.environ['DATABASE_URL'])

def utcnow():
    return datetime.now(UTC).replace(tzinfo=None)

class Model(database.Model):
    @classmethod
    def get_or_404(cls, *expressions):
        return get_object_or_404(cls, *expressions)


# models
class User(Model):
    name = peewee.CharField()
    email = peewee.CharField()
    password = peewee.CharField()
    scores = peewee.IntegerField()
    solved_count = peewee.IntegerField()

    last_solved_at = peewee.DateTimeField(null=True)
    updated_at = peewee.DateTimeField(null=True)
    created_at = peewee.DateTimeField(default=utcnow)

    class Meta:
        table_name = 'ctf_mn--user'

    def link(self):
        return f'/user/{self.name}'

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = utcnow()
        return super().save(*args, **kwargs)


class Challenge(Model):
    title = peewee.CharField()
    content = peewee.TextField()
    flag = peewee.CharField()
    author = peewee.CharField()
    category = peewee.CharField()
    event = peewee.CharField()

    score = peewee.IntegerField()
    solved_count = peewee.IntegerField()

    updated_at = peewee.DateTimeField(null=True)
    created_at = peewee.DateTimeField(default=utcnow)

    class Meta:
        table_name = 'ctf_mn--challenge'

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = utcnow()
        return super().save(*args, **kwargs)


class Submission(Model):
    user_id = peewee.IntegerField()
    challenge_id = peewee.IntegerField()
    flag = peewee.CharField()
    status = peewee.CharField()  # CORRECT, INCORRECT

    updated_at = peewee.DateTimeField(null=True)
    created_at = peewee.DateTimeField(default=utcnow)

    class Meta:
        table_name = 'ctf_mn--submission'

    @property
    def challenge(self):
        return Challenge.get_or_none(Challenge.id == self.challenge_id)

    @property
    def user(self):
        return User.get_or_none(User.id == self.user_id)

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = utcnow()
        return super().save(*args, **kwargs)


# contest
class Contest(Model):
    title = peewee.CharField()
    status = peewee.CharField()  # DRAFT, ACTIVE, FINISHED
    start_at = peewee.DateTimeField()
    finish_at = peewee.DateTimeField()

    updated_at = peewee.DateTimeField(null=True)
    created_at = peewee.DateTimeField(default=utcnow)

    class Meta:
        table_name = 'ctf_mn--contest'

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = utcnow()
        return super().save(*args, **kwargs)


class ContestTeam(Model):
    contest_id = peewee.IntegerField()
    title = peewee.CharField()
    status = peewee.CharField()  # DRAFT, ACTIVE
    members = peewee.CharField()  # |id1|id2|id3|
    service = peewee.CharField()

    scores = peewee.IntegerField()
    solved_count = peewee.IntegerField()
    last_solved_at = peewee.DateTimeField(null=True)

    updated_at = peewee.DateTimeField(null=True)
    created_at = peewee.DateTimeField(default=utcnow)

    @property
    def member_users(self):
        result = []
        if self.members == '|':
            return result
        for name in self.members.strip('|').split('|'):
            result.append(User.get(User.name == name))
        return result

    class Meta:
        table_name = 'ctf_mn--contest_team'

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = utcnow()
        return super().save(*args, **kwargs)


class ContestChallenge(Model):
    contest = peewee.ForeignKeyField(Contest)

    title = peewee.CharField()
    content = peewee.TextField()
    flag = peewee.CharField()
    author = peewee.CharField()
    category = peewee.CharField()

    score = peewee.IntegerField()
    solved_count = peewee.IntegerField()

    updated_at = peewee.DateTimeField(null=True)
    created_at = peewee.DateTimeField(default=utcnow)

    class Meta:
        table_name = 'ctf_mn--contest_challenge'

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = utcnow()
        return super().save(*args, **kwargs)


class ContestSubmission(Model):
    contest = peewee.ForeignKeyField(Contest)
    challenge = peewee.ForeignKeyField(ContestChallenge)
    team = peewee.ForeignKeyField(ContestTeam)
    user = peewee.ForeignKeyField(User)

    flag = peewee.CharField()
    flag_data = peewee.CharField()
    status = peewee.CharField()  # CORRECT, INCORRECT

    updated_at = peewee.DateTimeField(null=True)
    created_at = peewee.DateTimeField(default=utcnow)

    class Meta:
        table_name = 'ctf_mn--contest_submission'

    def save(self, *args, **kwargs):
        if self.id:
            self.updated_at = utcnow()
        return super().save(*args, **kwargs)
