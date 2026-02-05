import os
import secrets
from urllib.parse import urlencode

import requests
from flask import Blueprint, flash, g, redirect, request, session

import models as db

bp = Blueprint('discord', __name__)

DISCORD_AUTH_URL = 'https://discord.com/oauth2/authorize'
DISCORD_TOKEN_URL = 'https://discord.com/api/v10/oauth2/token'
DISCORD_USER_URL = 'https://discord.com/api/v10/users/@me'

DISCORD_CLIENT_ID = os.environ['DISCORD_CLIENT_ID']
DISCORD_CLIENT_SECRET = os.environ['DISCORD_CLIENT_SECRET']


@bp.route('/link/discord')
def link_discord():
    if not g.user:
        return redirect('/login')
    if g.user.discord_user_id:
        flash('You have already linked a Discord account!', 'error')
        return redirect('/')

    state = secrets.token_urlsafe(32)
    session['discord_oauth_state'] = state

    redirect_uri = request.host_url + 'link/discord/callback'
    params = {
        'client_id': DISCORD_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'identify',
        'state': state,
    }
    return redirect(f'{DISCORD_AUTH_URL}?{urlencode(params)}')


@bp.route('/link/discord/callback')
def link_discord_callback():
    if not g.user:
        return redirect('/login')
    if g.user.discord_user_id:
        flash('You have already linked a Discord account!', 'error')
        return redirect('/')

    stored_state = session.pop('discord_oauth_state', None)
    if not stored_state or stored_state != request.args.get('state'):
        flash('Failed to link a Discord account. Please try again.', 'error')
        return redirect('/')
    if request.args.get('error'):
        flash('Discord linking was cancelled.', 'error')
        return redirect('/')
    code = request.args.get('code')
    if not code:
        flash('Failed to link a Discord account. Please try again.', 'error')
        return redirect('/')

    redirect_uri = request.host_url + 'link/discord/callback'
    token_data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
    }
    token_response = requests.post(DISCORD_TOKEN_URL, data=token_data)
    if token_response.status_code != 200:
        flash('Failed to link a Discord account. Please try again.', 'error')
        return redirect('/')
    access_token = token_response.json().get('access_token')
    if not access_token:
        flash('Failed to link a Discord account. Please try again.', 'error')
        return redirect('/')

    headers = {'Authorization': f'Bearer {access_token}'}
    user_response = requests.get(DISCORD_USER_URL, headers=headers)
    if user_response.status_code != 200:
        flash('Failed to link a Discord account. Please try again.', 'error')
        return redirect('/')

    discord_user = user_response.json()
    discord_user_id = discord_user.get('id')
    if not discord_user_id:
        flash('Failed to link a Discord account. Please try again.', 'error')
        return redirect('/')

    existing_user = db.User.get_or_none(db.User.discord_user_id == discord_user_id)
    if existing_user and existing_user.id != g.user.id:
        flash('This Discord account is already associated with other user!', 'error')
        return redirect('/')

    g.user.discord_user_id = discord_user_id
    g.user.save()

    flash('Linked a Discord account successfully!', 'success')
    return redirect('/')
