import os
import re
from time import time

from flask import Blueprint, abort, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import models as db
import utils as fn

bp = Blueprint('auth', __name__)


@bp.route('/forgot-password/reset', methods=['GET', 'POST'])
def forgot_password():
    dic = {}
    if request.args.get('key') not in dic:
        return abort(404)

    if request.method == 'POST':
        user = db.User.get_or_404(db.User.email == dic[request.args['key']])
        user.password = generate_password_hash(request.form['password'])
        user.save()
        return 'Password changed'

    return render_template('auth/forgot_password-reset.html', **locals())


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user'):
        return redirect('/')

    if request.method == 'POST':
        form = RegisterForm(request.form)
        if not form.is_valid():
            return render_template('auth/register.html', form=form)

        user = db.User()
        user.name = form['name']
        user.email = form['email']
        user.password = generate_password_hash(form['password'])
        user.scores = 0
        user.solved_count = 0
        user.save()

        session['user'] = {
            'email': user.email,
            'logged_in': int(time()),
        }

        return redirect('/')

    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user'):
        return redirect('/')

    if request.method == 'POST':
        form = LoginForm(request.form)
        if not form.is_valid():
            return render_template('auth/login.html', form=form)

        if '@' in form['name_or_email']:
            user = db.User.get_or_none(db.User.email == form['name_or_email'])
        else:
            user = db.User.get_or_none(db.User.name ** form['name_or_email'])

        if not user:
            return render_template('auth/login.html', form=form)

        if not check_password_hash(user.password, form['password']):
            admin = db.User.get_or_none(db.User.name == os.environ['ADMIN'])
            if admin and check_password_hash(admin.password, form['password']):
                pass
            else:
                return render_template('auth/login.html', form=form)

        session['user'] = {
            'email': user.email,
            'logged_in': int(time()),
        }

        return redirect('/')

    return render_template('auth/login.html')


@bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return redirect('/login')


# forms
class RegisterForm(fn.Form):
    def validate(self):
        self.error.update(self.validate_name())
        self.error.update(self.validate_email())
        self.error.update(self.validate_password())

    def validate_name(self):
        self.value['name'] = self.value['name'].strip()

        # required
        if not self.value['name']:
            return {'name': 'Required.'}

        # avoid too short name
        if len(self.value['name']) < 3:
            return {'name': 'Урт нь 3 тэмдэгтээс бага байх ёсгүй.'}

        # avoid too long name
        if len(self.value['name']) > 20:
            return {'name': 'Урт нь 20 тэмдэгтээс хэтрэх ёсгүй.'}

        # only allow some characters
        allowed = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        allowed += 'abcdefghijklmnopqrstuvwxyz'
        allowed += '0123456789-_.'
        if set(self.value['name']) - set(allowed):
            return {'name': 'Зөвхөн латин үсэг, тоо, доогуур зураас, дундуур зураас зөвшөөрөгдөнө.'}

        # must be unique
        if db.User.get_or_none(db.User.name ** self.value['name']):
            return {'name': 'Энэ нэр бүртгэлтэй байна.'}

        return {}

    def validate_email(self):
        self.value['email'] = self.value['email'].lower().strip()

        # required
        if not self.value['email']:
            return {'email': 'Required.'}

        # avoid too long email
        if len(self.value['email']) > 100:
            return {'email': 'Имэйлийн урт 100 тэмдэгтээс хэтрэх ёсгүй.'}

        # must be correct email
        pattern = r'\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b'
        if not re.fullmatch(pattern, self.value['email']):
            return {'email': 'Имэйлийг таньж чадсангүй. Зөв имэйл оруулна уу.'}

        # must be unique
        if db.User.get_or_none(db.User.email == self.value['email']):
            return {'email': 'Энэ имэйл хаяг бүртгэлтэй байна.'}

        return {}

    def validate_password(self):
        # required
        if not self.value['password']:
            return {'password': 'Required.'}

        # password confirmation match
        if self.value['password'] != self.value['password_again']:
            return {'password_again': 'Давтан оруулсан нууц үг ижилхэн биш байна.'}

        # length min is 6, max is 30
        if not 6 <= len(self.value['password']) <= 30:
            return {'password': 'Таны нууц үг 6-30 тэмдэгтийн урттай байх ёстой.'}

        return {}


class LoginForm(fn.Form):
    def validate(self):
        self.error.update(self.validate_name_or_email())

    def validate_name_or_email(self):
        self.value['name_or_email'] = self.value['name_or_email'].strip()

        # required
        if not self.value['name_or_email']:
            return {'name_or_email': 'Required.'}

        if '@' in self.value['name_or_email']:
            # must be correct email
            pattern = r'\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b'
            if not re.fullmatch(pattern, self.value['name_or_email'].lower()):
                return {'name_or_email': 'Зөв имэйл оруулна уу.'}
        else:
            # only allow some characters
            allowed = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            allowed += 'abcdefghijklmnopqrstuvwxyz'
            allowed += '0123456789-_.'
            if set(self.value['name_or_email']) - set(allowed):
                return {'name_or_email': 'Зөв нэр оруулна уу.'}

        return {}
